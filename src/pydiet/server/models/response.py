"""
Response models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from typing import Optional

from astropy import units as u #type: ignore[import-untyped]
from pydantic import BaseModel, Field, Json

from ..types import AnnotatedQuantity
from .types import ComputeID, FilterID, InstrumentID
from .instrument import TransmissionModel


class ETCResponseModel(BaseModel):

    instrument: str

    filter: str

    compute: ComputeID

    zp: float=Field(
        default=0.,
        ge=-100.,
        le=100.,
        description="Estimate magnitude zero-point"
    )

    etime: float=Field(
        default=1.,
        ge=0.,
        lt=1e30,
        description="Estimated exposure time"
    )

    ttime: float=Field(
        default=1.,
        ge=0.,
        lt=1e30,
        description="Estimated total time"
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

    sky_mag: float=Field(
        default=99.,
        ge=-100.,
        le=100.,
        description="Estimated sky background in mag/arcsec2"
    )

    cutout: Optional[str]=Field(
        default=None,
        description="GIF animation of the source"
    )

    filter_transmission: Optional[Json] = None

    atmosphere_transmission: Optional[Json] = None


