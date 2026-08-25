"""
Quantity module tests
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from typing import Annotated

from astropy import units as u
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import pytest

from pydiet.server.types import quantity

def test_QuantityAnnotation():
    """
    Test Quantity annotations
    """
    # Exercise valid and invalid scalar quantities through a Pydantic model.
    class Coordinates(BaseModel): 
        lat: Annotated[ 
            u.Quantity, quantity.QuantityAnnotation(
                "deg",
                ge=-90.*u.deg,
                le=90.*u.deg
            ) 
        ] 
        lon: Annotated[u.Quantity, quantity.QuantityAnnotation("deg")] 
        alt: Annotated[u.Quantity, quantity.QuantityAnnotation("km")] 
    # The following instantiation should validate 
    coord = Coordinates(lat="39.905 deg", lon="-75.166 deg", alt="12 m")
    assert coord
    assert coord.model_dump()
    assert coord.model_dump(mode="json")
    assert coord.model_dump_json()
    # The following instantiations should NOT validate 
    with pytest.raises(Exception):
        coord = Coordinates(lat="99.905 deg", lon="-75.166 deg", alt="12 m")
    with pytest.raises(Exception):
        coord = Coordinates(lat="-99.905 deg", lon="-75.166 deg", alt="12 m")
    with pytest.raises(Exception):
        coord = Coordinates(lat="-99.905 deg", lon="-75.166 deg", alt="12")
    with pytest.raises(Exception):
        coord = Coordinates(
        lat="[39.905, 38.2] deg",
        lon="-75.166 deg",
        alt="12 m"
    )
    # The following instantiation using dictionaries should validate
    assert Coordinates(
        lat={'value': 39.905, 'unit': "deg"},
        lon={'value': -75.166, 'unit': "deg"},
        alt={'value': 12., 'unit': "m"}
    )
    # The following instantiation using dictionaries should NOT validate
    with pytest.raises(Exception):
        coord = Coordinates(
            lat={'value': 39.905},
            lon={'value': -75.166, 'unit': "deg"},
            alt={'value': 12., 'unit': "m"}
        )


def test_QuantityAnnotation_dict_serialization():
    """Test JSON-safe dictionary serialization of quantity arrays."""
    # Ensure NumPy-backed values remain Python-safe and become JSON-safe lists.
    class Measurements(BaseModel):
        lengths: Annotated[
            u.Quantity,
            quantity.QuantityAnnotation(
                "m", min_shape=(1,), max_shape=(2,), ser_mode="dict"
            )
        ]

    measurements = Measurements(lengths="[1.25, 2.5] m")
    python_value = measurements.model_dump()["lengths"]["value"]
    assert python_value.tolist() == [1.25, 2.5]
    assert measurements.model_dump(mode="json") == {
        "lengths": {"value": [1.25, 2.5], "unit": "m"}
    }
    assert measurements.model_dump_json() == (
        '{"lengths":{"value":[1.25,2.5],"unit":"m"}}'
    )


def test_AnnotatedQuantity():
    """
    Test annotated quantity pseudo Pydantic-field
    """
    # Verify vector shape, unit, and range constraints on the pseudo-field.
    class Settings(BaseSettings): 
        size: quantity.AnnotatedQuantity( 
            short='S', 
            description="an arbitrary length", 
            default=10. * u.m,
            gt=1. * u.micron, 
            lt=1. * u.km,
            min_shape=(2,),
            max_shape=(2,)
        ) 
    # The following instantiation should validate 
    assert Settings(size="[3., 4.] cm")
    # The following instantiations should NOT validate 
    with pytest.raises(Exception):
        s = Settings(size="[3., 4.] deg")
    with pytest.raises(Exception):
        s = Settings(size="[0.001, 4.] mm")
    with pytest.raises(Exception):
        s = Settings(size="[3., 4.] au")
    with pytest.raises(Exception):
        s = Settings(size="3. cm")
    with pytest.raises(Exception):
        s = Settings(size="[3., 4., 5.] cm")


def test_quantity_annotation_edge_cases():
    # Cover permissive units, invalid types, and alternate serialization modes.
    permissive = quantity.QuantityAnnotation("m", strict=False)
    assert permissive.validate(2) == 2 * u.m
    with pytest.raises(ValueError, match="value.*unit"):
        permissive.validate({"unit": "m"})
    with pytest.raises(ValueError, match="unknown type"):
        quantity.QuantityAnnotation("m").validate(object())
    with pytest.raises(ValueError):
        quantity.QuantityAnnotation("m").validate("2 s")

    string_mode = quantity.QuantityAnnotation("m", decimals=1, ser_mode="str")
    assert string_mode.serialize(1.26 * u.m) == "1.3 m"
    assert quantity.QuantityAnnotation("m").serialize(2 * u.m) == 2 * u.m
    with pytest.raises(ValueError):
        quantity.AnnotatedQuantity()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("2 m", 2 * u.m),
        ("1, 2, 3 m", [1, 2, 3] * u.m),
        ("[[1, 2], [3, 4]] m", [[1, 2], [3, 4]] * u.m),
        ("[1, 2; 3, 4] m", [[1, 2], [3, 4]] * u.m),
    ],
)
def test_quantity_string_parser_shapes(text, expected):
    # Parse representative scalar, vector, nested, and row-separated inputs.
    parsed = quantity.str_to_quantity_array(text)
    assert u.allclose(parsed, expected)


@pytest.mark.parametrize(
    "value", [None, "", "[] m", "[1, 2 m", "[1, 2]] m", "[1, bad] m", "1 mystery"]
)
def test_quantity_string_parser_rejects_malformed_values(value):
    # Confirm malformed or unsupported inputs fail cleanly with None.
    assert quantity.str_to_quantity_array(value) is None
