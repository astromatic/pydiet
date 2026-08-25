"""Tests for enhanced string annotations."""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from typing import Annotated

import pytest
from pydantic import BaseModel, ValidationError
from pydantic_settings import BaseSettings

from pydiet.server.types.string import AnnotatedStr, StrAnnotation


def test_string_annotation_constraints_and_serialization():
    # Exercise each direct string constraint and the identity serializer.
    annotation = StrAnnotation(
        min_length=2, max_length=4, pattern=r"[A-Z]+$", valid_list=["AB", "XYZ"]
    )
    assert annotation.validate("AB") == "AB"
    assert annotation.serialize("AB") == "AB"

    for value, message in [
        (1, "not a string"),
        ("A", "at least 2"),
        ("ABCDE", "at most 4"),
        ("Ab", "match"),
        ("CD", "any of"),
    ]:
        with pytest.raises(ValueError, match=message):
            annotation.validate(value)  # type: ignore[arg-type]


def test_string_annotation_with_pydantic_python_and_json():
    # Verify the annotation works through Pydantic's Python and JSON paths.
    class Code(BaseModel):
        value: Annotated[str, StrAnnotation(pattern=r"[A-Z]{2}")]

    code = Code(value="AB")
    assert code.model_dump() == {"value": "AB"}
    assert Code.model_validate_json('{"value":"CD"}').value == "CD"
    with pytest.raises(ValidationError):
        Code(value="bad")


def test_annotated_string_defaults_schema_and_validation():
    # Check pseudo-field defaults, schema metadata, and invalid input handling.
    class Settings(BaseSettings):
        code: AnnotatedStr(
            default="AB", short="c", description="Code", min_length=2,
            max_length=3, pattern=r"[A-Z]+$", valid_list=["AB", "XYZ"]
        )

    assert Settings().code == "AB"
    schema = Settings.model_json_schema()["properties"]["code"]
    assert schema["description"] == "Code"
    assert schema["short"] == "c"
    assert schema["valid_list"] == ["AB", "XYZ"]
    with pytest.raises(ValidationError):
        Settings(code="NOPE")
