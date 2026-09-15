"""Integration tests for ETC response computation."""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from types import SimpleNamespace

import pytest

from pydiet.server.models.query import ETCQueryModel
from pydiet.server.models.instrument import TransmissionModel
from pydiet.server.response import get_response, spectrum_from_airmass


def test_spectrum_airmass_interpolation_and_filtering():
    # Exercise interpolation, filtering, endpoints, and empty model selection.
    models = {
        "low": SimpleNamespace(vars={"am": 1.0, "sky": "dark"}, spectral=10.0),
        "high": SimpleNamespace(vars={"am": 2.0, "sky": "dark"}, spectral=20.0),
        "other": SimpleNamespace(vars={"am": 1.0, "sky": "bright"}, spectral=99.0),
    }
    assert spectrum_from_airmass(models, 1.5, {"sky": "dark"}) == 15.0
    assert spectrum_from_airmass(models, 0.5, {"sky": "dark"}) == 5.0
    assert spectrum_from_airmass(models, 0.0, {"sky": "dark"}) == 0.0
    assert spectrum_from_airmass(models, -1.0, {"sky": "dark"}) == 0.0
    assert spectrum_from_airmass(models, 1.0, {"sky": "dark"}) == 10.0
    assert spectrum_from_airmass(models, 3.0, {"sky": "dark"}) == 20.0
    assert spectrum_from_airmass(models, 2.0, {"sky": "dark"}) == 20.0
    with pytest.raises(IndexError):
        spectrum_from_airmass(models, extra={"sky": "missing"})


def test_default_etime_response():
    # Run the default end-to-end exposure-time calculation.
    result = get_response(ETCQueryModel())
    assert result.compute == "etime"
    assert result.etime > 0
    assert result.snr == pytest.approx(10.0)
    assert result.cutout is None


@pytest.mark.parametrize("variables", [None, {"am": 1.0}])
def test_spectrum_airmass_requires_initialized_models(variables):
    # Reject missing metadata or spectra before attempting interpolation.
    model = TransmissionModel(id="incomplete", name="Incomplete", vars=variables)
    with pytest.raises(AssertionError):
        spectrum_from_airmass({"incomplete": model})


def test_snr_response_with_direct_sky_photons():
    # Compute SNR using direct photon units and median stacking.
    query = ETCQueryModel(
        compute="snr", etime=2.0, exposures=4, stacking="median",
        sky="specify", sky_unit="photons", sky_brightness=3.0,
        unit="photons",
    )
    result = get_response(query)
    assert result.compute == "snr"
    assert result.etime == 2.0
    assert result.snr > 0
    assert result.ttime > result.etime * query.exposures


def test_specified_ab_sky_response():
    # Exercise reference-spectrum source and specified sky conversions.
    result = get_response(ETCQueryModel(
        compute="snr", etime=1.0, sky="specify", sky_unit="fmegajy",
        sky_brightness=1.0, unit="vegamag",
    ))
    assert result.snr > 0
    assert result.bkg_rate > 0
