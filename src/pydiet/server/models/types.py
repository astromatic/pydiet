"""
Data types
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

import sys
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum
from typing import Literal

from .data import filters, instruments


ComputeID = Literal['etime', 'snr']


InstrumentID = StrEnum(  # type: ignore[misc]
    "InstrumentID",
    list(instruments.keys())
)


FilterID = StrEnum(  # type: ignore[misc]
    "FilterID",
    list(filters.keys())
)



