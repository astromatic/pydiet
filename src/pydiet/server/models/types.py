"""
Custom types for PyDIET data models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from enum import Enum
from typing import Literal

from .default import filters, instruments, mirrors

class StrEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


ComputeID = Literal['etime', 'snr']

FilterID = StrEnum(  # type: ignore[misc]
    "FilterID",
    {tag : tag for tag in filters.keys()} | {'upload' : 'upload'}
)

InstrumentID = StrEnum(  # type: ignore[misc]
    "InstrumentID",
    {tag : tag for tag in instruments.keys()}
)

MirrorID = StrEnum(  # type: ignore[misc]
    "MirrorID",
    {tag : tag for tag in mirrors.keys()}
)

PhotometryID = Literal['model_fitting', 'fixed_aperture', 'optimal_aperture', 'large_aperture']

PhotSysID = Literal['abmag', 'vegamag', 'fmegajy', 'fmujy', 'flux', 'photons']

SkyID = Literal['dark', 'grey', 'bright', 'specify']

SourceID = Literal['point_source', 'galaxy', 'extended']

StackingID = Literal['average', 'median']

