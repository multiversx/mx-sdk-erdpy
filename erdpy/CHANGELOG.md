# Change Log

All notable changes will be documented in this file.

Check [Keep a Changelog](http://keepachangelog.com/) for recommendations on how to structure this file.

## [Unreleased]
 - TBD

## [2.0.5]
 - [Prepare erdpy for accepting any address hrp](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/158)

## [2.0.4]
 - Fix resolving latest release of Github repositories

## [2.0.3]
 - [Hot fix: Rust env for contract reports is missing system PATH](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/154)

## [2.0.2]
 - [Fix environment variables for Rust](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/153)

## [2.0.1]
 - [Fix erdpy testnet config](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/150)
 - [Fix tests](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/149)
 - [Fix test replacement rules](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/148)

## [2.0.0]
 - [Show password prompt if no passfile specificied](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/144)

## [1.5.2]
 - [Fix build arguments for report creator](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/143)

## [1.5.1]
 - [Pass contract build options to report creator](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/142)

## [1.5.0]
 - [Improve "contract build" for Rust projects](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/140)

## [1.4.0]
 - [Add `ledgercomm[hid]`](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/139)

## [1.3.3]
 - [Pin cryptography](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/137)

## [1.3.2]
 - [Do not copy test wallets into the newly created contract (not necessary anymore)](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/134)

## [1.3.1]
 - [Re-add the pattern erdpy/wallet/*.txt in MANIFEST.in. Was removed by mistake in a previous release.](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/133)

## [1.3.0]
 - [Prepare integration with erdjs-snippets (from templates)](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/126)
 - [Move test wallets to a separate repository. Handle them as an erdpy dependency.](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/127)
 - [Fix log for builds using absolute paths.](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/128)
 - [CLI output builder: remove deprecated fields.](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/129)

## [1.2.3]
 - [Fix activation flag check, fix flag name](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/123)
 - [Fix reference to libwasmer (referenced by mandos-test)](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/124)

## [1.2.2]
 - [Add (update) examples of using erdpy in Python scripts. Refactoring.](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/120)
 - [Allow "str:" and "0x" as contract arguments, as well](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/121)

## [1.2.1] - 07.03.2022
 - [Bugfix: fix functions in EEI registry](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/119)
 - [Bit of cleanup (remove deprecated files / functionality)](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/113)

## [1.2.0] - 07.03.2022
 - [On contract builld, reveal imported functions and check compatibility](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/111)

## [1.1.0] - 01.03.2022
 - [Add reports: contract sizes and twiggy symbol checks](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/106)
 - [Add `--recursive` option on contract build](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/104)
 - [Local testnet: minor refactoring, and remove `*:TRACE` from the default log-level](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/103)
 - [Transaction simulation & cost simulation: fix & redesign](https://github.com/ElrondNetwork/elrond-sdk-erdpy/pull/102)

## [1.0.25] - 02.02.2022
 - Remove old & deprecated, experimental code related to the Elrond IDE
 - Fix `erdpy account get-transactions` (handle transactions with no data field)
 - Fix link in documentation
 - Fix build (test) issues on Github Actions by setting erdpy's `github_api_token`
 - Added caching for the github releases URL when creating projects from templates in order to avoid rate limit errors
 - Fix issue with project creation when using the `crowdfunding-esdt` template due to dependencies
 - Add `readable` and `payable_by_sc` code metadata flags
 - `erdpy contract clean` fix - the `meta/target` folder is removed

## [1.0.24] - 16.12.2021
 - Refactor and fix Ledger signing
 - Fix erdpy-up `venv` installation on Ubuntu
 - Remove tests for ERC20 contracts, they have been deprecated

## [1.0.23] - 29.11.2021
 - Fix - when specifying `latest` for a dependency, get the highest semantic version instead of the most recent release
 - Fix github actions to run `pytest` tests as well

## [1.0.22] - 22.11.2021
 - Fix the patching of the `meta` subproject
 - Add a check when signing transactions so that the gas limit is below the maximum allowed
 - Add `--from-branch` option for `erdpy-up.py`
 - Add github actions check for MacOS
 - Update help strings and `CLI.md`

## [1.0.21] - 01.11.2021
 - New command `erdpy wallet new`, which generates a new wallet mnemonic and optionally saves it to JSON or PEM
 - Add support for Rust contract `meta` crates
 - Update reference to the renamed VM repository (VM dependency is now named `vmtools`)
 - Change `erdpy deps install all` to avoid installing / overwriting non-repository dependencies, e.g. Rust, LLVM, Go
 - Update help strings and `CLI.md`

## [1.0.20] - 26.10.2021
 - Bugfix by [phanletrunghieu](https://github.com/phanletrunghieu): use $PATH in `erdpy-up`
 - Bugfix by [x2ocoder](https://github.com/x2ocoder): add missing `enable_epochs` configurations
 - Dependency tags now accept `latest`
 - New optional configuration value `github_api_token` for querying latest versions from Github
 - The command `erdpy deps install` now accepts `all` as an argument
 - More fixes for `erdpy testnet`

## [1.0.19] - 05.10.2021
 - Bugfix by [MWFIAE](https://github.com/MWFIAE): add missing `enable_epochs` configurations

## [1.0.18] - 14.09.2021
 - Load a local `erdpy.json` file when running `erdpy` commands, containing default values for CLI options per project
 - Bugfix by [MWFIAE](https://github.com/MWFIAE): correctly verify the value of the `--bytecode` argument
 - Bugfix by [MWFIAE](https://github.com/MWFIAE): `QueryResult` objects are now properly JSON-serializable
 - Add more output information after building and deploying contracts
 - Improve error reporting to standard output
 - Enable `mypy` checking as a GitHub action
 - Add and fix more type hints for `mypy`

## [1.0.16] - 27.08.2021
 - Merge branch `legolas-addons`
 - Fix `erdpy testnet` to work with recent changes in `elrond-go`
 - Add more type hints for `mypy`
 - Many small improvements

## [1.0.12] - 22.03.2021
 - Minor fixes to the configuration profiles support
 - Dependency `arwentools` is now built locally, instead of fetching precompiled binaries

## [1.0.11] - 12.03.2021
 - Update commands for testnet in order to work with the development and master elrond-go branch
 - Update the proxy config for testnet in order to have all the api routes active
 - Added new commands for validator
 - Fix bug with the command add-nodes for staking-provider
 - Add --wait-result flag for erdpy tx new cli command.

## [1.0.10] - 25.02.2021
 - [Fixed a bug in the testnet setup process when creating the config for the proxy app #213](https://github.com/ElrondNetwork/elrond-sdk/pull/213) 

## [1.0.9] - 29.01.2021
 -  [Multiple config templates #152](https://github.com/ElrondNetwork/elrond-sdk/pull/152). One can now `switch` between different **configuration** profiles.
 -  [Refactor validator.pem parser, allow lookup by index #126](https://github.com/ElrondNetwork/elrond-sdk/pull/126).
 -  [erdpy contract build - naming fix, extra CLI options #161](https://github.com/ElrondNetwork/elrond-sdk/pull/161).

## [1.0.8] - 25.01.2021
 -  Fix flags for phase 3 features #162.

## [1.0.7] - 19.01.2021
 - Update reference to newer Arwentools (Mandos).

## [1.0.6] - 15.01.2021
 - Add commands for the delegation manager contract.
 - Added commands for DNS. Tests for DNS CLI.
 - Added `--sender-username` and `--receiver-username` parameters.
 - For Rust projects, run ABI generator upon building the WASM file.
 - For Rust projects, patch contract templates wrt. ABI module.
 - Cache templates repository (30 seconds). 
 - Add github workflow for erdpy.
 - Optimize running time for tests, build time (for rust projects).
 - Add PIP update prior installing dependencies #136 @tebayoso (PR from community).
 - `erdpy testnet` - enabled Phase 3 features.
 - `erdpy testnet`: Fixes for MacOS, enable log-save for Proxy.

## [1.0.3] - 28.12.2020
 - `erdpy contract new`: Fix typo (`crate` / `create`).
 - `erdpy contract new`: remove `path` of `dev-dependencies`, for rust templates.
 - `erdpy contract new`: remove debug-related logic (not needed anymore).

## [1.0.2] - 28.12.2020
 - Update reference to templates.

## [1.0.1] - 21.12.2020
 - Update reference to templates.

## [1.0.0] - 16.12.2020
 - Update reference to templates.

## [0.9.9] - 14.12.2020
 - Update reference to templates, to arwentools.
 - Handle empty query response.
 - Remove some redundant logging.
 - Automatically copy devnet wallets into the project (at `contract new`).

## [0.9.8] - 10.12.2020
 - Fix devnet config wrt. latest node changes.
 - Fix path to templates (for contract new).

## [0.9.7] - 03.12.2020
 - Refactor (mostly around validator commands).
 - Add "send", "simulate" for `validator` commands.
 - Fix `staking.py` example.
 - Add `Address.is_contract_address()`.
 - Change testnet URL.
 - Fix tests, cleanup test data.

## [0.9.5] - 28.10.2020
 - Add dependency tag for elrond-wasm-rs.

## [0.9.4] - 27.10.2020
 - Minor fix for Rust templates.

## [0.9.3] - 26.10.2020
 - Add better output for simulated deployments.

## [0.9.2] - 26.10.2020
 - Do not build `.hex` file anymore at `contract build`.
 - Patch field `name` in contract templates / mandos tests.
 - Patch logging and log-level for local testnet. Include `arwen` logs.
 - Optimize local testnet: **no observers, only 4 DNS contracts, less waiting time.**
 - Fix `testnet clean` (when folder is missing).
 - Implement global scope. Initialize `chainID` and `proxy` parameters from `testnet.toml`, if any. 
 - Add `erdpy data` sub-command to parse files, store and load key-value pairs. Useful for IDE snippets, but not limited to.
 - Pretty handling of `Ctrl+C`, overall.
 - Reference newest **Mandos**.
 - For NodeJS dependency, add a symlink to latest version. Set `env` for nodejs execution. Will be used for `erdtestjs` etc.
 - Prettier dump of `account` json (`erdpy get account`).
 - Support `omit-fields` parameter (when dumping) for `account get` and `tx get`.

## [0.9.1] - 15.10.2020
 - Adjust `erdpy validator` commands to use the `MCL signer` (external component).
 - Fix `erdpy account` with flags `--nonce, --balance`.
 - Possible fix for setup / installation: https://github.com/ElrondNetwork/elrond-sdk/issues/58.

## [0.8.9] - 09.10.2020
 - Minor `erdpy-up` improvements.
 - Minor `erdpy testnet ...` fixes regarding the patched configuration of the Node (`config.toml`).
 - Reference newest `arwentools`.
 - Fix response casing for `contract query`.

## [0.8.7] - 29.09.2020
 - Allow one to start a local testnet via `erdpy testnet ...` commands.
 - Simulate transactions via `--simulate` flag (both regular and smart contract transactions).
 - Rust build - fix name of binary artifact ("-" vs. "_").

## [0.8.5] - 14.09.2020
 - Fix templates patching to work with elrond-wasm `0.6.0`.
 - Update build with respect to elrond-wasm `0.6.0`.
 - Update reference to newest Mandos `v0.3.35`, update tests runner.
 - Remove dependency on `list_api.txt` for C projects.
 - Trim whitespace for "wallet derive --mnemonic".
 - Fix `erdpy validator` commands (were broken upon refactoring).

## [0.8.3] - 12.08.2020
 - Fix proxy requests, implement `hyperblock` route.

## [0.8.2] - 06.08.2020
 - Strip password for keyfile (remove left & right spaces, newlines)
 - Allow one to specify path to WASM (bytecode) for `contract deploy` and `contract upgrade`
 - Update reference to Arwen Tools
 - Allow sending SC transactions in offline mode (`--send` defaults to `false`).
 - Allow multi-pem files (selection via `--pem-index` parameter).


## [0.8.1] - 29.07.2020

 - Add SDK helpers to generate relayed transactions.

## [0.8.0] - 26.07.2020

 - Updated signing procedure with respect to the `data` field (which is now base64-encoded)
 - Redesigned the CLI for `validator stake`
 - Refactoring and design improvements


**Note that below, the changelog is in chronological order. It will be soon updated to be in inverse chronological order (how it should have been in the first place).**

## [0.0.4]

- Initial release

## [0.0.5]

### Fixed

- Include **psutil** in the list of dependencies in `setup.py`.
- Handle missing / `none` arguments at deploy.
- Default to current directory in `build` command.
- Allow paths starting with `~` when specifying PEM.
- Forward gas limit, gas price parameters correctly.

### Changed

- Improve example for testnet to allow query after deploy.

## [0.0.6]

### Fixed

- Default to current directory in `build` command.

## [0.0.7]

### Added

- Enabled test runner: `erdpy test --wildcard='*'`

## [0.0.8]

### Fixed

- Set `LD_LIBRARY_PATH` before executing `nodedebug` and `testrunner`.

## [0.0.9]

### Fixed

- Fixed passing environment variables to test runner.

## [0.1.0]

### Fixed

- Fixed node-debug stdout & stderr decode.

### Other

- Updated reference to node-debug.
- SOLL migration in progress (Solidity build does not work yet).

## [0.1.1]

### Fixed

- Fixed Solidity / SOLL buildchain.

## [0.1.2]

### Fixed

- Default to current directory for `erdpy deploy`.

## [0.1.3]

### Fixed

- Fix passing arguments for command `erdpy call`.

## [0.1.4]

### Fixed

- Fix passing arguments for command `erdpy query`.

## [0.1.5]

### Fixed

- For MacOS `chmod +x` upon downloading SOLL, nodedebug.

## [0.1.6]

### Fixed

- Downloads performed using `requests` module (certificate errors on MacOS otherwise).

## [0.1.7]

### Fixed

- Node-debug build for MacOS.

### Other

- Updated reference to node-debug.

## [0.1.9]

### Fixed

- Transaction signing - updated to **Ed25519**
- Removed **node-debug** from the testnet flows (deployment and execution of smart contracts)
- Fixed contract project generation from Rust templates
- Minor fixes on the build flow.

### Other

- Temporarily disabled node-debug interaction (node-debug's place will be soon taken by a debug version of Arwen VM)
- Added extra command to prepare and send transactions against the testnet
- Added extra examples.

## [0.2.0]

### Fixed

- Fixed getting metrics from testnet.

### Other

- Temporarily disabled transaction costs estimators.

## [0.2.1]

### Fixed

- Fixed reference to pycryptodomex.

## [0.2.2]

### Fixed

- Fixed (improved) handling of proxy request errors.

## [0.2.3]

### Fixed

- Fixed CPP compilation support.

## [0.2.4]

### Fixed

- Dependency to psutils.

### Added

- Extra CLI command to prepare and send transaction.

## [0.2.5]

### Fixed

- Format of "transaction.data" field.


## [0.2.6]

### Fixed

- Upgradeable smart contracts.

## [0.2.7]

### Other

- Implement bech32 addresses.

## [0.2.8]

### Fixed

- Fixed calls to estimators.

## [0.2.9]

### Fixed

- Adjust reference to the new JSON testing tool.
- Other minor fixes.

## [0.3.0]

### Fixed

- Fix path to WASM binary (for rust projects).
- Fix build of rust projects (trim size of artifact).

## [0.3.1], [0.3.2]

### Fixed

- Fix path to contract binary within JSON tests.
- Fix templates download by deleting the "templates" folder at first.

## [0.3.3]

### Fixed

- Display address of smart contract upon deploy
- Improve tests CLI
- Copy build artifacts to "output" folder

## [0.3.4]

### Fixed

- Extra exported function for C builds

## [0.3.5]

### Features

- Stake, UnStake, UnBound, UnJail, ChangeRewardAddress

## [0.3.6]

### Fixed

- Extra exported function for C builds

## [0.3.7]

### Fixed

- Serialization algorithm used for signing ("data as string")
- Prettier CLI

## [0.3.8]

### Fixed

- Long description for setup (temporary workaround).

## [0.3.9]

### Fixed

- Add `claim` function for validators

## [0.4.0]

### Fixed

- Fixed action of CLI / network.

## [0.4.1]

## [0.4.2]

### Fixed

- Fixed passing arguments for stake.

## [0.4.3]

### Features

- First implementation of the transactions dispatcher.

## [0.4.4]

### Features

- Fix packaging.


## [0.4.5]

### Features

- Fix gas estimators for staking.
- Add mnemonic to PEM converter.


## [0.4.6]

### Fixed

- Fixed `new` command (default directory).
- Improved `deploy` command (add parameter `outfile`).

## [0.4.7]

### Fixed

- Mark `gas-limit` field as required.

## [0.4.8]

### Fixed

- Update reference to `mandos`, fix templating for tests.


## [0.4.9] - 24.06.2020

### Fixed

- Improved CLI for contracts (added CLI group of actions)
- Fixed response handling for `send-multiple`

## [0.5.0] - 25.06.2020

### Fixed

- Fixed list of `elrondei` functions.

## [0.5.1] - 25.06.2020

### Fixed

- Fix passing `--nonce` argument to validator commands.
- Add flag `--recall-nonce`, as an alternative to specifying the `--nonce=42`.

### Other

- Deprecated commands `stake-prepare` and `stake-send`. Will be replaced soon by `stake --prepare` and `tx send`.

## [0.7.0] - 13.07.2022

 - Redesigned CLI for creating and broadcasting transactions (`erdpy tx`).
 - Included `chainID` and `version` in transactions (erdpy, erdjs), updated signature accordingly.
 - Allow provisioning of wallet JSON **key-file** as well, in addition to PEM files (which will be deprecated). Many thanks to [flyingbasalt](https://github.com/flyingbasalt/erdkeys).
 - Redesign `erdpy-up` to use light Python virtual environments (`venv`).
 - Allow options `--no-modiy-path` and `--exact-version` in `erdpy-up`
 - Renamed some CLI commands (for `wallet`, for `tx`).
 - Cleanup templating logic for Smart Contracts - moved some features to Elrond IDE.
 - erdtestjs fixes and design improvements / refactoring.
 - Completely redesigned dependency management (`erdpy deps`), improved associated CLI.
 - Refactor and group (under `erdpy group`) validator-related commands.
 - Improved CLI help, added descriptions.
 - Do not receive mnemonic as parameter in `erdpy wallet derive`, but ask for user input instead.
 - Add Clean command for Smart Contract projects.
 - Create symlinks for `arwentools` binaries.
 - Updated references to `arwentools` components (Mandos, Arwen Debug).
 - Added CLI group `erdpy config`, which manages `~/elrondsdk/elrond.json`.
 - Deprecated `~/ElrondSCTools`, which will be removed by `erdpy-up`. The new installation folder is `~/elrondsdk`.
 - Require Python 3.8 on MacOS.
 - Smart Contracts `query` - return as base64, hex, number.
 - Require nonce for SC `deploy` & `call`.
 - Removed .py SC interaction samples, moved to `sc-examples` `sc-examples-rs` repositories, so that they become available in Elrond IDE.
 - Removed some deprecated code.
 - `mypy`-related refactoring.
 - Fix accounts CLI. Truncate data for "account get-transactions".

## [0.7.1] - 13.07.2020

### Fixed

 - Installation of `rust` (was broken upon refactoring).
 - Re-added command `erdpy contract test`.
 - Throw error when bad input for `erdpy validator ...`.

## [0.7.2] - 13.07.2020

### Fixed

 - Fixed call to `BunchOfTransactions`.
