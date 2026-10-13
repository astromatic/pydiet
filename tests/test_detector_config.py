"""Tests for configured detector saturation limits."""

from astropy import units as u
from pydantic import ValidationError
import pytest

from pydiet.server.datafiles import get_data_config, get_detector
from pydiet.server.models.dataconfig import DetectorConfigModel
from pydiet.server.models.instrument import DetectorModel
from pydiet.server.models.query import ETCQueryModel
from pydiet.server.response import get_response
from pydiet.server import response as response_module


@pytest.fixture
def detector_values():
    return {
        "gain": "2 electron/adu",
        "ron": "4 electron",
        "scale": "[0.3, 0.3] arcsec/pix",
        "full_well": "100000 electron",
        "range": "65536 adu",
        "bias": "1200 adu",
    }


@pytest.mark.parametrize("model", [DetectorConfigModel, DetectorModel])
@pytest.mark.parametrize("field,value", [
    ("full_well", "0 electron"),
    ("full_well", "-1 electron"),
    ("full_well", "1 adu"),
    ("range", "1 adu"),
    ("range", "65536 electron"),
    ("bias", "-1 adu"),
    ("bias", "1 electron"),
])
def test_detector_rejects_invalid_saturation_quantities(model, field, value, detector_values):
    # Reject incompatible units and capacities outside the physical bounds.
    values = detector_values | {field: value}
    if model is DetectorConfigModel:
        values.update(path="detector", transmission={}, emission={})
    else:
        values.update(transmissions={}, emissions={})
    with pytest.raises(ValidationError) as error:
        model(**values)
    assert error.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize("model", [DetectorConfigModel, DetectorModel])
def test_detector_saturation_defaults_preserve_existing_configurations(model, detector_values):
    # Older detector definitions retain the image model's original saturation limits.
    for field in ("full_well", "range", "bias"):
        detector_values.pop(field)
    if model is DetectorConfigModel:
        detector_values.update(path="detector", transmission={}, emission={})
    else:
        detector_values.update(transmissions={}, emissions={})
    detector = model(**detector_values)
    assert detector.full_well == 1e6 * u.electron
    assert detector.range == 65536 * u.adu
    assert detector.bias == 0 * u.adu


def test_detector_loader_preserves_toml_saturation_limits():
    # Read the bundled TOML and retain the detector limits through spectral loading.
    config = get_data_config()
    instrument = config.instruments[0]
    detector = get_detector(str(config.path / instrument.path), instrument.detector)
    assert detector.full_well == 240000 * u.electron
    assert detector.range == 65536 * u.adu
    assert detector.bias == 1200 * u.adu
    assert detector.model_dump(mode="json")["bias"] == {"value": 1200.0, "unit": "adu"}


@pytest.mark.parametrize("full_well,digital_range,bias,threshold", [
    (1000, 65536, 0, 500),
    (100000, 1001, 200, 800),
])
def test_configured_detector_limits_control_saturation_times(
        monkeypatch, full_well, digital_range, bias, threshold):
    # Verify both full-well-limited and digital-headroom-limited ETC predictions.
    query = ETCQueryModel(compute="snr", etime=1.0)
    instrument = response_module.instruments[query.instrument]
    detector = instrument.detector.model_copy(update={
        "gain": 2 * u.electron / u.adu,
        "full_well": full_well * u.electron,
        "range": digital_range * u.adu,
        "bias": bias * u.adu,
    })
    monkeypatch.setitem(
        response_module.instruments, query.instrument,
        instrument.model_copy(update={"detector": detector})
    )
    result = get_response(query)
    assert result.etime_skysat == pytest.approx(threshold / result.bkg_rate)
    assert 0 < result.etime_sourcesat <= result.etime_skysat
