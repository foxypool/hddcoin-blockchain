# -*- coding: utf-8 -*-
from __future__ import annotations

class HodlError(Exception):
    def __init__(self, msg: str = "") -> None:
        self.msg = msg

class ClientUpgradeRequired(HodlError): pass
class CancelValidationError(HodlError): pass
class ContractValidationError(HodlError): pass
class HodlApiError(HodlError): pass
class HodlConnectionError(HodlError): pass
class KeyNotFound(HodlError): pass
class InsufficientFunds(HodlError): pass
class UnhandledError(HodlError): pass
class WalletIdNotFound(HodlError): pass
class WalletNotSynced(HodlError): pass
class FingerprintNeeded(HodlError): pass
class WalletTooFragmented(HodlError): pass
