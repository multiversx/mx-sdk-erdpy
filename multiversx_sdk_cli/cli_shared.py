import argparse
import ast
import copy
import sys
from argparse import FileType
from typing import Any, Dict, List, Text, cast

from multiversx_sdk_core import Address
from multiversx_sdk_network_providers.proxy_network_provider import \
    ProxyNetworkProvider

from multiversx_sdk_cli import config, errors, utils
from multiversx_sdk_cli.accounts import Account, LedgerAccount
from multiversx_sdk_cli.cli_output import CLIOutputBuilder
from multiversx_sdk_cli.cli_password import (load_guardian_password,
                                             load_password)
from multiversx_sdk_cli.constants import (DEFAULT_TX_VERSION,
                                          TRANSACTION_OPTIONS_TX_GUARDED)
from multiversx_sdk_cli.errors import ArgumentsNotProvidedError
from multiversx_sdk_cli.interfaces import ITransaction
from multiversx_sdk_cli.ledger.ledger_functions import do_get_ledger_address
from multiversx_sdk_cli.simulation import Simulator
from multiversx_sdk_cli.transactions import send_and_wait_for_result
from multiversx_sdk_cli.utils import log_explorer_transaction
from multiversx_sdk_cli.ux import show_warning


def wider_help_formatter(prog: Text):
    return argparse.RawDescriptionHelpFormatter(prog, max_help_position=50, width=120)


def add_group_subparser(subparsers: Any, group: str, description: str) -> Any:
    parser = subparsers.add_parser(
        group,
        usage=f"mxpy {group} COMMAND [-h] ...",
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser._positionals.title = "COMMANDS"
    parser._optionals.title = "OPTIONS"

    return parser


def build_group_epilog(subparsers: Any) -> str:
    epilog = """
----------------
COMMANDS summary
----------------
"""
    for choice, sub in subparsers.choices.items():
        description_first_line = sub.description.splitlines()[0]
        epilog += f"{choice.ljust(30)} {description_first_line}\n"

    return epilog


def add_command_subparser(subparsers: Any, group: str, command: str, description: str):
    return subparsers.add_parser(
        command,
        usage=f"mxpy {group} {command} [-h] ...",
        description=description,
        formatter_class=wider_help_formatter
    )


def add_tx_args(args: List[str], sub: Any, with_nonce: bool = True, with_receiver: bool = True, with_data: bool = True, with_estimate_gas: bool = False, with_guardian: bool = False):
    if with_nonce:
        sub.add_argument("--nonce", type=int, required=not ("--recall-nonce" in args), help="# the nonce for the transaction")
        sub.add_argument("--recall-nonce", action="store_true", default=False, help="⭮ whether to recall the nonce when creating the transaction (default: %(default)s)")

    if with_receiver:
        sub.add_argument("--receiver", required=True, help="🖄 the address of the receiver")
        sub.add_argument("--receiver-username", required=False, help="🖄 the username of the receiver")

    sub.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE, help="⛽ the gas price (default: %(default)d)")
    sub.add_argument("--gas-limit", required=not ("--estimate-gas" in args), help="⛽ the gas limit")
    if with_estimate_gas:
        sub.add_argument("--estimate-gas", action="store_true", default=False, help="⛽ whether to estimate the gas limit (default: %(default)d)")

    sub.add_argument("--value", default="0", help="the value to transfer (default: %(default)s)")

    if with_data:
        sub.add_argument("--data", default="", help="the payload, or 'memo' of the transaction (default: %(default)s)")

    sub.add_argument("--chain", help="the chain identifier")
    sub.add_argument("--version", type=int, default=DEFAULT_TX_VERSION, help="the transaction version (default: %(default)s)")

    if with_guardian:
        add_guardian_args(sub)

    sub.add_argument("--options", type=int, default=0, help="the transaction options (default: 0)")


def add_guardian_args(sub: Any):
    sub.add_argument("--guardian", type=str, help="the address of the guradian", default="")
    sub.add_argument("--guardian-service-url", type=str, help="the url of the guardian service", default="")
    sub.add_argument("--guardian-2fa-code", type=str, help="the 2fa code for the guardian", default="")


def add_wallet_args(args: List[str], sub: Any):
    sub.add_argument("--pem", required=check_if_sign_method_required(args, "--pem"), help="🔑 the PEM file, if keyfile not provided")
    sub.add_argument("--pem-index", type=int, default=0, help="🔑 the index in the PEM file (default: %(default)s)")
    sub.add_argument("--keyfile", required=check_if_sign_method_required(args, "--keyfile"), help="🔑 a JSON keyfile, if PEM not provided")
    sub.add_argument("--passfile", help="🔑 a file containing keyfile's password, if keyfile provided")
    sub.add_argument("--ledger", action="store_true", required=check_if_sign_method_required(args, "--ledger"), default=False, help="🔐 bool flag for signing transaction using ledger")
    sub.add_argument("--ledger-account-index", type=int, default=0, help="🔐 the index of the account when using Ledger")
    sub.add_argument("--ledger-address-index", type=int, default=0, help="🔐 the index of the address when using Ledger")
    sub.add_argument("--sender-username", required=False, help="🖄 the username of the sender")


def add_guardian_wallet_args(args: List[str], sub: Any):
    sub.add_argument("--guardian-pem", required=check_if_sign_method_required(args, "--guardian-pem"), help="🔑 the PEM file, if keyfile not provided")
    sub.add_argument("--guardian-pem-index", type=int, default=0, help="🔑 the index in the PEM file (default: %(default)s)")
    sub.add_argument("--guardian-keyfile", required=check_if_sign_method_required(args, "--guardian-keyfile"), help="🔑 a JSON keyfile, if PEM not provided")
    sub.add_argument("--guardian-passfile", help="🔑 a file containing keyfile's password, if keyfile provided")
    sub.add_argument("--guardian-ledger", action="store_true", required=check_if_sign_method_required(args, "--guardian-ledger"), default=False, help="🔐 bool flag for signing transaction using ledger")
    sub.add_argument("--guardian-ledger-account-index", type=int, default=0, help="🔐 the index of the account when using Ledger")
    sub.add_argument("--guardian-ledger-address-index", type=int, default=0, help="🔐 the index of the address when using Ledger")


def add_proxy_arg(sub: Any):
    sub.add_argument("--proxy", help="🔗 the URL of the proxy")


def add_outfile_arg(sub: Any, what: str = ""):
    what = f"({what})" if what else ""
    sub.add_argument("--outfile", type=FileType("w"), default=sys.stdout, help=f"where to save the output {what} (default: stdout)")


def add_infile_arg(sub: Any, what: str = ""):
    what = f"({what})" if what else ""
    sub.add_argument("--infile", type=FileType("r"), required=True, help=f"input file {what}")


def add_omit_fields_arg(sub: Any):
    sub.add_argument("--omit-fields", default="[]", type=str, required=False, help="omit fields in the output payload (default: %(default)s)")


def add_token_transfers_arg(sub: Any):
    sub.add_argument("--token-transfers", nargs='+',
                     help="token transfers for transfer & execute, as [token, amount] "
                     "E.g. --token-transfers NFT-123456-0a 1 ESDT-987654 100000000")


def add_multisig_address_arg(sub: Any):
    sub.add_argument("--multisig", help="the address of the multisig contract")


def add_multisig_view_address_arg(sub: Any):
    sub.add_argument("--multisig-view", help="the address of the multisig-view contract")


def add_multisig_action_arg(sub: Any):
    sub.add_argument("--action-id", help="an integer representing the ID of the action; can also be `all`")


def parse_omit_fields_arg(args: Any) -> List[str]:
    literal = args.omit_fields
    parsed = ast.literal_eval(literal)
    return cast(List[str], parsed)


def prepare_account(args: Any):
    if args.pem:
        account = Account(pem_file=args.pem, pem_index=args.pem_index)
    elif args.keyfile:
        password = load_password(args)
        account = Account(key_file=args.keyfile, password=password)
    elif args.ledger:
        account = LedgerAccount(account_index=args.ledger_account_index, address_index=args.ledger_address_index)
    else:
        raise errors.NoWalletProvided()

    return account


def prepare_guardian_account(args: Any):
    if args.guardian_pem:
        account = Account(pem_file=args.guardian_pem, pem_index=args.guardian_pem_index)
    elif args.guardian_keyfile:
        password = load_guardian_password(args)
        account = Account(key_file=args.guardian_keyfile, password=password)
    elif args.guardian_ledger:
        address = do_get_ledger_address(account_index=args.guardian_ledger_account_index, address_index=args.guardian_ledger_address_index)
        account = Account(Address.new_from_bech32(address))
    else:
        raise errors.NoWalletProvided()

    return account


def prepare_nonce_in_args(args: Any):
    if args.recall_nonce and not args.proxy:
        raise ArgumentsNotProvidedError("When using `--recall-nonce`, `--proxy` must be provided, as well")

    if args.recall_nonce:
        account = prepare_account(args)
        account.sync_nonce(ProxyNetworkProvider(args.proxy))
        args.nonce = account.nonce


def prepare_chain_id_in_args(args: Any):
    if not args.chain and not args.proxy:
        raise ArgumentsNotProvidedError("chain ID cannot be decided: `--chain` or `--proxy` should be provided")

    if args.chain and args.proxy:
        proxy = ProxyNetworkProvider(args.proxy)
        fetched_chain_id = proxy.get_network_config().chain_id

        if args.chain != fetched_chain_id:
            show_warning(f"The chain ID you have provided does not match the chain ID you got from the proxy. Will use the proxy's value: '{fetched_chain_id}'")
            args.chain = fetched_chain_id
            return
        # if the CLI provided chain ID is correct, we do not patch the arguments
        return

    if args.chain:
        return
    elif args.proxy:
        proxy = ProxyNetworkProvider(args.proxy)
        args.chain = proxy.get_network_config().chain_id


def add_broadcast_args(sub: Any, simulate: bool = True, relay: bool = False):
    sub.add_argument("--send", action="store_true", default=False, help="✓ whether to broadcast the transaction (default: %(default)s)")

    if simulate:
        sub.add_argument("--simulate", action="store_true", default=False, help="whether to simulate the transaction (default: %(default)s)")
    if relay:
        sub.add_argument("--relay", action="store_true", default=False, help="whether to relay the transaction (default: %(default)s)")


def check_broadcast_args(args: Any):
    if hasattr(args, "relay") and args.relay and args.send:
        raise errors.BadUsage("Cannot directly send a relayed transaction. Use 'mxpy tx new --relay' first, then 'mxpy tx send --data-file'")
    if args.send and args.simulate:
        raise errors.BadUsage("Cannot both 'simulate' and 'send' a transaction")


def check_guardian_and_options_args(args: Any):
    check_guardian_args(args)
    if args.guardian:
        check_options_for_guarded_tx(args.options)


def check_guardian_args(args: Any):
    if args.guardian:
        if should_sign_with_cosigner_service(args) and should_sign_with_guardian_key(args):
            raise errors.BadUsage("Guarded tx should be signed using either a cosigning service or a guardian key")

        if not should_sign_with_cosigner_service(args) and not should_sign_with_guardian_key(args):
            raise errors.BadUsage("Missing guardian signing arguments")


def should_sign_with_cosigner_service(args: Any) -> bool:
    return all([args.guardian_service_url, args.guardian_2fa_code])


def should_sign_with_guardian_key(args: Any) -> bool:
    return any([args.guardian_pem, args.guardian_keyfile, args.guardian_ledger])


def check_options_for_guarded_tx(options: int):
    if not options & TRANSACTION_OPTIONS_TX_GUARDED == TRANSACTION_OPTIONS_TX_GUARDED:
        raise errors.BadUsage("Invalid guarded transaction's options. The second least significant bit must be set.")


def send_or_simulate(tx: ITransaction, args: Any, dump_output: bool = True) -> CLIOutputBuilder:
    proxy = ProxyNetworkProvider(args.proxy)

    is_set_wait_result = hasattr(args, "wait_result") and args.wait_result
    is_set_send = hasattr(args, "send") and args.send
    is_set_simulate = hasattr(args, "simulate") and args.simulate

    send_wait_result = is_set_wait_result and is_set_send and not is_set_simulate
    send_only = is_set_send and not (is_set_wait_result or is_set_simulate)
    simulate = is_set_simulate and not (send_only or send_wait_result)

    output_builder = CLIOutputBuilder()
    output_builder.set_emitted_transaction(tx)
    outfile = args.outfile if hasattr(args, "outfile") else None

    try:
        if send_wait_result:
            transaction_on_network = send_and_wait_for_result(tx, proxy, args.timeout)
            output_builder.set_awaited_transaction(transaction_on_network)
        elif send_only:
            hash = proxy.send_transaction(tx)
            output_builder.set_emitted_transaction_hash(hash)
        elif simulate:
            simulation = Simulator(proxy).run(tx)
            output_builder.set_simulation_results(simulation)
    finally:
        output_transaction = output_builder.build()

        if dump_output:
            utils.dump_out_json(output_transaction, outfile=outfile)

        if send_only:
            log_explorer_transaction(
                chain=output_transaction["emittedTransaction"]["chainID"],
                transaction_hash=output_transaction["emittedTransactionHash"]
            )

    return output_builder


def check_if_sign_method_required(args: List[str], checked_method: str) -> bool:
    methods = ["--pem", "--keyfile", "--ledger"]
    rest_of_methods: List[str] = []
    for method in methods:
        if method != checked_method:
            rest_of_methods.append(method)

    for method in rest_of_methods:
        if utils.is_arg_present(args, method):
            return False

    return True


def convert_args_object_to_args_list(args: Any) -> List[str]:
    arguments = copy.deepcopy(args)
    args_dict: Dict[str, Any] = arguments.__dict__

    # delete the function key because we don't need to pass it along
    args_dict.pop("func", None)

    args_list: List[str] = []
    for key, val in args_dict.items():
        modified_key = "--" + key.replace("_", "-")

        if isinstance(val, bool) and val:
            args_list.extend([modified_key])
            continue

        if val:
            args_list.extend([modified_key, val])

    return args_list
