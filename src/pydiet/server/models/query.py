"""
Query models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from enum import Enum

from pydantic import BaseModel, Field

from ..data import instruments



Instrument = Enum(  # type: ignore[misc]
    "Instrument",
    [instrument.id for instrument in instruments]
)



class ETCQueryModel(BaseModel):
    instrument: Instrument=Field(
        default="megacam",
        description="Instrument"
    )
    airmass: float=Field(
        default=1.2,
        ge=1.,
        description="Observation airmass"
        )
    brightness: float=Field(
        default=20.,
        ge=-100.,
        le=100.,
        description="Source brightness"
        )
    compute: T_COMPUTE
    etime: float=Field(
        default=20.,
        ge=0.,
        le=1e30,
        description="Required exposure time"
        )
    filter: Literal['u', 'g', 'r', 'i', 'z']
    
    photometry: Literal['aperture', 'psf']
    seeing: float=Field(
        default=0.7,
        ge=0.1,
        le=100.
        )
    sky: Literal['dark', 'grey', 'bright', 'custom']
    snr: float=Field(
        default=10.,
        gt=0.,
        description="Required source Signal-to-Noise Ratio"
        )
    source: Literal['pointsource', 'galaxy', 'extended']
    transparency: float=Field(
        default=1.,
        gt=0.,
        le=1.,
        description="Sky transparency"
        )
    unit: Literal['mag', 'flux']


