"""Tests for instrument obstruction-area overrides and telescope defaults."""

from astropy import units as u
from pydantic import ValidationError
import pytest

from pydiet.server.datafiles import get_data_config, get_instruments
from pydiet.server.models.dataconfig import DataConfigModel, InstrumentConfigModel
from pydiet.server.models.query import ETCQueryModel
from pydiet.server import response as response_module


@pytest.mark.parametrize("value", ["omitted", None, "0.5 m2"])
def test_instrument_obstruction_fallback_and_override(value, monkeypatch):
    # Inherited areas produce the same derived quantities and results as explicit areas.
    values = get_data_config().model_dump()
    instrument = values["instruments"][0]
    values["telescopes"].append(values["telescopes"][0] | {
        "id": "other", "obstruction_area": "1.25 m2"
    })
    instrument["telescope_id"] = "other"
    if value == "omitted":
        instrument.pop("obstruction_area")
    else:
        instrument["obstruction_area"] = value
    config = DataConfigModel.model_validate(values)
    expected = 0.5 * u.m**2 if value == "0.5 m2" else next(
        telescope.obstruction_area for telescope in config.telescopes
        if telescope.id == config.instruments[0].telescope_id
    )
    loaded = get_instruments(config)
    assert loaded[instrument["id"]].obstruction_area == expected
    monkeypatch.setattr(response_module, "instruments", loaded)
    query = ETCQueryModel(instrument=instrument["id"])
    result = response_module.get_response(query)

    config.instruments[0].obstruction_area = expected
    explicit = get_instruments(config)
    assert loaded[instrument["id"]].cache.zp_abmags == explicit[instrument["id"]].cache.zp_abmags
    monkeypatch.setattr(response_module, "instruments", explicit)
    assert response_module.get_response(query).model_dump() == result.model_dump()


@pytest.mark.parametrize("area", ["-1 m2", "0 m2", "1 m"])
def test_instrument_obstruction_override_requires_positive_area(area):
    # Nullable overrides retain physical-unit and positive-area validation.
    values = get_data_config().instruments[0].model_dump()
    values["obstruction_area"] = area
    with pytest.raises(ValidationError) as error:
        InstrumentConfigModel.model_validate(values)
    assert error.value.errors()[0]["loc"] == ("obstruction_area",)
