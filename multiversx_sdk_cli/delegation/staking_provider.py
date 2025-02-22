from typing import Optional

from multiversx_sdk import (
    Address,
    DelegationTransactionsFactory,
    Transaction,
    TransactionsFactoryConfig,
    ValidatorPublicKey,
)
from multiversx_sdk.abi import BigUIntValue, Serializer

from multiversx_sdk_cli.base_transactions_controller import BaseTransactionsController
from multiversx_sdk_cli.config import get_address_hrp
from multiversx_sdk_cli.errors import BadUsage
from multiversx_sdk_cli.interfaces import IAccount

DELEGATION_MANAGER_SC_ADDRESS_HEX = "000000000000000000010000000000000000000000000000000000000004ffff"


class DelegationOperations(BaseTransactionsController):
    def __init__(self, config: TransactionsFactoryConfig) -> None:
        self._factory = DelegationTransactionsFactory(config)

    def prepare_transaction_for_new_delegation_contract(
        self,
        owner: IAccount,
        native_amount: int,
        total_delegation_cap: int,
        service_fee: int,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        tx = self._factory.create_transaction_for_new_delegation_contract(
            sender=owner.address,
            total_delegation_cap=total_delegation_cap,
            service_fee=service_fee,
            amount=native_amount,
        )
        tx.gas_price = gas_price
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return tx

    def prepare_transaction_for_adding_nodes(
        self,
        owner: IAccount,
        delegation_contract: Address,
        public_keys: list[ValidatorPublicKey],
        signed_messages: list[bytes],
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        tx = self._factory.create_transaction_for_adding_nodes(
            sender=owner.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
            signed_messages=signed_messages,
        )
        tx.value = value
        tx.gas_price = gas_price
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return tx

    def prepare_transaction_for_removing_nodes(
        self,
        owner: IAccount,
        delegation_contract: Address,
        public_keys: list[ValidatorPublicKey],
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        tx = self._factory.create_transaction_for_removing_nodes(
            sender=owner.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
        )
        tx.value = value
        tx.gas_price = gas_price
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return tx

    def prepare_transaction_for_staking_nodes(
        self,
        owner: IAccount,
        delegation_contract: Address,
        public_keys: list[ValidatorPublicKey],
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        tx = self._factory.create_transaction_for_staking_nodes(
            sender=owner.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
        )
        tx.value = value
        tx.gas_price = gas_price
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return tx

    def prepare_transaction_for_unbonding_nodes(
        self,
        owner: IAccount,
        delegation_contract: Address,
        public_keys: list[ValidatorPublicKey],
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        tx = self._factory.create_transaction_for_unbonding_nodes(
            sender=owner.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
        )
        tx.value = value
        tx.gas_price = gas_price
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return tx

    def prepare_transaction_for_unstaking_nodes(
        self,
        owner: IAccount,
        delegation_contract: Address,
        public_keys: list[ValidatorPublicKey],
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        tx = self._factory.create_transaction_for_unstaking_nodes(
            sender=owner.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
        )
        tx.value = value
        tx.gas_price = gas_price
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return tx

    def prepare_transaction_for_unjailing_nodes(
        self,
        owner: IAccount,
        delegation_contract: Address,
        public_keys: list[ValidatorPublicKey],
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        tx = self._factory.create_transaction_for_unjailing_nodes(
            sender=owner.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
            amount=value,
        )
        tx.gas_price = gas_price
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return tx

    def prepare_transaction_for_delegating(
        self,
        owner: IAccount,
        delegation_contract: Address,
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        tx = self._factory.create_transaction_for_delegating(
            sender=owner.address,
            delegation_contract=delegation_contract,
            amount=value,
        )
        tx.gas_price = gas_price
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return tx

    def prepare_transaction_for_claiming_rewards(
        self,
        owner: IAccount,
        delegation_contract: Address,
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        tx = self._factory.create_transaction_for_claiming_rewards(
            sender=owner.address, delegation_contract=delegation_contract
        )
        tx.value = value
        tx.gas_price = gas_price
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return tx

    def prepare_transaction_for_redelegating_rewards(
        self,
        owner: IAccount,
        delegation_contract: Address,
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        tx = self._factory.create_transaction_for_redelegating_rewards(
            sender=owner.address, delegation_contract=delegation_contract
        )
        tx.value = value
        tx.gas_price = gas_price
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return tx

    def prepare_transaction_for_undelegating(
        self,
        owner: IAccount,
        delegation_contract: Address,
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        tx = self._factory.create_transaction_for_undelegating(
            sender=owner.address,
            delegation_contract=delegation_contract,
            amount=value,
        )
        tx.gas_price = gas_price
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return tx

    def prepare_transaction_for_withdrawing(
        self,
        owner: IAccount,
        delegation_contract: Address,
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        tx = self._factory.create_transaction_for_withdrawing(
            sender=owner.address, delegation_contract=delegation_contract
        )
        tx.value = value
        tx.gas_price = gas_price
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return tx

    def prepare_transaction_for_changing_service_fee(
        self,
        owner: IAccount,
        delegation_contract: Address,
        service_fee: int,
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        tx = self._factory.create_transaction_for_changing_service_fee(
            sender=owner.address,
            delegation_contract=delegation_contract,
            service_fee=service_fee,
        )
        tx.value = value
        tx.gas_price = gas_price
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return tx

    def prepare_transaction_for_modifying_delegation_cap(
        self,
        owner: IAccount,
        delegation_contract: Address,
        delegation_cap: int,
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        tx = self._factory.create_transaction_for_modifying_delegation_cap(
            sender=owner.address,
            delegation_contract=delegation_contract,
            delegation_cap=delegation_cap,
        )
        tx.value = value
        tx.gas_price = gas_price
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return tx

    def prepare_transaction_for_automatic_activation(
        self,
        owner: IAccount,
        delegation_contract: Address,
        set: bool,
        unset: bool,
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        if set and unset:
            raise BadUsage("Cannot set and unset at the same time")

        if set:
            tx = self._factory.create_transaction_for_setting_automatic_activation(
                sender=owner.address, delegation_contract=delegation_contract
            )
        elif unset:
            tx = self._factory.create_transaction_for_unsetting_automatic_activation(
                sender=owner.address, delegation_contract=delegation_contract
            )
        else:
            raise BadUsage("Both set and unset automatic activation are False")

        tx.value = value
        tx.gas_price = gas_price
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return tx

    def prepare_transaction_for_redelegate_cap(
        self,
        owner: IAccount,
        delegation_contract: Address,
        set: bool,
        unset: bool,
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        if set and unset:
            raise BadUsage("Cannot set and unset at the same time")

        if set:
            tx = self._factory.create_transaction_for_setting_cap_check_on_redelegate_rewards(
                sender=owner.address, delegation_contract=delegation_contract
            )
        elif unset:
            tx = self._factory.create_transaction_for_unsetting_cap_check_on_redelegate_rewards(
                sender=owner.address, delegation_contract=delegation_contract
            )
        else:
            raise BadUsage("Either set or unset should be True")

        tx.value = value
        tx.gas_price = gas_price
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return tx

    def prepare_transaction_for_setting_metadata(
        self,
        owner: IAccount,
        delegation_contract: Address,
        name: str,
        website: str,
        identifier: str,
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        tx = self._factory.create_transaction_for_setting_metadata(
            sender=owner.address,
            delegation_contract=delegation_contract,
            name=name,
            website=website,
            identifier=identifier,
        )
        tx.value = value
        tx.gas_price = gas_price
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return tx

    # will be replaced in the future once it's implemented in sdk-py
    def prepare_transaction_for_creating_delegation_contract_from_validator(
        self,
        owner: IAccount,
        max_cap: int,
        service_fee: int,
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        receiver = Address.new_from_hex(DELEGATION_MANAGER_SC_ADDRESS_HEX, get_address_hrp())

        serializer = Serializer()
        data = "makeNewContractFromValidatorData@" + serializer.serialize(
            [BigUIntValue(max_cap), BigUIntValue(service_fee)]
        )

        tx = Transaction(
            sender=owner.address,
            receiver=receiver,
            gas_limit=510000000,
            chain_id=self._factory.config.chain_id,
            data=data.encode(),
            nonce=nonce,
            version=version,
            options=options,
            guardian=guardian_address,
            relayer=relayer_address,
            gas_price=gas_price,
            value=value,
        )

        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return tx
