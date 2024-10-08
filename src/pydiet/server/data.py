"""
Data management module
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence
from os import scandir
from os.path import basename, join
from typing import Optional
from astropy.io import ascii
from astropy import units as u  #type: ignore[import-untyped]
from pydantic import BaseModel, Field

from .. import package
from .config import override, settings
from .models.instrument import InstrumentModel, ResponseModel


def get_dirs(parent_dir: str) ->list[str]:
    return [d.path for d in scandir(parent_dir) if d.is_dir()]


def get_data(filename: str):
    return ascii.read(filename)


def get_description(parent_dir: str, default: str):
    try:
        f = open(join(parent_dir, "description.txt"))
    except FileNotFoundError:
        description=defaut
    else:
        with f:
            description=f.readlines()
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
            description = get_description(filter_name, "Another filter")
            response = ResponseModel(
            	wave = data['wavelength'],
                response = data['transmission']
            )
        )
    return filters


def get_instruments(data_dir: Optional[str] = None) -> dict:
    data_dir = override("data_dir", data_dir)
    instruments = {}
    for instrument_name in get_dirs(data_dir):
        # Get the name alone
        instrument_basename = basename(instrument_name)
        # Get the ID
        instrument_id = instrument_basename.lower()
        # Instantiate the model
        instruments[instrument_id] = InstrumentModel(
            id = instrument_id,
            name = instrument_basename,
            description = get_description(instrument_name, "Another instrument."),
            filters = get_filters(instrument_name)
        )
    return instruments


instruments = get_instruments()

