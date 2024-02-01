import logging
from typing import Any, List

from multiversx_sdk_core import Address
from multiversx_sdk_core.transaction_factories.transactions_factory_config import \
    TransactionsFactoryConfig

from multiversx_sdk_cli import cli_shared
from multiversx_sdk_cli.contracts import SmartContract
from multiversx_sdk_cli.errors import BadUsage
from multiversx_sdk_cli.multisig import \
    prepare_transaction_for_depositing_funds
from multiversx_sdk_cli.transactions import (compute_relayed_v1_data,
                                             sign_tx_by_guardian)

logger = logging.getLogger("cli.multisig")

MULTISIG_SIGN_ACTION_FUNCTION = "sign"
MULTISIG_UNSIGN_ACTION_FUNCTION = "unsign"
MULTISIG_PERFORM_ACTION_FUNCTION = "performAction"
MULTISIG_DISCARD_ACTION_FUNCTION = "discardAction"
MULTISIG_ADD_NEW_BOARD_MEMBER = "proposeAddBoardMember"
MULTISIG_ADD_PROPOSER = "proposeAddProposer"
MULTISIG_REMOVE_USER = "proposeRemoveUser"
MULTISIG_CHAGE_QUORUM = "proposeChangeQuorum"


def setup_parser(args: List[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "multisig", "Interact with a multisig smart contract")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "multisig", "sign", f"Sign a proposed action.")
    cli_shared.add_multisig_address_arg(sub)
    cli_shared.add_multisig_view_address_arg(sub)
    cli_shared.add_multisig_action_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False, with_guardian=True)

    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")
    cli_shared.add_broadcast_args(sub, relay=True)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    sub.add_argument("--wait-result", action="store_true", default=False,
                     help="signal to wait for the transaction result - only valid if --send is set")
    sub.add_argument("--timeout", default=100, help="max num of seconds to wait for result"
                                                    " - only valid if --wait-result is set")
    sub.set_defaults(func=sign_action)

    sub = cli_shared.add_command_subparser(subparsers, "multisig", "unsign", f"Unsign a previously signed proposed action.")
    cli_shared.add_multisig_address_arg(sub)
    cli_shared.add_multisig_view_address_arg(sub)
    cli_shared.add_multisig_action_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False, with_guardian=True)

    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")
    cli_shared.add_broadcast_args(sub, relay=True)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    sub.add_argument("--wait-result", action="store_true", default=False,
                     help="signal to wait for the transaction result - only valid if --send is set")
    sub.add_argument("--timeout", default=100, help="max num of seconds to wait for result"
                                                    " - only valid if --wait-result is set")
    sub.set_defaults(func=unsign_action)

    sub = cli_shared.add_command_subparser(subparsers, "multisig", "perform-action", f"Perform an action that has reached quorum.")
    cli_shared.add_multisig_address_arg(sub)
    cli_shared.add_multisig_view_address_arg(sub)
    cli_shared.add_multisig_action_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False, with_guardian=True)

    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")
    cli_shared.add_broadcast_args(sub, relay=True)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    sub.add_argument("--wait-result", action="store_true", default=False,
                     help="signal to wait for the transaction result - only valid if --send is set")
    sub.add_argument("--timeout", default=100, help="max num of seconds to wait for result"
                                                    " - only valid if --wait-result is set")
    sub.set_defaults(func=perform_action)

    sub = cli_shared.add_command_subparser(subparsers, "multisig", "discard-action", f"Discard a proposed action.")
    cli_shared.add_multisig_address_arg(sub)
    cli_shared.add_multisig_view_address_arg(sub)
    cli_shared.add_multisig_action_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False, with_guardian=True)

    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")
    cli_shared.add_broadcast_args(sub, relay=True)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    sub.add_argument("--wait-result", action="store_true", default=False,
                     help="signal to wait for the transaction result - only valid if --send is set")
    sub.add_argument("--timeout", default=100, help="max num of seconds to wait for result"
                                                    " - only valid if --wait-result is set")
    sub.set_defaults(func=discard_action)

    sub = cli_shared.add_command_subparser(subparsers, "multisig", "deposit", f"Deposit assets into the multisig contract.")
    cli_shared.add_multisig_address_arg(sub)
    cli_shared.add_multisig_view_address_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False, with_guardian=True)
    cli_shared.add_token_transfers_arg(sub)

    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")
    cli_shared.add_broadcast_args(sub, relay=True)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    sub.add_argument("--wait-result", action="store_true", default=False,
                     help="signal to wait for the transaction result - only valid if --send is set")
    sub.add_argument("--timeout", default=100, help="max num of seconds to wait for result"
                                                    " - only valid if --wait-result is set")
    sub.set_defaults(func=deposit_funds)

    sub = cli_shared.add_command_subparser(subparsers, "multisig", "add-board-member", f"Propose an action to add a new board member.")
    cli_shared.add_multisig_address_arg(sub)
    _add_member_arg(sub)
    cli_shared.add_multisig_view_address_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False, with_guardian=True)

    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")
    cli_shared.add_broadcast_args(sub, relay=True)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    sub.add_argument("--wait-result", action="store_true", default=False,
                     help="signal to wait for the transaction result - only valid if --send is set")
    sub.add_argument("--timeout", default=100, help="max num of seconds to wait for result"
                                                    " - only valid if --wait-result is set")
    sub.set_defaults(func=propose_add_board_member)

    sub = cli_shared.add_command_subparser(subparsers, "multisig", "add-proposer", f"Propose an action to add a new proposer.")
    cli_shared.add_multisig_address_arg(sub)
    _add_member_arg(sub)
    cli_shared.add_multisig_view_address_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False, with_guardian=True)

    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")
    cli_shared.add_broadcast_args(sub, relay=True)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    sub.add_argument("--wait-result", action="store_true", default=False,
                     help="signal to wait for the transaction result - only valid if --send is set")
    sub.add_argument("--timeout", default=100, help="max num of seconds to wait for result"
                                                    " - only valid if --wait-result is set")
    sub.set_defaults(func=propose_add_proposer)

    sub = cli_shared.add_command_subparser(subparsers, "multisig", "remove-user", f"Propose an action to remove an user.")
    cli_shared.add_multisig_address_arg(sub)
    _add_member_arg(sub)
    cli_shared.add_multisig_view_address_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False, with_guardian=True)

    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")
    cli_shared.add_broadcast_args(sub, relay=True)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    sub.add_argument("--wait-result", action="store_true", default=False,
                     help="signal to wait for the transaction result - only valid if --send is set")
    sub.add_argument("--timeout", default=100, help="max num of seconds to wait for result"
                                                    " - only valid if --wait-result is set")
    sub.set_defaults(func=propose_remove_user)

    sub = cli_shared.add_command_subparser(subparsers, "multisig", "quorum", f"Propose an action to change the quorum size.")
    cli_shared.add_multisig_address_arg(sub)
    _add_quorum_arg(sub)
    cli_shared.add_multisig_view_address_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False, with_guardian=True)

    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")
    cli_shared.add_broadcast_args(sub, relay=True)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    sub.add_argument("--wait-result", action="store_true", default=False,
                     help="signal to wait for the transaction result - only valid if --send is set")
    sub.add_argument("--timeout", default=100, help="max num of seconds to wait for result"
                                                    " - only valid if --wait-result is set")
    sub.set_defaults(func=propose_change_quorum_size)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_member_arg(sub: Any):
    sub.add_argument("--proposed-member", required=True, help="the address of the proposed member")


def _add_quorum_arg(sub: Any):
    sub.add_argument("--quorum-size", required=True, help="the proposed quorum size")


def sign_action(args: Any):
    cli_shared.check_guardian_and_options_args(args)
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_chain_id_in_args(args)
    cli_shared.prepare_nonce_in_args(args)

    config = TransactionsFactoryConfig(args.chain)
    contract = SmartContract(config)

    sender = cli_shared.prepare_account(args)
    contract_address = Address.new_from_bech32(args.multisig)

    action_id = args.action_id
    if action_id == "all":
        raise BadUsage("`all` is not supported at the moment. Please use a specific action id")

    tx = contract.prepare_execute_transaction(
        caller=sender,
        contract=contract_address,
        function=MULTISIG_SIGN_ACTION_FUNCTION,
        arguments=[args.action_id],
        gas_limit=int(args.gas_limit),
        value=int(args.value),
        transfers=None,
        nonce=int(args.nonce),
        version=int(args.version),
        options=int(args.options),
        guardian=args.guardian)

    if tx.guardian:
        tx = sign_tx_by_guardian(args, tx)

    if hasattr(args, "relay") and args.relay:
        args.outfile.write(compute_relayed_v1_data(tx))
        return

    cli_shared.send_or_simulate(tx, args)


def unsign_action(args: Any):
    cli_shared.check_guardian_and_options_args(args)
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_chain_id_in_args(args)
    cli_shared.prepare_nonce_in_args(args)

    config = TransactionsFactoryConfig(args.chain)
    contract = SmartContract(config)

    sender = cli_shared.prepare_account(args)
    contract_address = Address.new_from_bech32(args.multisig)

    action_id = args.action_id
    if action_id == "all":
        raise BadUsage("`all` is not supported at the moment. Please use a specific action id")

    tx = contract.prepare_execute_transaction(
        caller=sender,
        contract=contract_address,
        function=MULTISIG_UNSIGN_ACTION_FUNCTION,
        arguments=[args.action_id],
        gas_limit=int(args.gas_limit),
        value=int(args.value),
        transfers=None,
        nonce=int(args.nonce),
        version=int(args.version),
        options=int(args.options),
        guardian=args.guardian)

    if tx.guardian:
        tx = sign_tx_by_guardian(args, tx)

    if hasattr(args, "relay") and args.relay:
        args.outfile.write(compute_relayed_v1_data(tx))
        return

    cli_shared.send_or_simulate(tx, args)


def perform_action(args: Any):
    cli_shared.check_guardian_and_options_args(args)
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_chain_id_in_args(args)
    cli_shared.prepare_nonce_in_args(args)

    config = TransactionsFactoryConfig(args.chain)
    contract = SmartContract(config)

    sender = cli_shared.prepare_account(args)
    contract_address = Address.new_from_bech32(args.multisig)

    action_id = args.action_id
    if action_id == "all":
        raise BadUsage("`all` is not supported at the moment. Please use a specific action id")

    tx = contract.prepare_execute_transaction(
        caller=sender,
        contract=contract_address,
        function=MULTISIG_PERFORM_ACTION_FUNCTION,
        arguments=[args.action_id],
        gas_limit=int(args.gas_limit),
        value=int(args.value),
        transfers=None,
        nonce=int(args.nonce),
        version=int(args.version),
        options=int(args.options),
        guardian=args.guardian)

    if tx.guardian:
        tx = sign_tx_by_guardian(args, tx)

    if hasattr(args, "relay") and args.relay:
        args.outfile.write(compute_relayed_v1_data(tx))
        return

    cli_shared.send_or_simulate(tx, args)


def discard_action(args: Any):
    cli_shared.check_guardian_and_options_args(args)
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_chain_id_in_args(args)
    cli_shared.prepare_nonce_in_args(args)

    config = TransactionsFactoryConfig(args.chain)
    contract = SmartContract(config)

    sender = cli_shared.prepare_account(args)
    contract_address = Address.new_from_bech32(args.multisig)

    action_id = args.action_id
    if action_id == "all":
        raise BadUsage("`all` is not supported at the moment. Please use a specific action id")

    tx = contract.prepare_execute_transaction(
        caller=sender,
        contract=contract_address,
        function=MULTISIG_DISCARD_ACTION_FUNCTION,
        arguments=[args.action_id],
        gas_limit=int(args.gas_limit),
        value=int(args.value),
        transfers=None,
        nonce=int(args.nonce),
        version=int(args.version),
        options=int(args.options),
        guardian=args.guardian)

    if tx.guardian:
        tx = sign_tx_by_guardian(args, tx)

    if hasattr(args, "relay") and args.relay:
        args.outfile.write(compute_relayed_v1_data(tx))
        return

    cli_shared.send_or_simulate(tx, args)


def deposit_funds(args: Any):
    cli_shared.check_guardian_and_options_args(args)
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_chain_id_in_args(args)
    cli_shared.prepare_nonce_in_args(args)

    sender = cli_shared.prepare_account(args)

    tx = prepare_transaction_for_depositing_funds(
        sender=sender,
        multisig=args.multisig,
        chain_id=args.chain,
        value=int(args.value),
        transfers=args.token_transfers,
        gas_limit=int(args.gas_limit),
        nonce=int(args.nonce),
        version=int(args.version),
        options=int(args.options),
        guardian=args.guardian)

    if tx.guardian:
        tx = sign_tx_by_guardian(args, tx)

    if hasattr(args, "relay") and args.relay:
        args.outfile.write(compute_relayed_v1_data(tx))
        return

    cli_shared.send_or_simulate(tx, args)


def propose_add_board_member(args: Any):
    cli_shared.check_guardian_and_options_args(args)
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_chain_id_in_args(args)
    cli_shared.prepare_nonce_in_args(args)

    sender = cli_shared.prepare_account(args)

    config = TransactionsFactoryConfig(args.chain)
    contract = SmartContract(config)

    tx = contract.prepare_execute_transaction(
        caller=sender,
        contract=Address.new_from_bech32(args.multisig),
        function=MULTISIG_ADD_NEW_BOARD_MEMBER,
        arguments=[args.proposed_member],
        gas_limit=int(args.gas_limit),
        value=int(args.value),
        transfers=None,
        nonce=int(args.nonce),
        version=int(args.version),
        options=int(args.options),
        guardian=args.guardian)

    if tx.guardian:
        tx = sign_tx_by_guardian(args, tx)

    if hasattr(args, "relay") and args.relay:
        args.outfile.write(compute_relayed_v1_data(tx))
        return

    cli_shared.send_or_simulate(tx, args)


def propose_add_proposer(args: Any):
    cli_shared.check_guardian_and_options_args(args)
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_chain_id_in_args(args)
    cli_shared.prepare_nonce_in_args(args)

    sender = cli_shared.prepare_account(args)

    config = TransactionsFactoryConfig(args.chain)
    contract = SmartContract(config)

    tx = contract.prepare_execute_transaction(
        caller=sender,
        contract=Address.new_from_bech32(args.multisig),
        function=MULTISIG_ADD_PROPOSER,
        arguments=[args.proposed_member],
        gas_limit=int(args.gas_limit),
        value=int(args.value),
        transfers=None,
        nonce=int(args.nonce),
        version=int(args.version),
        options=int(args.options),
        guardian=args.guardian)

    if tx.guardian:
        tx = sign_tx_by_guardian(args, tx)

    if hasattr(args, "relay") and args.relay:
        args.outfile.write(compute_relayed_v1_data(tx))
        return

    cli_shared.send_or_simulate(tx, args)


def propose_remove_user(args: Any):
    cli_shared.check_guardian_and_options_args(args)
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_chain_id_in_args(args)
    cli_shared.prepare_nonce_in_args(args)

    sender = cli_shared.prepare_account(args)

    config = TransactionsFactoryConfig(args.chain)
    contract = SmartContract(config)

    tx = contract.prepare_execute_transaction(
        caller=sender,
        contract=Address.new_from_bech32(args.multisig),
        function=MULTISIG_REMOVE_USER,
        arguments=[args.proposed_member],
        gas_limit=int(args.gas_limit),
        value=int(args.value),
        transfers=None,
        nonce=int(args.nonce),
        version=int(args.version),
        options=int(args.options),
        guardian=args.guardian)

    if tx.guardian:
        tx = sign_tx_by_guardian(args, tx)

    if hasattr(args, "relay") and args.relay:
        args.outfile.write(compute_relayed_v1_data(tx))
        return

    cli_shared.send_or_simulate(tx, args)


def propose_change_quorum_size(args: Any):
    cli_shared.check_guardian_and_options_args(args)
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_chain_id_in_args(args)
    cli_shared.prepare_nonce_in_args(args)

    sender = cli_shared.prepare_account(args)

    config = TransactionsFactoryConfig(args.chain)
    contract = SmartContract(config)

    tx = contract.prepare_execute_transaction(
        caller=sender,
        contract=Address.new_from_bech32(args.multisig),
        function=MULTISIG_CHAGE_QUORUM,
        arguments=[args.quorum_size],
        gas_limit=int(args.gas_limit),
        value=int(args.value),
        transfers=None,
        nonce=int(args.nonce),
        version=int(args.version),
        options=int(args.options),
        guardian=args.guardian)

    if tx.guardian:
        tx = sign_tx_by_guardian(args, tx)

    if hasattr(args, "relay") and args.relay:
        args.outfile.write(compute_relayed_v1_data(tx))
        return

    cli_shared.send_or_simulate(tx, args)
