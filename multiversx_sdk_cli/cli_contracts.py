import json
import logging
import os
from pathlib import Path
from typing import Any

from multiversx_sdk import (
    Address,
    AddressComputer,
    ProxyNetworkProvider,
    Transaction,
    TransactionsFactoryConfig,
)
from multiversx_sdk.abi import Abi

from multiversx_sdk_cli import cli_shared, utils
from multiversx_sdk_cli.args_validation import (
    ensure_broadcast_args,
    ensure_chain_id_args,
    ensure_proxy_argument,
    ensure_required_transaction_args_are_provided,
    ensure_wallet_args_are_provided,
)
from multiversx_sdk_cli.cli_output import CLIOutputBuilder
from multiversx_sdk_cli.config import get_config_for_network_providers
from multiversx_sdk_cli.constants import NUMBER_OF_SHARDS
from multiversx_sdk_cli.contract_verification import trigger_contract_verification
from multiversx_sdk_cli.contracts import SmartContract
from multiversx_sdk_cli.docker import is_docker_installed, run_docker
from multiversx_sdk_cli.errors import DockerMissingError
from multiversx_sdk_cli.ux import show_warning

logger = logging.getLogger("cli.contracts")


def setup_parser(args: list[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(
        subparsers,
        "contract",
        "Deploy, upgrade and interact with Smart Contracts",
    )
    subparsers = parser.add_subparsers()

    output_description = CLIOutputBuilder.describe(
        with_contract=True, with_transaction_on_network=True, with_simulation=True
    )

    sub = cli_shared.add_command_subparser(
        subparsers,
        "contract",
        "deploy",
        f"Deploy a Smart Contract.{output_description}",
    )
    _add_bytecode_arg(sub)
    _add_contract_abi_arg(sub)
    _add_metadata_arg(sub)
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)
    _add_arguments_arg(sub)
    sub.add_argument(
        "--wait-result",
        action="store_true",
        default=False,
        help="signal to wait for the transaction result - only valid if --send is set",
    )
    sub.add_argument(
        "--timeout",
        default=100,
        help="max num of seconds to wait for result" " - only valid if --wait-result is set",
    )
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=deploy)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "contract",
        "call",
        f"Interact with a Smart Contract (execute function).{output_description}",
    )
    _add_contract_arg(sub)
    _add_contract_abi_arg(sub)
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)
    _add_function_arg(sub)
    _add_arguments_arg(sub)
    cli_shared.add_token_transfers_args(sub)
    sub.add_argument(
        "--wait-result",
        action="store_true",
        default=False,
        help="signal to wait for the transaction result - only valid if --send is set",
    )
    sub.add_argument(
        "--timeout",
        default=100,
        help="max num of seconds to wait for result" " - only valid if --wait-result is set",
    )
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=call)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "contract",
        "upgrade",
        f"Upgrade a previously-deployed Smart Contract.{output_description}",
    )
    _add_contract_arg(sub)
    _add_contract_abi_arg(sub)
    cli_shared.add_outfile_arg(sub)
    _add_bytecode_arg(sub)
    _add_metadata_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)
    _add_arguments_arg(sub)
    sub.add_argument(
        "--wait-result",
        action="store_true",
        default=False,
        help="signal to wait for the transaction result - only valid if --send is set",
    )
    sub.add_argument(
        "--timeout",
        default=100,
        help="max num of seconds to wait for result" " - only valid if --wait-result is set",
    )
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=upgrade)

    sub = cli_shared.add_command_subparser(
        subparsers, "contract", "query", "Query a Smart Contract (call a pure function)"
    )
    _add_contract_arg(sub)
    _add_contract_abi_arg(sub)
    cli_shared.add_proxy_arg(sub)
    _add_function_arg(sub)
    _add_arguments_arg(sub)
    sub.set_defaults(func=query)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "contract",
        "verify",
        "Verify the authenticity of the code of a deployed Smart Contract",
    )

    sub.add_argument(
        "--packaged-src",
        required=True,
        help="JSON file containing the source code of the contract",
    )

    _add_contract_arg(sub)
    sub.add_argument(
        "--verifier-url",
        required=True,
        help="the url of the service that validates the contract",
    )
    sub.add_argument("--docker-image", required=True, help="the docker image used for the build")
    sub.add_argument(
        "--contract-variant",
        required=False,
        default=None,
        help="in case of a multicontract, specify the contract variant you want to verify",
    )
    cli_shared.add_wallet_args(args, sub)
    sub.set_defaults(func=verify)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "contract",
        "reproducible-build",
        "Build a Smart Contract and get the same output as a previously built Smart Contract",
    )
    _add_project_arg(sub)
    _add_build_options_args(sub)
    sub.add_argument(
        "--docker-image",
        required=True,
        type=str,
        help="the docker image tag used to build the contract",
    )
    sub.add_argument(
        "--contract",
        type=str,
        help="contract to build (contract name, as found in Cargo.toml)",
    )
    sub.add_argument("--no-docker-interactive", action="store_true", default=False)
    sub.add_argument("--no-docker-tty", action="store_true", default=False)
    sub.add_argument(
        "--no-default-platform",
        action="store_true",
        default=False,
        help="do not set DOCKER_DEFAULT_PLATFORM environment variable to 'linux/amd64'",
    )
    sub.set_defaults(func=do_reproducible_build)

    sub = cli_shared.add_command_subparser(
        subparsers, "contract", "build", "Build a Smart Contract project. This command is DISABLED."
    )
    sub.set_defaults(func=build)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_project_arg(sub: Any):
    sub.add_argument(
        "project",
        nargs="?",
        default=os.getcwd(),
        help="the project directory (default: current directory)",
    )


def _add_build_options_args(sub: Any):
    sub.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="set debug flag (default: %(default)s)",
    )
    sub.add_argument(
        "--no-optimization",
        action="store_true",
        default=False,
        help="bypass optimizations (for clang) (default: %(default)s)",
    )
    sub.add_argument(
        "--no-wasm-opt",
        action="store_true",
        default=False,
        help="do not optimize wasm files after the build (default: %(default)s)",
    )
    sub.add_argument(
        "--cargo-target-dir",
        type=str,
        help="for rust projects, forward the parameter to Cargo",
    )
    sub.add_argument(
        "--wasm-symbols",
        action="store_true",
        default=False,
        help="for rust projects, does not strip the symbols from the wasm output. Useful for analysing the bytecode. Creates larger wasm files. Avoid in production (default: %(default)s)",
    )
    sub.add_argument(
        "--wasm-name",
        type=str,
        help="for rust projects, optionally specify the name of the wasm bytecode output file",
    )
    sub.add_argument(
        "--wasm-suffix",
        type=str,
        help="for rust projects, optionally specify the suffix of the wasm bytecode output file",
    )


def _add_bytecode_arg(sub: Any):
    sub.add_argument(
        "--bytecode",
        type=str,
        required=True,
        help="the file containing the WASM bytecode",
    )


def _add_contract_arg(sub: Any):
    sub.add_argument("contract", type=str, help="🖄 the bech32 address of the Smart Contract")


def _add_contract_abi_arg(sub: Any):
    sub.add_argument("--abi", type=str, help="the ABI file of the Smart Contract")


def _add_function_arg(sub: Any):
    sub.add_argument("--function", required=True, type=str, help="the function to call")


def _add_arguments_arg(sub: Any):
    sub.add_argument(
        "--arguments",
        nargs="+",
        help="arguments for the contract transaction, as [number, bech32-address, ascii string, "
        "boolean] or hex-encoded. E.g. --arguments 42 0x64 1000 0xabba str:TOK-a1c2ef true erd1[..]",
    )
    sub.add_argument(
        "--arguments-file",
        type=str,
        help="a json file containing the arguments. ONLY if abi file is provided. "
        "E.g. [{ 'to': 'erd1...', 'amount': 10000000000 }]",
    )


def _add_metadata_arg(sub: Any):
    sub.add_argument(
        "--metadata-not-upgradeable",
        dest="metadata_upgradeable",
        action="store_false",
        help="‼ mark the contract as NOT upgradeable (default: upgradeable)",
    )
    sub.add_argument(
        "--metadata-not-readable",
        dest="metadata_readable",
        action="store_false",
        help="‼ mark the contract as NOT readable (default: readable)",
    )
    sub.add_argument(
        "--metadata-payable",
        dest="metadata_payable",
        action="store_true",
        help="‼ mark the contract as payable (default: not payable)",
    )
    sub.add_argument(
        "--metadata-payable-by-sc",
        dest="metadata_payable_by_sc",
        action="store_true",
        help="‼ mark the contract as payable by SC (default: not payable by SC)",
    )
    sub.set_defaults(metadata_upgradeable=True, metadata_payable=False)


def build(args: Any):
    message = """This command cannot build smart contracts anymore.

The primary tool for building smart contracts is `sc-meta`.
To install `sc-meta` check out the documentation: https://docs.multiversx.com/sdk-and-tools/troubleshooting/rust-setup.
After installing, use the `sc-meta all build` command. To lear more about `sc-meta`, check out this page: https://docs.multiversx.com/developers/meta/sc-meta-cli/#calling-build."""
    show_warning(message)


def deploy(args: Any):
    logger.debug("deploy")

    ensure_required_transaction_args_are_provided(args)
    ensure_wallet_args_are_provided(args)
    ensure_broadcast_args(args)
    ensure_chain_id_args(args)

    sender = cli_shared.prepare_account(args)

    if args.nonce is None:
        nonce = cli_shared.get_current_nonce_for_address(sender.address, args.proxy)
    else:
        nonce = int(args.nonce)

    guardian = cli_shared.load_guardian_account(args)
    guardian_address = cli_shared.get_guardian_address(guardian, args)

    relayer = cli_shared.load_relayer_account(args)
    relayer_address = cli_shared.get_relayer_address(relayer, args)

    chain_id = cli_shared.get_chain_id(args.chain, args.proxy)
    config = TransactionsFactoryConfig(chain_id)

    abi = Abi.load(Path(args.abi)) if args.abi else None
    contract = SmartContract(config, abi)

    arguments, should_prepare_args = _get_contract_arguments(args)

    tx = contract.prepare_deploy_transaction(
        owner=sender,
        bytecode=Path(args.bytecode),
        arguments=arguments,
        should_prepare_args=should_prepare_args,
        upgradeable=args.metadata_upgradeable,
        readable=args.metadata_readable,
        payable=args.metadata_payable,
        payable_by_sc=args.metadata_payable_by_sc,
        gas_limit=int(args.gas_limit),
        value=int(args.value),
        nonce=nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_account=guardian,
        guardian_address=guardian_address,
        relayer_account=relayer,
        relayer_address=relayer_address,
        guardian_service_url=args.guardian_service_url,
        guardian_2fa_code=args.guardian_2fa_code,
    )

    address_computer = AddressComputer(NUMBER_OF_SHARDS)
    contract_address = address_computer.compute_contract_address(deployer=sender.address, deployment_nonce=tx.nonce)

    logger.info("Contract address: %s", contract_address.to_bech32())
    utils.log_explorer_contract_address(args.chain, contract_address.to_bech32())

    _send_or_simulate(tx, contract_address, args)


def call(args: Any):
    logger.debug("call")

    ensure_required_transaction_args_are_provided(args)
    ensure_wallet_args_are_provided(args)
    ensure_broadcast_args(args)
    ensure_chain_id_args(args)

    sender = cli_shared.prepare_account(args)

    if args.nonce is None:
        nonce = cli_shared.get_current_nonce_for_address(sender.address, args.proxy)
    else:
        nonce = int(args.nonce)

    guardian = cli_shared.load_guardian_account(args)
    guardian_address = cli_shared.get_guardian_address(guardian, args)

    relayer = cli_shared.load_relayer_account(args)
    relayer_address = cli_shared.get_relayer_address(relayer, args)

    chain_id = cli_shared.get_chain_id(args.chain, args.proxy)
    config = TransactionsFactoryConfig(chain_id)

    abi = Abi.load(Path(args.abi)) if args.abi else None
    contract = SmartContract(config, abi)

    arguments, should_prepare_args = _get_contract_arguments(args)
    contract_address = Address.new_from_bech32(args.contract)

    tx = contract.prepare_execute_transaction(
        caller=sender,
        contract=contract_address,
        function=args.function,
        arguments=arguments,
        should_prepare_args=should_prepare_args,
        gas_limit=int(args.gas_limit),
        value=int(args.value),
        transfers=args.token_transfers,
        nonce=nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_account=guardian,
        guardian_address=guardian_address,
        relayer_account=relayer,
        relayer_address=relayer_address,
        guardian_service_url=args.guardian_service_url,
        guardian_2fa_code=args.guardian_2fa_code,
    )

    _send_or_simulate(tx, contract_address, args)


def upgrade(args: Any):
    logger.debug("upgrade")

    ensure_required_transaction_args_are_provided(args)
    ensure_wallet_args_are_provided(args)
    ensure_broadcast_args(args)
    ensure_chain_id_args(args)

    sender = cli_shared.prepare_account(args)

    if args.nonce is None:
        nonce = cli_shared.get_current_nonce_for_address(sender.address, args.proxy)
    else:
        nonce = int(args.nonce)

    guardian = cli_shared.load_guardian_account(args)
    guardian_address = cli_shared.get_guardian_address(guardian, args)

    relayer = cli_shared.load_relayer_account(args)
    relayer_address = cli_shared.get_relayer_address(relayer, args)

    chain_id = cli_shared.get_chain_id(args.chain, args.proxy)
    config = TransactionsFactoryConfig(chain_id)

    abi = Abi.load(Path(args.abi)) if args.abi else None
    contract = SmartContract(config, abi)

    arguments, should_prepare_args = _get_contract_arguments(args)
    contract_address = Address.new_from_bech32(args.contract)

    tx = contract.prepare_upgrade_transaction(
        owner=sender,
        contract=contract_address,
        bytecode=Path(args.bytecode),
        arguments=arguments,
        should_prepare_args=should_prepare_args,
        upgradeable=args.metadata_upgradeable,
        readable=args.metadata_readable,
        payable=args.metadata_payable,
        payable_by_sc=args.metadata_payable_by_sc,
        gas_limit=int(args.gas_limit),
        value=int(args.value),
        nonce=nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_account=guardian,
        guardian_address=guardian_address,
        relayer_account=relayer,
        relayer_address=relayer_address,
        guardian_service_url=args.guardian_service_url,
        guardian_2fa_code=args.guardian_2fa_code,
    )

    _send_or_simulate(tx, contract_address, args)


def query(args: Any):
    logger.debug("query")

    ensure_proxy_argument(args)

    # we don't need chainID to query a contract; we use the provided proxy
    factory_config = TransactionsFactoryConfig("")
    abi = Abi.load(Path(args.abi)) if args.abi else None
    contract = SmartContract(factory_config, abi)

    arguments, should_prepare_args = _get_contract_arguments(args)
    contract_address = Address.new_from_bech32(args.contract)

    network_provider_config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=network_provider_config)
    function = args.function

    result = contract.query_contract(
        contract_address=contract_address,
        proxy=proxy,
        function=function,
        arguments=arguments,
        should_prepare_args=should_prepare_args,
    )

    utils.dump_out_json(result)


def _get_contract_arguments(args: Any) -> tuple[list[Any], bool]:
    json_args = json.loads(Path(args.arguments_file).expanduser().read_text()) if args.arguments_file else None

    if json_args and args.arguments:
        raise Exception("Provide either '--arguments' or '--arguments-file'.")

    if json_args:
        if not args.abi:
            raise Exception("Can't use '--arguments-file' without providing the Abi file.")

        return json_args, False
    else:
        return args.arguments, True


def _send_or_simulate(tx: Transaction, contract_address: Address, args: Any):
    output_builder = cli_shared.send_or_simulate(tx, args, dump_output=False)
    output_builder.set_contract_address(contract_address)
    utils.dump_out_json(output_builder.build(), outfile=args.outfile)


def verify(args: Any) -> None:
    contract = Address.new_from_bech32(args.contract)
    verifier_url = args.verifier_url

    packaged_src = Path(args.packaged_src).expanduser().resolve()

    owner = cli_shared.prepare_account(args)
    docker_image = args.docker_image
    contract_variant = args.contract_variant

    trigger_contract_verification(packaged_src, owner, contract, verifier_url, docker_image, contract_variant)
    logger.info("Contract verification request completed!")


def do_reproducible_build(args: Any):
    project_path = args.project
    docker_image = args.docker_image
    contract_path = args.contract
    docker_interactive = not args.no_docker_interactive
    docker_tty = not args.no_docker_tty
    no_default_platform = args.no_default_platform

    project_path = Path(project_path).expanduser().resolve()
    output_path = project_path / "output-docker"
    artifacts_path = output_path / "artifacts.json"

    utils.ensure_folder(output_path)

    options = args.__dict__
    no_wasm_opt = options.get("no_wasm_opt", False)

    if not is_docker_installed():
        raise DockerMissingError()

    logger.info("Starting the docker run...")
    run_docker(
        docker_image,
        project_path,
        contract_path,
        output_path,
        no_wasm_opt,
        docker_interactive,
        docker_tty,
        no_default_platform,
    )

    logger.info("Docker build ran successfully!")
    logger.info(f"Inspect summary of generated artifacts here: {artifacts_path}")
    logger.info("You can deploy you Smart Contract, then verify it using the mxpy contract verify command")
