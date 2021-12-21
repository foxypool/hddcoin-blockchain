# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import typing as th

import blspy  #type:ignore

from hddcoin.hodl.ContractDetails import ContractDetails
from hddcoin.hodl.hodlrpc import HodlRpcClient
from hddcoin.hodl.util import vlog

from .colours import *
from .colours import _


async def cmd_show(hodlRpcClient: HodlRpcClient,
                   *,
                   contract_id: str,
                   dumpJson: bool,
                   ) -> None:
    vlog(1, "Fetching contract information")
    if contract_id:
        apiDict = await hodlRpcClient.get(f"getContract/{contract_id}")
        if dumpJson:
            apiDict.pop("tstamp_cancel_ok", None)  # confused testers, and is only a UX thing
            print(json.dumps(apiDict, indent=4))
        else:
            contractDetails = ContractDetails.fromApiDict(apiDict)
            contractDetails.printSummary(indent = 0)
    else:  # get ALL of our contracts and print a summary
        apiRet = await hodlRpcClient.get(f"getContracts")
        apiDicts = apiRet["contracts"]
        if dumpJson:
            print(json.dumps(apiDicts, indent = 4))
        else:
            if len(apiDicts) == 0:
                print(f"{Y}Fingerprint {hodlRpcClient._fingerprint} has no HODL contracts. :({_}")
            else:
                _printMultiContractSummary(apiDicts)


def _printMultiContractSummary(apiDicts: th.List[th.Dict[str, th.Any]]) -> None:
    ContractDetails.printShortSummaryHeader()
    for apiDict in apiDicts:
        cd = ContractDetails.fromApiDict(apiDict)
        cd.printShortSummaryLine(indent = 0)
