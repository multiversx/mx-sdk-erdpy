import base64
import json
import logging
import time
from typing import Any, Dict, Optional, Protocol, Sequence, TextIO, Tuple

from multiversx_sdk_core import Address, Transaction, TransactionPayload

from multiversx_sdk_cli import errors
from multiversx_sdk_cli.accounts import Account, LedgerAccount
from multiversx_sdk_cli.cli_password import (load_guardian_password,
                                             load_password)
from multiversx_sdk_cli.cosign_transaction import cosign_transaction
from multiversx_sdk_cli.errors import NoWalletProvided
from multiversx_sdk_cli.interfaces import ITransaction
from multiversx_sdk_cli.ledger.ledger_functions import do_get_ledger_address

logger = logging.getLogger("transactions")


class ITransactionOnNetwork(Protocol):
    hash: str
    is_completed: Optional[bool]

    def to_dictionary(self) -> Dict[str, Any]:
        ...


class INetworkProvider(Protocol):
    def send_transaction(self, transaction: ITransaction) -> str:
        ...

    def send_transactions(self, transactions: Sequence[ITransaction]) -> Tuple[int, Dict[str, str]]:
        ...

    def get_transaction(self, tx_hash: str, with_process_status: Optional[bool] = False) -> ITransactionOnNetwork:
        ...


class JSONTransaction:
    def __init__(self) -> None:
        self.hash = ""
        self.nonce = 0
        self.value = "0"
        self.receiver = ""
        self.sender = ""
        self.senderUsername = ""
        self.receiverUsername = ""
        self.gasPrice = 0
        self.gasLimit = 0
        self.data: str = ""
        self.chainID = ""
        self.version = 0
        self.options = 0
        self.signature = ""
        self.guardian = ""
        self.guardianSignature = ""


def do_prepare_transaction(args: Any) -> Transaction:
    account = Account()
    if args.ledger:
        account = LedgerAccount(account_index=args.ledger_account_index, address_index=args.ledger_address_index)
    if args.pem:
        account = Account(pem_file=args.pem, pem_index=args.pem_index)
    elif args.keyfile:
        password = load_password(args)
        account = Account(key_file=args.keyfile, password=password)

    tx = Transaction(
        chain_id=args.chain,
        sender=account.address.to_bech32(),
        receiver=args.receiver,
        gas_limit=int(args.gas_limit),
        sender_username=getattr(args, "sender_username", ""),
        receiver_username=getattr(args, "receiver_username", ""),
        gas_price=int(args.gas_price),
        data=str(args.data).encode(),
        nonce=int(args.nonce),
        amount=int(args.value),
        version=int(args.version),
        options=int(args.options)
    )

    if args.guardian:
        tx.guardian = args.guardian

    tx.signature = bytes.fromhex(account.sign_transaction(tx))
    tx = sign_tx_by_guardian(args, tx)

    return tx


def sign_tx_by_guardian(args: Any, tx: Transaction) -> Transaction:
    try:
        guardian_account = get_guardian_account_from_args(args)
    except NoWalletProvided:
        guardian_account = None

    if guardian_account:
        tx.guardian_signature = bytes.fromhex(guardian_account.sign_transaction(tx))
    elif args.guardian:
        tx = cosign_transaction(tx, args.guardian_service_url, args.guardian_2fa_code)  # type: ignore

    return tx


# TODO: this is duplicated code; a proper refactoring will come later
def get_guardian_account_from_args(args: Any):
    if args.guardian_pem:
        account = Account(pem_file=args.guardian_pem, pem_index=args.guardian_pem_index)
    elif args.guardian_keyfile:
        password = load_guardian_password(args)
        account = Account(key_file=args.guardian_keyfile, password=password)
    elif args.guardian_ledger:
        address = do_get_ledger_address(account_index=args.guardian_ledger_account_index, address_index=args.guardian_ledger_address_index)
        account = Account(address=Address.new_from_bech32(address))
    else:
        raise errors.NoWalletProvided()

    return account


def send_and_wait_for_result(transaction: ITransaction, proxy: INetworkProvider, timeout: int) -> ITransactionOnNetwork:
    if not transaction.signature:
        raise errors.TransactionIsNotSigned()

    txOnNetwork = _send_transaction_and_wait_for_result(proxy, transaction, timeout)
    return txOnNetwork


def _send_transaction_and_wait_for_result(proxy: INetworkProvider, payload: ITransaction, num_seconds_timeout: int = 100) -> ITransactionOnNetwork:
    AWAIT_TRANSACTION_PERIOD = 5

    tx_hash = proxy.send_transaction(payload)
    num_periods_to_wait = int(num_seconds_timeout / AWAIT_TRANSACTION_PERIOD)

    for _ in range(0, num_periods_to_wait):
        time.sleep(AWAIT_TRANSACTION_PERIOD)

        tx = proxy.get_transaction(tx_hash, True)
        if tx.is_completed:
            return tx
        else:
            logger.info("Transaction not yet done.")

    raise errors.KnownError("Took too long to get transaction.")


def tx_to_dictionary_as_inner_for_relayed_V1(tx: Transaction) -> Dict[str, Any]:
    dictionary: Dict[str, Any] = {}

    dictionary["nonce"] = tx.nonce
    dictionary["sender"] = base64.b64encode(Address.new_from_bech32(tx.sender).get_public_key()).decode()
    dictionary["receiver"] = base64.b64encode(Address.new_from_bech32(tx.receiver).get_public_key()).decode()
    dictionary["value"] = tx.amount
    dictionary["gasPrice"] = tx.gas_price
    dictionary["gasLimit"] = tx.gas_limit
    dictionary["data"] = base64.b64encode(tx.data).decode()
    dictionary["signature"] = base64.b64encode(tx.signature).decode()
    dictionary["chainID"] = base64.b64encode(tx.chain_id.encode()).decode()
    dictionary["version"] = tx.version

    if tx.options:
        dictionary["options"] = tx.options

    if tx.guardian:
        guardian = Address.new_from_bech32(tx.guardian).to_hex()
        dictionary["guardian"] = base64.b64encode(bytes.fromhex(guardian)).decode()

    if tx.guardian_signature:
        dictionary["guardianSignature"] = base64.b64encode(tx.guardian_signature).decode()

    if tx.sender_username:
        dictionary["sndUserName"] = base64.b64encode(tx.sender_username.encode()).decode()

    if tx.receiver_username:
        dictionary[f"rcvUserName"] = base64.b64encode(tx.receiver_username.encode()).decode()

    return dictionary


def _dict_to_json(dictionary: Dict[str, Any]) -> bytes:
    serialized = json.dumps(dictionary, separators=(',', ':')).encode("utf8")
    return serialized


def compute_relayed_v1_data(tx: Transaction) -> str:
    inner_dictionary = tx_to_dictionary_as_inner_for_relayed_V1(tx)
    serialized = _dict_to_json(inner_dictionary)
    serialized_hex = serialized.hex()
    return f"relayedTx@{serialized_hex}"


def load_transaction_from_file(f: TextIO) -> Transaction:
    data_json: bytes = f.read().encode()
    fields = json.loads(data_json).get("tx") or json.loads(data_json).get("emittedTransaction")

    instance = JSONTransaction()
    instance.__dict__.update(fields)

    loaded_tx = Transaction(
        chain_id=instance.chainID,
        sender=instance.sender,
        receiver=instance.receiver,
        sender_username=decode_field_value(instance.senderUsername),
        receiver_username=decode_field_value(instance.receiverUsername),
        gas_limit=instance.gasLimit,
        gas_price=instance.gasPrice,
        amount=int(instance.value),
        data=TransactionPayload.from_encoded_str(instance.data).data,
        version=instance.version,
        options=instance.options,
        nonce=instance.nonce
    )

    if instance.guardian:
        loaded_tx.guardian = instance.guardian

    if instance.signature:
        loaded_tx.signature = bytes.fromhex(instance.signature)

    if instance.guardianSignature:
        loaded_tx.guardian_signature = bytes.fromhex(instance.guardianSignature)

    return loaded_tx


def decode_field_value(value: str) -> str:
    return base64.b64decode(value).decode()
