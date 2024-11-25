"""
Data models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from typing import Annotated, Dict

from astropy import units as u  #type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict

from ... import package
from ..types.quantity import QuantityAnnotation


class InstrumentModel(BaseModel):
    id: str
    name: str
    description: str
    filters: Dict[str, 'FilterModel']
    #sky: SkyModel
    default: bool = False



class FilterModel(BaseModel):
    id: str
    name: str
    description: str
    response: 'ResponseModel'
    default: bool = False



class ResponseModel(BaseModel):
    wave: Annotated[
        u.Quantity,
        QuantityAnnotation(
            "nm",
            ge = 100. * u.nm,
            le = 100. * u.micron,
            min_shape = (2),
            max_shape = (20000),
            decimals = 3
        )
    ]
    response: Annotated[
        u.Quantity,
        QuantityAnnotation(
            "",
            ge = -100.,
            le = 100.,
            min_shape = (2),
            max_shape = (20000),
            decimals = 4
        )
    ]

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



