import base64
import logging
from pathlib import Path
from typing import Any, List, Optional, Protocol, Sequence, Union

from multiversx_sdk_core import (Token, TokenComputer, TokenTransfer,
                                 Transaction, TransactionPayload)
from multiversx_sdk_core.address import Address
from multiversx_sdk_core.transaction_factories import \
    SmartContractTransactionsFactory
from multiversx_sdk_network_providers.interface import IContractQuery

from multiversx_sdk_cli import errors
from multiversx_sdk_cli.accounts import Account
from multiversx_sdk_cli.constants import DEFAULT_HRP
from multiversx_sdk_cli.interfaces import IAddress
from multiversx_sdk_cli.utils import Object

logger = logging.getLogger("contracts")

HEX_PREFIX = "0x"
FALSE_STR_LOWER = "false"
TRUE_STR_LOWER = "true"
STR_PREFIX = "str:"


class INetworkProvider(Protocol):
    def query_contract(self, query: Any) -> 'IContractQueryResponse':
        ...


class QueryResult(Object):
    def __init__(self, as_base64: str, as_hex: str, as_number: Optional[int]):
        self.base64 = as_base64
        self.hex = as_hex
        self.number = as_number


class ContractQuery(IContractQuery):
    def __init__(self, address: IAddress, function: str, value: int, arguments: List[bytes], caller: Optional[IAddress] = None):
        self.contract = address
        self.function = function
        self.caller = caller
        self.value = value
        self.encoded_arguments = [item.hex() for item in arguments]

    def get_contract(self) -> IAddress:
        return self.contract

    def get_function(self) -> str:
        return self.function

    def get_encoded_arguments(self) -> Sequence[str]:
        return self.encoded_arguments

    def get_caller(self) -> Optional[IAddress]:
        return self.caller

    def get_value(self) -> int:
        return self.value


class IContractQueryResponse(Protocol):
    return_data: List[str]
    return_code: str
    return_message: str


class IConfig(Protocol):
    chain_id: str
    min_gas_limit: int
    gas_limit_per_byte: int


class SmartContract:
    def __init__(self, config: IConfig):
        self._factory = SmartContractTransactionsFactory(config, TokenComputer())

    def prepare_deploy_transaction(self,
                                   owner: Account,
                                   bytecode: Path,
                                   arguments: Union[List[str], None],
                                   upgradeable: bool,
                                   readable: bool,
                                   payable: bool,
                                   payable_by_sc: bool,
                                   gas_limit: int,
                                   value: int,
                                   nonce: int,
                                   version: int,
                                   options: int,
                                   guardian: str) -> Transaction:
        args = prepare_args_for_factory(arguments) if arguments else []

        tx = self._factory.create_transaction_for_deploy(
            sender=owner.address,
            bytecode=bytecode,
            gas_limit=gas_limit,
            arguments=args,
            native_transfer_amount=value,
            is_upgradeable=upgradeable,
            is_readable=readable,
            is_payable=payable,
            is_payable_by_sc=payable_by_sc
        )
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian
        tx.signature = bytes.fromhex(owner.sign_transaction(tx))

        return tx

    def prepare_execute_transaction(self,
                                    caller: Account,
                                    contract: IAddress,
                                    function: str,
                                    arguments: Union[List[str], None],
                                    gas_limit: int,
                                    value: int,
                                    transfers: Union[List[str], None],
                                    nonce: int,
                                    version: int,
                                    options: int,
                                    guardian: str) -> Transaction:
        if value and transfers:
            raise errors.BadUsage("Can't send both native and custom tokens")

        token_transfers = self.prepare_token_transfers(transfers) if transfers else []
        args = prepare_args_for_factory(arguments) if arguments else []

        tx = self._factory.create_transaction_for_execute(
            sender=caller.address,
            contract=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=args,
            native_transfer_amount=value,
            token_transfers=token_transfers
        )
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian
        tx.signature = bytes.fromhex(caller.sign_transaction(tx))

        return tx

    def prepare_upgrade_transaction(self,
                                    owner: Account,
                                    contract: IAddress,
                                    bytecode: Path,
                                    arguments: Union[List[str], None],
                                    upgradeable: bool,
                                    readable: bool,
                                    payable: bool,
                                    payable_by_sc: bool,
                                    gas_limit: int,
                                    value: int,
                                    nonce: int,
                                    version: int,
                                    options: int,
                                    guardian: str) -> Transaction:
        args = prepare_args_for_factory(arguments) if arguments else []

        tx = self._factory.create_transaction_for_upgrade(
            sender=owner.address,
            contract=contract,
            bytecode=bytecode,
            gas_limit=gas_limit,
            arguments=args,
            native_transfer_amount=value,
            is_upgradeable=upgradeable,
            is_readable=readable,
            is_payable=payable,
            is_payable_by_sc=payable_by_sc
        )
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian
        tx.signature = bytes.fromhex(owner.sign_transaction(tx))

        return tx

    def prepare_token_transfers(self, transfers: List[str]) -> List[TokenTransfer]:
        token_computer = TokenComputer()
        token_transfers: List[TokenTransfer] = []

        for i in range(0, len(transfers) - 1, 2):
            identifier = transfers[i]
            amount = int(transfers[i + 1])
            nonce = token_computer.extract_nonce_from_extended_identifier(identifier)

            token = Token(identifier, nonce)
            transfer = TokenTransfer(token, amount)
            token_transfers.append(transfer)

        return token_transfers


def query_contract(
    contract_address: IAddress,
    proxy: INetworkProvider,
    function: str,
    arguments: List[Any],
    value: int = 0,
    caller: Optional[IAddress] = None
) -> List[Any]:
    response_data = query_detailed(contract_address, proxy, function, arguments, value, caller)
    return_data = response_data.return_data
    return [_interpret_return_data(data) for data in return_data]


def query_detailed(contract_address: IAddress, proxy: INetworkProvider, function: str, arguments: List[Any],
                   value: int = 0, caller: Optional[IAddress] = None) -> Any:
    arguments = arguments or []
    # Temporary workaround, until we use sdk-core's serializer.
    arguments_hex = [_prepare_argument(arg) for arg in arguments]
    prepared_arguments_bytes = [bytes.fromhex(arg) for arg in arguments_hex]

    query = ContractQuery(contract_address, function, value, prepared_arguments_bytes, caller)

    response = proxy.query_contract(query)
    # Temporary workaround, until we add "isSuccess" on the response class.
    if response.return_code != "ok":
        raise RuntimeError(f"Query failed: {response.return_message}")
    return response


def _interpret_return_data(data: str) -> Any:
    if not data:
        return data

    try:
        as_bytes = base64.b64decode(data)
        as_hex = as_bytes.hex()
        as_number = _interpret_as_number_if_safely(as_hex)

        result = QueryResult(data, as_hex, as_number)
        return result
    except Exception:
        logger.warn(f"Cannot interpret return data: {data}")
        return None


def _interpret_as_number_if_safely(as_hex: str) -> Optional[int]:
    """
    Makes sure the string can be safely converted to an int (and then back to a string).

    See:
        - https://stackoverflow.com/questions/73693104/valueerror-exceeds-the-limit-4300-for-integer-string-conversion 
        - https://github.com/python/cpython/issues/95778
    """
    try:
        return int(str(int(as_hex or "0", 16)))
    except:
        return None


def prepare_execute_transaction_data(function: str, arguments: List[Any]) -> TransactionPayload:
    tx_data = function

    for arg in arguments:
        tx_data += f"@{_prepare_argument(arg)}"

    return TransactionPayload.from_str(tx_data)


def prepare_args_for_factory(arguments: List[str]) -> List[Any]:
    args: List[Any] = []

    for arg in arguments:
        if arg.startswith(HEX_PREFIX):
            args.append(hex_to_bytes(arg))
        elif arg.isnumeric():
            args.append(int(arg))
        elif arg.startswith(DEFAULT_HRP):
            args.append(Address.new_from_bech32(arg))
        elif arg.lower() == FALSE_STR_LOWER:
            args.append(False)
        elif arg.lower() == TRUE_STR_LOWER:
            args.append(True)
        elif arg.startswith(STR_PREFIX):
            args.append(arg[len(STR_PREFIX):])

    return args


def hex_to_bytes(arg: str):
    argument = arg[len(HEX_PREFIX):]
    argument = argument.upper()
    argument = ensure_even_length(argument)
    return bytes.fromhex(argument)


# only used for contract queries and stake operations
def _prepare_argument(argument: Any):
    as_str = str(argument)
    as_hex = _to_hex(as_str)
    return as_hex


def _to_hex(arg: str):
    if arg.startswith(HEX_PREFIX):
        return _prepare_hexadecimal(arg)

    if arg.isnumeric():
        return _prepare_decimal(arg)
    elif arg.startswith(DEFAULT_HRP):
        addr = Address.new_from_bech32(arg)
        return _prepare_hexadecimal(f"{HEX_PREFIX}{addr.hex()}")
    elif arg.lower() == FALSE_STR_LOWER or arg.lower() == TRUE_STR_LOWER:
        as_str = f"{HEX_PREFIX}01" if arg.lower() == TRUE_STR_LOWER else f"{HEX_PREFIX}00"
        return _prepare_hexadecimal(as_str)
    elif arg.startswith(STR_PREFIX):
        as_hex = f"{HEX_PREFIX}{arg[len(STR_PREFIX):].encode('ascii').hex()}"
        return _prepare_hexadecimal(as_hex)
    else:
        raise Exception(f"could not convert {arg} to hex")


def _prepare_hexadecimal(argument: str) -> str:
    argument = argument[len(HEX_PREFIX):]
    argument = argument.upper()
    argument = ensure_even_length(argument)

    if argument == "":
        return ""

    try:
        _ = int(argument, 16)
    except ValueError:
        raise errors.UnknownArgumentFormat(argument)
    return argument


def _prepare_decimal(argument: str) -> str:
    if not argument.isnumeric():
        raise errors.UnknownArgumentFormat(argument)

    as_number = int(argument)
    as_hexstring = hex(as_number)[len(HEX_PREFIX):]
    as_hexstring = ensure_even_length(as_hexstring)
    return as_hexstring.upper()


def ensure_even_length(string: str) -> str:
    if len(string) % 2 == 1:
        return '0' + string
    return string
