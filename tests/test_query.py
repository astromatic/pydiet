"""Tests for instrument-dependent query validation."""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from pydiet.server.models.default import default_instrument
from pydiet.server.models.query import ETCQueryModel
from pydiet.server.models import query as query_module
from pydiet.server.models.exceptions import ETCValidationError


def test_unknown_filter_and_mirror_report_enum_errors():
    # Unknown enum IDs fail Pydantic validation before custom validators run.
    with pytest.raises(ValidationError) as filter_error:
        ETCQueryModel(instrument=default_instrument.id, filter="missing")
    assert filter_error.value.errors()[0]["type"] == "enum"
    assert filter_error.value.errors()[0]["loc"] == ("filter",)
    assert filter_error.value.errors()[0]["input"] == "missing"

    with pytest.raises(ValidationError) as mirror_error:
        ETCQueryModel(instrument=default_instrument.id, mirror="missing")
    assert mirror_error.value.errors()[0]["type"] == "enum"
    assert mirror_error.value.errors()[0]["loc"] == ("mirror",)
    assert mirror_error.value.errors()[0]["input"] == "missing"


@pytest.mark.parametrize("field", ["filter", "mirror"])
def test_instrument_unavailable_ids_report_custom_errors(field, monkeypatch):
    # Valid enum IDs reach the instrument-specific validator and its payload.
    selected_id = getattr(ETCQueryModel(), field)
    instrument = SimpleNamespace(
        filters=SimpleNamespace(transmissions={"other": None}),
        telescope=SimpleNamespace(transmissions={"other": None}),
    )
    monkeypatch.setitem(query_module.instruments, default_instrument.id, instrument)

    with pytest.raises(ETCValidationError) as error:
        ETCQueryModel(instrument=default_instrument.id, **{field: selected_id})

    assert error.value.args[0] == {
        "type": "enum",
        "loc": ("query", field),
        "input": selected_id,
        "expected": "'other' or 'upload'" if field == "filter" else "'other'",
    }
