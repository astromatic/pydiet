"""
Gather data and prepare assets.
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from .datafiles import (
    get_data_config,
    get_default,
    get_instruments,
    get_webapi_instruments
)


# Data configuration model
data_config = get_data_config()

# Instrument models
instruments = get_instruments(data_config)
default_instrument = get_default(instruments)

# Get version of the instrument models trimmed for serving by the webAPI.
winstruments = get_webapi_instruments(instruments)

# Collect filters from all instruments
filters = {k:v for key,val in instruments.items() for k,v in val.filters.transmissions.items()}
default_filter = get_default(default_instrument.filters.transmissions)

# Collect mirror conditions from telescopes of all instruments
mirrors = {k:v for key,val in instruments.items() for k,v in val.telescope.transmissions.items()}
default_mirror = get_default(default_instrument.telescope.transmissions)


