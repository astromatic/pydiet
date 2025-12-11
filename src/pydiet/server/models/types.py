"""
Custom types for PyDIET data models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from enum import Enum
from typing import Literal

from ..types import AnnotatedStr
from .default import default_instrument, filters, instruments

ApertureID: Literal['optimal', 'fixed']

ComputeID = Literal['etime', 'snr']

FilterID = Enum(  # type: ignore[misc]
    "FilterID",
    {tag : tag for tag in filters.keys()},
    type=str
)

InstrumentID = Enum(  # type: ignore[misc]
    "InstrumentID",
    {tag : tag for tag in instruments.keys()},
    type=str
)

SkyID = Literal['dark', 'grey', 'bright', 'specify']

PhotometryID = Literal['aperture', 'psf']

PhotSysID = Literal['abmag', 'vegamag', 'fmegajy', 'fmujy', 'photons']

SourceID = Literal['pointsource', 'galaxy', 'extended']


