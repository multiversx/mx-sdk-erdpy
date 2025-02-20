from typing import Any

from multiversx_sdk_cli.errors import InvalidArgumentsError


def ensure_required_transaction_args_are_provided(args: Any):
    _ensure_nonce_args(args)
    _ensure_receiver_args(args)
    _ensure_gas_limit_args(args)


def _ensure_nonce_args(args: Any):
    """If nonce is not provided, ensure that recall_nonce is provided. If recall_nonce is provided, ensure that proxy is provided."""
    if hasattr(args, "nonce") and args.nonce is None:
        if not args.recall_nonce:
            raise InvalidArgumentsError("Either --nonce or --recall-nonce must be provided")

        if hasattr(args, "proxy") and not args.proxy:
            raise InvalidArgumentsError("--proxy must be provided if --recall-nonce is used")


def _ensure_receiver_args(args: Any):
    """Ensure that receiver is provided."""
    if hasattr(args, "receiver") and not args.receiver:
        raise InvalidArgumentsError("--receiver must be provided")


def _ensure_gas_limit_args(args: Any):
    """Ensure that gas_limit is provided."""
    if hasattr(args, "gas_limit") and not args.gas_limit:
        if hasattr(args, "estimate_gas") and not args.estimate_gas:
            raise InvalidArgumentsError("If --gas-limit not provided, --estimate-gas must be provided")


def ensure_wallet_args_are_provided(args: Any):
    signing_methods = [args.pem, args.keyfile, args.ledger]

    if all(signing_methods):
        raise InvalidArgumentsError("Only one of --pem, --keyfile, or --ledger must be provided")

    if not any(signing_methods):
        raise InvalidArgumentsError("One of --pem, --keyfile, or --ledger must be provided")


def ensure_relayer_wallet_args_are_provided(args: Any):
    signing_methods = [args.relayer_pem, args.relayer_keyfile, args.relayer_ledger]

    if all(signing_methods):
        raise InvalidArgumentsError(
            "Only one of --relayer-pem, --relayer-keyfile, or --relayer-ledger must be provided"
        )

    if not any(signing_methods):
        raise InvalidArgumentsError("One of --relayer-pem, --relayer-keyfile, or --relayer-ledger must be provided")


def ensure_broadcast_args(args: Any):
    if args.send and args.simulate:
        raise InvalidArgumentsError("Cannot both 'simulate' and 'send' a transaction")


def ensure_chain_id_args(args: Any):
    if not args.chain and not args.proxy:
        raise InvalidArgumentsError("Either --chain or --proxy must be provided")


def ensure_proxy_argument(args: Any):
    if not args.proxy:
        raise InvalidArgumentsError("--proxy must be provided")
