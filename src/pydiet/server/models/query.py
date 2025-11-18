"""
Query models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from typing import Literal
from pydantic import (
    BaseModel,
    Field,
    PydanticUserError,
    ValidationInfo,
    field_validator
)

from .default import default_filter, default_instrument, filters, instruments
from .exceptions import ETCValidationError
from .types import (
    ComputeID,
    FilterID,
    InstrumentID,
    PhotSysID,
    SkyID,
    SourceID
)

class ETCQueryModel(BaseModel):

    instrument: InstrumentID = Field(
        description="Instrument ID"
    )

    airmass: float = Field(
        default=1.2,
        ge=1.,
        description="Observation airmass"
    )

    brightness: float = Field(
        default=20.,
        ge=-100.,
        le=1000.,
        description="Source brightness"
    )

    compute: ComputeID = Field(
        description="Computation type"
    )

    etime: float = Field(
        default=20.,
        ge=0.,
        le=1e30,
        description="Required exposure time [s]"
    )

    filter: FilterID = Field(
        description="Instrument filter"
    )

    photometry: Literal['aperture', 'psf']

    seeing: float = Field(
        default=0.7,
        ge=0.1,
        le=100.
    )
    sky: SkyID

    sky_brightness: float = Field(
        default=22.,
        ge=-100.,
        le=1000.,
        description="Sky surface brightness"
    )

    sky_unit: PhotSysID

    sersic_radius: float = Field(
        default=1.,
        gt=0.,
        le=10.,
        description="Sérsic effective radius [\"]"
    )

    sersic_index: float = Field(
        default=1.,
        ge=0.3,
        le=10.,
        description="Sersic index"
    )

    snr: float = Field(
        default=10.,
        gt=0.,
        description="Required source Signal-to-Noise Ratio"
    )

    source: SourceID = Field(
        description="Source type"
    )

    transparency: float = Field(
        default=1.,
        gt=0.,
        le=1.,
        description="Sky transparency"
    )

    unit: PhotSysID = Field(
        default='abmag',
        description="Photometric system"
    )

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

