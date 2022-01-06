import asyncio
import sys
import time
from datetime import datetime
from decimal import Decimal
from typing import Callable, List, Optional, Tuple, Dict

import aiohttp

from hddcoin.cmds.units import units
from hddcoin.rpc.wallet_rpc_client import WalletRpcClient
from hddcoin.server.start_wallet import SERVICE_NAME
from hddcoin.util.bech32m import encode_puzzle_hash
from hddcoin.util.byte_types import hexstr_to_bytes
from hddcoin.util.config import load_config
from hddcoin.util.default_root import DEFAULT_ROOT_PATH
from hddcoin.util.ints import uint16, uint64
from hddcoin.wallet.transaction_record import TransactionRecord
from hddcoin.wallet.util.wallet_types import WalletType


def print_transaction(tx: TransactionRecord, verbose: bool, name) -> None:
    if verbose:
        print(tx)
    else:
        hddcoin_amount = Decimal(int(tx.amount)) / units["hddcoin"]
        to_address = encode_puzzle_hash(tx.to_puzzle_hash, name)
        print(f"Transaction {tx.name}")
        print(f"Status: {'Confirmed' if tx.confirmed else ('In mempool' if tx.is_in_mempool() else 'Pending')}")
        print(f"Amount {'sent' if tx.sent else 'received'}: {hddcoin_amount} {name}")
        print(f"To address: {to_address}")
        print("Created at:", datetime.fromtimestamp(tx.created_at_time).strftime("%Y-%m-%d %H:%M:%S"))
        print("")


async def get_transaction(args: dict, wallet_client: WalletRpcClient, fingerprint: int) -> None:
    wallet_id = args["id"]
    transaction_id = hexstr_to_bytes(args["tx_id"])
    config = load_config(DEFAULT_ROOT_PATH, "config.yaml", SERVICE_NAME)
    name = config["network_overrides"]["config"][config["selected_network"]]["address_prefix"]
    tx: TransactionRecord = await wallet_client.get_transaction(wallet_id, transaction_id=transaction_id)
    print_transaction(tx, verbose=(args["verbose"] > 0), name=name)


async def get_transactions(args: dict, wallet_client: WalletRpcClient, fingerprint: int) -> None:
    wallet_id = args["id"]
    paginate = args["paginate"]
    if paginate is None:
        paginate = sys.stdout.isatty()
    txs: List[TransactionRecord] = await wallet_client.get_transactions(wallet_id)
    config = load_config(DEFAULT_ROOT_PATH, "config.yaml", SERVICE_NAME)
    name = config["network_overrides"]["config"][config["selected_network"]]["address_prefix"]
    if len(txs) == 0:
        print("There are no transactions to this address")

    offset = args["offset"]
    num_per_screen = 5 if paginate else len(txs)
    for i in range(offset, len(txs), num_per_screen):
        for j in range(0, num_per_screen):
            if i + j >= len(txs):
                break
            print_transaction(txs[i + j], verbose=(args["verbose"] > 0), name=name)
        if i + num_per_screen >= len(txs):
            return None
        print("Press q to quit, or c to continue")
        while True:
            entered_key = sys.stdin.read(1)
            if entered_key == "q":
                return None
            elif entered_key == "c":
                break


def check_unusual_transaction(amount: Decimal, fee: Decimal):
    return fee >= amount


async def send(args: dict, wallet_client: WalletRpcClient, fingerprint: int) -> None:
    wallet_id = args["id"]
    amount = Decimal(args["amount"])
    fee = Decimal(args["fee"])
    address = args["address"]
    override = args["override"]

    if not override and check_unusual_transaction(amount, fee):
        print(
            f"A transaction of amount {amount} and fee {fee} is unusual.\n"
            f"Pass in --override if you are sure you mean to do this."
        )
        return
    print("Submitting transaction...")
    final_amount = uint64(int(amount * units["hddcoin"]))
    final_fee = uint64(int(fee * units["hddcoin"]))
    res = await wallet_client.send_transaction(wallet_id, final_amount, address, final_fee)
    tx_id = res.name
    start = time.time()
    while time.time() - start < 10:
        await asyncio.sleep(0.1)
        tx = await wallet_client.get_transaction(wallet_id, tx_id)
        if len(tx.sent_to) > 0:
            print(f"Transaction submitted to nodes: {tx.sent_to}")
            print(f"Do hddcoin wallet get_transaction -f {fingerprint} -tx 0x{tx_id} to get status")
            return None

    print("Transaction not yet submitted to nodes")
    print(f"Do 'hddcoin wallet get_transaction -f {fingerprint} -tx 0x{tx_id}' to get status")


async def get_address(args: dict, wallet_client: WalletRpcClient, fingerprint: int) -> None:
    wallet_id = args["id"]
    res = await wallet_client.get_next_address(wallet_id, False)
    print(res)


async def delete_unconfirmed_transactions(args: dict, wallet_client: WalletRpcClient, fingerprint: int) -> None:
    wallet_id = args["id"]
    await wallet_client.delete_unconfirmed_transactions(wallet_id)
    print(f"Successfully deleted all unconfirmed transactions for wallet id {wallet_id} on key {fingerprint}")


def wallet_coin_unit(typ: WalletType, address_prefix: str) -> Tuple[str, int]:
    if typ == WalletType.COLOURED_COIN:
        return "", units["colouredcoin"]
    if typ in [WalletType.STANDARD_WALLET, WalletType.POOLING_WALLET, WalletType.MULTI_SIG, WalletType.RATE_LIMITED]:
        return address_prefix, units["hddcoin"]
    return "", units["byte"]


def print_balance(amount: int, scale: int, address_prefix: str) -> str:
    ret = f"{amount/scale} {address_prefix} "
    if scale > 1:
        ret += f"({amount} byte)"
    return ret


async def print_balances(args: dict, wallet_client: WalletRpcClient, fingerprint: int) -> None:
    summaries_response = await wallet_client.get_wallets()
    config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
    address_prefix = config["network_overrides"]["config"][config["selected_network"]]["address_prefix"]

    # lazy load HODL stuff here for cleaner diff
    import hddcoin.hodl.exc
    from hddcoin.hodl.hodlrpc import HodlRpcClient
    hodlRpcClient = HodlRpcClient(fingerprint)
    try:
        rpcRet  = await hodlRpcClient.get("getTotalHodlForWallet")
        hodl_balance_bytes = rpcRet["committed_bytes"]
        hodl_balance_hdd = Decimal(hodl_balance_bytes) / int(1e12)
        # emulating upstream repr for now
        hodl_balance_str = f"{hodl_balance_hdd} hdd ({hodl_balance_bytes} byte)"
    except hddcoin.hodl.exc.HodlConnectionError:
        hodl_balance_str = "< UNABLE TO CONNECT TO HODL SERVER >"
    except Exception as e:
        hodl_balance_str = f"ERROR: {e!r}"
    finally:
        hodlRpcClient.close()
        await hodlRpcClient.await_closed()

    print(f"Wallet height: {await wallet_client.get_height_info()}")
    print(f"Sync status: {'Synced' if (await wallet_client.get_synced()) else 'Not synced'}")
    print(f"Balances, fingerprint: {fingerprint}")
    print(f"HODL deposits: {hodl_balance_str}")
    for summary in summaries_response:
        wallet_id = summary["id"]
        balances = await wallet_client.get_wallet_balance(wallet_id)
        typ = WalletType(int(summary["type"]))
        address_prefix, scale = wallet_coin_unit(typ, address_prefix)
        print(f"Wallet ID {wallet_id} type {typ.name} {summary['name']}")
        print(f"   -Total Balance: {print_balance(balances['confirmed_wallet_balance'], scale, address_prefix)}")
        print(
            f"   -Pending Total Balance: {print_balance(balances['unconfirmed_wallet_balance'], scale, address_prefix)}"
        )
        print(f"   -Spendable: {print_balance(balances['spendable_balance'], scale, address_prefix)}")
        print(f"   -Max Send Amount: {print_balance(balances['max_send_amount'], scale, address_prefix)}")


async def get_wallet(wallet_client: WalletRpcClient, fingerprint: int = None) -> Optional[Tuple[WalletRpcClient, int]]:
    if fingerprint is not None:
        fingerprints = [fingerprint]
    else:
        fingerprints = await wallet_client.get_public_keys()
    if len(fingerprints) == 0:
        print("No keys loaded. Run 'hddcoin keys generate' or import a key")
        return None
    if len(fingerprints) == 1:
        fingerprint = fingerprints[0]
    if fingerprint is not None:
        log_in_response = await wallet_client.log_in(fingerprint)
    else:
        print("Choose wallet key:")
        for i, fp in enumerate(fingerprints):
            print(f"{i+1}) {fp}")
        val = None
        while val is None:
            val = input("Enter a number to pick or q to quit: ")
            if val == "q":
                return None
            if not val.isdigit():
                val = None
            else:
                index = int(val) - 1
                if index >= len(fingerprints):
                    print("Invalid value")
                    val = None
                    continue
                else:
                    fingerprint = fingerprints[index]
        assert fingerprint is not None
        log_in_response = await wallet_client.log_in(fingerprint)

    if log_in_response["success"] is False:
        if log_in_response["error"] == "not_initialized":
            use_cloud = True
            if "backup_path" in log_in_response:
                path = log_in_response["backup_path"]
                print(f"Backup file from backup.hddcoin.org downloaded and written to: {path}")
                val = input("Do you want to use this file to restore from backup? (Y/N) ")
                if val.lower() == "y":
                    log_in_response = await wallet_client.log_in_and_restore(fingerprint, path)
                else:
                    use_cloud = False

            if "backup_path" not in log_in_response or use_cloud is False:
                if use_cloud is True:
                    val = input(
                        "No online backup file found,\n Press S to skip restore from backup"
                        "\n Press F to use your own backup file: "
                    )
                else:
                    val = input(
                        "Cloud backup declined,\n Press S to skip restore from backup"
                        "\n Press F to use your own backup file: "
                    )

                if val.lower() == "s":
                    log_in_response = await wallet_client.log_in_and_skip(fingerprint)
                elif val.lower() == "f":
                    val = input("Please provide the full path to your backup file: ")
                    log_in_response = await wallet_client.log_in_and_restore(fingerprint, val)

    if "success" not in log_in_response or log_in_response["success"] is False:
        if "error" in log_in_response:
            error = log_in_response["error"]
            print(f"Error: {log_in_response[error]}")
        return None
    return wallet_client, fingerprint


async def defrag(args: dict, wallet_client: WalletRpcClient, fingerprint: int) -> None:
    """Defragment the wallet, reducing the number of coins in it.

    This increases the maximum amount that can be sent in a single transaction.

    """
    # This is currently an extremely simple algorithm. We just send the maximum possible amount to
    # ourselves, using the built in wallet restrictions (which are based on "reasonable" cost limits
    # per block).
    #
    # Successive calls to this will always result in a single coin in the wallet.
    from hddcoin.hodl.util import getNthWalletAddr, getPkSkFromFingerprint, loadConfig

    wallet_id = args["id"]
    fee_hdd = Decimal(args["fee"])
    fee_bytes = uint64(int(fee_hdd * units["hddcoin"]))
    target_address = args["address"]
    override = args["override"]
    no_confirm = args["no_confirm"]

    if fee_hdd >= 1 and (override == False):
        print(f"fee of {fee_hdd} HDD seems too large (use --override to force)")
        return
    elif target_address and len(target_address) != 62:
        print("Address is invalid")
        return

    config = loadConfig()
    sk = getPkSkFromFingerprint(fingerprint)[1]

    if not target_address:
        target_address = getNthWalletAddr(config, sk, 0)
    else:
        check_count = 100
        for i in range(check_count):
            if target_address == getNthWalletAddr(config, sk, i):
                break  # address is confirmed as one of ours
        else:
            print("WARNING!!!\nWARNING!!!\nWARNING!!!  ", end = "")
            print(f"The given address is not one of the first {check_count} wallet addresses!")
            print("WARNING!!!\nWARNING!!!")
            inp = input(f"Is {target_address} where you want to defrag to? [y/N] ")
            if not inp or inp[0].lower() == "n":
                print("Aborting defrag!")
                return

    # Figure out the maximum value the wallet can send at the moment
    balances = await wallet_client.get_wallet_balance(wallet_id)
    max_send_bytes = balances["max_send_amount"]
    spendable_bytes = balances["spendable_balance"]
    max_send_hdd = Decimal(max_send_bytes) / units["hddcoin"]
    spendable_hdd = Decimal(spendable_bytes) / units["hddcoin"]
    print(f"Total of spendable coins in wallet (right now):    {spendable_hdd} HDD")
    print(f"Maximum value you can send right now (pre-defrag): {max_send_hdd} HDD")

    if not no_confirm:
        if max_send_bytes == spendable_bytes:
            inp = input("Your wallet is not currently limited by fragmentation! Continue? [y/N] ")
        else:
            inp = input("Do you wish to defrag and consolidate some coins? [y/N] ")
        if not inp or inp[0].lower() == "n":
            print("Aborting defrag!")
            return

    # Now do one round of defrag!
    defrag_coin_size_bytes = max_send_bytes - fee_bytes
    res = await wallet_client.send_transaction(wallet_id,
                                               defrag_coin_size_bytes,
                                               target_address,
                                               fee_bytes)

    tx_id = res.name
    start = time.time()
    while time.time() - start < 10:
        await asyncio.sleep(0.1)
        tx = await wallet_client.get_transaction(wallet_id, tx_id)
        if len(tx.sent_to) > 0:
            print(f"Defrag transaction submitted to nodes: {tx.sent_to}")
            print(f"Do hddcoin wallet get_transaction -f {fingerprint} -tx 0x{tx_id} to get status")
            return

    print("Defrag transaction not yet submitted to nodes")
    print(f"Do 'hddcoin wallet get_transaction -f {fingerprint} -tx 0x{tx_id}' to get status")


async def execute_with_wallet(
    wallet_rpc_port: Optional[int], fingerprint: int, extra_params: Dict, function: Callable,
    eat_exceptions: bool = True,
) -> None:
    try:
        config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
        self_hostname = config["self_hostname"]
        if wallet_rpc_port is None:
            wallet_rpc_port = config["wallet"]["rpc_port"]
        wallet_client = await WalletRpcClient.create(self_hostname, uint16(wallet_rpc_port), DEFAULT_ROOT_PATH, config)
        wallet_client_f = await get_wallet(wallet_client, fingerprint=fingerprint)
        if wallet_client_f is None:
            wallet_client.close()
            await wallet_client.await_closed()
            return None
        wallet_client, fingerprint = wallet_client_f
        await function(extra_params, wallet_client, fingerprint)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if not eat_exceptions:
            wallet_client.close()
            await wallet_client.await_closed()
            raise e
        if isinstance(e, aiohttp.ClientConnectorError):
            print(
                f"Connection error. Check if the wallet is running at {wallet_rpc_port}. "
                "You can run the wallet via:\n\thddcoin start wallet"
            )
        else:
            print(f"Exception from 'wallet' {e}")
    wallet_client.close()
    await wallet_client.await_closed()

