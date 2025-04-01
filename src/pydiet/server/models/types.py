"""
Custom types for PyDIET data models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from enum import Enum
from typing import Literal

from ..types import AnnotatedStr
from .data import default_instrument, filters, instruments


ComputeID = Literal['etime', 'snr']


InstrumentID = Enum(  # type: ignore[misc]
    "InstrumentID",
    {tag : tag for tag in instruments.keys()},
    type=str
)


FilterID = Enum(  # type: ignore[misc]
    "FilterID",
    {tag : tag for tag in filters.keys()},
    type=str
)


