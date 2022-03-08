# -*- coding: utf-8 -*-
# NOTES:
#  - this file contains the CLI implementation for `hddcoin hodl commit`
from __future__ import annotations
import asyncio
import decimal
import pathlib
import sys
import time
import typing as th

import aiohttp
import blspy  # type: ignore
import yaml

import hddcoin.hodl
import hddcoin.hodl.exc as exc
import hddcoin.util
from hddcoin.hodl.hodlrpc import HodlRpcClient
from hddcoin.hodl.util import vlog
from hddcoin.hodl.val import validateContract

from .colours import *
from .colours import _


# Set the threshold for minimum useful/recommended fee value
#  - this is a rough recommendation based on the minimum fee per cost (see https://bit.ly/31zLWqG)
#  - fees smaller than this amount risk getting treated as having zero fee (this is a dust storm
#     mitigation thing), and thus not having any prioritization effect
#  - the actual minimum depends entirely on how many wallet coins need to be collected and spent to
#     make the deposit. If more than a few coins are needed the minmum fee should be higher.
#  - since HODL deposits are typically big, and are more likely to require more wallet coins, we
#     estimate a little higher than the "normal" fee/cost limits
#  - this is only even checked if the client decides to add a fee, which is itself only needed to
#     boost the priority of the deposit in the mempool if/when the blockchain is extremely busy
#       - at time of writing this, fees are completely unnecessary to deposit (or just transfer) HDD
SMALLEST_USEFUL_FEE_hdd = 0.0001


async def cmd_commit(hodlRpcClient: hddcoin.hodl.hodlrpc.HodlRpcClient,
                     *,
                     config: th.Dict[str, th.Any],
                     walletRpcClient: hddcoin.rpc.wallet_rpc_client.WalletRpcClient,
                     program_name: str,
                     wallet_rpc_port: th.Optional[int],
                     wallet_id: int,
                     commit_hdd: decimal.Decimal,
                     fee_hdd: decimal.Decimal,
                     payout_address: str,
                     override: bool,
                     ) -> None:
    fingerprint = hodlRpcClient._fingerprint
    fee_bytes = hddcoin.util.ints.uint64(int(fee_hdd * hddcoin.hodl.BYTES_PER_HDD))

    if commit_hdd < 1:
        raise exc.HodlError(f"The minimum HODL contract amount is 1 HDD.")
    elif int(commit_hdd) != commit_hdd:
        raise exc.HodlError("The HODL deposit must be a whole number of HDD.")
    elif commit_hdd > 2**31:
        raise exc.HodlError("You wish you had that much HDD to deposit! :)")
    elif fee_hdd >= 1 and (override == False):
        raise exc.HodlError(f"fee of {fee_hdd} HDD seems too large (use --override to force)")
    elif fee_hdd and (fee_bytes < 1):
        raise exc.HodlError("Fee must be at least one byte")
    elif fee_hdd and (fee_hdd < SMALLEST_USEFUL_FEE_hdd) and (override == False):
        msg = (f"Fee < {SMALLEST_USEFUL_FEE_hdd} HDD.\n"
               f"{W}If adding a fee to prioritize your deposit, you probably need to spend more in "
               f"order to make it effective.\n"
               f"Use --override to force the low fee (or just don't add a fee).")
        raise exc.HodlError(msg)

    vlog(1, f"Checking for sufficient funds")

    if not await _cli_checkWallet(config,
                                  hodlRpcClient,
                                  walletRpcClient,
                                  wallet_id,
                                  commit_hdd + fee_hdd,
                                  ):
        # Error happened while checking the wallet (and was handled)
        return


    if not payout_address:
        vlog(1, f"Calculating default/first wallet address to use as payout_address")
        payout_address = hddcoin.hodl.util.getFirstWalletAddr(config, hodlRpcClient.sk)
        vlog(1, f"payout_address automatically set to {payout_address}")

    vlog(1, f"Fetching contract from HODL server")
    deposit_bytes = hddcoin.util.ints.uint64(int(commit_hdd * hddcoin.hodl.BYTES_PER_HDD))
    requestRet = await hodlRpcClient.post("requestContract", dict(program_name = program_name,
                                                                  deposit_bytes = deposit_bytes,
                                                                  payout_address = payout_address))
    receipt = requestRet["receipt"]
    contract_id = receipt["receipt_info"]["contract_id"]
    vlog(1, f"Received contract id {contract_id}")

    ## VALIDATE WHAT WE GOT!!
    ##  - i.e. don't blindly trust a contract we just got from the internet with our HDDs
    ##  - ONLY THE PARANOID SURVIVE
    term_in_months = decimal.Decimal(receipt["terms"]["term_in_months"])
    reward_percent = decimal.Decimal(receipt["terms"]["reward_percent"])
    vlog(1, "Starting contract validation")
    validateContract(program_name,
                     deposit_bytes,
                     payout_address,
                     str(hodlRpcClient.pk),
                     term_in_months, # to be visually confirmed below
                     reward_percent, # to be visually confirmed below
                     receipt,
                     )

    # The contract details are now confirmed from a technical accuracy perspective, but we now need
    # the user to confirm the received terms...
    confirmed = _confirmContractRequest(fingerprint,
                                        program_name,
                                        commit_hdd,
                                        payout_address,
                                        hodlRpcClient.pk,
                                        term_in_months,
                                        reward_percent,
                                        receipt["terms"]["agreement"],
                                        requestRet["limits"],
                                        )
    if not confirmed:
        await _cancelHodlRegistration(hodlRpcClient, contract_id)
        return  # Maybe next time!

    #### USER HAS ACCEPTED THE CONTRACT.  TIME TO HODL THOSE HDDs!!
    #### USER HAS ACCEPTED THE CONTRACT.  TIME TO HODL THOSE HDDs!!
    precommitReceiptPath = _stashPrecommitReceipt(receipt)
    contract_address = receipt["coin_details"]["contract_address"]
    tx_id, pushTxComplete = \
        await _createContractCoin(walletRpcClient, fingerprint, wallet_id, deposit_bytes,
                                  fee_bytes, contract_address, contract_id)

    receiptStorageFailure = ""
    try:
        finalReceiptPath = _storeFinalReceipt(precommitReceiptPath)
    except Exception as e:
        receiptStorageFailure = repr(e)
        finalReceiptPath = receiptStorageFailure

    _printFinalSummary(finalReceiptPath, contract_id, fingerprint, tx_id, pushTxComplete)

    if receiptStorageFailure:
        # This is very odd, but we will let the user know the info is in the precommit path
        print(f"{R}ERROR: {Y}Unable to store final receipt: {receiptStorageFailure}{_}")
        print(f"  ==> The contract has been pushed, as per details above")
        print(f"  ==> For your receipt, please see: {Y}{precommitReceiptPath}{_}")


async def _cli_checkWallet(config: th.Dict[str, th.Any],
                           hodlRpcClient: HodlRpcClient,
                           walletRpcClient: hddcoin.rpc.wallet_rpc_client.WalletRpcClient,
                           wallet_id: int,
                           requiredFunds_hdd: decimal.Decimal,
                           ) -> bool:
    print("Checking for sufficient funds... ", end = "")
    sys.stdout.flush()
    try:
        await hddcoin.hodl.util.verifyWalletFunds(walletRpcClient, wallet_id, requiredFunds_hdd)
    except aiohttp.ClientConnectionError:
        print(f"{R}CONNECTION FAILURE\n{R}Unable to connect to wallet. {W}Is your wallet running?{_}")
    except exc.InsufficientFunds:
        print(f"{R}FAILED\n{R}Insufficient funds in wallet for requested HODL contract amount.{_}")
        print(f"  ==> This may be a temporary situation (some of your wallet coins may be in use)")
        print(f"  ==> Check your spendable wallet balance with `{Y}hddcoin wallet show{_}`")
    except exc.WalletTooFragmented as e:
        maxSend_bytes = int(e.args[0])
        maxSend_hdd = decimal.Decimal(maxSend_bytes) / hddcoin.hodl.BYTES_PER_HDD

        fp = hodlRpcClient._fingerprint
        defragCmd = f"hddcoin wallet defrag -f {fp}"

        print(f"{R}FAILED")
        print(f"{Y}Your wallet is too fragmented to send {W}{requiredFunds_hdd}{Y} HDD{_}")
        print(f" ==> rest assured that your wallet DOES have sufficient funds for the deposit!")
        print(f" ==> the maximum your wallet can currently send is {Y}{maxSend_hdd} {_}HDD")
        print(f" ==> this 'max_send' limit is driven by two things:")
        print(f"       1) the number (and size) of coins you have in your wallet")
        print(f"       2) the maximum number of coins you can reasonably spend at one time")
        print(f" ==> you have a LOT of small coins (e.g. farmer rewards) and this is what limits you")
        print(f"{G}NOTE: You can HODL a larger amount by first defragging your wallet a bit with:")
        print(f"{Y}  {defragCmd}{_}")
        print(f"The above command will (after a blockchain delay) result in a larger spend limit!")
        print(f" ==> it does this by merging a lot of wallet coins into a single coin")
        print(f" ==> the command just sends funds to yourself, and is a simple defragging trick")
    except exc.WalletIdNotFound:
        print(f"{R}WALLET ID NOT FOUND\n{R}No wallet exists with id {wallet_id}.{_}")
    except exc.WalletNotSynced:
        print(f"{R}NOT SYNCED\n{R}The specified wallet is not currently synced. Sync is required.{_}")
    except Exception as e:
        print(f"{R}FAILED\n{R}Unhandled error while verifying funds: {W}{e!r}{_}")
    else:
        print(f"{G}OK{_}")
        return True
    # On exception...
    return False


async def _cancelHodlRegistration(hodlRpcClient: HodlRpcClient,
                                  contract_id: str,
                                  ) -> None:
    vlog(1, f"Declining HODL contract: {contract_id}")
    try:
        await hodlRpcClient.get(f"declineContract/{contract_id}")
    except Exception as e:
        print(f"{R}NOTE:{Y} Notification of contract decline FAILED!\n"
              f"  ==> {W}Contract will show REGISTERED for several minutes until auto-expiry.{_}")

    print(f"{R}--------{_}")
    print(f"{R}CANCELED. {G}No problem. Nothing has been spent from your wallet.{_}")
    print(f"{R}--------{_}")


def _confirmContractRequest(fingerprint: int,
                            program_name: str,
                            commit_hdd: decimal.Decimal,
                            payout_address: str,
                            pk: blspy.G1Element,
                            term_in_months: decimal.Decimal,
                            reward_percent: decimal.Decimal,
                            terms: str,
                            limits: th.Dict[str, int],
                            ) -> bool:
    start_s = time.monotonic()

    if commit_hdd > 1000:
        flavor = f"{R}<- WHALE ALERT!!! Woohoo! {Y}:D"
    elif commit_hdd > 100:
        flavor = f"{W}<- Niiiiice!"
    else:
        flavor = ""

    max_24h = limits["max_24h"]
    max_total = limits["max_total"]
    cur_24h = limits["cur_24h"]
    cur_total = limits["cur_total"]

    prompt = (
        f"{Y}============================================================\n{_}"
        f"{Y}================== {W}ARE YOU READY TO {C}HODL{W}?{Y} =================={_}\n"
        f"{Y}============================================================{_}\n"
        f"\n"
        f"{C}The HODL contract you have specified is as follows:{_}\n"
        f"\n"
        f"  {W}HODL Program:      {Y}{program_name}{_}\n"
        f"  {W}Contract duration: {Y}{term_in_months} months{_}\n"
        f"  {W}Reward percent:    {Y}{reward_percent} %{_}\n"
        f"  {W}Amount to lock in: {Y}{commit_hdd} HDD  {flavor}{_}\n"
        f"  {W}Payout address:    {Y}{payout_address}{_}\n"
        f"  {W}Pubkey authorized to cancel:{_}\n"
        f"    {Y}{pk}{_}\n"
        f"\n"
        f"{C}Once you commit to this contract:{_}\n"
        f"\n"
        f" 1. The specified wallet amount will be sent to the on-chain HODL contract\n"
        f" 2. The committed amount will no longer be available for spending in your wallet\n"
        f" 3. Deposit & reward will be automatically sent to the payout address at term end\n"
        f" 4. Your HODL'd funds will be clearly visible in `{Y}hddcoin wallet show{_}` output\n"
        f" 5. You will get a receipt describing the contract, and how to manage it\n"
        f" 6. You can always cancel the contract later (with `{Y}hddcoin hodl cancel{_}`)\n"
        f"\n"
        f"{C}ADDITIONAL NOTES:{_}\n"
        f" - Only YOU can cancel the contract (with the key having fingerprint {Y}{fingerprint}{_}){_}\n"
        f" - This is contract request {Y}{cur_24h}{_} out of a daily max of {Y}{max_24h}{_}\n"
        f" - This wallet/key has {Y}{cur_total}{_} active HODL contracts (max is {Y}{max_total}{_}){_}\n"
        f" - Check current HODL contract limits with `{Y}hddcoin hodl limits{_}`\n"
        f"\n"
        #f"{R}AGREEING TO PROCEED BELOW WILL SPEND THE FUNDS INDICATED ABOVE!{_}\n"
        #f"\n"
        f"{C}Do you wish to proceed with this HODL contract?{_} (y/[n]): "
    )
    print(prompt, end = "")
    response = input("")
    if (time.monotonic() - start_s) > hddcoin.hodl.CONTRACT_EXPIRATION_TIME_s:
        print(f"{R}CONTRACT OFFER EXPIRED! {Y}Please try again.{_}")
        return False
    elif not response or response[0].lower() != "y":
        return False

    prompt = (
        f"\n"
        f"{Y}============================================================\n{_}"
        f"{Y}================== {W}FINAL CONFIRMATION{Y} ======================{_}\n"
        f"{Y}============================================================{_}\n"
        f"\n"
        f"{C}Enrolling in a HODL contract is subject to the following terms:{_}\n"
        f"\n"
        f"{Y}----------------------\n"
        f"{W}{terms}{_}\n"
        f"{Y}----------------------\n"
        f"\n"
        f"{R}THIS IS THE FINAL CONFIRMATION BEFORE SPENDING {Y}{commit_hdd}{R} HDD!{_}\n"
        f"\n"
        f"{C}Do you wish to proceed with this HODL contract?{_} (y/[n]): "
    )
    print(prompt, end = "")
    response = input("")
    if (time.monotonic() - start_s) > hddcoin.hodl.CONTRACT_EXPIRATION_TIME_s:
        print(f"{R}CONTRACT OFFER EXPIRED! {Y}Please try again.{_}")
        return False
    elif not response or response[0].lower() != "y":
        return False

    prompt = (
        f"\n"
        f"{G}============================================================\n{_}"
        f"{G}================== {W}HODL {Y}CONTRACT AGREED!{Y} =================={_}\n"
        f"{G}============================================================{_}\n"
        f"\n"
    )
    return True


def _stashPrecommitReceipt(receipt: th.Dict[str, th.Any]) -> pathlib.Path:
    hddcoin.hodl.HODL_DIR_TMP.mkdir(parents = True, exist_ok = True)
    contract_id = receipt["receipt_info"]["contract_id"]
    precommitPath = hddcoin.hodl.HODL_DIR_TMP / f"{contract_id}.yaml"
    with open(precommitPath, "w") as fp:
        fp.write(yaml.dump(receipt, sort_keys = False))
    return precommitPath


async def _createContractCoin(walletClient: hddcoin.rpc.wallet_rpc_client.WalletRpcClient,
                              fingerprint: int,
                              wallet_id: int,
                              deposit_bytes: hddcoin.util.ints.uint64,
                              fee_bytes: hddcoin.util.ints.uint64,
                              contract_address: str,
                              contract_id: str,
                              ) -> th.Tuple[str, bool]:
    tx: hddcoin.wallet.transaction_record.TransactionRecord

    deposit_hdd = decimal.Decimal(deposit_bytes) / hddcoin.hodl.BYTES_PER_HDD
    vlog(1, "Sending transaction")
    print(f"{W}Submitting transaction to purchase HODL contract for "
          f"{Y}{deposit_hdd} {W}HDD ... {_}", end = "")

    try:
        tx = await walletClient.send_transaction(str(wallet_id), deposit_bytes, contract_address,
                                                 fee_bytes)
    except ValueError as e:
        # This is odd since we *should* have pre-validated everything, but maybe something changed?
        vlog(1, f"Error trying to submit the HODL deposit transaction: {e!r}")
        raise exc.HodlError(f"Unexpected error submitting the HODL deposit transaction: {e}")

    tx_id = tx.name
    vlog(2, "Waiting for transmission confirmation from nodes")
    pushTxComplete = False
    start_s = time.monotonic()
    while time.monotonic() - start_s < 10:
        await asyncio.sleep(0.1)
        tx = await walletClient.get_transaction(str(wallet_id), tx_id)
        if len(tx.sent_to) > 0:
            pushTxComplete = True
            print(f"{G}OK{_}")
            break
    else:
        print(f"{Y}RESULT UNCERTAIN{_}")

    return tx_id, pushTxComplete


def _storeFinalReceipt(precommitReceiptPath: pathlib.Path) -> pathlib.Path:
    hddcoin.hodl.HODL_DIR_RECEIPTS.mkdir(parents = True, exist_ok = True)
    finalReceiptPath = hddcoin.hodl.HODL_DIR_RECEIPTS / precommitReceiptPath.name
    precommitReceiptPath.rename(finalReceiptPath)
    return finalReceiptPath


def _printFinalSummary(finalReceiptPath: pathlib.Path,
                       contract_id: str,
                       fingerprint: int,
                       tx_id: str,
                       pushTxComplete: bool,
                       ) -> None:
    p = print  # width-saver
    p(f"{Y}============================================================{_}")
    if pushTxComplete:
        p(f"{C}HODL contract purchase complete! {_}(contract amount sent to the mempool){_}")
    else:
        p(f"{Y}The wallet transaction for the deposit is taking a long time to submit...{_}")
        p(f" ==> {G}Rest easy! Your HDD will either end up as a contract, or stay in your wallet!{_}`\n")
    p(f" ==> Detailed receipt stored to {Y}{finalReceiptPath}{_}")
    p(f" ==> Monitor contract status with `{Y}hddcoin hodl show -C {contract_id}{_}`")
    p(f" ==> The actual deposit may take a minute to appear on the blockchain")
    p(f" ==> Deposit confirmation and reward guarantee may take a few minutes")
    p(f" ==> Monitor blockchain contract creation with:")
    p(f"    `{Y}hddcoin wallet get_transaction -f {fingerprint} -tx 0x{tx_id}{_}`")
    p(f" ==> {G}REMEMBER{W}: contract access is limited to this wallet ({Y}{fingerprint}){_}")
    p(f"{Y}============================================================{_}")
    print(f"{C}HAPPY HODL'ING!!{_}")
