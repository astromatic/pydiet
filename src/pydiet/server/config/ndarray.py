"""
Provide a roughly pydantified Numpy array datatype
"""
# Copyright UParisSaclay/CEA/CFHT/CNRS
# Licensed under the MIT licence

from typing import Annotated

import numpy as np
from pydantic import BeforeValidator, PlainSerializer

# Rough "pydantification" of Numpy array datatype
def nd_array_custom_before_validator(x):
    # custome before validation logic
    return x


def nd_array_custom_serializer(x):
    # custome serialization logic
    return str(x)


NdArray = Annotated[
    np.ndarray,
    BeforeValidator(nd_array_custom_before_validator),
    PlainSerializer(nd_array_custom_serializer, return_type=str)
]


