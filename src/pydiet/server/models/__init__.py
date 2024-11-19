"""
Data models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from .exceptions import ETCValidationError
from .query import ETCQueryModel
from .response import ETCResponseModel
from .instrument import FilterModel, InstrumentModel, ResponseModel, SkyModel

