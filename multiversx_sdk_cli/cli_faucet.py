import logging
import webbrowser
from enum import Enum
from typing import Any

from multiversx_sdk import Message, NativeAuthClient, NativeAuthClientConfig

from multiversx_sdk_cli import cli_shared
from multiversx_sdk_cli.errors import BadUserInput

logger = logging.getLogger("cli.faucet")


class WebWalletUrls(Enum):
    DEVNET = "https://devnet-wallet.multiversx.com"
    TESTNET = "https://testnet-wallet.multiversx.com"


class ApiUrls(Enum):
    DEVNET = "https://devnet-api.multiversx.com"
    TESTNET = "https://testnet-api.multiversx.com"


def setup_parser(args: list[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "faucet", "Get xEGLD on Devnet or Testnet")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "faucet", "request", "Request xEGLD.")
    cli_shared.add_wallet_args(args, sub)
    sub.add_argument("--chain", required=True, choices=["D", "T"], help="the chain identifier")
    sub.set_defaults(func=faucet)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def faucet(args: Any):
    account = cli_shared.prepare_account(args)
    wallet, api = get_wallet_and_api_urls(args)

    config = NativeAuthClientConfig(origin=wallet, api_url=api)
    client = NativeAuthClient(config)

    init_token = client.initialize()
    token_for_siginig = f"{account.address.to_bech32()}{init_token}"
    signature = account.sign_message(Message(token_for_siginig.encode()))

    access_token = client.get_token(address=account.address, token=init_token, signature=signature.hex())

    logger.info(f"Requesting funds for address: {account.address.to_bech32()}")
    call_web_wallet_faucet(wallet_url=wallet, access_token=access_token)


def call_web_wallet_faucet(wallet_url: str, access_token: str):
    faucet_url = f"{wallet_url}/faucet?accessToken={access_token}"
    webbrowser.open_new_tab(faucet_url)


def get_wallet_and_api_urls(args: Any) -> tuple[str, str]:
    chain: str = args.chain

    if chain.upper() == "D":
        return WebWalletUrls.DEVNET.value, ApiUrls.DEVNET.value

    if chain.upper() == "T":
        return WebWalletUrls.TESTNET.value, ApiUrls.TESTNET.value

    raise BadUserInput("Invalid chain id. Choose between 'D' for devnet and 'T' for testnet.")
