from typing import Any, List, Protocol

from Cryptodome.Hash import keccak
from multiversx_sdk_core import Address, AddressComputer

from multiversx_sdk_cli import cli_shared, utils
from multiversx_sdk_cli.accounts import Account
from multiversx_sdk_cli.constants import ADDRESS_ZERO_BECH32, DEFAULT_HRP
from multiversx_sdk_cli.contracts import query_contract
from multiversx_sdk_cli.transactions import (compute_relayed_v1_data,
                                             do_prepare_transaction)

MaxNumShards = 256
ShardIdentiferLen = 2
InitialDNSAddress = bytes([1] * 32)


class INetworkProvider(Protocol):
    def query_contract(self, query: Any) -> Any:
        ...


def resolve(name: str, proxy: INetworkProvider) -> Address:
    name_arg = "0x{}".format(str.encode(name).hex())
    dns_address = dns_address_for_name(name)

    result = query_contract(dns_address, proxy, "resolve", [name_arg])
    if len(result) == 0:
        return Address.new_from_bech32(ADDRESS_ZERO_BECH32)
    return Address.new_from_hex(result[0].hex, DEFAULT_HRP)


def validate_name(name: str, shard_id: int, proxy: INetworkProvider):
    name_arg = "0x{}".format(str.encode(name).hex())
    dns_address = compute_dns_address_for_shard_id(shard_id)

    query_contract(dns_address, proxy, "validateName", [name_arg])


def register(args: Any):
    args = utils.as_object(args)

    cli_shared.check_guardian_and_options_args(args)
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    cli_shared.prepare_chain_id_in_args(args)
    args.receiver = dns_address_for_name(args.name).bech32()
    args.data = dns_register_data(args.name)

    tx = do_prepare_transaction(args)

    if hasattr(args, "relay") and args.relay:
        args.outfile.write(compute_relayed_v1_data(tx))
        return

    cli_shared.send_or_simulate(tx, args)


def compute_all_dns_addresses() -> List[Address]:
    addresses: List[Address] = []
    for i in range(0, 256):
        addresses.append(compute_dns_address_for_shard_id(i))
    return addresses


def name_hash(name: str) -> bytes:
    return keccak.new(digest_bits=256).update(str.encode(name)).digest()


def registration_cost(shard_id: int, proxy: INetworkProvider) -> int:
    dns_address = compute_dns_address_for_shard_id(shard_id)
    result = query_contract(dns_address, proxy, "getRegistrationCost", [])
    if len(result[0]) == 0:
        return 0
    else:
        return int("0x{}".format(result[0]))


def version(shard_id: int, proxy: INetworkProvider) -> str:
    dns_address = compute_dns_address_for_shard_id(shard_id)
    result = query_contract(dns_address, proxy, "version", [])
    return bytearray.fromhex(result[0].hex).decode()


def dns_address_for_name(name: str) -> Address:
    hash = name_hash(name)
    shard_id = hash[31]
    return compute_dns_address_for_shard_id(shard_id)


def compute_dns_address_for_shard_id(shard_id: int) -> Address:
    deployer_pubkey_prefix = InitialDNSAddress[:len(InitialDNSAddress) - ShardIdentiferLen]

    deployer_pubkey = deployer_pubkey_prefix + bytes([0, shard_id])
    deployer = Account(address=Address(deployer_pubkey, DEFAULT_HRP))
    deployer.nonce = 0
    address_computer = AddressComputer(number_of_shards=3)
    contract_address = address_computer.compute_contract_address(deployer.address, deployer.nonce)
    return contract_address


def dns_register_data(name: str) -> str:
    name_enc: bytes = str.encode(name)
    return "register@{}".format(name_enc.hex())
