"""
Photometric system conversion module
"""
# Copyright CFHT
# Licensed under the MIT licence

from typing import Optional

from astropy import units as u  #type: ignore[import-untyped]

from .models.types import PhotSysID

from .data import ab_spectrum, vega_spectrum


class PhotSys(object):
    def __init__(
            self,
            id: PhotSysID = 'abmag',
            wavelength: Optional[u.Quantity[u.nm]] =  None,
            dwavelength: Optional[u.Quantity[u.nm]] = None):

        self.eps = 1e-30
        self.id = id
        if id == 'abmag':
            self.spectrum = ab_spectrum
            self.photon_rate = self._rate_from_mag
        elif id == 'vegamag':
            self.spectrum = vega_spectrum
            self.photon_rate = self._rate_from_mag  #type: ignore[assignment]
        elif id == 'fmegajy':
            self.spectrum = ab_spectrum
            self.photon_rate = self._rate_from_fmegajy  #type: ignore[assignment]
        elif id == 'fmujy':
            self.spectrum = ab_spectrum
            self.photon_rate = self._rate_from_fmujy  #type: ignore[assignment]
        elif id == 'flux':
            self.spectrum = ab_spectrum
            self.photon_rate = self._rate_from_flux  #type: ignore[assignment]
            if wavelength is None:
                raise ValueError("wavelength is required when id == 'flux'")
            if dwavelength is None:
                raise ValueError("dwavelength is required when id == 'flux'")
            self.wavelength = wavelength.to_value(u.nm)
            self.dwavelength = dwavelength.to_value(u.nm)
        else:
            self.spectrum = None
            self.photon_rate = self._rate_from_photons  #type: ignore[assignment]


    def _rate_from_mag(self, mag: float) -> float:
        return 10.**(-0.4 * mag) if mag < 40. else 1e-16

    def _rate_from_fmegajy(self, fnu: float) -> float:
        return 2.754e+02 * (fnu if fnu >= self.eps else self.eps)

    def _rate_from_fmujy(self, fnu: float) -> float:
        return 2.754e-10 * (fnu if fnu >= self.eps else self.eps)

    def _rate_from_flux(self, flux: float) -> float:
        if self.dwavelength < self.eps:
          self.dwavelength = self.eps
        # 10**(0.4*48.6) / 3e17 (in nm/s) = 91.808
        return 91.808 * self.wavelength ** 2 / self.dwavelength \
          * (flux if flux >= self.eps else self.eps) * 1e-15

    def _rate_from_photons(self, photons: float) -> float:
        return photons if photons >= self.eps else self.eps



