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
from .instrument import (
    DetectorModel,
    FilterModel,
    InstrumentModel,
    SBSEDModel,
    SEDModel,
    SiteModel
)


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


def get_detector(instrument_dir: str) -> DetectorModel:
    qes = {}
    for qe_name in get_dirs(join(instrument_dir, "detector", "qes")):
        # Get the name alone
        qe_basename = basename(qe_name)
        # Get the ID
        qe_id = qe_basename.lower()
        data = get_data(join(qe_name, qe_basename + ".fits"))
        # Instantiate the model
        qes[qe_id] = FilterModel(
            id = qe_id,
            name = qe_basename,
            description = get_description(qe_name, "A Quantum Efficiency curve"),
            wave = u.Quantity(data['wavelength']),
            response = u.Quantity(data['transmission'])
        )
    return DetectorModel(
        gain = 1.5 * u.electron / u.adu,
        ron = 5. * u.electron,
        pixel = [0.186, 0.186] * u.arcsec**2,
        qes = qes
    )


def get_filters(parent_dir: str, subdir: str="filters") -> dict:
    filters = {}
    for filter_name in get_dirs(join(parent_dir, subdir)):
        # Get the name alone
        filter_basename = basename(filter_name)
        # Get the ID
        filter_id = filter_basename.lower()
        data = get_data(join(filter_name, filter_basename + ".fits"))
        # Instantiate the model
        filters[filter_id] = FilterModel(
            id = filter_id,
            name = filter_basename,
            description = get_description(filter_name, "A filter"),
            wave = u.Quantity(data['wavelength']),
            response = u.Quantity(data['transmission'])
        )
    return filters


def get_seds(parent_dir: str, subdir: str="seds") -> dict:
    seds = {}
    for sed_name in get_dirs(join(parent_dir, subdir)):
        # Get the name alone
        sed_basename = basename(sed_name)
        # Get the ID
        sed_id = sed_basename.lower()
        data = get_data(join(sed_name, sed_basename + ".fits"))
        # Instantiate the model
        seds[sed_id] = SEDModel(
            id = sed_id,
            name = sed_basename,
            description = get_description(
                sed_name,
                "A spectral energy distribution"
            ),
            wave = u.Quantity(data['wavelength']),
            sed = u.Quantity(data['spectral flux density'])
        )
    return seds


def get_sbseds(parent_dir: str, subdir: str="seds") -> dict:
    sbseds = {}
    for sbsed_name in get_dirs(join(parent_dir, subdir)):
        # Get the name alone
        sbsed_basename = basename(sbsed_name)
        # Get the ID
        sbsed_id = sbsed_basename.lower()
        data = get_data(join(sbsed_name, sbsed_basename + ".fits"))
        # Instantiate the model
        sbseds[sbsed_id] = SBSEDModel(
            id = sbsed_id,
            name = sbsed_basename,
            description = get_description(
                sbsed_name,
                "A surface brightness spectral energy distribution"
            ),
            wave = u.Quantity(data['wavelength']),
            sbsed = u.Quantity(data['surface brightness'])
        )
    return sbseds


def get_instruments(data_dir: Optional[str] = None) -> dict:
    data_dir = override("data_dir", data_dir)
    assert data_dir is not None     # make mypy happy
    instrument_dir = join(data_dir, "instruments")
    instruments = {}
    for instrument_name in get_dirs(instrument_dir): #type: ignore[arg-type]
        # Get the name alone
        instrument_basename = basename(instrument_name)
        # Get the ID
        instrument_id = instrument_basename.lower()
        # Instantiate the model
        instruments[instrument_id] = InstrumentModel(
            id = instrument_id,
            name = instrument_basename,
            description = get_description(instrument_name, "An instrument."),
            filters = get_filters(instrument_name),
            optics = get_filters(join(instrument_name, "optics"), "transmission"),
            detector = get_detector(instrument_name),
            telescope = 'cfht',
            site = 'mko',
            default = is_default(instrument_name)
        )
    return instruments


def get_sites(data_dir: Optional[str] = None) -> dict:
    data_dir = override("data_dir", data_dir)
    assert data_dir is not None     # make mypy happy
    site_dir = join(data_dir, "sites")
    sites = {}
    for site_name in get_dirs(site_dir): #type: ignore[arg-type]
        # Get the name alone
        site_basename = basename(site_name)
        # Get the ID
        site_id = site_basename.lower()
        # Instantiate the model
        sites[site_id] = SiteModel(
            id = site_id,
            name = site_basename,
            description = get_description(site_name, "An observation site."),
            sky_transmissions = get_filters(site_name, "transmission"),
            sky_emissions = get_sbseds(site_name, "emission"),
            default = is_default(site_name)
        )
    return sites


def is_default(parent_dir):
    return exists(join(parent_dir, "default"))


sites = get_sites()
default_site = get_default(sites)
instruments = get_instruments()
default_instrument = get_default(instruments)
filters = {k:v for key,val in instruments.items() for k,v in val.filters.items()}
default_filter = get_default(default_instrument.filters)

