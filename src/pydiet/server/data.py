"""
Data management module
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence
from glob import glob
from os import scandir
from typing import Optional
from astropy.io import ascii
from astropy import units as u  #type: ignore[import-untyped]
from pydantic import BaseModel, Field

from .. import package
from config import override, settings
from config.quantity import QuantityAnnotation

def nd_array_custom_before_validator(x):
    # custome before validation logic
    return x


def nd_array_custom_serializer(x):
    # custome serialization logic
    return str(x)

NdArray = Annotated[
    np.ndarray,
    BeforeValidator(nd_array_custom_before_validator),
    PlainSerializer(nd_array_custom_serializer, return_type=str),
]



class FilterModel(BaseModel):
    id: str
    name: str
    description: str
    response: ResponseModel



class InstrumentModel(BaseModel):
    id: str
    name: str
    description: str
    filters: list[FilterModel]
    sky: SkyModel



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


def get_dirs(parent_dir: str) ->list[str]:
    return [d.path for d in os.scandir(parent_dir) if d.is_dir()]


def get_data(filename: str):
    return ascii.read(filename)

def get_description(filename: str):
    with open(filename as f):
        s = f.read()
    return s


def get_filters_from_path(instrument_dir: str) -> list[InstrumentModel]:
    filters = []
    for filter_name in get_dirs(instrument_dir):
        data = get_data(path.join(filter_name, "data.txt"))
        filters.append(
            FilterModel(
                id = filter_name.tolower(),
                name = filter_name,
                description = get_description(
                    path.join(filter_name, "description.txt")
                ),
                response = ResponseModel(
                    wave = data["col1"] * u.angstroem,
                    response = data["col2"]
                )
        )


def get_instruments_from_path(
		data_dir: Optional[str] = None
		) -> list[InstrumentModel]:
	data_dir = override("data_dir", data_dir)
   	instruments = []
    for instrument_name in get_dirs(data_dir):
            filter_names = get_dirs(instrument_names)
	        instruments.append(
                InstrumentModel(
                    id=instrument_name.tolower(),
                    name=instrument_name,
                    
                    
	            )
	return [d.name for d in scandir(dir) if d.is_dir() ]


