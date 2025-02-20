from typing import Any

from multiversx_sdk import ProxyNetworkProvider, TransactionsFactoryConfig

from multiversx_sdk_cli import cli_shared, errors, utils
from multiversx_sdk_cli.config import get_config_for_network_providers
from multiversx_sdk_cli.delegation import DelegationOperations


def setup_parser(args: list[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "staking-provider", "Staking provider omnitool")
    subparsers = parser.add_subparsers()

    # create new delegation contract
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "create-new-delegation-contract",
        "Create a new delegation system smart contract, transferred value must be "
        "greater than baseIssuingCost + min deposit value",
    )
    _add_common_arguments(args, sub)
    sub.add_argument(
        "--total-delegation-cap",
        required=True,
        help="the total delegation contract capacity",
    )
    sub.add_argument("--service-fee", required=True, help="the delegation contract service fee")
    sub.set_defaults(func=do_create_delegation_contract)

    # get contract address
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "get-contract-address",
        "Get create contract address by transaction hash",
    )
    sub.add_argument("--create-tx-hash", required=True, help="the hash")
    sub.add_argument("--sender", required=False, help="the sender address")
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=get_contract_address_by_deploy_tx_hash)

    # add a new node
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "add-nodes",
        "Add new nodes must be called by the contract owner",
    )
    sub.add_argument("--validators-file", required=True, help="a JSON file describing the Nodes")
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=add_new_nodes)

    # remove nodes
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "remove-nodes",
        "Remove nodes must be called by the contract owner",
    )
    sub.add_argument("--bls-keys", help="a list with the bls keys of the nodes")
    sub.add_argument("--validators-file", help="a JSON file describing the Nodes")
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=remove_nodes)

    # stake nodes
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "stake-nodes",
        "Stake nodes must be called by the contract owner",
    )
    sub.add_argument("--bls-keys", help="a list with the bls keys of the nodes")
    sub.add_argument("--validators-file", help="a JSON file describing the Nodes")
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=stake_nodes)

    # unbond nodes
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "unbond-nodes",
        "Unbond nodes must be called by the contract owner",
    )
    sub.add_argument("--bls-keys", help="a list with the bls keys of the nodes")
    sub.add_argument("--validators-file", help="a JSON file describing the Nodes")
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=unbond_nodes)

    # unstake nodes
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "unstake-nodes",
        "Unstake nodes must be called by the contract owner",
    )
    sub.add_argument("--bls-keys", help="a list with the bls keys of the nodes")
    sub.add_argument("--validators-file", help="a JSON file describing the Nodes")
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=unstake_nodes)

    # unjail nodes
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "unjail-nodes",
        "Unjail nodes must be called by the contract owner",
    )
    sub.add_argument("--bls-keys", help="a list with the bls keys of the nodes")
    sub.add_argument("--validators-file", help="a JSON file describing the Nodes")
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=unjail_nodes)

    # delegate
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "delegate",
        "Delegate funds to a delegation contract",
    )
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=delegate)

    # claim rewards
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "claim-rewards",
        "Claim the rewards earned for delegating",
    )
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=claim_rewards)

    # redelegate rewards
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "redelegate-rewards",
        "Redelegate the rewards earned for delegating",
    )
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=redelegate_rewards)

    # undelegate
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "undelegate",
        "Undelegate funds from a delegation contract",
    )
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=undelegate)

    # withdraw
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "withdraw",
        "Withdraw funds from a delegation contract",
    )
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=withdraw)

    # change service fee
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "change-service-fee",
        "Change service fee must be called by the contract owner",
    )
    sub.add_argument("--service-fee", required=True, help="new service fee value")
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=change_service_fee)

    # modify total delegation cap
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "modify-delegation-cap",
        "Modify delegation cap must be called by the contract owner",
    )
    sub.add_argument("--delegation-cap", required=True, help="new delegation contract capacity")
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=modify_delegation_cap)

    # set automatic activation
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "automatic-activation",
        "Automatic activation must be called by the contract owner",
    )

    sub.add_argument(
        "--set",
        action="store_true",
        required=not (utils.is_arg_present(args, "--unset")),
        help="set automatic activation True",
    )
    sub.add_argument(
        "--unset",
        action="store_true",
        required=not (utils.is_arg_present(args, "--set")),
        help="set automatic activation False",
    )
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=automatic_activation)

    # set redelegate cap
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "redelegate-cap",
        "Redelegate cap must be called by the contract owner",
    )

    sub.add_argument(
        "--set",
        action="store_true",
        required=not (utils.is_arg_present(args, "--unset")),
        help="set redelegate cap True",
    )
    sub.add_argument(
        "--unset",
        action="store_true",
        required=not (utils.is_arg_present(args, "--set")),
        help="set redelegate cap False",
    )
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=redelegate_cap)

    # set metadata
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "set-metadata",
        "Set metadata must be called by the contract owner",
    )

    sub.add_argument("--name", required=True, help="name field in staking provider metadata")
    sub.add_argument("--website", required=True, help="website field in staking provider metadata")
    sub.add_argument(
        "--identifier",
        required=True,
        help="identifier field in staking provider metadata",
    )
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=set_metadata)

    # convert validator to delegation contract
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "make-delegation-contract-from-validator",
        "Create a delegation contract from validator data. Must be called by the node operator",
    )

    sub.add_argument(
        "--max-cap",
        required=True,
        help="total delegation cap in EGLD, fully denominated. Use value 0 for uncapped",
    )
    sub.add_argument(
        "--fee",
        required=True,
        help="service fee as hundredths of percents. (e.g.  a service fee of 37.45 percent is expressed by the integer 3745)",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=make_new_contract_from_validator_data)

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


def ensure_arguments_are_provided_and_prepared(args: Any):
    cli_shared.check_guardian_args(args)
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_chain_id_in_args(args)
    cli_shared.prepare_nonce_in_args(args)


def do_create_delegation_contract(args: Any):
    ensure_arguments_are_provided_and_prepared(args)

    sender = cli_shared.prepare_account(args)
    config = TransactionsFactoryConfig(args.chain)
    delegation = DelegationOperations(config)

    tx = delegation.prepare_transaction_for_new_delegation_contract(sender, args)
    cli_shared.send_or_simulate(tx, args)


def get_contract_address_by_deploy_tx_hash(args: Any):
    args = utils.as_object(args)

    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)

    transaction = proxy.get_transaction(args.create_tx_hash)
    transaction_events = transaction.logs.events
    if len(transaction_events) == 1:
        contract_address = transaction_events[0].address
        print(contract_address.to_bech32())
    else:
        raise errors.ProgrammingError(
            "Tx has more than one event. Make sure it's a staking provider SC Deploy transaction."
        )


def add_new_nodes(args: Any):
    ensure_arguments_are_provided_and_prepared(args)

    sender = cli_shared.prepare_account(args)
    config = TransactionsFactoryConfig(args.chain)
    delegation = DelegationOperations(config)

    tx = delegation.prepare_transaction_for_adding_nodes(sender, args)
    cli_shared.send_or_simulate(tx, args)


def remove_nodes(args: Any):
    _check_if_either_bls_keys_or_validators_file_are_provided(args)
    ensure_arguments_are_provided_and_prepared(args)

    sender = cli_shared.prepare_account(args)
    config = TransactionsFactoryConfig(args.chain)
    delegation = DelegationOperations(config)

    tx = delegation.prepare_transaction_for_removing_nodes(sender, args)
    cli_shared.send_or_simulate(tx, args)


def stake_nodes(args: Any):
    _check_if_either_bls_keys_or_validators_file_are_provided(args)
    ensure_arguments_are_provided_and_prepared(args)

    sender = cli_shared.prepare_account(args)
    config = TransactionsFactoryConfig(args.chain)
    delegation = DelegationOperations(config)

    tx = delegation.prepare_transaction_for_staking_nodes(sender, args)
    cli_shared.send_or_simulate(tx, args)


def _check_if_either_bls_keys_or_validators_file_are_provided(args: Any):
    bls_keys = args.bls_keys
    validators_file = args.validators_file

    if not bls_keys and not validators_file:
        raise errors.BadUsage("No bls keys or validators file provided. Use either `--bls-keys` or `--validators-file`")


def unbond_nodes(args: Any):
    _check_if_either_bls_keys_or_validators_file_are_provided(args)
    ensure_arguments_are_provided_and_prepared(args)

    sender = cli_shared.prepare_account(args)
    config = TransactionsFactoryConfig(args.chain)
    delegation = DelegationOperations(config)

    tx = delegation.prepare_transaction_for_unbonding_nodes(sender, args)
    cli_shared.send_or_simulate(tx, args)


def unstake_nodes(args: Any):
    _check_if_either_bls_keys_or_validators_file_are_provided(args)
    ensure_arguments_are_provided_and_prepared(args)

    sender = cli_shared.prepare_account(args)
    config = TransactionsFactoryConfig(args.chain)
    delegation = DelegationOperations(config)

    tx = delegation.prepare_transaction_for_unstaking_nodes(sender, args)
    cli_shared.send_or_simulate(tx, args)


def unjail_nodes(args: Any):
    _check_if_either_bls_keys_or_validators_file_are_provided(args)
    ensure_arguments_are_provided_and_prepared(args)

    sender = cli_shared.prepare_account(args)
    config = TransactionsFactoryConfig(args.chain)
    delegation = DelegationOperations(config)

    tx = delegation.prepare_transaction_for_unjailing_nodes(sender, args)
    cli_shared.send_or_simulate(tx, args)


def delegate(args: Any):
    ensure_arguments_are_provided_and_prepared(args)

    if not (int(args.value)):
        raise errors.BadUrlError("Value not provided. Minimum value to delegate is 1 EGLD")

    sender = cli_shared.prepare_account(args)
    config = TransactionsFactoryConfig(args.chain)
    delegation = DelegationOperations(config)

    tx = delegation.prepare_transaction_for_delegating(sender, args)
    cli_shared.send_or_simulate(tx, args)


def claim_rewards(args: Any):
    ensure_arguments_are_provided_and_prepared(args)

    sender = cli_shared.prepare_account(args)
    config = TransactionsFactoryConfig(args.chain)
    delegation = DelegationOperations(config)

    tx = delegation.prepare_transaction_for_claiming_rewards(sender, args)
    cli_shared.send_or_simulate(tx, args)


def redelegate_rewards(args: Any):
    ensure_arguments_are_provided_and_prepared(args)

    sender = cli_shared.prepare_account(args)
    config = TransactionsFactoryConfig(args.chain)
    delegation = DelegationOperations(config)

    tx = delegation.prepare_transaction_for_redelegating_rewards(sender, args)
    cli_shared.send_or_simulate(tx, args)


def undelegate(args: Any):
    ensure_arguments_are_provided_and_prepared(args)

    if not (int(args.value)):
        raise errors.BadUrlError("Value not provided. Minimum value to undelegate is 1 EGLD")

    sender = cli_shared.prepare_account(args)
    config = TransactionsFactoryConfig(args.chain)
    delegation = DelegationOperations(config)

    tx = delegation.prepare_transaction_for_undelegating(sender, args)
    cli_shared.send_or_simulate(tx, args)


def withdraw(args: Any):
    ensure_arguments_are_provided_and_prepared(args)

    sender = cli_shared.prepare_account(args)
    config = TransactionsFactoryConfig(args.chain)
    delegation = DelegationOperations(config)

    tx = delegation.prepare_transaction_for_withdrawing(sender, args)
    cli_shared.send_or_simulate(tx, args)


def change_service_fee(args: Any):
    ensure_arguments_are_provided_and_prepared(args)

    sender = cli_shared.prepare_account(args)
    config = TransactionsFactoryConfig(args.chain)
    delegation = DelegationOperations(config)

    tx = delegation.prepare_transaction_for_changing_service_fee(sender, args)
    cli_shared.send_or_simulate(tx, args)


def modify_delegation_cap(args: Any):
    ensure_arguments_are_provided_and_prepared(args)

    sender = cli_shared.prepare_account(args)
    config = TransactionsFactoryConfig(args.chain)
    delegation = DelegationOperations(config)

    tx = delegation.prepare_transaction_for_modifying_delegation_cap(sender, args)
    cli_shared.send_or_simulate(tx, args)


def automatic_activation(args: Any):
    ensure_arguments_are_provided_and_prepared(args)

    sender = cli_shared.prepare_account(args)
    config = TransactionsFactoryConfig(args.chain)
    delegation = DelegationOperations(config)

    tx = delegation.prepare_transaction_for_automatic_activation(sender, args)
    cli_shared.send_or_simulate(tx, args)


def redelegate_cap(args: Any):
    ensure_arguments_are_provided_and_prepared(args)

    sender = cli_shared.prepare_account(args)
    config = TransactionsFactoryConfig(args.chain)
    delegation = DelegationOperations(config)

    tx = delegation.prepare_transaction_for_redelegate_cap(sender, args)
    cli_shared.send_or_simulate(tx, args)


def set_metadata(args: Any):
    ensure_arguments_are_provided_and_prepared(args)

    sender = cli_shared.prepare_account(args)
    config = TransactionsFactoryConfig(args.chain)
    delegation = DelegationOperations(config)

    tx = delegation.prepare_transaction_for_setting_metadata(sender, args)
    cli_shared.send_or_simulate(tx, args)


def make_new_contract_from_validator_data(args: Any):
    ensure_arguments_are_provided_and_prepared(args)

    sender = cli_shared.prepare_account(args)
    config = TransactionsFactoryConfig(args.chain)
    delegation = DelegationOperations(config)

    tx = delegation.prepare_transaction_for_creating_delegation_contract_from_validator(sender, args)
    cli_shared.send_or_simulate(tx, args)
