"""
Data models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from typing import Annotated, Dict

from astropy import units as u  #type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict

from ... import package
from ..types import AnnotatedQuantity


class ResponseModel(BaseModel):
    '''
    Pydantic model for an instrumental response curve as a function of wavelength.
    '''
    wave: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "nm",
        ge = 100. * u.nm,
        le = 100. * u.micron,
        min_shape = (2),
        max_shape = (20000),
        decimals = 3
    )
    response: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "",
        ge = -100.,
        le = 100.,
        min_shape = (2),
        max_shape = (20000),
        decimals = 4
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )



class SEDModel(BaseModel):
    wave: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "nm",
        ge = 100. * u.nm,
        le = 100. * u.micron,
        min_shape = (2),
        max_shape = (20000),
        decimals = 4
    )
    sed:  AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "W / (m2 Hz)",
        ge = 0. * u.Watt / u.m**2 / u.Hz,
        min_shape = (2),
        max_shape = (20000),
        decimals = 6
    )



class TransmissionModel(BaseModel):
    id: str
    name: str
    description: str
    response: 'ResponseModel'
    default: bool = False



class FilterModel(TransmissionModel):
    pass



class DetectorModel(TransmissionModel):
    pass



class SkyModel(BaseModel):
    id: str
    name: str
    description: str
    sed: SEDModel



class InstrumentModel(BaseModel):
    '''
    Pydantic model for a PyDIET instrument.
    '''
    id: str
    name: str
    description: str
    filters: Dict[str, 'FilterModel']
    #optics: FilterModel
    #atmosphere: FilterModel
    #background: SkyModel
    default: bool = False





