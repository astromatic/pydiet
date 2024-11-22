"""
Functions that gather data.
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence
from os import scandir
from os.path import basename, exists, join
from typing import Any, Optional
from astropy.table import QTable #type: ignore[import-untyped]
from astropy import units as u  #type: ignore[import-untyped]
from pydantic import BaseModel, Field

from ... import package
from ..config import override, settings
from .instrument import FilterModel, InstrumentModel, ResponseModel


def get_data(filename: str):
    return QTable.read(filename)


def get_default(d: dict) -> Any:
    lst = [val for val in d.values() if val.default]
    return lst[0] if len(lst) > 0 else list(d.values())[0]


def get_dirs(parent_dir: str) -> list[str]:
    return [d.path for d in scandir(parent_dir) if d.is_dir()]


def get_description(parent_dir: str, default: str):
    try:
        f = open(join(parent_dir, "description.txt"))
    except FileNotFoundError:
        description=default
    else:
        with f:
            description="".join(f.read().splitlines())
    return description


def get_filters(instrument_dir: str) -> dict:
    filters = {}
    for filter_name in get_dirs(join(instrument_dir, "filters")):
        # Get the name alone
        filter_basename = basename(filter_name)
        # Get the ID
        filter_id = filter_basename.lower()
        data = get_data(join(filter_name, filter_basename + ".fits"))
        # Instantiate the model
        filters[filter_id] = FilterModel(
            id = filter_id,
            name = filter_basename,
            description = get_description(filter_name, "Another filter"),
            response = ResponseModel(
            	wave = data['wavelength'],
                response = data['transmission']
            )
        )
    return filters


def get_instruments(data_dir: Optional[str] = None) -> dict:
    data_dir = override("data_dir", data_dir)
    instruments = {}
    for instrument_name in get_dirs(data_dir): #type: ignore[arg-type]
        # Get the name alone
        instrument_basename = basename(instrument_name)
        # Get the ID
        instrument_id = instrument_basename.lower()
        # Instantiate the model
        instruments[instrument_id] = InstrumentModel(
            id = instrument_id,
            name = instrument_basename,
            description = get_description(instrument_name, "Another instrument."),
            filters = get_filters(instrument_name),
            default = is_default(instrument_name)
        )
    return instruments


def is_default(parent_dir):
    return exists(join(parent_dir, "default"))


instruments = get_instruments()
default_instrument = get_default(instruments)
filters = {k:v for key,val in instruments.items() for k,v in val.filters.items()}
default_filter = get_default(default_instrument.filters)

