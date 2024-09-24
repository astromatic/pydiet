"""
Data models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from typing import Annotated, Dict

from astropy import units as u  #type: ignore[import-untyped]
import numpy as np
from pydantic import BaseModel, BeforeValidator, ConfigDict, PlainSerializer

from ... import package
from ..config import settings
from ..config.quantity import QuantityAnnotation


# Rough "pydantification" of Numpy array datatype
def nd_array_custom_before_validator(x):
    # custome before validation logic
    return x


def nd_array_custom_serializer(x):
    # custome serialization logic
    return str(x)

NdArray = Annotated[
    np.ndarray,
    BeforeValidator(nd_array_custom_before_validator),
    PlainSerializer(nd_array_custom_serializer, return_type=str)
]



class InstrumentModel(BaseModel):
    id: str
    name: str
    description: str
    filters: Dict[str, 'FilterModel']
    #sky: SkyModel



class FilterModel(BaseModel):
    id: str
    name: str
    description: str
    #response: ResponseModel



class ResponseModel(BaseModel):
    wave: Annotated[
        u.Quantity,
        QuantityAnnotation(
            "micron",
            ge = 100. * u.nm,
            le = 100. * u.micron,
            min_shape = (2),
            max_shape = (20000)
        )
    ]
    response: NdArray

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )



class SEDModel(BaseModel):
    wave: Annotated[
        u.Quantity,
        QuantityAnnotation(
            "micron",
            ge = 100. * u.nm,
            le = 100. * u.micron,
            min_shape = (2),
            max_shape = (20000)
        )
    ]
    sed:  Annotated[
        u.Quantity,
        QuantityAnnotation(
            "W/m**2/Hz",
            ge = 0. * u.Watt / u.m**2 / u.Hz,
            min_shape = (2),
            max_shape = (20000)
        )
    ]



class SkyModel(BaseModel):
    id: str
    name: str
    description: str
    sed: SEDModel



