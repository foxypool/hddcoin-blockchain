# -*- coding: utf-8 -*-
# NOTES:
#  - this file is all about the trust model for the HODL contracts. TRUST NO ONE. VALIDATE ALL.
from __future__ import annotations
import dataclasses
import decimal
import re
import time
import typing as th

import hddcoin.hodl
from clvm_tools.binutils import disassemble, int_to_bytes  #type:ignore
from hddcoin.hodl import exc as exc
from hddcoin.hodl.ContractDetails import ContractDetails
from hddcoin.hodl.util import vlog, puzhash2addr
from hddcoin.types.blockchain_format.program import Program, SerializedProgram
from hddcoin.types.blockchain_format.sized_bytes import bytes32
from hddcoin.util.byte_types import hexstr_to_bytes

SECONDS_PER_MONTH = int(86400 * 365 / 12)

conPat = (
    '\(a\ \(q\ 4\ \(c\ 44\ \(c\ 11\ \(\)\)\)\ \(c\ \(c\ 92\ \(c\ 23\ \(\)\)\)\ \(c\ \(c\ 52\ \('
    'q\ 1\)\)\ \(a\ \(i\ \(=\ 5\ 32\)\ \(q\ 4\ \(c\ 36\ \(c\ 34\ \(c\ 50\ \(\)\)\)\)\ \(a\ \(i'
    '\ \(>\ 11\ 38\)\ \(q\ 4\ \(c\ 90\ \(c\ 46\ \(c\ 38\ \(\)\)\)\)\ \(c\ \(c\ 90\ \(c\ 54\ \(c'
    '\ \(\-\ 11\ 38\)\ \(\)\)\)\)\ \(\)\)\)\ \(q\ 4\ \(c\ 90\ \(c\ 46\ \(c\ 11\ \(\)\)\)\)\ \(\)'
    '\)\)\ 1\)\)\ \(q\ 2\ \(i\ \(=\ 5\ 48\)\ \(q\ 2\ \(i\ \(any\ \(>\ \(/\ \(\*\ \(q\ \.\ 1000'
    '\)\ 94\)\ 38\)\ \(q\ \.\ 350\)\)\ \(>\ \(q\ \.\ 0x00e8d4a51000\)\ 38\)\ \(>\ 38\ \(q\ \.\ 0'
    'x0d8d726b7177a80000\)\)\)\ \(q\ 8\)\ \(q\ 4\ \(c\ 44\ \(c\ 38\ \(\)\)\)\ \(c\ \(c\ 90\ \(c'
    '\ 23\ \(c\ \(\+\ 38\ 94\)\ \(\)\)\)\)\ \(c\ \(c\ 122\ \(c\ 50\ \(\)\)\)\ \(\)\)\)\)\)\ 1\)'
    '\ \(q\ 2\ \(i\ \(=\ 5\ 56\)\ \(q\ 4\ \(c\ 44\ \(c\ \(\+\ 38\ 94\)\ \(\)\)\)\ \(c\ \(c\ 124'
    '\ \(c\ 126\ \(\)\)\)\ \(c\ \(c\ 90\ \(c\ 46\ \(c\ \(\+\ 38\ 94\)\ \(\)\)\)\)\ \(\)\)\)\)\ '
    '\(q\ 2\ \(i\ \(=\ 5\ 40\)\ \(q\ 8\ 42\ 50\ 38\ 94\ 126\ 46\)\ \(q\ 8\)\)\ 1\)\)\ 1\)\)\ 1'
    '\)\)\ 1\)\)\)\)\ \(c\ \(q\ \(\(\(q\ \.\ 2\)\ 4\ \.\ 3\)\ \(50\ \.\ 82\)\ 73\ 72\ \.\ 81\)\ '
    '\(\((?P<v7>.*)\ \.\ (?P<v5>.*)\)\ (?P<v6>.*)\ 51\ \.\ 62\)\ \((?P<v1>.*)\ \.\ (?P<v8>.*)\)'
    '\ (?P<v2>.*)\ (?P<v4>.*)\ \.\ (?P<v3>.*)\)\ 1\)\)'
)


@dataclasses.dataclass
class BakedInTerms:
    deposit_bytes: int
    payout_puzhash: str
    payout_tstamp: int
    reward_bytes: int
    contract_id: str
    program_name: str
    client_pubkey: str


def _cmpRct(tok: str, expected: th.Any, received: th.Any) -> None:
    if expected != received:
        raise exc.ContractValidationError(f"Unexpected receipt value for {tok}: {received}")


def _cmpCon(tok: str, expected: th.Any, received: th.Any) -> None:
    if expected != received:
        raise exc.ContractValidationError(
            f"Unexpected contract value for {tok}. Expected: {expected}; Received: {received}")


def _atomReprAsInt(s: str) -> int:
    """Translate CLVM atom repr to int."""
    if s.startswith("0x"):
        return int(s, base=16)
    elif s.startswith('"'):
        return int.from_bytes(s[1:-1].encode("ascii"), "big")
    return int(s)


def _atomReprAsStr(s: str) -> str:
    """Translate CLVM atom repr to str."""
    if s.startswith("0x"):
        return bytes.fromhex(s[2:]).decode("ascii")
    elif s.startswith('"'):
        return s[1:-1]
    return int_to_bytes(int(s)).decode("ascii")


def _atomReprAsHex(s: str) -> str:
    """Translate CLVM integer atom repr to a 0x-prefixed hex string."""
    if s.startswith("0x"):
        return s
    elif s.startswith('"'):
        return "0x" + s[1:-1].encode("ascii").hex()
    return hex(int(s))


def _extractBakedInTerms(reveal: str) -> BakedInTerms:
    try:
        m = th.cast(re.Match, re.search(conPat,
                                        disassemble(Program.from_bytes(hexstr_to_bytes(reveal)))))
        yum = BakedInTerms(
            deposit_bytes  = _atomReprAsInt(m.group("v1")),
            payout_puzhash = _atomReprAsHex(m.group("v2")),
            payout_tstamp  = _atomReprAsInt(m.group("v3")),
            reward_bytes   = _atomReprAsInt(m.group("v4")),
            contract_id    = _atomReprAsHex(m.group("v5")),
            program_name   = _atomReprAsStr(m.group("v6")),
            client_pubkey  = _atomReprAsHex(m.group("v7")),
        )
    except Exception:
        raise exc.ContractValidationError("Contract reveal is not valid.")
    return yum


def _validatePuzzleHash(addr: str, reveal: str) -> bytes32:
    sp: SerializedProgram = SerializedProgram.fromhex(reveal)
    ph = hddcoin.hodl.util.addr2puzhash(addr)
    ph_b32 = sp.get_tree_hash()
    if ph != ph_b32.hex():
        raise exc.ContractValidationError(f"Reveal does not match address")
    return ph_b32


def validateContract(# Given to server...
                     ex_program_name: str,
                     ex_deposit_bytes: int,
                     ex_payout_address: str,
                     ex_client_pubkey: str,

                     # Expected from server based on program details we had...
                     ex_term_in_months: decimal.Decimal,
                     ex_reward_percent: decimal.Decimal,

                     receipt: th.Dict[str, th.Any],
                     ) -> None:  # raises exc.ContractValidationError on issues
    """Make sure that the receipt, and instructions therein, are what we expect.

    Raises exc.ContractValidationError if any issues are found.

    """
    # The overall trust model here is: TRUST NO ONE. THESE ARE MY PRECIOUS HDDs!!
    #
    # In the comments below, there are two parties:
    #
    #    1. The "client" --> This hddcoin application (i.e. this code) or the person running it
    #    2. The "server" --> The HODL server that has been contacted to provide contract terms,
    #                         which include a specific contract/puzzle to send an amount to.
    #
    # Although the HDDcoin team are certainly a trustable bunch and can be expected to provide the
    # correct/expected contract terms to the client to follow, if the client is concerned about
    # overall security and precious HDD funds (which the client obviously should be!!), the client
    # should ABSOLUTELY ASSUME THAT THE SERVER IS NOT TRUSTABLE, UNTIL VERIFIED. More specifically,
    # the client should assume that whoever/whatever provided the client the contract terms to
    # follow could definitely have been compromised by EVIL HACKERS AFTER THE CLIENT'S PRECIOUS HDD.
    #
    # Nasty scenarios we should be concerned about include (with overlapping concerns):
    #
    #   1. the HODL API server could have been hacked
    #   2. there could be a man-in-the-middle attack happening, making data untrustworthy
    #   3. the contract terms provided could have been falsified in some/any way
    #   4. the on-chain contract (smart coin via puzzlehash/reveal) could be bogus
    #   5. sneaky hacker farmers could mess with how pushed coins/puzzles are processed on-chain
    #   6. and more!
    #
    # With these concerns in mind, the client needs to be sure that everything is secure before
    # committing funds on-chain. The smart contract itself provides excellent on-chain security to
    # make sure that no adverse shenanigans can happen once funds are on chain. The purpose in this
    # `validateContract` function is to make sure that there are no other surprises in store (as
    # listed above).
    #
    # As stated in the docstring: This function makes sure that sure that the provided contract is
    # what the client expects.
    #
    # What the HODL contract is all about is providing a secure conditional lockbox where:
    #
    #    A) the client can stash a deposit into the box that ONLY THE CLIENT CAN EVER ACCESS
    #    B) a secure way is provided for the server (i.e. the HDDcoin team) to add the guaranteed
    #        reward to the lockbox for later payout (at end of contract)
    #         - IMPORTANT NOTE: the server can never access the deposit in any way whatsoever
    #         - the HDDcoin team gets reward funds from a HODL reserve in the pre-farm funds
    #    C) if the client meets the contract terms (i.e. the HODL deposit sits in the box for the
    #        length of the term), both the deposit and the reward pay out to the client's wallet
    #    D) if the client decides to cancel the contract, the deposit is returned to the client, and
    #        the guaranteed reward is returned to the HDDcoin HODL reserve
    #         - ONLY THE CLIENT CAN EVER CANCEL THE CONTRACT. NOBODY ELSE.
    #         - once the reward is added, it is GUARANTEED for the client (unless canceled). Sweet!
    #    E) there are other various bits involved... but they mostly revolve around ensuring that
    #        the mechanics of the contract are secure against nefarious hackers... I see you there
    #        reading this... SHOO!! Go away!! ¬_¬
    #
    # All of those listed things are *if all is as expected*. Again, this is what this validation
    # function is about. Even if the server is compromised (which it should not be, but... TRUST
    # NOBODY!), the client's HDD must NEVER be placed at risk here. This is fundamental to the HODL
    # program, and is supported through all supporting client code, server code, and on-chain code.

    vlog(1, "Extracting receipt fields for validation")
    try:
        rx_program_name     = receipt["requested"]["program_name"]
        rx_deposit_bytes    = receipt["requested"]["deposit_bytes"]
        rx_payout_address   = receipt["requested"]["payout_address"]
        rx_client_pubkey    = receipt["requested"]["client_pubkey"]
        rx_contract_id      = receipt["receipt_info"]["contract_id"]
        rx_contract_address = receipt["coin_details"]["contract_address"]
        rx_reveal           = receipt["coin_details"]["reveal"]
        rx_solCancelDep     = receipt["coin_details"]["solution_cancel_deposited"]
        rx_solCancelGuar    = receipt["coin_details"]["solution_cancel_guaranteed"]
        rx_solPayout        = receipt["coin_details"]["solution_payout"]
    except KeyError as e:
        raise exc.ContractValidationError(f"Missing receipt key: {e.args[0]}")

    # Check the receipt fields (which don't matter that much, but still...)
    vlog(1, "Validating requested vs received")
    _cmpRct("program_name",   ex_program_name,   rx_program_name)
    _cmpRct("deposit_bytes",  ex_deposit_bytes,  rx_deposit_bytes)
    _cmpRct("payout_address", ex_payout_address, rx_payout_address)
    _cmpRct("client_pubkey",  ex_client_pubkey,  rx_client_pubkey)

    # Contract address and reveal must match...
    vlog(1, "Validating puzzle hash")
    ph_b32 = _validatePuzzleHash(rx_contract_address, rx_reveal)

    # Reveal must be the contract we expect...
    vlog(1, "Validating puzzle reveal")
    ex_payout_ph = f"0x{hddcoin.hodl.util.addr2puzhash(ex_payout_address)}"
    ex_reward_bytes = int(ex_deposit_bytes * (ex_reward_percent / 100))
    epoch_s = int(time.time())
    ex_payout_tstamp = int(epoch_s + (ex_term_in_months * SECONDS_PER_MONTH))
    try:
        terms = _extractBakedInTerms(rx_reveal)
        _cmpCon("deposit_bytes", ex_deposit_bytes, terms.deposit_bytes)
        _cmpCon("payout_address", ex_payout_ph, terms.payout_puzhash)
        _cmpCon("reward_bytes", ex_reward_bytes, terms.reward_bytes)
        _cmpCon("contract_id", f"0x{rx_contract_id}", terms.contract_id)
        _cmpCon("program_name", ex_program_name, terms.program_name)
        _cmpCon("client_pubkey", f"0x{ex_client_pubkey}", terms.client_pubkey)
    except Exception as e:
        raise exc.ContractValidationError(f"Error validating contract terms: {e!r}")
    if abs(ex_payout_tstamp - terms.payout_tstamp) > 3600:  # 1h good enough for validation
        msg = f"Unexpected contract value for payout_timestamp: {terms.payout_tstamp}"
        raise exc.ContractValidationError(msg)

    # Solutions must match...
    vlog(1, "Validating solutions")
    ex_solCancelDep  = str(Program.to([1, ex_deposit_bytes, ph_b32]))
    ex_solCancelGuar = str(Program.to([1, ex_deposit_bytes + ex_reward_bytes, ph_b32]))
    ex_solPayout     = str(Program.to([3, ex_deposit_bytes + ex_reward_bytes, ph_b32]))
    _cmpRct("solution_cancel_deposited",  ex_solCancelDep,  rx_solCancelDep)
    _cmpRct("solution_cancel_guaranteed", ex_solCancelGuar, rx_solCancelGuar)
    _cmpRct("solution_payout",            ex_solPayout,     rx_solPayout)

    # ALL IS WELL IF WE GOT HERE!
    vlog(1, "Contract provided by server is as expected!")


def validateCancellation(ex_contract_id: str,
                         contractDetails: ContractDetails,
                         ) -> None:
    """Makes sure that the contract details fetched from the HODL server by the cancel request are a
    match to what the user expects."""
    # This is essentially just cross-checking the contract dict details with what is actually in the
    # reveal. We don't need to validate the cancellation solutions since we don't use/need them.
    # Those are only for users who want to do it on their own without HODL tooling.
    rx_contract_id = contractDetails.contract_id
    rx_contract_address = contractDetails.contract_address
    rx_reveal = contractDetails.puzzle_reveal

    if rx_contract_id != ex_contract_id:
        raise exc.CancelValidationError("contract_id mismatch")

    vlog(1, "Validating puzzle hash")
    _validatePuzzleHash(rx_contract_address, rx_reveal)

    vlog(1, "Validating puzzle reveal")
    # Not much to validate here. If it is the right contract form, it can only be a HODL contract.
    # Even still, to be ABSOLUTELY sure, we'll validate that the baked-in terms match the contract
    # details displayed to the user.
    terms = _extractBakedInTerms(rx_reveal)
    _cmpCon("deposit_bytes", contractDetails.deposit_bytes, terms.deposit_bytes)
    _cmpCon("payout_address", contractDetails.payout_address, puzhash2addr(terms.payout_puzhash))
    _cmpCon("reward_bytes", contractDetails.reward_bytes, terms.reward_bytes)
    _cmpCon("contract_id", f"0x{contractDetails.contract_id}", terms.contract_id)
    _cmpCon("program_name", f"{contractDetails.program_name}", terms.program_name)
    _cmpCon("client_pubkey", f"0x{contractDetails.client_pubkey}", terms.client_pubkey)
