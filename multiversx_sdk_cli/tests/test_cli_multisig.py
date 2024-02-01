import base64
import json
from pathlib import Path
from typing import Any, Dict

from multiversx_sdk_cli.cli import main

parent = Path(__file__).parent
alice = parent / "testdata" / "alice.pem"


def test_sign_action(capsys: Any):
    return_code = main([
        "multisig", "sign",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--action-id", "2",
        "--pem", str(alice),
        "--nonce", "1289",
        "--chain", "T",
        "--gas-limit", "10000000"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "sign@02"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"


def test_unsign_action(capsys: Any):
    return_code = main([
        "multisig", "unsign",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--action-id", "2",
        "--pem", str(alice),
        "--nonce", "1289",
        "--chain", "T",
        "--gas-limit", "10000000"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "unsign@02"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"


def test_perform_action(capsys: Any):
    return_code = main([
        "multisig", "perform-action",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--action-id", "2",
        "--pem", str(alice),
        "--nonce", "1290",
        "--chain", "T",
        "--gas-limit", "10000000"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "performAction@02"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"


def test_discard_action(capsys: Any):
    return_code = main([
        "multisig", "discard-action",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--action-id", "15",
        "--pem", str(alice),
        "--nonce", "55",
        "--chain", "T",
        "--gas-limit", "10000000"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "discardAction@0f"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"


def test_deposit_egld(capsys: Any):
    return_code = main([
        "multisig", "deposit",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--pem", str(alice),
        "--nonce", "1449",
        "--chain", "T",
        "--gas-limit", "10000000",
        "--value", "50000000000000000"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "deposit"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 50000000000000000

    signature = transaction["signature"]
    assert signature == "ba823e12c7eba1cb8e7c41f7f4042d54742a8162114875150e0f9d1e3535fdb74e7a89adfbda4360cd9f02de531facaf2a60a8f53ae48765ff2c7ae685f61704"


def test_deposit_esdt(capsys: Any):
    return_code = main([
        "multisig", "deposit",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--pem", str(alice),
        "--nonce", "1525",
        "--chain", "T",
        "--gas-limit", "10000000",
        "--token-transfers", "TST-267761", "1000"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "ESDTTransfer@5453542d323637373631@03e8@6465706f736974"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0

    signature = transaction["signature"]
    assert signature == "4bb4421783ba2b19060d6d7b84bcdda484f475a52eab6eb44679af2cac1dfae0c10552efd84ef7bdae028a40bc656f30e52984aa4f90581700377e44c4d4810b"


def test_deposit_multi_esdt(capsys: Any):
    return_code = main([
        "multisig", "deposit",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--pem", str(alice),
        "--nonce", "1531",
        "--chain", "T",
        "--gas-limit", "10000000",
        "--token-transfers", "TST-267761", "1700", "ZZZ-9ee87d", "1200"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "MultiESDTNFTTransfer@000000000000000005000a2a0f13340978c2eea268a5a2dcf917012978f61f5c@02@5453542d323637373631@@06a4@5a5a5a2d396565383764@@04b0@6465706f736974"

    receiver = transaction["receiver"]
    assert receiver == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0

    signature = transaction["signature"]
    assert signature == "034e8644e4363640224c20556b9a3abb3aef36d59697754a44e9d0cbe26e31de8bd78d4529b5c5a3b74a7e51a14f0f62e10f01386318b005f384c69e885c960c"


def test_propose_egld_transfer(capsys: Any):
    return_code = main([
        "tx", "new",
        "--pem", str(alice),
        "--receiver", "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
        "--nonce", "1429",
        "--chain", "T",
        "--gas-limit", "10000000",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--value", "1000000000000000"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "proposeTransferExecute@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8@038d7ea4c68000"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0

    signature = transaction["signature"]
    assert signature == "285edffe65006f738ce6fff640ddd9cb69c7380a219ec3549cb35744cd1106ffd41005b8d471899eb1db55e556b042db7bab0830a5250860348fb101d644c805"


def test_propose_esdt_transfer(capsys: Any):
    return_code = main([
        "tx", "new",
        "--pem", str(alice),
        "--receiver", "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
        "--nonce", "1427",
        "--chain", "T",
        "--gas-limit", "10000000",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--token-transfers", "TST-267761", "10"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "proposeAsyncCall@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8@00@455344545472616e73666572@5453542d323637373631@0a"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0

    signature = transaction["signature"]
    assert signature == "dc80e70409fce3a20bd5c80ef1f1039a0474729ddb27188afacbd2d8237294172d5bf8b4bc759e48a2e5c724983dbb6ba5f17b48bb7a8d2dfc4c076a113fa50f"


def test_propose_multi_esdt_nft_transfer(capsys: Any):
    return_code = main([
        "tx", "new",
        "--pem", str(alice),
        "--receiver", "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
        "--nonce", "1434",
        "--chain", "T",
        "--gas-limit", "10000000",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--token-transfers", "TST-267761", "10", "ZZZ-9ee87d", "10000"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "proposeAsyncCall@000000000000000005000a2a0f13340978c2eea268a5a2dcf917012978f61f5c@00@4d756c7469455344544e46545472616e73666572@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8@02@5453542d323637373631@@0a@5a5a5a2d396565383764@@2710"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0

    signature = transaction["signature"]
    assert signature == "563fc6eefe9469cf90191462cfe21ab25ae7291c1c411cd4b3778717c827045eabc58b689308e8ee45676a8e49cf75c2856a83e41e93dad5c4acb5ccb65c5b04"


def test_propose_contract_deploy_from_source(capsys: Any):
    return_code = main([
        "contract", "deploy",
        "--pem", str(alice),
        "--nonce", "60",
        "--chain", "T",
        "--proxy", "https://testnet-api.multiversx.com",
        "--gas-limit", "100000000",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--deployed-contract", "erd1qqqqqqqqqqqqqpgq8z2zzyu30f4607hth0tfj5m3vpjvwrvvrawqw09jem",
        "--arguments", "0"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "proposeSCDeployFromSource@@0000000000000000050038942113917a6ba7faebbbd69953716064c70d8c1f5c@0500@"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0


def test_propose_contract_upgrade_from_source(capsys: Any):
    return_code = main([
        "contract", "upgrade", "erd1qqqqqqqqqqqqqpgqz0kha878srg82eznjhdyvgarwycwjgs6rawq02lh6j",
        "--pem", str(alice),
        "--nonce", "6241",
        "--chain", "T",
        "--gas-limit", "100000000",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--upgraded-contract", "erd1qqqqqqqqqqqqqpgq8z2zzyu30f4607hth0tfj5m3vpjvwrvvrawqw09jem",
        "--arguments", "0"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "proposeSCUpgradeFromSource@0000000000000000050013ed7e9fc780d075645395da4623a37130e9221a1f5c@@0000000000000000050038942113917a6ba7faebbbd69953716064c70d8c1f5c@0500@"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0


def test_propose_contract_call_no_transfer(capsys: Any):
    return_code = main([
        "contract", "call", "erd1qqqqqqqqqqqqqpgq8z2zzyu30f4607hth0tfj5m3vpjvwrvvrawqw09jem",
        "--pem", str(alice),
        "--nonce", "9550",
        "--chain", "T",
        "--gas-limit", "100000000",
        "--function", "add",
        "--arguments", "10",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "proposeAsyncCall@0000000000000000050038942113917a6ba7faebbbd69953716064c70d8c1f5c@@616464@0a"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0


def test_propose_contract_call_with_egld_transfer(capsys: Any):
    return_code = main([
        "contract", "call", "erd1qqqqqqqqqqqqqpgq8z2zzyu30f4607hth0tfj5m3vpjvwrvvrawqw09jem",
        "--pem", str(alice),
        "--nonce", "9552",
        "--chain", "T",
        "--value", "1000000000000000",
        "--gas-limit", "100000000",
        "--function", "add",
        "--arguments", "10",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "proposeAsyncCall@0000000000000000050038942113917a6ba7faebbbd69953716064c70d8c1f5c@038d7ea4c68000@616464@0a"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0


def test_propose_contract_call_with_esdt_transfer(capsys: Any):
    return_code = main([
        "contract", "call", "erd1qqqqqqqqqqqqqpgq8z2zzyu30f4607hth0tfj5m3vpjvwrvvrawqw09jem",
        "--pem", str(alice),
        "--nonce", "9553",
        "--chain", "T",
        "--token-transfers", "ZZZ-9ee87d", "1000",
        "--gas-limit", "100000000",
        "--function", "add",
        "--arguments", "10",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "proposeAsyncCall@0000000000000000050038942113917a6ba7faebbbd69953716064c70d8c1f5c@@455344545472616e73666572@5a5a5a2d396565383764@03e8@616464@0a"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0


def test_propose_contract_call_with_multi_esdt_transfer(capsys: Any):
    return_code = main([
        "contract", "call", "erd1qqqqqqqqqqqqqpgq8z2zzyu30f4607hth0tfj5m3vpjvwrvvrawqw09jem",
        "--pem", str(alice),
        "--nonce", "9554",
        "--chain", "T",
        "--token-transfers", "ZZZ-9ee87d", "1300", "TST-267761", "600",
        "--gas-limit", "100000000",
        "--function", "add",
        "--arguments", "10",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "proposeAsyncCall@000000000000000005000a2a0f13340978c2eea268a5a2dcf917012978f61f5c@@4d756c7469455344544e46545472616e73666572@0000000000000000050038942113917a6ba7faebbbd69953716064c70d8c1f5c@02@5a5a5a2d396565383764@@0514@5453542d323637373631@@0258@616464@0a"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0


def test_propose_contract_call_with_multi_esdt_nft_transfer(capsys: Any):
    return_code = main([
        "contract", "call", "erd1qqqqqqqqqqqqqpgq8z2zzyu30f4607hth0tfj5m3vpjvwrvvrawqw09jem",
        "--pem", str(alice),
        "--nonce", "9555",
        "--chain", "T",
        "--token-transfers", "ZZZ-9ee87d", "700", "METATEST-e05d11-01", "1500",
        "--gas-limit", "100000000",
        "--function", "add",
        "--arguments", "10",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "proposeAsyncCall@000000000000000005000a2a0f13340978c2eea268a5a2dcf917012978f61f5c@@4d756c7469455344544e46545472616e73666572@0000000000000000050038942113917a6ba7faebbbd69953716064c70d8c1f5c@02@5a5a5a2d396565383764@@02bc@4d455441544553542d653035643131@01@05dc@616464@0a"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0


def test_propose_add_board_member(capsys: Any):
    return_code = main([
        "multisig", "add-board-member",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--proposed-member", "erd1fggp5ru0jhcjrp5rjqyqrnvhr3sz3v2e0fm3ktknvlg7mcyan54qzccnan",
        "--pem", str(alice),
        "--nonce", "12243",
        "--chain", "T",
        "--gas-limit", "10000000"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "proposeAddBoardMember@4a101a0f8f95f1218683900801cd971c6028b1597a771b2ed367d1ede09d9d2a"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0


def test_propose_add_proposer(capsys: Any):
    return_code = main([
        "multisig", "add-proposer",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--proposed-member", "erd1fggp5ru0jhcjrp5rjqyqrnvhr3sz3v2e0fm3ktknvlg7mcyan54qzccnan",
        "--pem", str(alice),
        "--nonce", "12244",
        "--chain", "T",
        "--gas-limit", "10000000"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "proposeAddProposer@4a101a0f8f95f1218683900801cd971c6028b1597a771b2ed367d1ede09d9d2a"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0


def test_propose_remove_user(capsys: Any):
    return_code = main([
        "multisig", "remove-user",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--proposed-member", "erd1fggp5ru0jhcjrp5rjqyqrnvhr3sz3v2e0fm3ktknvlg7mcyan54qzccnan",
        "--pem", str(alice),
        "--nonce", "12245",
        "--chain", "T",
        "--gas-limit", "10000000"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "proposeRemoveUser@4a101a0f8f95f1218683900801cd971c6028b1597a771b2ed367d1ede09d9d2a"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0


def test_propose_change_quorum_size(capsys: Any):
    return_code = main([
        "multisig", "quorum",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--quorum-size", "2",
        "--pem", str(alice),
        "--nonce", "12247",
        "--chain", "T",
        "--gas-limit", "10000000"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "proposeChangeQuorum@02"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0


def get_transaction(capsys: Any) -> Dict[str, Any]:
    out = _read_stdout(capsys)
    output = json.loads(out)
    return output["emittedTransaction"]


def _read_stdout(capsys: Any) -> str:
    return capsys.readouterr().out.strip()
