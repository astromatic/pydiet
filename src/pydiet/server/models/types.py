"""
Custom types for PyDIET data models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from enum import Enum
from typing import Literal

from .default import filters, instruments, mirrors


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

MirrorID = Enum(  # type: ignore[misc]
    "MirrorID",
    {tag : tag for tag in mirrors.keys()},
    type=str
)

PhotometryID = Literal['model_fitting', 'fixed_aperture', 'optimal_aperture', 'large_aperture']

PhotSysID = Literal['abmag', 'vegamag', 'fmegajy', 'fmujy', 'flux', 'photons']

SkyID = Literal['dark', 'grey', 'bright', 'specify']

SolarID = Literal['low', 'average', 'high']

SourceID = Literal['point_source', 'galaxy', 'extended']

StackingID = Literal['average', 'median']

