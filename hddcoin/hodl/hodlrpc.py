# -*- coding: utf-8 -*-
# NOTES:
#  - This contains all common client-side HODL operations
#  - All functions must be usable by both the CLI view and the GUI view
from __future__ import annotations
import asyncio
import http
import os
import platform
import ssl
import time
import typing as th

import aiohttp
import blspy   #type:ignore
import distro

import hddcoin
import hddcoin.hodl.exc as exc
from hddcoin.ssl.create_ssl import get_mozilla_ca_crt  #type:ignore
from hddcoin.util.clvm import int_to_bytes


HODL_SERVER_BASE = "https://hodl.hddcoin.org"
HODL_SERVER_PORT = 443

HODL_API_URL = f"{HODL_SERVER_BASE}:{HODL_SERVER_PORT}/hodl/api/v1"

DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total = 1000 if "WINGDB_ACTIVE" in os.environ else 10)

HTTP_GET = "get"
HTTP_POST = "post"

CLIENT_OS = platform.system()
CLIENT_DISTRO = distro.id()
CLIENT_APPVER = hddcoin.__version__


class HodlRpcClient:
    _fingerprint: int
    pk: blspy.G1Element
    sk: blspy.PrivateKey
    _session: aiohttp.ClientSession
    _closing_task: th.Optional[asyncio.Task]  # emulating hddcoin.rpc.rpc_client.RpcClient
    _sslcontext: ssl.SSLContext

    def __init__(self,
                 fingerprint: int,
                 ) -> None:
        import hddcoin.hodl.util  # lazy circref avoidance
        self._vlog_ = hddcoin.hodl.util.vlog

        self.pk, self.sk = hddcoin.hodl.util.getPkSkFromFingerprint(fingerprint)
        self._fingerprint = fingerprint

        self._sslcontext = ssl.create_default_context(cafile = get_mozilla_ca_crt())
        self._session = aiohttp.ClientSession(timeout = DEFAULT_TIMEOUT)
        self._closing_task = None


    def vlog(self, threshold: int, msg: str) -> None:
        self._vlog_(threshold, msg)

    async def get(self, endpoint: str, params: th.Optional[th.Dict[str, th.Any]] = None):
        return await self._call(endpoint, HTTP_GET, params)

    async def post(self, endpoint: str, params: th.Optional[th.Dict[str, th.Any]] = None):
        return await self._call(endpoint, HTTP_POST, params)

    def _getHodlAuthHeaders(self) -> th.Dict[str, th.Any]:
        self.vlog(1, "Generating signed RPC auth package")
        tstamp: int = int(time.time() * 1e6)  # in µs
        tstamp_sig: blspy.G2Element = blspy.AugSchemeMPL.sign(self.sk, int_to_bytes(tstamp))
        authHeaders = {
            "HODL-cpk":    str(self.pk),
            "HODL-tstamp": str(tstamp),
            "HODL-sig":    str(tstamp_sig),
            "HODL-os":     CLIENT_OS,
            "HODL-distro": CLIENT_DISTRO,
            "HODL-appver": CLIENT_APPVER,
        }
        return authHeaders

    async def _call(self,
                    endpoint: str,
                    verb: str,
                    params: th.Optional[th.Dict[str, th.Any]],
                    ) -> th.Dict[str, th.Any]:
        """Make an API call to the HODL server and capture basic connection errors.

        Connection errors are reported up as HodlConnectionError.

        """
        verbKwargs: th.Dict[str, th.Any]

        api_endpoint = f"{HODL_API_URL}/{endpoint}"
        self.vlog(2, f"Connecting to HDDcoin HODL Server at {api_endpoint}")

        if params is None:
            params = {}

        verbKwargs = dict(ssl = self._sslcontext)
        if verb == HTTP_GET:
            verbFn = self._session.get
            verbKwargs["params"] = params
        elif verb == HTTP_POST:
            verbFn = self._session.post
            verbKwargs["json"] = params
        else:
            raise ValueError(f"Unsupported verb: {verb}")

        # Fetch our BLS-based auth headers...
        hodlAuthHeaders = self._getHodlAuthHeaders()

        # Make the call and process the response!
        try:
            async with verbFn(api_endpoint,
                              headers = hodlAuthHeaders,
                              **verbKwargs,
                              ) as resp:
                if resp.status == 200:
                    self.vlog(2, "HODL Server responded cleanly")
                    rpcRet = await resp.json()
                    return _parseHodlRpcReturn(rpcRet)
                else:
                    status_text = http.client.responses.get(resp.status, "UNKNOWN CODE!")
                    err_msg = f"HTTP STATUS {resp.status} ({status_text})"
                    self.vlog(1, f"Server is unhappy: {err_msg}")
                    raise exc.HodlConnectionError(err_msg)
        except aiohttp.ClientConnectionError as e:
            self.vlog(1, f"ERROR CONNECTING TO HODL SERVER: {e!r}")
            err_msg = f"HODL Server not responding. Please check your network, or try again later!"
            raise exc.HodlConnectionError(err_msg)
        except asyncio.TimeoutError:
            self.vlog(1, f"Timed out connecting to {api_endpoint}")
            raise exc.HodlConnectionError("Timed out (HODL server took too long to respond)")

    # RpcClient API emulation methods...
    #  - these make managing the multiple RPC clients more convenient
    def close(self) -> None:
        self._closing_task = asyncio.create_task(self._session.close())
    async def await_closed(self) -> None:
        if self._closing_task is not None:
            await self._closing_task


def _parseHodlRpcReturn(rpcRet: th.Any) -> th.Dict[str, th.Any]:
    # Handle any mandatory future API upgrades..
    upgradeNotice = rpcRet.setdefault("upgrade_notice", "")
    if upgradeNotice:
        raise exc.ClientUpgradeRequired(upgradeNotice)

    # Handle server-reported errors...
    apiError = rpcRet.setdefault("error", "")
    if apiError:
        raise exc.HodlApiError(apiError)

    return rpcRet["result"]
