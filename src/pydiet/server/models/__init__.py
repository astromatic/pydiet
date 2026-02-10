"""
Data models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from .dataconfig import (
    DataConfigModel,
    DetectorConfigModel,
    EmissionConfigModel,
    FileConfigModel,
    FiltersConfigModel,
    InstrumentConfigModel,
    OpticsConfigModel,
    SiteConfigModel,
    TelescopeConfigModel,
    TransmissionConfigModel
)
from .exceptions import ETCValidationError
from .query import ETCQueryModel
from .response import ETCResponseModel
from .instrument import (
    DetectorModel,
    FiltersModel,
    InstrumentModel,
    OpticsModel,
    SBSEDModel,
    SEDModel,
    SiteModel,
    TelescopeModel,
    TransmissionModel,
    spectral_to_arrays
)

