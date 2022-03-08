# -*- coding: utf-8 -*-
from __future__ import annotations
import dataclasses
import datetime
import decimal
import time
import typing as th

from .cli.colours import *
from .cli.colours import _
import hddcoin.hodl


keyReprDict = dict(
    contract_id      = "Contract ID:",
    client_pubkey    = "Client public key:",
    register_date    = "Registration date:",
    program_name     = "Program name:",
    term_months      = "Term (in months):",
    reward_percent   = "Reward percentage:",
    deposit_bytes    = "Deposit:",
    payout_address   = "Payout address:",
    timestamp_start  = "Timestamp at start:",
    timestamp_payout = "Timestamp at payout:",
    reward_bytes     = "Reward value:",
    contract_address = "Contract address:",
    puzzle_reveal    = "Puzzle reveal:",
    status           = "Status:",
    wait_time_days   = "Time until payout:",  # not in the dict (it's derived)
    payout_date      = "Payout date:",        # not in the dict (it's derived)
)

@dataclasses.dataclass
class ContractDetails:
    contract_id: str
    status: str
    client_pubkey: str
    register_date: str  # iso8601 string
    program_name: str
    term_months: decimal.Decimal
    reward_percent: decimal.Decimal
    deposit_bytes: int
    reward_bytes: int
    payout_address: str
    contract_address: str
    timestamp_start: int
    timestamp_payout: int
    puzzle_reveal: str
    tstamp_cancel_ok: int

    @classmethod
    def fromApiDict(cls, apiDict: th.Dict[str, th.Any]) -> ContractDetails:
        contractDetails = cls(
            contract_id       = apiDict["contract_id"],
            status            = apiDict["status"],
            client_pubkey     = apiDict["client_pubkey"],
            register_date     = apiDict["register_date"],
            program_name      = apiDict["program_name"],
            term_months       = decimal.Decimal(apiDict["term_months"]),
            reward_percent    = decimal.Decimal(apiDict["reward_percent"]),
            deposit_bytes     = apiDict["deposit_bytes"],
            reward_bytes      = apiDict["reward_bytes"],
            payout_address    = apiDict["payout_address"],
            contract_address  = apiDict["contract_address"],
            timestamp_start   = apiDict["timestamp_start"],
            timestamp_payout  = apiDict["timestamp_payout"],
            puzzle_reveal     = apiDict["puzzle_reveal"],
            tstamp_cancel_ok  = apiDict["tstamp_cancel_ok"],  # == 0 if when not confirmed yet
        )
        return contractDetails


    def toDict(self) -> th.Dict[str, th.Union[str, datetime.datetime, int, decimal.Decimal]]:
        import copy
        return copy.deepcopy(self.__dict__)

    def printSummary(self, indent: int, colour: bool = True) -> None:
        krd = keyReprDict
        t = " " * indent
        K = W if colour else ""  # Key colour
        V = Y if colour else ""  # Value colour
        H = G if colour else ""  # Highlight colour
        bph = hddcoin.hodl.BYTES_PER_HDD
        sc = getStateColour(self.status, V) if colour else ""
        if sc == Y:
            sc = W  # better contrast in this view
        flavor = ""
        if self.status == "PAID":
            flavor = f"{H} <- WOOHOO!!{_}"
        daysRemaining = max(0, (self.timestamp_payout - time.time())) / 86400
        wait_time_days = f"{daysRemaining:.2f}"
        payout_date = datetime.datetime.fromtimestamp(self.timestamp_payout,
                                                      tz = datetime.timezone.utc)
        payout_date_str = payout_date.isoformat(timespec = "seconds")

        kw = max(len(v) for v in krd.values())
        print(f"{t}{K}{krd['contract_id']:<{kw}}{_} {V}{self.contract_id}{_}")
        print(f"{t}{K}{krd['status']:<{kw}}{_} {sc}{self.status}{flavor}{_}")
        print(f"{t}{K}{krd['client_pubkey']:<{kw}}{_} {V}{self.client_pubkey}{_}")
        print(f"{t}{K}{krd['program_name']:<{kw}}{_} {V}{self.program_name}{_}")
        print(f"{t}{K}{krd['term_months']:<{kw}}{_} {V}{self.term_months} {K}months{_}")
        print(f"{t}{K}{krd['reward_percent']:<{kw}}{_} {V}{self.reward_percent} {K}%{_}")
        print(f"{t}{K}{krd['deposit_bytes']:<{kw}}{_} {V}{self.deposit_bytes/bph} {K}HDD{_}")
        print(f"{t}{K}{krd['reward_bytes']:<{kw}}{_} {V}{self.reward_bytes/bph} {K}HDD{_}")
        print(f"{t}{K}{krd['register_date']:<{kw}}{_} {V}{self.register_date}{_}")
        print(f"{t}{K}{krd['payout_date']:<{kw}}{_} {V}{payout_date_str}{_}")
        print(f"{t}{K}{krd['wait_time_days']:<{kw}}{_} {V}{wait_time_days} {K}days{_}")
        print(f"{t}{K}{krd['payout_address']:<{kw}}{_} {V}{self.payout_address}{_}")
        print(f"{t}{K}{krd['contract_address']:<{kw}}{_} {V}{self.contract_address}{_}")
        print(f"{t}{K}{krd['timestamp_start']:<{kw}}{_} {V}{self.timestamp_start}{_}")
        print(f"{t}{K}{krd['timestamp_payout']:<{kw}}{_} {V}{self.timestamp_payout}{_}")

    @classmethod
    def printShortSummaryHeader(cls) -> None:
        print(f"{C}{'CONTRACT ID':<16s}  "
              f"{'STATUS':<10s}  "
              f"{'REG DATE':<10s}  "
              f"{'TERM':>5s}  "
              f"{'REWARD':>12s}  "
              f"{'DEPOSIT':>10s}  "
              f"{'WAIT':>8s}"
              )

    def printShortSummaryLine(self, indent: int, colour: bool = True) -> None:
        s = self
        t = " " * indent
        K = W if colour else ""  # Key colour
        V = _ if colour else ""  # Value colour
        #H = C if colour else ""  # Highlight colour
        bph = hddcoin.hodl.BYTES_PER_HDD
        sc = getStateColour(self.status, V) if colour else ""
        sTxt = f"{sc}{self.status:<10s}"
        if self.status not in {"DECLINED", "EXPIRED"}:
            sTxt += V
        dtTxt = f"{self.register_date[:10]}"
        deposit_hdd = int(self.deposit_bytes / bph)  # we only accept whole number HDD deposits
        reward_hdd = decimal.Decimal(self.reward_bytes) / bph
        if self.status in {"REGISTERED", "CONFIRMED", "GUARANTEED"}:
            daysRemaining = max(0, (self.timestamp_payout - time.time())) / 86400
            wait = f"{daysRemaining:6.1f} d"
        else:
            wait = "      --"

        # Tried to keep under 80 chars, but... to no avail :(
        print(f"{t}{K}{s.contract_id:16s}  "
              f"{sTxt:10s}  "
              f"{dtTxt:10s}  "
              f"{self.term_months:4.1f}M  "
              f"{reward_hdd:8.2f} HDD  "  # whales may misalign
              f"{deposit_hdd:6d} HDD  "
              f"{wait}"
              f"{_}"
              )


stateColourMap = dict(
    REGISTERED = Y,
    CONFIRMED  = Y,
    GUARANTEED = G,
    PAID       = C,
    CANCELLED  = DY,
    EXPIRED    = Gy,
    DECLINED   = Gy,
    ERROR      = R,
    REJECTED   = R,
)
def getStateColour(state: str, defaultColour: str) -> str:
    return stateColourMap.get(state, defaultColour)

