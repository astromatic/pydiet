"""Tests for photometric-system conversions."""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

import pytest
from astropy import units as u

from pydiet.server.photsys import PhotSys, ab_spectrum, vega_spectrum


@pytest.mark.parametrize(
    ("identifier", "value", "expected"),
    [
        ("abmag", 20.0, 1e-8),
        ("vegamag", 40.0, 1e-16),
        ("fmegajy", 2.0, 550.8),
        ("fmujy", 2.0, 5.508e-10),
        ("photons", 2.0, 2.0),
    ],
)
def test_photometric_system_rates(identifier, value, expected):
    # Verify representative conversion rates for every photometric system.
    system = PhotSys(identifier)
    assert system.photon_rate(value) == pytest.approx(expected)
    assert (system.spectrum is ab_spectrum) if identifier in {
        "abmag", "fmegajy", "fmujy"
    } else True
    if identifier == "vegamag":
        assert system.spectrum is vega_spectrum


def test_rate_floors_and_flux_requirements():
    # Exercise numerical floors and mandatory flux-conversion wavelengths.
    assert PhotSys("photons").photon_rate(-1) == 1e-30
    assert PhotSys("fmegajy").photon_rate(-1) == pytest.approx(2.754e-28)
    assert PhotSys("fmujy").photon_rate(-1) == pytest.approx(2.754e-40)
    with pytest.raises(ValueError, match="wavelength is required"):
        PhotSys("flux")
    with pytest.raises(ValueError, match="dwavelength is required"):
        PhotSys("flux", wavelength=500 * u.nm)

    system = PhotSys("flux", 500 * u.nm, 100 * u.nm)
    assert system.photon_rate(2.0) == pytest.approx(4.5904e-10)
    zero_width = PhotSys("flux", 500 * u.nm, 0 * u.nm)
    assert zero_width.photon_rate(0) > 0
