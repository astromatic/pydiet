"""
Exceptions for model validation.
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

class ETCValidationError(Exception):
    """Report an ETC query value that is not valid for the selected instrument.

    Parameters
    ----------
    error: dict
        Error details using Pydantic's ``type``, ``loc``, ``input``, and
        context conventions.
    """
    pass
