"""
Custom types for PyDIET data models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from enum import Enum
from typing import Literal

from .default import filters, instruments

ComputeID = Literal['etime', 'snr']

FilterID = Enum(  # type: ignore[misc]
    "FilterID",
    {tag : tag for tag in filters.keys()} | {'upload' : 'upload'},
    type=str
)

InstrumentID = Enum(  # type: ignore[misc]
    "InstrumentID",
    {tag : tag for tag in instruments.keys()},
    type=str
)

SkyID = Literal['dark', 'grey', 'bright', 'specify']

PhotometryID = Literal['model_fitting', 'fixed_aperture', 'optimal_aperture', 'large_aperture']

PhotSysID = Literal['abmag', 'vegamag', 'fmegajy', 'fmujy', 'photons']

SourceID = Literal['point_source', 'galaxy', 'extended']

StackingID = Literal['average', 'median']

