import json
from pathlib import Path
from typing import Any

import pytest

from multiversx_sdk_cli.cli import main

parent = Path(__file__).parent


# def test_contract_new():
#     main([
#         "contract",
#         "new",
#         "--template",
#         "adder",
#         "--path",
#         f"{parent}/testdata-out/SANDBOX"
#     ])
#     assert Path.is_dir(parent / "testdata-out" / "SANDBOX" / "adder")


# def test_contract_new_with_bad_code():
#     # we change the contract code so the build would fail so we can catch the error
#     main([
#         "contract",
#         "new",
#         "--template",
#         "adder",
#         "--path",
#         f"{parent}/testdata-out/SANDBOX",
#         "--name",
#         "adder-bad-src"
#     ])

#     assert Path.is_dir(parent / "testdata-out" / "SANDBOX" / "adder-bad-src")
#     replace_variable_with_unknown_variable_for_adder()


# def replace_variable_with_unknown_variable_for_adder():
#     # this is done in order to replace the value added in the adder contract with a unknown variable
#     with open(parent / "testdata-out" / "SANDBOX" / "adder-bad-src" / "src" / "adder_bad_src.rs", "r") as f:
#         contract_lines = f.readlines()

#     for index, line in reversed(list(enumerate(contract_lines))):
#         if "value" in line:
#             contract_lines[index] = line.replace("value", "unknown_variable")
#             break

#     with open(parent / "testdata-out" / "SANDBOX" / "adder-bad-src" / "src" / "adder_bad_src.rs", "w") as f:
#         f.writelines(contract_lines)


# @pytest.mark.skip_on_windows
# def test_contract_build():
#     main([
#         "contract",
#         "build",
#         "--path",
#         f"{parent}/testdata-out/SANDBOX/adder"
#     ])

#     assert Path.is_file(parent / "testdata-out" / "SANDBOX" / "adder" / "output" / "adder.wasm")


# @pytest.mark.skip_on_windows
# def test_bad_contract_build(capsys: Any):
#     ERROR = "Build error: error code = 101, see output."

#     main([
#         "contract",
#         "build",
#         "--path",
#         f"{parent}/testdata-out/SANDBOX/adder-bad-src"
#     ])

#     out, _ = capsys.readouterr()

#     if ERROR in out:
#         assert True
#     else:
#         assert False


def test_contract_deploy():
    output_file = parent / "testdata-out" / "deploy.json"

    main(
        [
            "contract",
            "deploy",
            "--bytecode",
            f"{parent}/testdata/adder.wasm",
            "--pem",
            f"{parent}/testdata/testUser.pem",
            "--proxy",
            "https://testnet-api.multiversx.com",
            "--chain",
            "T",
            "--recall-nonce",
            "--gas-limit",
            "5000000",
            "--arguments",
            "0",
            "--outfile",
            str(output_file),
        ]
    )
    assert Path.is_file(output_file)


def test_contract_upgrade():
    output_file = parent / "testdata-out" / "upgrade.json"
    contract_address = "erd1qqqqqqqqqqqqqpgq5l9jl0j0gnqmm7hn82zaydwux3s5xuwkyq8srt5vsy"

    main(
        [
            "contract",
            "upgrade",
            contract_address,
            "--bytecode",
            f"{parent}/testdata/adder.wasm",
            "--pem",
            f"{parent}/testdata/testUser.pem",
            "--proxy",
            "https://testnet-api.multiversx.com",
            "--chain",
            "T",
            "--recall-nonce",
            "--gas-limit",
            "5000000",
            "--arguments",
            "0",
            "--outfile",
            str(output_file),
        ]
    )
    assert Path.is_file(output_file)


def test_contract_call():
    output_file = parent / "testdata-out" / "call.json"
    contract_address = "erd1qqqqqqqqqqqqqpgq5l9jl0j0gnqmm7hn82zaydwux3s5xuwkyq8srt5vsy"

    main(
        [
            "contract",
            "call",
            contract_address,
            "--function",
            "add",
            "--pem",
            f"{parent}/testdata/testUser.pem",
            "--proxy",
            "https://testnet-api.multiversx.com",
            "--chain",
            "T",
            "--recall-nonce",
            "--gas-limit",
            "5000000",
            "--arguments",
            "5",
            "--outfile",
            str(output_file),
        ]
    )
    assert Path.is_file(output_file)


def test_contract_transfer_and_execute(capsys: Any):
    contract_address = "erd1qqqqqqqqqqqqqpgqv7sl6ws5dgwe5m04xtg0dvqyu2efz5a6d8ssxn4k9q"
    first_token = "NFT-123456-02"
    second_token = "ESDT-987654"

    main([
        "contract", "call", contract_address,
        "--pem", f"{parent}/testdata/testUser.pem",
        "--chain", "D",
        "--nonce", "7",
        "--gas-limit", "5000000",
        "--function", "add",
        "--arguments", "5",
        "--token-transfers", first_token, "1"
    ])
    data = get_transaction_data(capsys)
    assert data == "ESDTNFTTransfer@4e46542d313233343536@02@01@0000000000000000050067a1fd3a146a1d9a6df532d0f6b004e2b29153ba69e1@616464@05"

    # Clear the captured content
    capsys.readouterr()

    main([
        "contract", "call", contract_address,
        "--pem", f"{parent}/testdata/testUser.pem",
        "--chain", "D",
        "--nonce", "77",
        "--gas-limit", "5000000",
        "--function", "add",
        "--arguments", "5",
        "--token-transfers", first_token, "1", second_token, "100"
    ])
    data = get_transaction_data(capsys)
    assert data == "MultiESDTNFTTransfer@0000000000000000050067a1fd3a146a1d9a6df532d0f6b004e2b29153ba69e1@02@4e46542d313233343536@02@01@455344542d393837363534@@64@616464@05"


def test_contract_flow(capsys: Any):
    alice = f"{parent}/testdata/alice.pem"
    adder = f"{parent}/testdata/adder.wasm"

    main([
        "contract", "deploy",
        "--bytecode", adder,
        "--pem", alice,
        "--recall-nonce",
        "--gas-limit", "5000000",
        "--proxy", "https://testnet-api.multiversx.com",
        "--arguments", "0",
        "--send", "--wait-result"
    ])
    contract = get_contract_address(capsys)

    # Clear the captured content
    capsys.readouterr()

    main([
        "contract", "query", contract,
        "--function", "getSum",
        "--proxy", "https://testnet-api.multiversx.com"
    ])
    response = get_query_response(capsys)
    assert len(response) == 1
    assert response == [""]

    # Clear the captured content
    capsys.readouterr()

    main([
        "contract", "call", contract,
        "--pem", alice,
        "--function", "add",
        "--recall-nonce",
        "--gas-limit", "5000000",
        "--proxy", "https://testnet-api.multiversx.com",
        "--arguments", "7",
        "--send", "--wait-result"
    ])

    # Clear the captured content
    capsys.readouterr()

    main([
        "contract", "query", contract,
        "--function", "getSum",
        "--proxy", "https://testnet-api.multiversx.com"
    ])
    response = get_query_response(capsys)
    assert len(response) == 1
    assert response == ["07"]

    # Clear the captured content
    capsys.readouterr()

    main([
        "contract", "upgrade", contract,
        "--bytecode", adder,
        "--pem", alice,
        "--recall-nonce",
        "--gas-limit", "5000000",
        "--proxy", "https://testnet-api.multiversx.com",
        "--arguments", "0",
        "--send", "--wait-result"
    ])


def test_contract_deploy_without_required_arguments():
    alice = f"{parent}/testdata/alice.pem"
    adder = f"{parent}/testdata/adder.wasm"

    return_code = main([
        "contract", "deploy",
        "--bytecode", adder,
        "--pem", alice,
        "--recall-nonce",
        "--gas-limit", "5000000",
        "--arguments", "0",
        "--send", "--wait-result"
    ])
    assert return_code


def test_contract_commands_argument_parameter():
    alice = f"{parent}/testdata/alice.pem"
    adder = f"{parent}/testdata/adder.wasm"

    return_code = main([
        "contract", "deploy",
        "--bytecode", adder,
        "--pem", alice,
        "--nonce", "7",
        "--chain", "D",
        "--gas-limit", "5000000",
        "--arguments", "foobar",
    ])
    assert return_code

    return_code = main([
        "contract", "deploy",
        "--bytecode", adder,
        "--pem", alice,
        "--nonce", "7",
        "--chain", "D",
        "--gas-limit", "5000000",
        "--arguments", "str:foobar",
    ])
    assert not return_code


def test_contract_deploy_with_abi(capsys: Any):
    alice = f"{parent}/testdata/alice.pem"
    multisig = f"{parent}/testdata/multisig.wasm"
    multisig_abi = f"{parent}/testdata/multisig.abi.json"

    return_code = main([
        "contract", "deploy",
        "--bytecode", multisig,
        "--pem", alice,
        "--chain", "T",
        "--nonce", "7",
        "--gas-limit", "5000000",
        "--arguments", "2", "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th", "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"
    ])
    assert not return_code

    deploy_without_abi_data = get_transaction_data(capsys)
    # Clear the captured content
    capsys.readouterr()

    return_code = main([
        "contract", "deploy",
        "--bytecode", multisig,
        "--abi", multisig_abi,
        "--pem", alice,
        "--chain", "T",
        "--nonce", "7",
        "--gas-limit", "5000000",
        "--arguments-file", f"{parent}/testdata/deploy_multisig_args.json"
    ])
    assert not return_code

    deploy_with_abi_data = get_transaction_data(capsys)
    assert deploy_without_abi_data == deploy_with_abi_data
    assert deploy_without_abi_data.endswith("@02@0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1@c0006edaaee4fd479f2f248b341eb11eaecaec4d7dee190619958332bba5200f")
    assert deploy_with_abi_data.endswith("@02@0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1@c0006edaaee4fd479f2f248b341eb11eaecaec4d7dee190619958332bba5200f")


def test_contract_call_with_abi(capsys: Any):
    alice = f"{parent}/testdata/alice.pem"
    multisig_abi = f"{parent}/testdata/multisig.abi.json"

    return_code = main([
        "contract", "call", "erd1qqqqqqqqqqqqqpgqpg2tnjelx3s3dhkksqhjavprtgmt9xt4d8ss9al8m4",
        "--pem", alice,
        "--chain", "T",
        "--nonce", "7",
        "--gas-limit", "5000000",
        "--function", "proposeBatch",
        "--abi", multisig_abi,
        "--arguments-file", f"{parent}/testdata/call_multisig_propose_batch_args.json"
    ])
    assert not return_code

    data = get_transaction_data(capsys)
    assert data == "proposeBatch@0500000000000000000500ed8e25a94efa837aae0e593112cfbb01b448755069e1000000080de0b6b3a7640000010000000000e4e1c000000003616464000000010000000107"


def test_contract_upgrade_with_abi(capsys: Any):
    alice = f"{parent}/testdata/alice.pem"
    multisig_abi = f"{parent}/testdata/multisig.abi.json"

    return_code = main([
        "contract", "call", "erd1qqqqqqqqqqqqqpgqpg2tnjelx3s3dhkksqhjavprtgmt9xt4d8ss9al8m4",
        "--pem", alice,
        "--chain", "T",
        "--nonce", "7",
        "--gas-limit", "5000000",
        "--function", "proposeSCUpgradeFromSource",
        "--abi", multisig_abi,
        "--arguments-file", f"{parent}/testdata/upgrade_multisig_args.json"
    ])
    assert not return_code

    data = get_transaction_data(capsys)
    assert data == "proposeSCUpgradeFromSource@000000000000000005000a14b9cb3f346116ded6802f2eb0235a36b2997569e1@@00000000000000000500ed8e25a94efa837aae0e593112cfbb01b448755069e1@0500@"


def test_contract_query(capsys: Any):
    alice = f"{parent}/testdata/alice.pem"
    adder = f"{parent}/testdata/adder.wasm"
    adder_abi = f"{parent}/testdata/adder.abi.json"

    return_code = main([
        "contract", "deploy",
        "--bytecode", adder,
        "--abi", adder_abi,
        "--pem", alice,
        "--recall-nonce",
        "--gas-limit", "5000000",
        "--proxy", "https://testnet-api.multiversx.com",
        "--arguments", "0",
        "--send", "--wait-result"
    ])
    assert not return_code
    contract = get_contract_address(capsys)

    # Clear the captured content
    capsys.readouterr()

    return_code = main([
        "contract", "call", contract,
        "--pem", alice,
        "--function", "add",
        "--recall-nonce",
        "--gas-limit", "5000000",
        "--proxy", "https://testnet-api.multiversx.com",
        "--arguments", "14",
        "--send", "--wait-result"
    ])
    assert not return_code

    # Clear the captured content
    capsys.readouterr()

    # invalid, without abi
    return_code = main([
        "contract", "query", contract,
        "--function", "getSummm",
        "--proxy", "https://testnet-api.multiversx.com"
    ])
    assert return_code
    output = _read_stdout(capsys)
    if "invalid function (not found)" in output:
        assert True
    else:
        assert False

    # Clear the captured content
    capsys.readouterr()

    # invalid, with abi, error is thrown by sdk-py
    return_code = main([
        "contract", "query", contract,
        "--function", "getSummm",
        "--abi", adder_abi,
        "--proxy", "https://testnet-api.multiversx.com"
    ])
    assert return_code
    output = _read_stdout(capsys)
    if "endpoint 'getSummm' not found" in output:
        assert True
    else:
        assert False

    # Clear the captured content
    capsys.readouterr()

    # query contract, without abi
    return_code = main([
        "contract", "query", contract,
        "--function", "getSum",
        "--proxy", "https://testnet-api.multiversx.com"
    ])
    assert not return_code
    response = get_query_response(capsys)
    assert response == ["0e"]

    # Clear the captured content
    capsys.readouterr()

    # query contract, without abi
    return_code = main([
        "contract", "query", contract,
        "--function", "getSum",
        "--abi", adder_abi,
        "--proxy", "https://testnet-api.multiversx.com"
    ])
    assert not return_code
    response = get_query_response(capsys)
    assert response == [14]


def _read_stdout(capsys: Any) -> str:
    return capsys.readouterr().out.strip()


def get_contract_address(capsys: Any):
    out = _read_stdout(capsys)
    output = json.loads(out)
    return output["contractAddress"]


def get_query_response(capsys: Any):
    out = _read_stdout(capsys).replace("\n", "").replace(" ", "")
    return json.loads(out)


def get_transaction_data(capsys: Any) -> str:
    out = _read_stdout(capsys)
    output = json.loads(out)
    return output["emittedTransactionData"]
