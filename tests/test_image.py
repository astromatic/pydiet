"""Tests for image simulation and signal-to-noise calculations."""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

import base64

import numpy as np
import pytest
from astropy import units as u

from pydiet.server.image import Image


def make_image(**kwargs):
    options = {
        "image_size": (16, 16),
        "pixel_scale": (0.2, 0.2) * u.arcsec / u.pix,
        "rate": 20.0,
        "bkg_rate": 3.0,
        "ron": 2.0,
        "gain": 2.0,
        "max_etime": 123 * u.s,
    }
    options.update(kwargs)
    return Image(**options)


@pytest.mark.parametrize(
    "photometry", ["model_fitting", "fixed_aperture", "large_aperture", "optimal_aperture"]
)
def test_point_source_photometry_modes(photometry):
    # Compare the supported point-source photometry calculation paths.
    image = make_image(photometry=photometry)
    assert image.image.sum() == pytest.approx(1.0)
    assert image.snr(2.0) > 0
    assert image.delta_snr2(2.0, image.snr(2.0)) == pytest.approx(0.0)
    if photometry != "optimal_aperture":
        assert image.etime(image.snr(2.0)) == pytest.approx(2.0, abs=1e-5)


def test_galaxy_extended_and_saturation_paths():
    # Cover galaxy/extended profiles and finite or fallback saturation times.
    galaxy = make_image(source="galaxy", sersic_index=0.2)
    assert galaxy.image.sum() == pytest.approx(1.0)
    extended = make_image(source="extended")
    assert extended.snr(2.0) > 0
    assert extended.etime_bkg_sat() == pytest.approx(extended.saturation / 3.0)
    assert extended.etime_source_sat() == pytest.approx(
        extended.saturation / extended.max()
    )
    assert extended.max() > extended.bkg_rate

    no_signal = make_image(rate=0.0, bkg_rate=0.0)
    assert no_signal.etime(10) == 123
    assert no_signal.etime_bkg_sat() == 123
    assert no_signal.etime_source_sat() == 123

    source_only = make_image(rate=20.0, bkg_rate=0.0)
    assert source_only.etime_source_sat() == pytest.approx(
        source_only.saturation / source_only.max()
    )


def test_invalid_psf_and_gif_output():
    # Reject an invalid Moffat profile and validate generated GIF data URLs.
    with pytest.raises(ValueError, match="Moffat beta"):
        make_image(psf_beta=1.0)
    with pytest.raises(ValueError, match="unsupported photometry"):
        make_image(photometry="unknown")
    image = make_image(image_size=(8, 8))
    data_url = image.gif(0.1, exposures=2, frames=2)
    prefix, encoded = data_url.split(",", 1)
    assert prefix == "data:image/gif;base64"
    assert base64.b64decode(encoded).startswith(b"GIF")


def test_aperture_snr_formula():
    # Check aperture SNR against a small manually computable input.
    image = make_image()
    obj = np.array([0.25, 0.75])
    variance = np.array([1.0, 4.0])
    aperture = np.array([True, False])
    assert image.snr_aper(8.0, obj, variance, aperture) == pytest.approx(2.0)
