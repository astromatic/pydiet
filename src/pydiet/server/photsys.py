"""
Photometric system conversion module
"""
# Copyright CFHT
# Licensed under the MIT licence

from .models.types import PhotSysID

from .data import ab_spectrum, vega_spectrum


class PhotSys(object):
    def __init__(
            self,
            id: PhotSysID='abmag'):

        self.eps = 1e-30
        self.id = id
        if id == 'abmag':
            self.spectrum = ab_spectrum
            self.flux = self._flux_from_mag
        elif id == 'vegamag':
            self.spectrum = vega_spectrum
            self.flux = self._flux_from_mag
        elif id == 'fmegajy':
            self.spectrum = ab_spectrum
            self.flux = self._flux_from_fmegajy
        elif id == 'fmujy':
            self.spectrum = ab_spectrum
            self.flux = self._flux_from_fmujy
        else:
            self.spectrum = None
            self.flux = self._flux_from_flux


    def _flux_from_mag(self, brightness: float) -> float:
        return 10.**(-0.4*brightness) if brightness < 40. else 1e-16

    def _flux_from_fmegajy(self, brightness: float) -> float:
        return 2.754e+02 * brightness if brightness >= self.eps else self.eps

    def _flux_from_fmujy(self, brightness: float) -> float:
        return 2.754e-10 * brightness if brightness >= self.eps else self.eps

    def _flux_from_flux(self, brightness: float) -> float:
        return brightness if brightness >= self.eps else self.eps



