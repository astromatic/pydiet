"""Tests for instrument-dependent query validation."""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

import pytest
from pydantic import ValidationError

from pydiet.server.models.default import default_instrument
from pydiet.server.models.query import ETCQueryModel


def test_invalid_filter_and_mirror_report_enum_errors():
    # Ensure instrument-dependent identifiers produce structured enum errors.
    with pytest.raises(ValidationError) as filter_error:
        ETCQueryModel(instrument=default_instrument.id, filter="missing")
    assert filter_error.value.errors()[0]["type"] == "enum"

    with pytest.raises(ValidationError) as mirror_error:
        ETCQueryModel(instrument=default_instrument.id, mirror="missing")
    assert mirror_error.value.errors()[0]["type"] == "enum"
