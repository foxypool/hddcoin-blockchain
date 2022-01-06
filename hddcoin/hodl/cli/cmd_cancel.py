# -*- coding: utf-8 -*-
from __future__ import annotations
import decimal
import time

import blspy  #type:ignore

import hddcoin.types.coin_record
from hddcoin.hodl.ContractDetails import ContractDetails
from hddcoin.hodl.hodlrpc import HodlRpcClient
from hddcoin.hodl.util import vlog
from hddcoin.hodl.val import validateCancellation
from hddcoin.rpc.full_node_rpc_client import FullNodeRpcClient

from .colours import *
from .colours import _


async def cmd_cancel(hodlRpcClient: HodlRpcClient,
                     *,
                     fullNodeRpcClient: FullNodeRpcClient,
                     contract_id: str,
                     no_confirm: bool,
                     ) -> None:
    """Cancel the indicated HODL contract_id."""
    vlog(1, "Fetching contract information")
    apiDict = await hodlRpcClient.get(f"getContract/{contract_id}")
    contractDetails = ContractDetails.fromApiDict(apiDict)

    if contract_id != contractDetails.contract_id:
        print(f"{R}ERROR: {Y}contract_id provided by server does not match what you specified.")
        return
    elif contractDetails.status not in {"REGISTERED", "CONFIRMED", "GUARANTEED"}:
        print(f"{R}ERROR: {Y}Illegal state for cancel attempt: {W}{contractDetails.status}{_}")
        return

    cooldownRemaining_s = max(0, contractDetails.tstamp_cancel_ok - time.time())
    if cooldownRemaining_s > 0:
        # Since same-block cancel/guarantee can easily happen when someone tries to immediately
        # cancel, we want to avoid confusion if their cancel attempt ends up not happening on the
        # blockchain (because our guarantee attempt "wins" in the same block). A short cooldown is
        # all we need here. This clears the moment a contract is GUARANTEED, so can certainly be
        # shorter than the reported tstamp_cancel_ok. There is zero risk of funds going astray, but
        # it's not cool if the user thinks they cancelled but it didn't actually work.
        rwd_hdd = decimal.Decimal(contractDetails.reward_bytes) / int(1e12)
        print(f"{R}ERROR: {Y}Unable to cancel yet... please wait a few minutes!{_}")
        print(f"{W}  ==> This is TEMPORARY.  You will be able to cancel your contract shortly!")
        print(f"{W}  ==> We are in the process of guaranteeing your HODL rewards")
        print(f"{W}  ==> This short time is just to avoid simultaneous guarantee/cancel confusion")
        print(f"{C}Please use this time to reconsider cancelling your {Y}{rwd_hdd} HDD{C} HODL "
              f"reward {Y}:D{_}")
        return

    # need to validate the puzzlehash
    vlog(1, "Validating contract details received from server")
    validateCancellation(contract_id, contractDetails)

    if not _confirmCancel(contractDetails, no_confirm):
        print(f"{R}-------{_}")
        print(f"{R}ABORTED. {G}No problem. Your HODL contract still exists. {W}Wise choice! {Y};){_}")
        print(f"{R}-------{_}")
        return

    mempool_tx = await hddcoin.hodl.util.cancelContract(hodlRpcClient,
                                                        fullNodeRpcClient,
                                                        contractDetails)
    print(
        f"\n"
        f"{G}Contract cancellation request successfully sent to the mempool{_}\n"
        f"   ==> Actual cancellation may take a minute to appear on the blockchain\n"
        f"   ==> Monitor contract status directly with `{Y}hddcoin hodl show -C {contract_id}{_}`\n"
        f"   ==> The mempool tx_id for the request is {Y}{mempool_tx}{_}\n"
        f"   ==> Watch your wallet balance for progress with `{Y}hddcoin wallet show{_}`\n"
    )


def _confirmCancel(contractDetails: ContractDetails,
                   no_confirm: bool,
                   ) -> bool:
    if no_confirm:
        return True
    contract_id = contractDetails.contract_id  # validated
    print(f"{C}You have requested to cancel contract id {Y}{contract_id}{C}, which has these terms:{_}")
    contractDetails.printSummary(indent = 2)
    print(f"{C}Do you wish to cancel the above HODL contract?{_} (y/[n]): ", end = "")
    response = input("")
    if not response or response[0].lower() != "y":
        return False
    return True


