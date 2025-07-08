"""
Gather data.
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence
from astropy import units as u #type: ignore[import-untyped]
from synphot import ConstFlux1D, SourceSpectrum #type: ignore[import-untyped]

from .datafiles import (
    get_data_config,
    get_default,
    get_instruments,
    get_webapi_instruments,
)

data_config = get_data_config()

instruments = get_instruments(data_config)
default_instrument = get_default(instruments)
winstruments = get_webapi_instruments(instruments)

filters = {k:v for key,val in instruments.items() for k,v in val.filters.items()}
default_filter = get_default(default_instrument.filters)

# Load reference spectra
ab_spectrum = SourceSpectrum(ConstFlux1D, amplitude = 0.*u.ABmag)
st_spectrum = SourceSpectrum(ConstFlux1D, amplitude = 0.*u.STmag)
vega_spectrum = SourceSpectrum.from_vega()

