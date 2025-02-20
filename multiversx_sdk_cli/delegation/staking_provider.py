from pathlib import Path
from typing import Any

from multiversx_sdk import (
    Address,
    DelegationTransactionsFactory,
    Transaction,
    TransactionsFactoryConfig,
    ValidatorPublicKey,
)
from multiversx_sdk.abi import BigUIntValue, Serializer

from multiversx_sdk_cli.config import get_address_hrp
from multiversx_sdk_cli.errors import BadUsage
from multiversx_sdk_cli.interfaces import IAccount
from multiversx_sdk_cli.validators.validators_file import ValidatorsFile


class DelegationOperations:
    def __init__(self, config: TransactionsFactoryConfig) -> None:
        self._factory = DelegationTransactionsFactory(config)

    def prepare_transaction_for_new_delegation_contract(self, owner: IAccount, args: Any) -> Transaction:
        tx = self._factory.create_transaction_for_new_delegation_contract(
            sender=owner.address,
            total_delegation_cap=int(args.total_delegation_cap),
            service_fee=int(args.service_fee),
            amount=int(args.value),
        )
        tx.nonce = int(args.nonce)
        tx.version = int(args.version)
        tx.options = int(args.options)
        tx.guardian = args.guardian

        if args.gas_limit:
            tx.gas_limit = int(args.gas_limit)

        tx.signature = owner.sign_transaction(tx)

        return tx

    def prepare_transaction_for_adding_nodes(self, owner: IAccount, args: Any) -> Transaction:
        delegation_contract = Address.new_from_bech32(args.delegation_contract)
        public_keys, signed_messages = self._get_public_keys_and_signed_messages(args)

        tx = self._factory.create_transaction_for_adding_nodes(
            sender=owner.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
            signed_messages=signed_messages,
        )
        tx.nonce = int(args.nonce)
        tx.version = int(args.version)
        tx.options = int(args.options)
        tx.guardian = args.guardian

        if args.gas_limit:
            tx.gas_limit = int(args.gas_limit)

        tx.signature = owner.sign_transaction(tx)

        return tx

    def prepare_transaction_for_removing_nodes(self, owner: IAccount, args: Any) -> Transaction:
        delegation_contract = Address.new_from_bech32(args.delegation_contract)

        public_keys = self._load_validators_public_keys(args)

        tx = self._factory.create_transaction_for_removing_nodes(
            sender=owner.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
        )
        tx.nonce = int(args.nonce)
        tx.version = int(args.version)
        tx.options = int(args.options)
        tx.guardian = args.guardian

        if args.gas_limit:
            tx.gas_limit = int(args.gas_limit)

        tx.signature = owner.sign_transaction(tx)

        return tx

    def prepare_transaction_for_staking_nodes(self, owner: IAccount, args: Any) -> Transaction:
        delegation_contract = Address.new_from_bech32(args.delegation_contract)

        public_keys = self._load_validators_public_keys(args)

        tx = self._factory.create_transaction_for_staking_nodes(
            sender=owner.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
        )
        tx.nonce = int(args.nonce)
        tx.version = int(args.version)
        tx.options = int(args.options)
        tx.guardian = args.guardian

        if args.gas_limit:
            tx.gas_limit = int(args.gas_limit)

        tx.signature = owner.sign_transaction(tx)

        return tx

    def prepare_transaction_for_unbonding_nodes(self, owner: IAccount, args: Any) -> Transaction:
        delegation_contract = Address.new_from_bech32(args.delegation_contract)

        public_keys = self._load_validators_public_keys(args)

        tx = self._factory.create_transaction_for_unbonding_nodes(
            sender=owner.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
        )
        tx.nonce = int(args.nonce)
        tx.version = int(args.version)
        tx.options = int(args.options)
        tx.guardian = args.guardian

        if args.gas_limit:
            tx.gas_limit = int(args.gas_limit)

        tx.signature = owner.sign_transaction(tx)

        return tx

    def prepare_transaction_for_unstaking_nodes(self, owner: IAccount, args: Any) -> Transaction:
        delegation_contract = Address.new_from_bech32(args.delegation_contract)

        public_keys = self._load_validators_public_keys(args)

        tx = self._factory.create_transaction_for_unstaking_nodes(
            sender=owner.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
        )
        tx.nonce = int(args.nonce)
        tx.version = int(args.version)
        tx.options = int(args.options)
        tx.guardian = args.guardian

        if args.gas_limit:
            tx.gas_limit = int(args.gas_limit)

        tx.signature = owner.sign_transaction(tx)

        return tx

    def prepare_transaction_for_unjailing_nodes(self, owner: IAccount, args: Any) -> Transaction:
        delegation_contract = Address.new_from_bech32(args.delegation_contract)

        public_keys = self._load_validators_public_keys(args)
        amount = int(args.value)

        tx = self._factory.create_transaction_for_unjailing_nodes(
            sender=owner.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
            amount=amount,
        )
        tx.nonce = int(args.nonce)
        tx.version = int(args.version)
        tx.options = int(args.options)
        tx.guardian = args.guardian
        tx.value = args.value

        if args.gas_limit:
            tx.gas_limit = int(args.gas_limit)

        tx.signature = owner.sign_transaction(tx)

        return tx

    def prepare_transaction_for_delegating(self, owner: IAccount, args: Any) -> Transaction:
        delegation_contract = Address.new_from_bech32(args.delegation_contract)

        tx = self._factory.create_transaction_for_delegating(
            sender=owner.address,
            delegation_contract=delegation_contract,
            amount=int(args.value),
        )
        tx.nonce = int(args.nonce)
        tx.version = int(args.version)
        tx.options = int(args.options)
        tx.guardian = args.guardian

        if args.gas_limit:
            tx.gas_limit = int(args.gas_limit)

        tx.signature = owner.sign_transaction(tx)

        return tx

    def prepare_transaction_for_claiming_rewards(self, owner: IAccount, args: Any) -> Transaction:
        delegation_contract = Address.new_from_bech32(args.delegation_contract)

        tx = self._factory.create_transaction_for_claiming_rewards(
            sender=owner.address, delegation_contract=delegation_contract
        )
        tx.nonce = int(args.nonce)
        tx.version = int(args.version)
        tx.options = int(args.options)
        tx.guardian = args.guardian

        if args.gas_limit:
            tx.gas_limit = int(args.gas_limit)

        tx.signature = owner.sign_transaction(tx)

        return tx

    def prepare_transaction_for_redelegating_rewards(self, owner: IAccount, args: Any) -> Transaction:
        delegation_contract = Address.new_from_bech32(args.delegation_contract)

        tx = self._factory.create_transaction_for_redelegating_rewards(
            sender=owner.address, delegation_contract=delegation_contract
        )
        tx.nonce = int(args.nonce)
        tx.version = int(args.version)
        tx.options = int(args.options)
        tx.guardian = args.guardian

        if args.gas_limit:
            tx.gas_limit = int(args.gas_limit)

        tx.signature = owner.sign_transaction(tx)

        return tx

    def prepare_transaction_for_undelegating(self, owner: IAccount, args: Any) -> Transaction:
        delegation_contract = Address.new_from_bech32(args.delegation_contract)

        tx = self._factory.create_transaction_for_undelegating(
            sender=owner.address,
            delegation_contract=delegation_contract,
            amount=int(args.value),
        )
        tx.nonce = int(args.nonce)
        tx.version = int(args.version)
        tx.options = int(args.options)
        tx.guardian = args.guardian

        if args.gas_limit:
            tx.gas_limit = int(args.gas_limit)

        tx.signature = owner.sign_transaction(tx)

        return tx

    def prepare_transaction_for_withdrawing(self, owner: IAccount, args: Any) -> Transaction:
        delegation_contract = Address.new_from_bech32(args.delegation_contract)

        tx = self._factory.create_transaction_for_withdrawing(
            sender=owner.address, delegation_contract=delegation_contract
        )
        tx.nonce = int(args.nonce)
        tx.version = int(args.version)
        tx.options = int(args.options)
        tx.guardian = args.guardian

        if args.gas_limit:
            tx.gas_limit = int(args.gas_limit)

        tx.signature = owner.sign_transaction(tx)

        return tx

    def prepare_transaction_for_changing_service_fee(self, owner: IAccount, args: Any) -> Transaction:
        delegation_contract = Address.new_from_bech32(args.delegation_contract)

        tx = self._factory.create_transaction_for_changing_service_fee(
            sender=owner.address,
            delegation_contract=delegation_contract,
            service_fee=int(args.service_fee),
        )
        tx.nonce = int(args.nonce)
        tx.version = int(args.version)
        tx.options = int(args.options)
        tx.guardian = args.guardian

        if args.gas_limit:
            tx.gas_limit = int(args.gas_limit)

        tx.signature = owner.sign_transaction(tx)

        return tx

    def prepare_transaction_for_modifying_delegation_cap(self, owner: IAccount, args: Any) -> Transaction:
        delegation_contract = Address.new_from_bech32(args.delegation_contract)

        tx = self._factory.create_transaction_for_modifying_delegation_cap(
            sender=owner.address,
            delegation_contract=delegation_contract,
            delegation_cap=int(args.delegation_cap),
        )
        tx.nonce = int(args.nonce)
        tx.version = int(args.version)
        tx.options = int(args.options)
        tx.guardian = args.guardian

        if args.gas_limit:
            tx.gas_limit = int(args.gas_limit)

        tx.signature = owner.sign_transaction(tx)

        return tx

    def prepare_transaction_for_automatic_activation(self, owner: IAccount, args: Any) -> Transaction:
        delegation_contract = Address.new_from_bech32(args.delegation_contract)

        if args.set:
            tx = self._factory.create_transaction_for_setting_automatic_activation(
                sender=owner.address, delegation_contract=delegation_contract
            )
        elif args.unset:
            tx = self._factory.create_transaction_for_unsetting_automatic_activation(
                sender=owner.address, delegation_contract=delegation_contract
            )
        else:
            raise BadUsage("Either `--set` or `--unset` should be provided")

        tx.nonce = int(args.nonce)
        tx.version = int(args.version)
        tx.options = int(args.options)
        tx.guardian = args.guardian

        if args.gas_limit:
            tx.gas_limit = int(args.gas_limit)

        tx.signature = owner.sign_transaction(tx)

        return tx

    def prepare_transaction_for_redelegate_cap(self, owner: IAccount, args: Any) -> Transaction:
        delegation_contract = Address.new_from_bech32(args.delegation_contract)

        if args.set:
            tx = self._factory.create_transaction_for_setting_cap_check_on_redelegate_rewards(
                sender=owner.address, delegation_contract=delegation_contract
            )
        elif args.unset:
            tx = self._factory.create_transaction_for_unsetting_cap_check_on_redelegate_rewards(
                sender=owner.address, delegation_contract=delegation_contract
            )
        else:
            raise BadUsage("Either `--set` or `--unset` should be provided")

        tx.nonce = int(args.nonce)
        tx.version = int(args.version)
        tx.options = int(args.options)
        tx.guardian = args.guardian

        if args.gas_limit:
            tx.gas_limit = int(args.gas_limit)

        tx.signature = owner.sign_transaction(tx)

        return tx

    def prepare_transaction_for_setting_metadata(self, owner: IAccount, args: Any) -> Transaction:
        delegation_contract = Address.new_from_bech32(args.delegation_contract)

        tx = self._factory.create_transaction_for_setting_metadata(
            sender=owner.address,
            delegation_contract=delegation_contract,
            name=args.name,
            website=args.website,
            identifier=args.identifier,
        )
        tx.nonce = int(args.nonce)
        tx.version = int(args.version)
        tx.options = int(args.options)
        tx.guardian = args.guardian

        if args.gas_limit:
            tx.gas_limit = int(args.gas_limit)

        tx.signature = owner.sign_transaction(tx)

        return tx

    def prepare_transaction_for_creating_delegation_contract_from_validator(
        self, owner: IAccount, args: Any
    ) -> Transaction:
        receiver = Address.new_from_hex(
            "000000000000000000010000000000000000000000000000000000000004ffff",
            get_address_hrp(),
        )
        max_cap = int(args.max_cap)
        fee = int(args.fee)

        serializer = Serializer()
        data = "makeNewContractFromValidatorData@" + serializer.serialize([BigUIntValue(max_cap), BigUIntValue(fee)])

        tx = Transaction(
            sender=owner.address,
            receiver=receiver,
            gas_limit=510000000,
            chain_id=self._factory.config.chain_id,
            data=data.encode(),
            nonce=int(args.nonce),
            version=int(args.version),
            options=int(args.options),
            guardian=args.guardian,
        )

        if args.gas_limit:
            tx.gas_limit = int(args.gas_limit)

        tx.signature = owner.sign_transaction(tx)

        return tx

    def _load_validators_public_keys(self, args: Any) -> list[ValidatorPublicKey]:
        if args.bls_keys:
            return self._parse_public_bls_keys(args.bls_keys)

        validators_file_path = Path(args.validators_file).expanduser()
        validators_file = ValidatorsFile(validators_file_path)
        return validators_file.load_public_keys()

    def _parse_public_bls_keys(self, public_bls_keys: str) -> list[ValidatorPublicKey]:
        keys = public_bls_keys.split(",")
        validator_public_keys: list[ValidatorPublicKey] = []

        for key in keys:
            validator_public_keys.append(ValidatorPublicKey(bytes.fromhex(key)))

        return validator_public_keys

    def _get_public_keys_and_signed_messages(self, args: Any) -> tuple[list[ValidatorPublicKey], list[bytes]]:
        validators_file_path = Path(args.validators_file).expanduser()
        validators_file = ValidatorsFile(validators_file_path)
        signers = validators_file.load_signers()

        pubkey = Address.new_from_bech32(args.delegation_contract).get_public_key()

        public_keys: list[ValidatorPublicKey] = []
        signed_messages: list[bytes] = []
        for signer in signers:
            signed_message = signer.sign(pubkey)

            public_keys.append(signer.secret_key.generate_public_key())
            signed_messages.append(signed_message)

        return public_keys, signed_messages
