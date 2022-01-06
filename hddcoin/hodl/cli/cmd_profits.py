# -*- coding: utf-8 -*-
from __future__ import annotations
import decimal
import json

import blspy  #type:ignore

from hddcoin.hodl.hodlrpc import HodlRpcClient
from hddcoin.hodl.util import vlog

from .colours import *
from .colours import _


async def cmd_profits(hodlRpcClient: HodlRpcClient,
                      *,
                      dumpJson: bool,
                      ) -> None:
    vlog(1, "Fetching profit information")
    apiDict = await hodlRpcClient.get(f"getProfits")
    if dumpJson:
        print(json.dumps(apiDict, indent=4))
    else:
        pastProfits_bytes = apiDict["profits_past"]
        futureProfits_bytes = apiDict["profits_future"]
        pastProfits_hdd = decimal.Decimal(pastProfits_bytes) / int(1e12)
        futureProfits_hdd = decimal.Decimal(futureProfits_bytes) / int(1e12)
        print(f"{C}Your profits from the HODL program are as follows:{_} ")
        print(f"  {W}HODL rewards paid out in full to date:       {G}{pastProfits_hdd} {Y}HDD{_}")
        print(f"  {W}HODL rewards pending with current contracts: {G}{futureProfits_hdd} {Y}HDD{_}")
        print(f"{G}KEEP ON HODL'ING!!!{_}")
