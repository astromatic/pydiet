"""
Response models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from typing import Optional

from astropy import units as u #type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, Field, Json

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
        description="Estimated total photometric zero-point per second in magAB"
    )

    zp_instru: float=Field(
        default=0.,
        ge=-100.,
        le=100.,
        description="Estimated instrumental photometric zero-point per second in magAB"
    )

    snr: float=Field(
        default=10.,
        ge=0.,
        lt=1e30,
        description="Estimated source Signal-to-Noise Ratio"
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

    ttime: float=Field(
        default=1.,
        ge=0.,
        lt=1e30,
        description="Estimated total time"
    )

    bkg_mag: float=Field(
        default=99.,
        ge=-100.,
        le=100.,
        description="Estimated sky background in magAB/arcsec2"
    )

    bkg_rate: float=Field(
        default=99.,
        ge=0.,
        le=1e30,
        description="Estimated sky background in photons/pixel"
    )

    lambda_pivot: float=Field(
        default=0.,
        ge=0.,
        lt=1e12,
        description="Pivot wavelength of the full transmission curve in nm"
    )

    bandwidth_rect: float=Field(
        default=0.,
        ge=0.,
        lt=1e12,
        description="Equivalent rectangular bandwidth of the full transmission curve in nm"
    )

    trans_peak: float=Field(
        default=1.,
        ge=0.,
        le=1.,
        description="Peak amplitude of the total transmission curve"
    )

    trans_peak_instru: float=Field(
        default=1.,
        ge=0.,
        le=1.,
        description="Peak amplitude of the instrumental transmission curve"
    )

    cutout: Optional[str]=Field(
        default=None,
        description="GIF animation of the source"
    )

    filter_transmission: Optional[Json] = None

    atmosphere_transmission: Optional[Json] = None

    model_config = ConfigDict(use_enum_values=True)

