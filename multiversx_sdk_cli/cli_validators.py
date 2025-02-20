from pathlib import Path
from typing import Any

from multiversx_sdk import Address

from multiversx_sdk_cli import cli_shared, utils
from multiversx_sdk_cli.args_validation import (
    ensure_broadcast_args,
    ensure_chain_id_args,
    ensure_required_transaction_args_are_provided,
    ensure_wallet_args_are_provided,
)
from multiversx_sdk_cli.validators.core import ValidatorsController


def setup_parser(args: list[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(
        subparsers,
        "validator",
        "Stake, UnStake, UnBond, Unjail and other " "actions useful for " "Validators",
    )
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "validator", "stake", "Stake value into the Network")
    _add_common_arguments(args, sub)
    sub.add_argument("--reward-address", default="", help="the reward address")
    sub.add_argument(
        "--validators-file",
        required=not (utils.is_arg_present(args, "--top-up")),
        help="a JSON file describing the Nodes",
    )
    sub.add_argument(
        "--top-up",
        action="store_true",
        default=False,
        required=not (utils.is_arg_present(args, "--validators-file")),
        help="Stake value for top up",
    )
    sub.set_defaults(func=do_stake)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "unstake", "Unstake value")
    _add_common_arguments(args, sub)
    _add_nodes_arg(sub)
    sub.set_defaults(func=do_unstake)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "unjail", "Unjail a Validator Node")
    _add_common_arguments(args, sub)
    _add_nodes_arg(sub)
    sub.set_defaults(func=do_unjail)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "unbond", "Unbond tokens for a bls key")
    _add_common_arguments(args, sub)
    _add_nodes_arg(sub)
    sub.set_defaults(func=do_unbond)

    sub = cli_shared.add_command_subparser(
        subparsers, "validator", "change-reward-address", "Change the reward address"
    )
    _add_common_arguments(args, sub)
    sub.add_argument("--reward-address", required=True, help="the new reward address")
    sub.set_defaults(func=change_reward_address)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "claim", "Claim rewards")
    _add_common_arguments(args, sub)
    sub.set_defaults(func=do_claim)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "validator",
        "unstake-nodes",
        "Unstake-nodes will unstake " "nodes for provided bls keys",
    )
    _add_common_arguments(args, sub)
    _add_nodes_arg(sub)
    sub.set_defaults(func=do_unstake_nodes)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "validator",
        "unstake-tokens",
        "This command will un-stake the "
        "given amount (if value is "
        "greater than the existing "
        "topUp value, it will unStake "
        "one or several nodes)",
    )
    _add_common_arguments(args, sub)
    sub.add_argument("--unstake-value", default=0, help="the unstake value")
    sub.set_defaults(func=do_unstake_tokens)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "unbond-nodes", "It will unBond nodes")
    _add_common_arguments(args, sub)
    _add_nodes_arg(sub)
    sub.set_defaults(func=do_unbond_nodes)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "validator",
        "unbond-tokens",
        "It will unBond tokens, if " "provided value is bigger that " "topUp value will unBond nodes",
    )
    _add_common_arguments(args, sub)
    sub.add_argument("--unbond-value", default=0, help="the unbond value")
    sub.set_defaults(func=do_unbond_tokens)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "validator",
        "clean-registered-data",
        "Deletes duplicated keys " "from registered data",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=do_clean_registered_data)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "validator",
        "restake-unstaked-nodes",
        "It will reStake UnStaked nodes",
    )
    _add_common_arguments(args, sub)
    _add_nodes_arg(sub)
    sub.set_defaults(func=do_restake_unstaked_nodes)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_common_arguments(args: list[str], sub: Any):
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False, with_estimate_gas=True)
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)


def _add_nodes_arg(sub: Any):
    sub.add_argument(
        "--nodes-public-keys",
        required=True,
        help="the public keys of the nodes as CSV (addrA,addrB)",
    )


def do_stake(args: Any):
    validate_args(args)
    sender, nonce = prepare_sender(args)
    guardian, guardian_address = prepare_guardian(args)
    relayer, relayer_address = prepare_relayer(args)

    native_amount = int(args.value)
    gas_limit = 0 if args.estimate_gas else args.gas_limit
    rewards_address = Address.new_from_bech32(args.reward_address) if args.reward_address else None

    controller = ValidatorsController(args.chain)

    if args.top_up:
        tx = controller.create_transaction_for_topping_up(
            sender=sender,
            native_amount=native_amount,
            estimate_gas=args.estimate_gas,
            gas_limit=gas_limit,
            gas_price=args.gas_price,
            nonce=nonce,
            version=args.version,
            options=args.options,
            guardian_account=guardian,
            guardian_address=guardian_address,
            relayer_account=relayer,
            relayer_address=relayer_address,
            guardian_service_url=args.guardian_service_url,
            guardian_2fa_code=args.guardian_2fa_code,
        )
    else:
        validators_file = Path(args.validators_file)
        tx = controller.create_transaction_for_staking(
            sender=sender,
            validators_file=validators_file,
            native_amount=native_amount,
            estimate_gas=args.estimate_gas,
            gas_limit=gas_limit,
            gas_price=args.gas_price,
            nonce=nonce,
            version=args.version,
            options=args.options,
            rewards_address=rewards_address,
            guardian_account=guardian,
            guardian_address=guardian_address,
            relayer_account=relayer,
            relayer_address=relayer_address,
            guardian_service_url=args.guardian_service_url,
            guardian_2fa_code=args.guardian_2fa_code,
        )

    cli_shared.send_or_simulate(tx, args)


def validate_args(args: Any) -> None:
    ensure_required_transaction_args_are_provided(args)
    ensure_wallet_args_are_provided(args)
    ensure_broadcast_args(args)
    ensure_chain_id_args(args)


def prepare_sender(args: Any):
    sender = cli_shared.prepare_account(args)
    nonce = (
        int(args.nonce)
        if args.nonce is not None
        else cli_shared.get_current_nonce_for_address(sender.address, args.proxy)
    )
    return sender, nonce


def prepare_guardian(args: Any):
    guardian = cli_shared.load_guardian_account(args)
    guardian_address = cli_shared.get_guardian_address(guardian, args)
    return guardian, guardian_address


def prepare_relayer(args: Any):
    relayer = cli_shared.load_relayer_account(args)
    relayer_address = cli_shared.get_relayer_address(relayer, args)
    return relayer, relayer_address


def do_unstake(args: Any):
    validate_args(args)
    sender, nonce = prepare_sender(args)
    guardian, guardian_address = prepare_guardian(args)
    relayer, relayer_address = prepare_relayer(args)

    native_amount = int(args.value)
    gas_limit = 0 if args.estimate_gas else args.gas_limit
    keys = args.nodes_public_keys

    controller = ValidatorsController(args.chain)
    tx = controller.create_transaction_for_unstaking(
        sender=sender,
        keys=keys,
        native_amount=native_amount,
        estimate_gas=args.estimate_gas,
        gas_limit=gas_limit,
        gas_price=args.gas_price,
        nonce=nonce,
        version=args.version,
        options=args.options,
        guardian_account=guardian,
        guardian_address=guardian_address,
        relayer_account=relayer,
        relayer_address=relayer_address,
        guardian_service_url=args.guardian_service_url,
        guardian_2fa_code=args.guardian_2fa_code,
    )

    cli_shared.send_or_simulate(tx, args)


def do_unjail(args: Any):
    validate_args(args)
    sender, nonce = prepare_sender(args)
    guardian, guardian_address = prepare_guardian(args)
    relayer, relayer_address = prepare_relayer(args)

    native_amount = int(args.value)
    gas_limit = 0 if args.estimate_gas else args.gas_limit
    keys = args.nodes_public_keys

    controller = ValidatorsController(args.chain)
    tx = controller.create_transaction_for_unjailing(
        sender=sender,
        keys=keys,
        native_amount=native_amount,
        estimate_gas=args.estimate_gas,
        gas_limit=gas_limit,
        gas_price=args.gas_price,
        nonce=nonce,
        version=args.version,
        options=args.options,
        guardian_account=guardian,
        guardian_address=guardian_address,
        relayer_account=relayer,
        relayer_address=relayer_address,
        guardian_service_url=args.guardian_service_url,
        guardian_2fa_code=args.guardian_2fa_code,
    )

    cli_shared.send_or_simulate(tx, args)


def do_unbond(args: Any):
    validate_args(args)
    sender, nonce = prepare_sender(args)
    guardian, guardian_address = prepare_guardian(args)
    relayer, relayer_address = prepare_relayer(args)

    native_amount = int(args.value)
    gas_limit = 0 if args.estimate_gas else args.gas_limit
    keys = args.nodes_public_keys

    controller = ValidatorsController(args.chain)
    tx = controller.create_transaction_for_unbonding(
        sender=sender,
        keys=keys,
        native_amount=native_amount,
        estimate_gas=args.estimate_gas,
        gas_limit=gas_limit,
        gas_price=args.gas_price,
        nonce=nonce,
        version=args.version,
        options=args.options,
        guardian_account=guardian,
        guardian_address=guardian_address,
        relayer_account=relayer,
        relayer_address=relayer_address,
        guardian_service_url=args.guardian_service_url,
        guardian_2fa_code=args.guardian_2fa_code,
    )

    cli_shared.send_or_simulate(tx, args)


def change_reward_address(args: Any):
    validate_args(args)
    sender, nonce = prepare_sender(args)
    guardian, guardian_address = prepare_guardian(args)
    relayer, relayer_address = prepare_relayer(args)

    native_amount = int(args.value)
    gas_limit = 0 if args.estimate_gas else args.gas_limit
    rewards_address = Address.new_from_bech32(args.reward_address)

    controller = ValidatorsController(args.chain)
    tx = controller.create_transaction_for_changing_rewards_address(
        sender=sender,
        rewards_address=rewards_address,
        native_amount=native_amount,
        estimate_gas=args.estimate_gas,
        gas_limit=gas_limit,
        gas_price=args.gas_price,
        nonce=nonce,
        version=args.version,
        options=args.options,
        guardian_account=guardian,
        guardian_address=guardian_address,
        relayer_account=relayer,
        relayer_address=relayer_address,
        guardian_service_url=args.guardian_service_url,
        guardian_2fa_code=args.guardian_2fa_code,
    )

    cli_shared.send_or_simulate(tx, args)


def do_claim(args: Any):
    validate_args(args)
    sender, nonce = prepare_sender(args)
    guardian, guardian_address = prepare_guardian(args)
    relayer, relayer_address = prepare_relayer(args)

    native_amount = int(args.value)
    gas_limit = 0 if args.estimate_gas else args.gas_limit

    controller = ValidatorsController(args.chain)
    tx = controller.create_transaction_for_claiming(
        sender=sender,
        native_amount=native_amount,
        estimate_gas=args.estimate_gas,
        gas_limit=gas_limit,
        gas_price=args.gas_price,
        nonce=nonce,
        version=args.version,
        options=args.options,
        guardian_account=guardian,
        guardian_address=guardian_address,
        relayer_account=relayer,
        relayer_address=relayer_address,
        guardian_service_url=args.guardian_service_url,
        guardian_2fa_code=args.guardian_2fa_code,
    )

    cli_shared.send_or_simulate(tx, args)


def do_unstake_nodes(args: Any):
    validate_args(args)
    sender, nonce = prepare_sender(args)
    guardian, guardian_address = prepare_guardian(args)
    relayer, relayer_address = prepare_relayer(args)

    native_amount = int(args.value)
    gas_limit = 0 if args.estimate_gas else args.gas_limit

    keys = args.nodes_public_keys

    controller = ValidatorsController(args.chain)
    tx = controller.create_transaction_for_unstaking_nodes(
        sender=sender,
        keys=keys,
        native_amount=native_amount,
        estimate_gas=args.estimate_gas,
        gas_limit=gas_limit,
        gas_price=args.gas_price,
        nonce=nonce,
        version=args.version,
        options=args.options,
        guardian_account=guardian,
        guardian_address=guardian_address,
        relayer_account=relayer,
        relayer_address=relayer_address,
        guardian_service_url=args.guardian_service_url,
        guardian_2fa_code=args.guardian_2fa_code,
    )

    cli_shared.send_or_simulate(tx, args)


def do_unstake_tokens(args: Any):
    validate_args(args)
    sender, nonce = prepare_sender(args)
    guardian, guardian_address = prepare_guardian(args)
    relayer, relayer_address = prepare_relayer(args)

    native_amount = int(args.value)
    value = int(args.unstake_value)
    gas_limit = 0 if args.estimate_gas else args.gas_limit

    controller = ValidatorsController(args.chain)
    tx = controller.create_transaction_for_unstaking_tokens(
        sender=sender,
        value=value,
        native_amount=native_amount,
        estimate_gas=args.estimate_gas,
        gas_limit=gas_limit,
        gas_price=args.gas_price,
        nonce=nonce,
        version=args.version,
        options=args.options,
        guardian_account=guardian,
        guardian_address=guardian_address,
        relayer_account=relayer,
        relayer_address=relayer_address,
        guardian_service_url=args.guardian_service_url,
        guardian_2fa_code=args.guardian_2fa_code,
    )

    cli_shared.send_or_simulate(tx, args)


def do_unbond_nodes(args: Any):
    validate_args(args)
    sender, nonce = prepare_sender(args)
    guardian, guardian_address = prepare_guardian(args)
    relayer, relayer_address = prepare_relayer(args)

    native_amount = int(args.value)
    gas_limit = 0 if args.estimate_gas else args.gas_limit

    keys = args.nodes_public_keys

    controller = ValidatorsController(args.chain)
    tx = controller.create_transaction_for_unbonding_nodes(
        sender=sender,
        keys=keys,
        native_amount=native_amount,
        estimate_gas=args.estimate_gas,
        gas_limit=gas_limit,
        gas_price=args.gas_price,
        nonce=nonce,
        version=args.version,
        options=args.options,
        guardian_account=guardian,
        guardian_address=guardian_address,
        relayer_account=relayer,
        relayer_address=relayer_address,
        guardian_service_url=args.guardian_service_url,
        guardian_2fa_code=args.guardian_2fa_code,
    )

    cli_shared.send_or_simulate(tx, args)


def do_unbond_tokens(args: Any):
    validate_args(args)
    sender, nonce = prepare_sender(args)
    guardian, guardian_address = prepare_guardian(args)
    relayer, relayer_address = prepare_relayer(args)

    native_amount = int(args.value)
    value = int(args.unbond_value)
    gas_limit = 0 if args.estimate_gas else args.gas_limit

    controller = ValidatorsController(args.chain)
    tx = controller.create_transaction_for_unbonding_tokens(
        sender=sender,
        value=value,
        native_amount=native_amount,
        estimate_gas=args.estimate_gas,
        gas_limit=gas_limit,
        gas_price=args.gas_price,
        nonce=nonce,
        version=args.version,
        options=args.options,
        guardian_account=guardian,
        guardian_address=guardian_address,
        relayer_account=relayer,
        relayer_address=relayer_address,
        guardian_service_url=args.guardian_service_url,
        guardian_2fa_code=args.guardian_2fa_code,
    )

    cli_shared.send_or_simulate(tx, args)


def do_clean_registered_data(args: Any):
    validate_args(args)
    sender, nonce = prepare_sender(args)
    guardian, guardian_address = prepare_guardian(args)
    relayer, relayer_address = prepare_relayer(args)

    native_amount = int(args.value)
    gas_limit = 0 if args.estimate_gas else args.gas_limit

    controller = ValidatorsController(args.chain)
    tx = controller.create_transaction_for_cleaning_registered_data(
        sender=sender,
        native_amount=native_amount,
        estimate_gas=args.estimate_gas,
        gas_limit=gas_limit,
        gas_price=args.gas_price,
        nonce=nonce,
        version=args.version,
        options=args.options,
        guardian_account=guardian,
        guardian_address=guardian_address,
        relayer_account=relayer,
        relayer_address=relayer_address,
        guardian_service_url=args.guardian_service_url,
        guardian_2fa_code=args.guardian_2fa_code,
    )

    cli_shared.send_or_simulate(tx, args)


def do_restake_unstaked_nodes(args: Any):
    validate_args(args)
    sender, nonce = prepare_sender(args)
    guardian, guardian_address = prepare_guardian(args)
    relayer, relayer_address = prepare_relayer(args)

    native_amount = int(args.value)
    gas_limit = 0 if args.estimate_gas else args.gas_limit
    keys = args.nodes_public_keys

    controller = ValidatorsController(args.chain)
    tx = controller.create_transaction_for_restaking_unstaked_nodes(
        sender=sender,
        keys=keys,
        native_amount=native_amount,
        estimate_gas=args.estimate_gas,
        gas_limit=gas_limit,
        gas_price=args.gas_price,
        nonce=nonce,
        version=args.version,
        options=args.options,
        guardian_account=guardian,
        guardian_address=guardian_address,
        relayer_account=relayer,
        relayer_address=relayer_address,
        guardian_service_url=args.guardian_service_url,
        guardian_2fa_code=args.guardian_2fa_code,
    )

    cli_shared.send_or_simulate(tx, args)
