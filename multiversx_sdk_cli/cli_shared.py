import argparse
import ast
import sys
from argparse import FileType
from pathlib import Path
from typing import Any, Text, Union, cast

from multiversx_sdk import (
    Account,
    Address,
    LedgerAccount,
    ProxyNetworkProvider,
    Transaction,
)

from multiversx_sdk_cli import config, errors, utils
from multiversx_sdk_cli.cli_output import CLIOutputBuilder
from multiversx_sdk_cli.cli_password import (
    load_guardian_password,
    load_password,
    load_relayer_password,
)
from multiversx_sdk_cli.constants import DEFAULT_GAS_PRICE, DEFAULT_TX_VERSION
from multiversx_sdk_cli.errors import ArgumentsNotProvidedError, IncorrectWalletError
from multiversx_sdk_cli.interfaces import IAccount
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
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
        formatter_class=wider_help_formatter,
    )


def add_tx_args(
    args: list[str],
    sub: Any,
    with_nonce: bool = True,
    with_receiver: bool = True,
    with_data: bool = True,
    with_estimate_gas: bool = False,
):
    if with_nonce:
        sub.add_argument(
            "--nonce",
            type=int,
            required=False,
            default=None,
            help="# the nonce for the transaction",
        )
        sub.add_argument(
            "--recall-nonce",
            action="store_true",
            default=False,
            help="⭮ whether to recall the nonce when creating the transaction (default: %(default)s)",
        )

    if with_receiver:
        sub.add_argument("--receiver", required=False, help="🖄 the address of the receiver")
        sub.add_argument("--receiver-username", required=False, help="🖄 the username of the receiver")

    sub.add_argument(
        "--gas-price",
        default=DEFAULT_GAS_PRICE,
        type=int,
        help="⛽ the gas price (default: %(default)d)",
    )
    sub.add_argument("--gas-limit", required=False, type=int, help="⛽ the gas limit")

    if with_estimate_gas:
        sub.add_argument(
            "--estimate-gas",
            action="store_true",
            default=False,
            help="⛽ whether to estimate the gas limit (default: %(default)d)",
        )

    sub.add_argument("--value", default="0", type=int, help="the value to transfer (default: %(default)s)")

    if with_data:
        sub.add_argument(
            "--data",
            default="",
            help="the payload, or 'memo' of the transaction (default: %(default)s)",
        )

    sub.add_argument("--chain", type=str, help="the chain identifier")
    sub.add_argument(
        "--version",
        type=int,
        default=DEFAULT_TX_VERSION,
        help="the transaction version (default: %(default)s)",
    )

    sub.add_argument("--relayer", help="the bech32 address of the relayer")

    add_guardian_args(sub)

    sub.add_argument("--options", type=int, default=0, help="the transaction options (default: 0)")


def add_guardian_args(sub: Any):
    sub.add_argument("--guardian", type=str, help="the address of the guradian", default="")
    sub.add_argument(
        "--guardian-service-url",
        type=str,
        help="the url of the guardian service",
        default="",
    )
    sub.add_argument(
        "--guardian-2fa-code",
        type=str,
        help="the 2fa code for the guardian",
        default="",
    )


def add_wallet_args(args: list[str], sub: Any):
    sub.add_argument(
        "--pem",
        required=False,
        help="🔑 the PEM file, if keyfile not provided",
    )
    sub.add_argument(
        "--pem-index",
        type=int,
        default=0,
        help="🔑 the index in the PEM file (default: %(default)s)",
    )
    sub.add_argument(
        "--keyfile",
        required=False,
        help="🔑 a JSON keyfile, if PEM not provided",
    )
    sub.add_argument(
        "--passfile",
        help="🔑 a file containing keyfile's password, if keyfile provided",
    )
    sub.add_argument(
        "--address-index",
        type=int,
        default=None,
        help="🔑 the index of the address in the keyfile; should only be provided for keyfile of kind = mnemonic",
    )
    sub.add_argument(
        "--ledger",
        action="store_true",
        required=False,
        default=False,
        help="🔐 bool flag for signing transaction using ledger",
    )
    sub.add_argument(
        "--ledger-address-index",
        type=int,
        default=0,
        help="🔐 the index of the address when using Ledger",
    )
    sub.add_argument("--sender-username", required=False, help="🖄 the username of the sender")


def add_guardian_wallet_args(args: list[str], sub: Any):
    sub.add_argument(
        "--guardian-pem",
        help="🔑 the PEM file, if keyfile not provided",
    )
    sub.add_argument(
        "--guardian-pem-index",
        type=int,
        default=0,
        help="🔑 the index in the PEM file (default: %(default)s)",
    )
    sub.add_argument(
        "--guardian-keyfile",
        help="🔑 a JSON keyfile, if PEM not provided",
    )
    sub.add_argument(
        "--guardian-passfile",
        help="🔑 a file containing keyfile's password, if keyfile provided",
    )
    sub.add_argument(
        "--guardian-address-index",
        type=int,
        default=None,
        help="🔑 the index of the address in the keyfile; should only be provided for keyfile of kind = mnemonic",
    )
    sub.add_argument(
        "--guardian-ledger",
        action="store_true",
        default=False,
        help="🔐 bool flag for signing transaction using ledger",
    )
    sub.add_argument(
        "--guardian-ledger-address-index",
        type=int,
        default=0,
        help="🔐 the index of the address when using Ledger",
    )


def add_relayed_v3_wallet_args(args: list[str], sub: Any):
    sub.add_argument("--relayer-pem", help="🔑 the PEM file, if keyfile not provided")
    sub.add_argument(
        "--relayer-pem-index",
        type=int,
        default=0,
        help="🔑 the index in the PEM file (default: %(default)s)",
    )
    sub.add_argument("--relayer-keyfile", help="🔑 a JSON keyfile, if PEM not provided")
    sub.add_argument(
        "--relayer-passfile",
        help="🔑 a file containing keyfile's password, if keyfile provided",
    )
    sub.add_argument(
        "--relayer-address-index",
        type=int,
        default=None,
        help="🔑 the index of the address in the keyfile; should only be provided for keyfile of kind = mnemonic",
    )
    sub.add_argument(
        "--relayer-ledger",
        action="store_true",
        default=False,
        help="🔐 bool flag for signing transaction using ledger",
    )
    sub.add_argument(
        "--relayer-ledger-address-index",
        type=int,
        default=0,
        help="🔐 the index of the address when using Ledger",
    )


def add_proxy_arg(sub: Any):
    sub.add_argument("--proxy", type=str, help="🔗 the URL of the proxy")


def add_outfile_arg(sub: Any, what: str = ""):
    what = f"({what})" if what else ""
    sub.add_argument(
        "--outfile",
        type=FileType("w"),
        default=sys.stdout,
        help=f"where to save the output {what} (default: stdout)",
    )


def add_infile_arg(sub: Any, what: str = ""):
    what = f"({what})" if what else ""
    sub.add_argument("--infile", type=FileType("r"), required=True, help=f"input file {what}")


def add_omit_fields_arg(sub: Any):
    sub.add_argument(
        "--omit-fields",
        default="[]",
        type=str,
        required=False,
        help="omit fields in the output payload (default: %(default)s); fields should be passed as a string containing a list of fields (e.g. \"['field1', 'field2']\")",
    )


def add_token_transfers_args(sub: Any):
    sub.add_argument(
        "--token-transfers",
        nargs="+",
        help="token transfers for transfer & execute, as [token, amount] "
        "E.g. --token-transfers NFT-123456-0a 1 ESDT-987654 100000000",
    )


def parse_omit_fields_arg(args: Any) -> list[str]:
    literal = args.omit_fields
    parsed = ast.literal_eval(literal)
    return cast(list[str], parsed)


def prepare_account(args: Any):
    hrp = config.get_address_hrp()

    if args.pem:
        return Account.new_from_pem(file_path=Path(args.pem), index=args.pem_index, hrp=hrp)
    elif args.keyfile:
        password = load_password(args)
        return Account.new_from_keystore(
            file_path=Path(args.keyfile),
            password=password,
            address_index=args.address_index,
            hrp=hrp,
        )
    elif args.ledger:
        return LedgerAccount(address_index=args.ledger_address_index)
    else:
        raise errors.NoWalletProvided()


def prepare_relayer_account(args: Any) -> IAccount:
    hrp = config.get_address_hrp()

    if args.relayer_ledger:
        return LedgerAccount(address_index=args.relayer_ledger_address_index)
    if args.relayer_pem:
        return Account.new_from_pem(file_path=Path(args.relayer_pem), index=args.relayer_pem_index, hrp=hrp)
    elif args.relayer_keyfile:
        password = load_password(args)
        return Account.new_from_keystore(
            file_path=Path(args.relayer_keyfile),
            password=password,
            address_index=args.relayer_address_index,
            hrp=hrp,
        )
    else:
        raise errors.NoWalletProvided()


def prepare_guardian_account(args: Any) -> IAccount:
    hrp = config.get_address_hrp()

    if args.guardian_pem:
        return Account.new_from_pem(file_path=Path(args.guardian_pem), index=args.guardian_pem_index, hrp=hrp)
    elif args.guardian_keyfile:
        password = load_guardian_password(args)
        return Account.new_from_keystore(
            file_path=Path(args.guardian_keyfile),
            password=password,
            address_index=args.guardian_address_index,
            hrp=hrp,
        )
    elif args.guardian_ledger:
        return LedgerAccount(address_index=args.relayer_ledger_address_index)
    else:
        raise errors.NoWalletProvided()


def load_sender_account(args: Any) -> Union[IAccount, None]:
    hrp = config.get_address_hrp()

    if args.pem:
        return Account.new_from_pem(file_path=Path(args.pem), index=args.pem_index, hrp=hrp)
    elif args.keyfile:
        password = load_password(args)
        return Account.new_from_keystore(
            file_path=Path(args.keyfile),
            password=password,
            address_index=args.address_index,
            hrp=hrp,
        )
    elif args.ledger:
        return LedgerAccount(address_index=args.ledger_address_index)

    return None


def load_guardian_account(args: Any) -> Union[IAccount, None]:
    hrp = config.get_address_hrp()

    if args.guardian_pem:
        return Account.new_from_pem(file_path=Path(args.guardian_pem), index=args.guardian_pem_index, hrp=hrp)
    elif args.guardian_keyfile:
        password = load_guardian_password(args)
        return Account.new_from_keystore(
            file_path=Path(args.guardian_keyfile),
            password=password,
            address_index=args.guardian_address_index,
            hrp=hrp,
        )
    elif args.guardian_ledger:
        return LedgerAccount(address_index=args.guardian_ledger_address_index)

    return None


def get_guardian_address(guardian: Union[IAccount, None], args: Any) -> Union[Address, None]:
    address_from_account = guardian.address if guardian else None
    address_from_args = Address.new_from_bech32(args.guardian) if hasattr(args, "guardian") and args.guardian else None

    if not _is_matching_address(address_from_account, address_from_args):
        raise IncorrectWalletError("Guardian wallet does not match the guardian's address set in the arguments.")

    return address_from_account or address_from_args


def get_relayer_address(relayer: Union[IAccount, None], args: Any) -> Union[Address, None]:
    address_from_account = relayer.address if relayer else None
    address_from_args = Address.new_from_bech32(args.relayer) if hasattr(args, "relayer") and args.relayer else None

    if not _is_matching_address(address_from_account, address_from_args):
        raise IncorrectWalletError("Relayer wallet does not match the relayer's address set in the arguments.")

    return address_from_account or address_from_args


def _is_matching_address(account_address: Union[Address, None], args_address: Union[Address, None]) -> bool:
    if account_address and args_address and account_address != args_address:
        return False
    return True


def load_relayer_account(args: Any) -> Union[IAccount, None]:
    hrp = config.get_address_hrp()

    if args.relayer_pem:
        return Account.new_from_pem(file_path=Path(args.relayer_pem), index=args.relayer_pem_index, hrp=hrp)
    elif args.relayer_keyfile:
        password = load_relayer_password(args)
        return Account.new_from_keystore(
            file_path=Path(args.relayer_keyfile),
            password=password,
            address_index=args.relayer_address_index,
            hrp=hrp,
        )
    elif args.relayer_ledger:
        return LedgerAccount(address_index=args.relayer_ledger_address_index)

    return None


def prepare_nonce_in_args(args: Any):
    if args.recall_nonce and not args.proxy:
        raise ArgumentsNotProvidedError("When using `--recall-nonce`, `--proxy` must be provided, as well")

    if args.recall_nonce:
        account = prepare_account(args)
        network_provider_config = config.get_config_for_network_providers()
        proxy = ProxyNetworkProvider(url=args.proxy, config=network_provider_config)
        args.nonce = proxy.get_account(account.address).nonce


def get_current_nonce_for_address(address: Address, proxy_url: Union[str, None]) -> int:
    if not proxy_url:
        raise ArgumentsNotProvidedError("If `--nonce` is not explicitly provided, `--proxy` must be provided")

    network_provider_config = config.get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=proxy_url, config=network_provider_config)
    return proxy.get_account(address).nonce


def prepare_chain_id_in_args(args: Any):
    if not args.chain and not args.proxy:
        raise ArgumentsNotProvidedError("chain ID cannot be decided: `--chain` or `--proxy` should be provided")

    if args.chain and args.proxy:
        network_provider_config = config.get_config_for_network_providers()
        proxy = ProxyNetworkProvider(url=args.proxy, config=network_provider_config)
        fetched_chain_id = proxy.get_network_config().chain_id

        if args.chain != fetched_chain_id:
            show_warning(
                f"The chain ID you have provided does not match the chain ID you got from the proxy. Will use the proxy's value: '{fetched_chain_id}'"
            )
            args.chain = fetched_chain_id
            return
        # if the CLI provided chain ID is correct, we do not patch the arguments
        return

    if args.chain:
        return
    elif args.proxy:
        network_provider_config = config.get_config_for_network_providers()
        proxy = ProxyNetworkProvider(url=args.proxy, config=network_provider_config)
        args.chain = proxy.get_network_config().chain_id


def get_chain_id(chain_id: str, proxy_url: str) -> str:
    if chain_id and proxy_url:
        network_provider_config = config.get_config_for_network_providers()
        proxy = ProxyNetworkProvider(url=proxy_url, config=network_provider_config)
        fetched_chain_id = proxy.get_network_config().chain_id

        if chain_id != fetched_chain_id:
            show_warning(
                f"The chain ID you have provided does not match the chain ID you got from the proxy. Will use the proxy's value: '{fetched_chain_id}'"
            )
        return fetched_chain_id

    if chain_id:
        return chain_id
    else:
        network_provider_config = config.get_config_for_network_providers()
        proxy = ProxyNetworkProvider(url=proxy_url, config=network_provider_config)
        return proxy.get_network_config().chain_id


def add_broadcast_args(sub: Any, simulate: bool = True):
    sub.add_argument(
        "--send",
        action="store_true",
        default=False,
        help="✓ whether to broadcast the transaction (default: %(default)s)",
    )

    if simulate:
        sub.add_argument(
            "--simulate",
            action="store_true",
            default=False,
            help="whether to simulate the transaction (default: %(default)s)",
        )


def check_broadcast_args(args: Any):
    if args.send and args.simulate:
        raise errors.BadUsage("Cannot both 'simulate' and 'send' a transaction")


def check_guardian_args(args: Any):
    if args.guardian:
        if should_sign_with_cosigner_service(args) and should_sign_with_guardian_key(args):
            raise errors.BadUsage("Guarded tx should be signed using either a cosigning service or a guardian key")


def should_sign_with_cosigner_service(args: Any) -> bool:
    return all([args.guardian_service_url, args.guardian_2fa_code])


def should_sign_with_guardian_key(args: Any) -> bool:
    return any([args.guardian_pem, args.guardian_keyfile, args.guardian_ledger])


def send_or_simulate(tx: Transaction, args: Any, dump_output: bool = True) -> CLIOutputBuilder:
    network_provider_config = config.get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=network_provider_config)

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
            output_builder.set_emitted_transaction_hash(hash.hex())
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
                transaction_hash=output_transaction["emittedTransactionHash"],
            )

    return output_builder
