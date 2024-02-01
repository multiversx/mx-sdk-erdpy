from typing import Any, List, Union

from multiversx_sdk_core import (Address, CodeMetadata, TokenComputer,
                                 TokenTransfer, Transaction)
from multiversx_sdk_core.serializer import arg_to_string, args_to_strings
from multiversx_sdk_core.transaction_factories.token_transfers_data_builder import \
    TokenTransfersDataBuilder
from multiversx_sdk_core.transaction_factories.transactions_factory_config import \
    TransactionsFactoryConfig

from multiversx_sdk_cli.accounts import Account
from multiversx_sdk_cli.contracts import (SmartContract,
                                          prepare_args_for_factory)
from multiversx_sdk_cli.errors import BadUsage
from multiversx_sdk_cli.interfaces import IAddress

MULTISIG_DEPOSIT_FUNCTION = "deposit"
MULTISIG_TRANSFER_AND_EXECUTE = "proposeTransferExecute"
MULTISIG_ASYNC_CALL = "proposeAsyncCall"
MULTISIG_DEPLOY_FUNCTION = "proposeSCDeployFromSource"
MULTISIG_UPGRADE_FUNCTION = "proposeSCUpgradeFromSource"


def prepare_transaction_for_egld_transfer(sender: Account,
                                          multisig: str,
                                          receiver: str,
                                          chain_id: str,
                                          value: int,
                                          gas_limit: int,
                                          nonce: int,
                                          version: int,
                                          options: int,
                                          guardian: str) -> Transaction:
    config = TransactionsFactoryConfig(chain_id)
    contract = SmartContract(config)

    return contract.prepare_execute_transaction(
        caller=sender,
        contract=Address.new_from_bech32(multisig),
        function=MULTISIG_TRANSFER_AND_EXECUTE,
        arguments=[f"{receiver}", f"{value}"],
        gas_limit=gas_limit,
        value=0,
        transfers=None,
        nonce=nonce,
        version=version,
        options=options,
        guardian=guardian)


def prepare_transaction_for_custom_token_transfer(sender: Account,
                                                  multisig: str,
                                                  receiver: str,
                                                  chain_id: str,
                                                  transfers: List[str],
                                                  gas_limit: int,
                                                  nonce: int,
                                                  version: int,
                                                  options: int,
                                                  guardian: str) -> Transaction:
    config = TransactionsFactoryConfig(chain_id)
    contract = SmartContract(config)

    token_transfers = contract.prepare_token_transfers(transfers)
    transfer_receiver = Address.new_from_bech32(receiver)
    transfer_data_parts = _prepare_data_parts_for_multisig_transfer(transfer_receiver, token_transfers)
    multisig_contract = Address.new_from_bech32(multisig)

    arguments: List[str] = [transfer_receiver.to_hex(), "00"]
    if transfer_data_parts[0] != "ESDTTransfer":
        arguments[0] = multisig_contract.to_hex()

    transfer_data_parts[0] = arg_to_string(transfer_data_parts[0])
    arguments.extend(transfer_data_parts)

    tx = contract.prepare_execute_transaction(
        caller=sender,
        contract=multisig_contract,
        function=MULTISIG_ASYNC_CALL,
        arguments=None,
        gas_limit=gas_limit,
        value=0,
        transfers=None,
        nonce=nonce,
        version=version,
        options=options,
        guardian=guardian)

    data_field = tx.data.decode() + "@" + _build_data_payload(arguments)
    tx.data = data_field.encode()
    tx.signature = bytes.fromhex(sender.sign_transaction(tx))
    return tx


def prepare_transaction_for_depositing_funds(sender: Account,
                                             multisig: str,
                                             chain_id: str,
                                             value: int,
                                             transfers: Union[List[str], None],
                                             gas_limit: int,
                                             nonce: int,
                                             version: int,
                                             options: int,
                                             guardian: str) -> Transaction:
    config = TransactionsFactoryConfig(chain_id)
    contract = SmartContract(config)

    return contract.prepare_execute_transaction(
        caller=sender,
        contract=Address.new_from_bech32(multisig),
        function=MULTISIG_DEPOSIT_FUNCTION,
        arguments=None,
        gas_limit=gas_limit,
        value=value,
        transfers=transfers,
        nonce=nonce,
        version=version,
        options=options,
        guardian=guardian)


def prepare_transaction_for_deploying_contract(sender: Account,
                                               multisig: IAddress,
                                               deployed_contract: IAddress,
                                               arguments: Union[List[str], None],
                                               upgradeable: bool,
                                               readable: bool,
                                               payable: bool,
                                               payable_by_sc: bool,
                                               chain_id: str,
                                               value: int,
                                               gas_limit: int,
                                               nonce: int,
                                               version: int,
                                               options: int,
                                               guardian: str) -> Transaction:
    # convert the args to proper type instead of strings
    prepared_arguments = prepare_args_for_factory(arguments) if arguments else []
    metadata = CodeMetadata(upgradeable, readable, payable, payable_by_sc)

    data = _prepare_data_field_for_deploy_transaction(amount=value,
                                                      deployed_contract=deployed_contract,
                                                      metadata=metadata,
                                                      arguments=prepared_arguments)
    tx = Transaction(
        sender=sender.address.to_bech32(),
        receiver=multisig.to_bech32(),
        gas_limit=gas_limit,
        chain_id=chain_id,
        nonce=nonce,
        amount=0,
        data=data,
        version=version,
        options=options,
        guardian=guardian
    )
    tx.signature = bytes.fromhex(sender.sign_transaction(tx))

    return tx


def prepare_transaction_upgrading_contract(sender: Account,
                                           contract_address: IAddress,
                                           multisig: IAddress,
                                           upgraded_contract: IAddress,
                                           arguments: Union[List[str], None],
                                           upgradeable: bool,
                                           readable: bool,
                                           payable: bool,
                                           payable_by_sc: bool,
                                           chain_id: str,
                                           value: int,
                                           gas_limit: int,
                                           nonce: int,
                                           version: int,
                                           options: int,
                                           guardian: str) -> Transaction:
    # convert the args to proper type instead of strings
    prepared_arguments = prepare_args_for_factory(arguments) if arguments else []
    metadata = CodeMetadata(upgradeable, readable, payable, payable_by_sc)

    data = _prepare_data_field_for_upgrade_transaction(contract_address=contract_address,
                                                       amount=value,
                                                       upgraded_contract=upgraded_contract,
                                                       metadata=metadata,
                                                       arguments=prepared_arguments)
    tx = Transaction(
        sender=sender.address.to_bech32(),
        receiver=multisig.to_bech32(),
        gas_limit=gas_limit,
        chain_id=chain_id,
        nonce=nonce,
        amount=0,
        data=data,
        version=version,
        options=options,
        guardian=guardian
    )
    tx.signature = bytes.fromhex(sender.sign_transaction(tx))

    return tx


def prepare_transaction_for_contract_call(sender: Account,
                                          contract_address: IAddress,
                                          function: str,
                                          arguments: Union[List[str], None],
                                          multisig: IAddress,
                                          value: int,
                                          transfers: Union[List[str], None],
                                          gas_limit: int,
                                          chain_id: str,
                                          nonce: int,
                                          version: int,
                                          options: int,
                                          guardian: str) -> Transaction:
    if value and transfers:
        raise BadUsage("Can't send both native and custom tokens")

    config = TransactionsFactoryConfig(chain_id)
    contract = SmartContract(config)

    token_transfers = contract.prepare_token_transfers(transfers) if transfers else []
    prepared_args = prepare_args_for_factory(arguments) if arguments else []

    data_field = _prepare_data_field_for_contract_call(contract_address=contract_address,
                                                       multisig=multisig,
                                                       function=function,
                                                       arguments=prepared_args,
                                                       value=value,
                                                       token_transfers=token_transfers)
    tx = Transaction(
        sender=sender.address.to_bech32(),
        receiver=multisig.to_bech32(),
        gas_limit=gas_limit,
        chain_id=chain_id,
        nonce=nonce,
        amount=0,
        data=data_field,
        version=version,
        options=options,
        guardian=guardian
    )
    tx.signature = bytes.fromhex(sender.sign_transaction(tx))

    return tx


def _prepare_data_field_for_contract_call(contract_address: IAddress,
                                          multisig: IAddress,
                                          function: str,
                                          arguments: List[Any],
                                          value: int,
                                          token_transfers: List[TokenTransfer]):
    data_parts = [
        MULTISIG_ASYNC_CALL,
        contract_address.to_hex(),
        arg_to_string(value)
    ]

    transfer_data_parts = _prepare_data_parts_for_multisig_transfer(receiver=contract_address, token_transfers=token_transfers)

    if transfer_data_parts:
        if transfer_data_parts[0] != "ESDTTransfer":
            data_parts[1] = multisig.to_hex()

        transfer_data_parts[0] = arg_to_string(transfer_data_parts[0])
        data_parts.extend(transfer_data_parts)

    data_parts.append(arg_to_string(function))
    data_parts.extend(args_to_strings(arguments))

    data_field = _build_data_payload(data_parts)
    return data_field.encode()


def _prepare_data_field_for_upgrade_transaction(contract_address: IAddress,
                                                amount: int,
                                                upgraded_contract: IAddress,
                                                metadata: CodeMetadata,
                                                arguments: List[Any]) -> bytes:
    data_parts = [
        MULTISIG_UPGRADE_FUNCTION,
        contract_address.to_hex(),
        arg_to_string(amount),
        upgraded_contract.to_hex(),
        str(metadata)
    ]
    data_parts.extend(args_to_strings(arguments))
    payload = _build_data_payload(data_parts)

    return payload.encode()


def _prepare_data_field_for_deploy_transaction(amount: int,
                                               deployed_contract: IAddress,
                                               metadata: CodeMetadata,
                                               arguments: List[Any]) -> bytes:
    data_parts = [
        MULTISIG_DEPLOY_FUNCTION,
        arg_to_string(amount),
        deployed_contract.to_hex(),
        str(metadata)
    ]
    data_parts.extend(args_to_strings(arguments))
    payload = _build_data_payload(data_parts)

    return payload.encode()


def _prepare_data_parts_for_multisig_transfer(receiver: IAddress, token_transfers: List[TokenTransfer]) -> List[str]:
    token_computer = TokenComputer()
    data_builder = TokenTransfersDataBuilder(token_computer)
    data_parts: List[str] = []

    if len(token_transfers) == 1:
        transfer = token_transfers[0]
        if token_computer.is_fungible(transfer.token):
            data_parts = data_builder.build_args_for_esdt_transfer(transfer=transfer)
        else:
            data_parts = data_builder.build_args_for_single_esdt_nft_transfer(transfer=transfer, receiver=receiver)
    elif len(token_transfers) > 1:
        data_parts = data_builder.build_args_for_multi_esdt_nft_transfer(receiver=receiver, transfers=token_transfers)

    return data_parts


def _build_data_payload(parts: List[str]) -> str:
    return "@".join(parts)
