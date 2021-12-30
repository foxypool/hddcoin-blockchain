# -*- coding: utf-8 -*-

# ALL CLI OPERATIONS RUN THROUGH THIS API LAYERING...
#    CLI Interface => CLI Implementation => Core Operation

from __future__ import annotations
import asyncio
import typing as th

import click                      #type:ignore
from click_params import DECIMAL  #type:ignore

try:
    from . import wingdbstub  #type:ignore
except ImportError:
    pass


###############################
## Root for `hodl` commands
###############################
@click.group("hodl", short_help="Manage your HODL contracts")
def hodl_cmd() -> None:
    pass


###############################
## `hddcoin hodl programs`
###############################
@hodl_cmd.command("programs", short_help="Display currently available HODL programs")
@click.option("-f", "--fingerprint", type=int,
              help="Set the fingerprint to specify which wallet to use")
@click.option("--json", is_flag=True, default=False, help="Dump output in json format")
@click.option("--verbose", "-v", count=True, type=int,
              help="log some details to console (for debugging)")
def programs_cmd(fingerprint: int, json: bool, verbose: int) -> None:
    from hddcoin.hodl.cli.cmd_programs import cmd_programs
    from hddcoin.hodl.util import callCliCmdHandler
    asyncio.run(
        callCliCmdHandler(
            cmd_programs,
            verbose,
            fingerprint,
            cmdKwargs = dict(dumpJson = json),
        ),
    )


###############################
## `hddcoin hodl commit`
###############################
@hodl_cmd.command("commit", short_help="Register for, and commit funds to, a HODL contract")
@click.option("-P", "--program",
              help="HODL program name to commit to. See `hddcoin hodl programs` for options.",
              type=str, required=True)
@click.option("-wp", "--wallet-rpc-port", type=int, default=None,
              help=("Set the port where the Wallet is hosting the RPC interface. See the rpc_port "
                    "under wallet in config.yaml"))
@click.option("-f", "--fingerprint", type=int,
              help="Set the fingerprint to specify which wallet to use")
@click.option("-i", "--id", type=int, default=1, show_default=True, required=True,
              help="Id of the wallet to use", )
@click.option("-a", "--amount", type=DECIMAL, required=True,
              help="How many HDD to commit to the HODL contract. Must be a whole number.", )
@click.option("-m", "--fee", type=DECIMAL, default="0", show_default=True, required=True,
              help="Set the fees for the transaction, in HDD")
@click.option("-t","--address", type=str, required=False,
              help = ("Where to send all HODL proceeds/returns. Default is the 1st wallet address "
                      "for the specified wallet fingerprint."))
@click.option("-o", "--override", is_flag=True, default=False,
              help="Submits transaction without checking for unusual values")
@click.option("--verbose", "-v", count=True, type=int,
              help="log some details to console (for debugging)")
def commit_cmd(program: str,
               wallet_rpc_port: th.Optional[int],
               fingerprint: int,
               id: int,
               amount: str,
               fee: str,
               address: str,
               override: bool,
               verbose: int,
               ) -> None:
    from hddcoin.hodl.cli.cmd_commit import cmd_commit
    from hddcoin.hodl.util import callCliCmdHandler
    asyncio.run(
        callCliCmdHandler(
            cmd_commit,
            verbose,
            fingerprint,
            injectConfig = True,
            fullNodeRpcPort = None, # no full_node RPC connection needed
            walletRpcPort = wallet_rpc_port or 0,  # walletRpcClient needed (0 is automatic port)
            cmdKwargs = dict(program_name = program,
                             wallet_id = id,
                             wallet_rpc_port = wallet_rpc_port,
                             commit_hdd = amount,
                             fee_hdd = fee,
                             payout_address = address,
                             override = override,
                             )
        )
    )


###############################
## `hddcoin hodl cancel`
###############################
@hodl_cmd.command("cancel", short_help="Cancel an existing HODL contract")
@click.option("-C", "--contract", help="HODL contract to cancel", type=str, required=True)
@click.option("-p", "--rpc-port", type=int, default=None,
              help=("Set the port where the Full Node is hosting the RPC interface. See the "
                    "rpc_port under full_node in config.yaml"))
@click.option("-f", "--fingerprint", type=int,
              help="Set the fingerprint to specify which key/wallet to use to cancel")
#@click.option("-m", "--fee", type=DECIMAL, default="0", show_default=True, required=True,
#              help="Set the fees for the transaction, in HDD")
@click.option("--no-confirm", is_flag=True, default=False,
              help="bypass all confirmation messages")
@click.option("--verbose", "-v", count=True, type=int,
              help="log some details to console (for debugging)")
def cancel_cmd(contract: str,
               rpc_port: th.Optional[int],
               fingerprint: int,
               no_confirm: bool,
               verbose: int,
               ) -> None:
    from hddcoin.hodl.cli.cmd_cancel import cmd_cancel
    from hddcoin.hodl.util import callCliCmdHandler
    asyncio.run(
        callCliCmdHandler(
            cmd_cancel,
            verbose,
            fingerprint = fingerprint,
            injectConfig = False,
            fullNodeRpcPort = rpc_port or 0,  # FullNodeRpcClient needed (0 is automatic port)
            walletRpcPort = None,             # Wallet not currently needed
            cmdKwargs = dict(contract_id = contract,
                             no_confirm = no_confirm,
                             )
        )
    )


###############################
## `hddcoin hodl limits`
###############################
@hodl_cmd.command("limits", short_help="Check the current HODL contract limits, and status for key")
@click.option("-f", "--fingerprint", type=int,
              help="Set the fingerprint to specify which key/wallet to check")
@click.option("--json", is_flag=True, default=False, help="Dump output in json format")
@click.option("--verbose", "-v", count=True, type=int,
              help="log some details to console (for debugging)")
def limits_cmd(fingerprint: int,
               json: bool,
               verbose: int,
               ) -> None:
    from hddcoin.hodl.cli.cmd_limits import cmd_limits
    from hddcoin.hodl.util import callCliCmdHandler
    asyncio.run(
        callCliCmdHandler(
            cmd_limits,
            verbose,
            fingerprint,
            injectConfig = False,
            fullNodeRpcPort = None,  # not needed
            walletRpcPort = None,    # not needed
            cmdKwargs = dict(dumpJson = json),
        )
    )


###############################
## `hddcoin hodl show`
###############################

@hodl_cmd.command("show", short_help="Display contract details for contract(s).")
@click.option("-C", "--contract", help="HODL contract to display. If missing, show all.", type=str, required=False)
@click.option("-f", "--fingerprint", type=int,
              help="Set the fingerprint to specify which key/wallet to use")
@click.option("--json", is_flag=True, default=False, help="Dump output in json format")
@click.option("--verbose", "-v", count=True, type=int,
              help="log some details to console (for debugging)")
def show_cmd(contract: str,
             fingerprint: int,
             json: bool,
             verbose: int,
             ) -> None:
    from hddcoin.hodl.cli.cmd_show import cmd_show
    from hddcoin.hodl.util import callCliCmdHandler
    asyncio.run(
        callCliCmdHandler(
            cmd_show,
            verbose,
            fingerprint,
            injectConfig = False,
            fullNodeRpcPort = None,  # not needed
            walletRpcPort = None,    # not needed
            cmdKwargs = dict(contract_id = contract,
                             dumpJson = json),
        )
    )

###############################
## `hddcoin hodl profits`
###############################

@hodl_cmd.command("profits", short_help="Display past and future HODL profits.")
@click.option("-f", "--fingerprint", type=int,
              help="Set the fingerprint to specify which key/wallet to use")
@click.option("--json", is_flag=True, default=False, help="Dump output in json format")
@click.option("--verbose", "-v", count=True, type=int,
              help="log some details to console (for debugging)")
def profits_cmd(fingerprint: int,
                json: bool,
                verbose: int,
                ) -> None:
    from hddcoin.hodl.cli.cmd_profits import cmd_profits
    from hddcoin.hodl.util import callCliCmdHandler
    asyncio.run(
        callCliCmdHandler(
            cmd_profits,
            verbose,
            fingerprint,
            injectConfig = False,
            fullNodeRpcPort = None,  # not needed
            walletRpcPort = None,    # not needed
            cmdKwargs = dict(dumpJson = json),
        )
    )
