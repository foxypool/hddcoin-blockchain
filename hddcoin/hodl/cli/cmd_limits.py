# -*- coding: utf-8 -*-
from __future__ import annotations
import json

import blspy  #type:ignore

from hddcoin.hodl.hodlrpc import HodlRpcClient
from hddcoin.hodl.util import vlog

from .colours import *
from .colours import _


async def cmd_limits(hodlRpcClient: HodlRpcClient,
                     *,
                     dumpJson: bool,
                     ) -> None:
    """Show the current limits the HODL program has in place, and the status for the given key."""
    vlog(1, "Fetching contract information")
    limitDict = await hodlRpcClient.get(f"getLimits/{str(hodlRpcClient.pk)}")

    if dumpJson:
        print(json.dumps(limitDict, indent=4))
        return
    fp = hodlRpcClient._fingerprint
    cur24 = limitDict["cur_24h"]
    max24 = limitDict["max_24h"]
    curT = limitDict["cur_total"]
    maxT = limitDict["max_total"]
    N = _
    V = Y
    print(f"{C}Current HODL contract limits are as follows:")
    print(f"{N}  Max # of registrations per day: {V}{max24:>5d} {N}({V}{cur24:>5d}{N} used)")
    print(f"{N}  Max # of active contracts:      {V}{maxT:>5d} {N}({V}{curT:>5d}{N} active)")
    print(f"{N}Indicated used/active numbers are for fingerprint {V}{fp}{N}.{_}")

