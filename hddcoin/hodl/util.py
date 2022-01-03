# -*- coding: utf-8 -*-
from __future__ import annotations
import decimal
import sqlite3
import sys
import time
import typing as th

import aiohttp
import blspy   #type:ignore

import hddcoin.hodl
import hddcoin.util
import hddcoin.util.bech32m as bech32m
from hddcoin.consensus.coinbase import create_puzzlehash_for_pk
from hddcoin.consensus.default_constants import DEFAULT_CONSTANTS
from hddcoin.hodl.ContractDetails import ContractDetails
from hddcoin.rpc.full_node_rpc_client import FullNodeRpcClient
from hddcoin.rpc.wallet_rpc_client import WalletRpcClient
from hddcoin.types.blockchain_format.sized_bytes import bytes32
from hddcoin.types.blockchain_format.program import Program, SerializedProgram
from hddcoin.types.coin_spend import CoinSpend
from hddcoin.types.spend_bundle import SpendBundle
from hddcoin.util import bech32m
from hddcoin.util.default_root import DEFAULT_ROOT_PATH
from hddcoin.util.ints import uint32
from hddcoin.util.path import path_from_root
from hddcoin.wallet.derive_keys import master_sk_to_wallet_sk

from . import exc
from .cli.colours import *
from .cli.colours import _
from .hodlrpc import HodlRpcClient


START_TIME_s = time.monotonic()

verbosity = 0  # override this to 1 or 2 for more logging


def vlog(threshold: int, msg: str) -> None:
    if verbosity >= threshold:
        elapsed_s = time.monotonic() - START_TIME_s
        print(f"{DY}[{elapsed_s:6.3f}] {Gy}{msg}{_}")


def loadConfig() -> th.Dict[str, th.Any]:
    vlog(1, f"Loading config file from: {hddcoin.util.default_root.DEFAULT_ROOT_PATH}")
    config = hddcoin.util.config.load_config(hddcoin.util.default_root.DEFAULT_ROOT_PATH,
                                             "config.yaml")
    return config


def addr2puzhash(addr: str, asString = True) -> th.Union[str, bytes32]:
    puzhash = bech32m.decode_puzzle_hash(addr)
    if asString:
        return puzhash.hex()
    return puzhash


def puzhash2addr(puzhash: th.Union[str, bytes32]) -> str:
    if isinstance(puzhash, str):
        if puzhash.startswith("0x"):
            puzhash = puzhash[2:]
        return bech32m.encode_puzzle_hash(bytearray.fromhex(puzhash), "hdd")
    elif isinstance(puzhash, bytes32):
        return bech32m.encode_puzzle_hash(puzhash, "hdd")
    else:
        raise ValueError("Invalid puzzlehash type")


async def getFullNodeRpcClient(config: th.Dict[str, th.Any],
                               rpc_port: int = 0,  # 0 is automatic RPC port
                               ) -> FullNodeRpcClient:
    if not rpc_port:
        rpc_port = config["full_node"]["rpc_port"]
    rpc_port = hddcoin.util.ints.uint16(rpc_port)
    client = await FullNodeRpcClient.create(config["self_hostname"],
                                            rpc_port,
                                            hddcoin.util.default_root.DEFAULT_ROOT_PATH,
                                            config)
    return client


def getOnlyFingerprint(config: th.Dict[str, th.Any],
                       ) -> int:
    keychain = hddcoin.util.keychain.Keychain()
    private_keys = keychain.get_all_private_keys()
    if len(private_keys) != 1:
        # TODO: Proper error handling here!
        raise RuntimeError("There is more than one fingerprint! Cannot auto-select.")
    sk = private_keys[0][0]
    fingerprint = sk.get_g1().get_fingerprint()
    return fingerprint


async def getWalletRpcClient(config: th.Dict[str, th.Any],
                             fingerprint: int,
                             rpc_port: int = 0,  # 0 is automatic RPC port
                             ) -> WalletRpcClient:
    client: WalletRpcClient
    if not rpc_port:
        rpc_port = config["wallet"]["rpc_port"]
    rpc_port = hddcoin.util.ints.uint16(rpc_port)
    vlog(2, "Creating WalletRpcClient")
    client = await WalletRpcClient.create(config["self_hostname"],
                                          rpc_port,
                                          hddcoin.util.default_root.DEFAULT_ROOT_PATH,
                                          config)
    async def _closeClientConnection():
        vlog(2, "Closing walletRPC connection")
        client.close()
        await client.await_closed()
        vlog(2, "walletRPC connection closed")

    vlog(2, "Logging in to wallet")
    try:
        loginRet = (await client.log_in(fingerprint))
    except aiohttp.ClientConnectionError as cce:
        vlog(2, "Trapped ClientConnectionError (but will re-raise)")
        await _closeClientConnection()
        raise cce
    except Exception as e:
        vlog(2, "Trapped Exception (but will re-raise): {e!r}")
        await _closeClientConnection()
        raise e


    if not loginRet["success"]:
        vlog(1, "Unable to log in to standard wallet.")
        await _closeClientConnection()
        vlog(2, "Checking available key count")
        keyCount = len(hddcoin.util.keychain.Keychain().get_all_private_keys())
        vlog(2, f"Found {keyCount} available keys")
        raise exc.KeyNotFound(str(keyCount))

    vlog(2, "Wallet login complete")
    return client


def getNthWalletAddr(config: th.Dict[str, th.Any],
                     sk: blspy.PrivateKey,
                     n: int,
                     ) -> str:
    # Note that this does NOT check if the address has been issued yet.
    if n < 0:
        raise ValueError("n must be >= 0")

    selected = config["selected_network"]
    prefix = config["network_overrides"]["config"][selected]["address_prefix"]

    addr = bech32m.encode_puzzle_hash(
        create_puzzlehash_for_pk(master_sk_to_wallet_sk(sk, uint32(n)).get_g1()),
        prefix,
    )
    return addr


def getFirstWalletAddr(config: th.Dict[str, th.Any],
                       sk: blspy.PrivateKey,
                       ) -> str:
    return getNthWalletAddr(config, sk, 0)


async def _walletIdExists(walletRpcClient: hddcoin.rpc.wallet_rpc_client.WalletRpcClient,
                          wallet_id: int,
                          ) -> bool:
    summaries_response = await walletRpcClient.get_wallets()
    for summary in summaries_response:
        if summary["id"] == wallet_id:
            return True
    return False


async def verifyWalletFunds(walletRpcClient: hddcoin.rpc.wallet_rpc_client.WalletRpcClient,
                            wallet_id: int,
                            requiredFunds_hdd: decimal.Decimal,
                            ) -> None:
    """Checks the specified wallet for requiredFunds_hdd, raising various exceptions on failure."""
    if not await _walletIdExists(walletRpcClient, wallet_id):
        raise exc.WalletIdNotFound()

    if not await walletRpcClient.get_synced():
        raise exc.WalletNotSynced()

    balances = await walletRpcClient.get_wallet_balance(str(wallet_id))
    spendable_bytes = balances["spendable_balance"]
    max_send_bytes = balances["max_send_amount"]
    spendable_hdd = decimal.Decimal(spendable_bytes) / hddcoin.hodl.BYTES_PER_HDD
    max_send_hdd = decimal.Decimal(max_send_bytes) / hddcoin.hodl.BYTES_PER_HDD

    if spendable_hdd < requiredFunds_hdd:
        raise exc.InsufficientFunds(str(spendable_bytes))

    if max_send_hdd < requiredFunds_hdd:
        raise exc.WalletTooFragmented(str(max_send_bytes))


def _querySqliteDB(dbPath: str,
                   sql: str,
                   params: th.Tuple[th.Any, ...],
                   ) -> th.List[th.Tuple[th.Any, ...]]:
    conn = sqlite3.connect(dbPath)
    try:
        cur = conn.cursor()
        rows = cur.execute(sql, params).fetchall()
        return rows
    finally:
        conn.close()


def getBlockchainDbPath(config: th.Optional[th.Dict]) -> str:
    if config is None:
        config = loadConfig()
    fullnodeConfig = config["full_node"]
    network = fullnodeConfig["selected_network"]
    dbPath = fullnodeConfig["database_path"].replace("CHALLENGE", network)
    dbPath = path_from_root(DEFAULT_ROOT_PATH, dbPath)
    return dbPath


def queryBlockchainDB(sql: str,
                      params: th.Tuple[th.Any, ...],
                      config: th.Optional[th.Dict] = None,
                      ) -> th.List[th.Tuple[th.Any, ...]]:
    dbPath = getBlockchainDbPath(config)
    roPath = f"file:{dbPath}?mode=ro"
    return _querySqliteDB(roPath, sql, params)


sql_hodlContractSpendInfo = """\
WITH initial AS (
    SELECT coin_name, spent FROM coin_record WHERE puzzle_hash = ?
    ORDER BY confirmed_index LIMIT 1
)
SELECT * FROM initial
UNION ALL
SELECT cr.coin_name, cr.spent
FROM coin_record cr INNER JOIN initial i ON i.coin_name = cr.coin_parent
WHERE puzzle_hash = ?
"""
def getContractSpendInfo(contractAddress: str,
                         config: th.Optional[th.Dict] = None,
                         ) -> th.List[th.Tuple[str, bool]]:
    ph = addr2puzhash(contractAddress, True)
    rows = queryBlockchainDB(sql_hodlContractSpendInfo, (ph, ph), config = config)
    ret = [(row[0], bool(row[1])) for row in rows]
    return ret


async def cancelContract(hodlRpcClient: HodlRpcClient,
                         fullNodeRpcClient: FullNodeRpcClient,
                         validated_contract_details: ContractDetails,
                         config: th.Optional[th.Dict] = None,
                         ) -> str:
    """Pushes the transaction required to cancel the contract in validated_contract_details.

    Returns the tx_id (SpendBundle name) of the transaction pushed to the mempool.

    """
    # NOTE: If done from the matching key/wallet (only YOU can cancel your contracts... nobody
    # else!) this cancellation should essentially never fail once this function exits. However, the
    # mempool *does* have to accept the transaction, and this is not always guaranteed. For example,
    # the mempool could be full, or the contract could already be cancelled or paid out in the same
    # block. At no time will the contract ever be in jeopardy with such conditions, though.

    # IMPORTANT NOTE: As per the name, validated_contract_details MUST be 100% pre-validated here.
    vcd = validated_contract_details
    contract_id = vcd.contract_id
    contract_address = vcd.contract_address

    vlog(1, "Fetching contract spend records from blockchain")
    contractSpendInfo = getContractSpendInfo(contract_address, config)
    numRecords = len(contractSpendInfo)
    vlog(2, f"Found {numRecords} coin records for contract {contract_id}")
    if numRecords == 0:
        raise exc.HodlError(f"HODL contract coin not found on-chain. If just created, try again "
                            f"in a moment.")
    recentCoinName, recentCoinSpent = contractSpendInfo[-1]
    if recentCoinSpent == True:
        if numRecords == 1:
            raise exc.HodlError(f"HODL contract exists, but has been cancelled already!")
        elif numRecords == 2:
            raise exc.HodlError(f"HODL contract exists, but has either been cancelled or paid out. "
                                f"Check status with `hddcoin hodl show -C {contract_id}`.")
        else:  # Wat?
            raise exc.HodlError(f"Impossible cancel condition encountered with contract "
                                f"{contract_id}. PLEASE NOTIFY THE HDDCOIN TEAM!")

    cr = await fullNodeRpcClient.get_coin_record_by_name(bytes32.fromhex(recentCoinName))
    assert cr is not None
    ph_b32 = addr2puzhash(contract_address, asString = False)
    reveal = SerializedProgram.fromhex(vcd.puzzle_reveal)
    solution = SerializedProgram.fromhex(str(Program.to([1, cr.coin.amount, ph_b32])))
    msg = (
        hddcoin.hodl.bytes8.fromhex(contract_id)
        + cr.coin.name()
        + DEFAULT_CONSTANTS.AGG_SIG_ME_ADDITIONAL_DATA
    )
    sig = blspy.AugSchemeMPL.sign(hodlRpcClient.sk, msg)
    spendBundle = SpendBundle([CoinSpend(cr.coin, reveal, solution)], sig)
    await fullNodeRpcClient.push_tx(spendBundle)
    try:
        await hodlRpcClient.get(f"notifyOfCancelAttempt/{contract_id}")
    except Exception as _e:
        pass  # weird, but meh. Contract state update may lag a wee bit as a result, but that's all.

    return spendBundle.name()


async def _closeMultipleRpcClients(clients: th.Sequence[th.Union[FullNodeRpcClient,
                                                                 WalletRpcClient,
                                                                 HodlRpcClient]]) -> None:
    for client in clients:
        client.close()
    for client in clients:
        await client.await_closed()


def getPkSkFromFingerprint(fingerprint: int,
                           ) -> th.Tuple[blspy.G1Element, blspy.PrivateKey]:
    """Given a key fingerprint, return (pk, sk). Raises KeyNotFound(keyCount) if no match found."""
    if not fingerprint:
        raise ValueError("A fingerprint is required")

    allPrivateKeyInfo = hddcoin.util.keychain.Keychain().get_all_private_keys()

    for sk, _seed in allPrivateKeyInfo:
        pk = sk.get_g1()
        fp = pk.get_fingerprint()
        vlog(2, f"FOUND key with fingerprint = {fp}")
        if fp == fingerprint:
            vlog(2, f"SELECTING key with fingerprint = {fp}")
            return (pk, sk)

    vlog(1, f"No key exists with fingerprint of {fingerprint}")
    raise exc.KeyNotFound(str(len(allPrivateKeyInfo)))


async def callCliCmdHandler(handler: th.Callable,
                            verbosity: int,
                            fingerprint: th.Optional[int],
                            *,
                            injectConfig: bool = False,
                            fullNodeRpcPort: th.Optional[int] = None,
                            walletRpcPort: th.Optional[int] = None,
                            cmdKwargs: th.Optional[th.Dict[str, th.Any]],
                            ) -> None:
    """Wrapper call for all HODL CLI command handlers."""
    fullNodeRpcClient: th.Optional[FullNodeRpcClient] = None
    walletRpcClient: th.Optional[WalletRpcClient] = None

    hddcoin.hodl.util.verbosity = verbosity

    if cmdKwargs is None:
        cmdKwargs = {}

    if injectConfig or (fullNodeRpcPort is not None) or (walletRpcPort is not None):
        config = hddcoin.hodl.util.loadConfig()
        if injectConfig:
            cmdKwargs["config"] = config

    if fingerprint is None:
        # All HODL RPC calls require a public key, so we *need* a fingerprint.
        vlog(2, "Collecting available fingerprints (no fingerprint was specified)")
        fingerprints = [pki[0].get_g1().get_fingerprint()
                        for pki in hddcoin.util.keychain.Keychain().get_all_private_keys()]
        numFingerprints = len(fingerprints)
        if numFingerprints == 0:
            print(f"{R}ERROR: {Y}No keys found! HODL'ing requires a fully synced wallet.{_}")
            return
        elif numFingerprints == 1:
            vlog(1, f"Automatically selecting the only available fingerprint ({fingerprint})")
            fingerprint = fingerprints[0]
        else:
            vlog(1, "Prompting user for fingerprint (since none was specified)")
            print("Choose the wallet key/fingerprint you would like to use:")
            for i, fp in enumerate(sorted(fingerprints), 1):
                print(f"  {i}: {fp}")
            print("Enter a number, or pick q to quit [q]: ", end = "")
            response = input("")
            if not response or response[0].lower() == "q":
                print(f"Aborted.")
                print(f"To see wallet balances for these keys, use `{Y}hddcoin wallet show{_}`.")
                return
            try:
                fingerprint = fingerprints[int(response) - 1]
            except Exception:
                print(f"{R}ERROR: {Y}Invalid selection{_}")
                return

    # Create a HodlRpcClient...
    #  - every `hddcoin hodl` operation requires a call to the HODL server
    #  - WORTH NOTING: Once a HODL contract is launched (i.e. the smart coin is on-chain) this is
    #     not strictly necessary (since full reveal and solutions to copmpletely manage the coin are
    #     provided in the receipt), but it makes overall contract management portable (and easier)
    #     since there is no need to have the receipts at hand to work with the contracts.
    try:
        hodlRpcClient = HodlRpcClient(fingerprint)
    except exc.KeyNotFound as knf:
        # This can happen because A) we don't validate fingerprints given via -f, and B) the key
        # situation may have changed in the background.
        keyCount = int(knf.args[0])
        if keyCount:
            print(f"{R}ERROR: {Y}Unknown fingerprint. Please check `{W}hddcoin keys show{Y}`{_}")
        else:
            print(f"{R}ERROR: {Y}No keys found! HODL'ing requires a fully synced wallet.{_}")
        return
    except Exception as e:
        print(f"{R}ERROR: {Y}Unable to create HODL RPC client: {e!r}{_}")
        return
    toClose: th.List[th.Union[HodlRpcClient, WalletRpcClient, FullNodeRpcClient]] = [hodlRpcClient]

    # Create a full_node RPC client if needed by the command
    if fullNodeRpcPort is not None:
        vlog(2, "Creating RPC client connection with local full_node")
        try:
            fullNodeRpcClient = await hddcoin.hodl.util.getFullNodeRpcClient(config,
                                                                             fullNodeRpcPort)
        except Exception as e:
            print(f"{R}ERROR: {Y}Unable to connect to full_node RPC. {W}(Is it running?){_}")
            if not isinstance(e, aiohttp.ClientConnectionError):
                print(f"  → Error was: {e!r}")
            await _closeMultipleRpcClients(toClose)
            return
        cmdKwargs["fullNodeRpcClient"] = fullNodeRpcClient
        toClose.append(fullNodeRpcClient)

    if walletRpcPort is not None:
        vlog(2, "Creating RPC client connection with local wallet")
        connStart_s = time.monotonic()
        print("Connecting to local wallet (this can take a minute)... ", end = "")
        sys.stdout.flush()
        try:
            walletRpcClient = await hddcoin.hodl.util.getWalletRpcClient(config,
                                                                         fingerprint,
                                                                         walletRpcPort)
        except Exception as e:
            print(f"{R}ERROR{_}")
            print(f"{R}ERROR: {Y}Unable to connect to wallet RPC. {W}(Is it running?){_}")
            if not isinstance(e, aiohttp.ClientConnectionError):
                print(f"  → Error was: {e!r}")
            await _closeMultipleRpcClients(toClose)
            return
        print(f"{G}OK{_}  [took {time.monotonic() - connStart_s:.2f} s]")
        cmdKwargs["walletRpcClient"] = walletRpcClient
        toClose.append(walletRpcClient)

    vlog(2, "Calling click cmd handler")
    try:
        await handler(hodlRpcClient, **cmdKwargs)
    except exc.ClientUpgradeRequired as e:
        print(f"{Y}Client upgrade required to participate in the {G}HODL{Y} progam.{_}")
        if e.msg:
            print(f"{C}Server says: {W}{e.msg}{_}")
    except exc.CancelValidationError as e:
        print(f"{R}CANCEL VALIDATION FAILURE: {Y}{e.msg}{_}")
        print(f"{G}  --> {C}Please report this situation to the HDDcoin team! {W}This is unexpected.{_}")
        print(f"{G}  --> DO NOT WORRY! {Y}Your HODL contract has {W}NOT{Y} been cancelled.{_}")
    except exc.ContractValidationError as e:
        print(f"{R}CONTRACT VALIDATION FAILURE: {Y}{e.msg}{_}")
        print(f"{G}  --> {C}Please report this situation to the HDDcoin team! {W}This is unexpected.{_}")
        print(f"{G}  --> DO NOT WORRY! YOUR HDD FUNDS ARE SECURE. {Y}Nothing has been spent.{_}")
    except exc.HodlApiError as e:
        print(f"{R}HODL server reported an error: {Y}{e.msg}{_}")
    except exc.HodlConnectionError as e:
        if "HTTP STATUS 502" in e.msg:
            print(f"{R}Connection error: {Y}The HODL server is not available right now.\n"
                  f"{W}The server is likely under maintenance. Please try again later!\n"
                  f"If this problem persists, please contact the HDDcoin team!{_}")
        elif "HTTP STATUS 401" in e.msg:
            print(f"{R}Connection error: {Y}Unable to authenticate with the HODL server.\n"
                  f" ==> {W}HODL requires accurate time. Please make sure your clock is synced.\n"
                  f" ==> If this problem persists, please contact the HDDcoin team!{_}")
        else:
            print(f"{R}Connection error: {Y}{e.msg}{_}")
    except exc.HodlError as e:
        print(f"{R}ERROR: {Y}{e.msg}{_}")
    except Exception as unhandledExc:
        msg = (f"{R}An unexpected error happened: {Y}{unhandledExc!r}{_}\n"
               f"{G} --> {C}Please report this to the HDDcoin team (unexpected errors are bad!){_}")
        print(msg)

    finally:
        await _closeMultipleRpcClients(toClose)
