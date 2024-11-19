"""
Query models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from typing import Literal
from pydantic import BaseModel, Field, ValidationInfo, field_validator

from .data import default_filter, default_instrument, filters, instruments
from .types import ComputeID, FilterID, InstrumentID


class ETCQueryModel(BaseModel):
    instrument: InstrumentID = Field(
        default=default_instrument.id,
        description="Instrument"
    )
    airmass: float = Field(
        default=1.2,
        ge=1.,
        description="Observation airmass"
        )
    brightness: float = Field(
        default=20.,
        ge=-100.,
        le=100.,
        description="Source brightness"
        )
    compute: ComputeID
    etime: float = Field(
        default=20.,
        ge=0.,
        le=1e30,
        description="Required exposure time"
        )
    filter: FilterID = Field(
        default=default_filter.id,
        description="Filter"
    )
    photometry: Literal['aperture', 'psf']
    seeing: float = Field(
        default=0.7,
        ge=0.1,
        le=100.
        )
    sky: Literal['dark', 'grey', 'bright', 'custom']
    snr: float = Field(
        default=10.,
        gt=0.,
        description="Required source Signal-to-Noise Ratio"
        )
    source: Literal['pointsource', 'galaxy', 'extended']
    transparency: float = Field(
        default=1.,
        gt=0.,
        le=1.,
        description="Sky transparency"
        )
    unit: Literal['mag', 'flux']

    @field_validator('filter')
    def validate_filter(cls, f: str, info: ValidationInfo) -> str:
        instrument = ValidationInfo.data['instrument']
        fids = instruments[instrument].filters
        if f not in fids:
            raise ValueError(
                f"Input should be '{fids[0]}'" +
                (f"[', {fid}' for fid in fids[:-1]]" if len(fids) > 2 else "") +
                f" or '{fids[-1]}'" if len(fids) > 1 else ""
            )
        return f

