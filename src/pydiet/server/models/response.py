"""
Response models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from astropy import units as u #type: ignore[import-untyped]
from pydantic import BaseModel, Field

from ..types import AnnotatedQuantity
from .types import ComputeID, InstrumentID


class ETCResponseModel(BaseModel):
    instrument: InstrumentID
    compute: ComputeID
    zp: float=Field(
        default=0.,
        ge=0.,
        lt=1e30,
        description="Estimate magnitude zero-point"
    )
    etime: float=Field(
        default=1.,
        ge=0.,
        lt=1e30,
        description="Estimated exposure time"
    )
    etime_skysat: float=Field(
        default=0.,
        ge=0.,
        lt=1e30,
        description="Estimated exposure time for sky background saturation"
    )
    etime_sourcesat: float=Field(
        default=0.,
        ge=0.,
        lt=1e30,
        description="Estimated exposure time for source saturation"
    )
    snr: float=Field(
        default=10.,
        ge=0.,
        lt=1e30,
        description="Estimated source Signal-to-Noise Ratio"
    )



