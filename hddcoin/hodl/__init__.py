# -*- coding: utf-8 -*-
# NOTES:
#  - This contains all common client-side HODL operations
#  - All functions must be usable by both the CLI view and the GUI view
from __future__ import annotations
import pathlib

import hddcoin.util.default_root
from hddcoin.types.blockchain_format.sized_bytes import make_sized_bytes

HODL_DIR: pathlib.Path = hddcoin.util.default_root.DEFAULT_ROOT_PATH / "hodl"
HODL_DIR_TMP: pathlib.Path = HODL_DIR / "tmp"
HODL_DIR_RECEIPTS: pathlib.Path = HODL_DIR / "receipts"

CONTRACT_EXPIRATION_TIME_s = 600  # need to make a decision! ;) Short to handle registration aborts.

BYTES_PER_HDD = int(1e12)

HTTP_GET = "get"
HTTP_POST = "post"

bytes8 = make_sized_bytes(8)
