#!/usr/bin/env bash

source "./shared.sh"

testTrivialCommands() {
    echo "testTrivialCommands"
    ${CLI} contract templates
}

testCreateContracts() {
    echo "testCreateContracts"
    ${CLI} contract new --template adder --path ${SANDBOX} || return 1
}

testBuildContracts() {
    echo "testBuildContracts"

    # Improve compilation time by reusing build artifacts for Rust projects
    export TARGET_DIR=$(pwd)/${SANDBOX}/TARGET
    mkdir -p ${TARGET_DIR}

    ${CLI} contract build --path=${SANDBOX}/adder --target-dir=${TARGET_DIR} || return 1
    assertFileExists ${SANDBOX}/adder/output/adder.wasm || return 1
    assertFileExists ${SANDBOX}/adder/output/adder.abi.json || return 1
}

testCleanContracts() {
    echo "testCleanContracts"

    assertFileExists ${SANDBOX}/adder/output/adder.wasm || return 1
    assertFileExists ${SANDBOX}/adder/output/adder.abi.json || return 1
    ${CLI} contract clean --path ${SANDBOX}/adder || return 1
    assertFileDoesNotExist ${SANDBOX}/adder/output/adder.wasm || return 1
    assertFileDoesNotExist ${SANDBOX}/adder/output/adder.abi.json || return 1
}

testVerifyContract(){
    echo "testVerifyContract"

    nohup python3 local_verify_server.py >/dev/null 2>&1 &
    sleep 1

    query_response=$(curl -s localhost:7777/verify -X POST)

    command_response=$(${CLI} contract verify erd1qqqqqqqqqqqqqpgquzmh78klkqwt0p4rjys0qtp3la07gz4d396qn50nnm \
                        --verifier-url=http://localhost:7777 --packaged-src=testdata/dummy.json \
                        --pem=testdata/walletKey.pem --docker-image=multiversx/sdk-rust-contract-builder:v4.0.0)

    result_curl=$(echo $query_response | awk -F ": " '{ print $2 }' | awk -F'"' '{print $2}')
    result_cli=$(echo $command_response | awk -F ": " '{ print $2 }' | awk -F'"' '{print $2}')

    if [[ $result_curl == $result_cli ]];
    then
        echo "Test passed!"
    else
        return 1
    fi

    pkill -f local_verify_server.py
}

testReproducibleBuild() {
    echo "testReproducibleBuild"

    wget -O ${SANDBOX}/example.zip https://github.com/multiversx/mx-reproducible-contract-build-example-sc/archive/refs/tags/v0.2.1.zip || return 1
    unzip ${SANDBOX}/example.zip -d ${SANDBOX} || return 1
    ${CLI} contract reproducible-build ${SANDBOX}/mx-reproducible-contract-build-example-sc-0.2.1 --docker-image=multiversx/sdk-rust-contract-builder:v4.1.2 --no-docker-interactive --no-docker-tty || return 1
    assertFileExists ${SANDBOX}/mx-reproducible-contract-build-example-sc-0.2.1/output-docker/artifacts.json || return 1
}

testAll() {
    ${CLI} config set dependencies.rust.tag ${RUST_VERSION}

    cleanSandbox || return 1
    testTrivialCommands || return 1
    testCreateContracts || return 1
    testBuildContracts || return 1
    testCleanContracts || return 1
}
