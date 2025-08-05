"""
Query models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from typing import Literal
from pydantic import BaseModel, Field, PydanticUserError, ValidationInfo, field_validator

from .default import default_filter, default_instrument, filters, instruments
from .exceptions import ETCValidationError
from .types import ComputeID, FilterID, InstrumentID, SkyID


class ETCQueryModel(BaseModel):
    instrument: InstrumentID
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
    filter: FilterID
    photometry: Literal['aperture', 'psf']
    seeing: float = Field(
        default=0.7,
        ge=0.1,
        le=100.
        )
    sky: SkyID
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
    unit: Literal['abmag', 'vegamag', 'flambda', 'fnu', 'fjansky']

    @field_validator('filter')
    def validate_filter(cls, f: str, info: ValidationInfo) -> str:
        """
        Kind of emulate Enum validation and errors.
        """
        instrument = info.data['instrument']
        fids = list(instruments[instrument].filters)
        if f not in fids:
            expected = f"'{fids[0]}'" + \
                (
                    "".join(f", '{fid}'" for fid in fids[:-1]) \
                    if len(fids) > 2 else ""
                ) + (
                    f" or '{fids[-1]}'" if len(fids) > 1 else ""
                )
            raise ETCValidationError({
                "type": "enum",
                "loc": ("query", "filter"),
                "input": str(f),
                "expected": expected
            })
        return f

