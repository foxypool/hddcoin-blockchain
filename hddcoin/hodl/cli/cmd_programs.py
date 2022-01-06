# -*- coding: utf-8 -*-
# NOTES:
#  - this file contains the CLI implementation for `hddcoin hodl programs`
from __future__ import annotations
import decimal
import json
import textwrap

from hddcoin.hodl.hodlrpc import HodlRpcClient
from hddcoin.hodl import BYTES_PER_HDD

from .colours import *
from .colours import _


async def cmd_programs(hodlRpcClient: HodlRpcClient,
                       *,
                       dumpJson: bool,
                       ) -> None:
    """Fetch available HODL programs and display results nicely to the CLI."""
    program_details = await hodlRpcClient.get("getPrograms")

    if dumpJson:
        print(json.dumps(program_details, indent=4))
        return

    motd = program_details["motd"]
    programs = program_details["programs"]
    if motd:
        wrappedMOTD = "\n".join(textwrap.wrap(motd, 80))
        print(f"{Y}============================  MESSAGE OF THE DAY  ============================={_}")
        print(f"\n{W}{wrappedMOTD}{_}\n")
        print(f"{Y}==============================================================================={_}")
        print()

    if len(programs) == 0:
        print("Sorry! There are currently no HODL programs available. Check back soon!")
    else:
        print(f"{C}The following HDDcoin HODL programs are currently available:{_}")
        print(f"{W}{'-' * 83}{_}")
        print(f"{W}{'Name':<12} {'Term':>5} {'Rwd':>4}  {'Minimum':>8}  Description{_}")
        print(f"{W}{'-' * 83}{_}")
        for p in programs:
            name = p["name"]
            minimum_commit_hdd = decimal.Decimal(p["min_commit_bytes"]) / BYTES_PER_HDD
            term = f"{p['term_in_months']:.2f}".rstrip("0").strip(".") + "M"
            perc = f"{p['reward_percent']:.2f}".rstrip("0").strip(".") + "%"
            mch  = f"{minimum_commit_hdd:.1f}".rstrip("0").strip(".") + " HDD"
            desc = p["description"]
            print(f"{Y}{name:<12}{_} {term:>5} {perc:>4}  {mch:>8}  {desc}{_}")
        print(f"{W}{'-' * 83}{_}")
        print(f"{C}To commit funds to one of these programs, please use `{Y}hddcoin hodl commit{C}`.{_}")
        print(f"{G}HAPPY HODL'ING!!{_}")
        print()
