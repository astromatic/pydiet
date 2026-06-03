"""
Data models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from typing import Annotated, Optional, Tuple

from astropy import units as u  #type: ignore[import-untyped]
import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator
from synphot import (  #type: ignore[import-untyped]
    BlackBody1D,
    ConstFlux1D,
    Observation,
    SourceSpectrum,
    SpectralElement
)
from synphot.spectrum import BaseSpectrum  #type: ignore[import-untyped]

from ... import package
from ..photsys import PhotSys
from ..types.quantity import AnnotatedQuantity


# Setup AB photometric system
abphotsys = PhotSys('abmag')


def spectral_to_arrays(spectral: BaseSpectrum) -> Tuple[np.ndarray, np.ndarray]:
    w = spectral.waveset
    x = spectral(w)

    # Trim extra 0 values at beginning and at the end
    idx = np.where(x.value != 0.)[0]
    if len(idx):
        start = idx[0] - 1 if idx[0] > 0 else 0
        end = idx[-1] + 2 if idx[-1] < w.size - 1 else w.size
        w = w[start:end]
        x = x[start:end]

    return w, x


class CacheModel(BaseModel):
    '''
    Pydantic model for cached data.
    '''
    tpeaks: dict[str, float]
    zp_abmags: dict[str, AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "s / ct",
        decimals = 4,
        description = "Instrumental AB magnitude zero-point"
    )]
    transmissions: dict[str, 'TransmissionModel']
    emissions_ct: dict[str, float]


class DetectorModel(BaseModel):
    '''
    Pydantic model for an instrument detector (e.g., CMOS or CCD).
    '''
    gain: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "electron / adu",
        gt = 0. * u.electron / u.adu,
        decimals = 4,
        description = "Detector conversion factor."
    )
    ron: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "electron",
        ge = 0. * u.electron,
        decimals = 4,
        description = "Read-out noise RMS amplitude."
    )
    scale: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "arcsec/pix",
        gt = [0., 0.] * u.arcsec / u.pix,
        min_shape = (2),
        max_shape = (2),
        decimals = 4,
        description = "Angular pixel scale along each axis."
    )
    transmissions: dict[str, 'TransmissionModel']
    emissions: dict[str, 'SBSEDModel']



class InstrumentModel(BaseModel):
    '''
    Pydantic model for a PyDIET instrument.
    '''
    id: str
    name: str
    description: str
    wavelength_range: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "nm",
        gt = [0., 0.] * u.nm,
        min_shape = (2),
        max_shape = (2),
        decimals = 4,
        description = "Instrument minimum and maximum wavelengths."
    )
    obstruction_area:  AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "m2",
        gt = 0. * u.m**2,
        decimals = 3,
        description = "Default obstruction area (only used if not specified for the instrument)."
    )
    overhead:  AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "s",
        ge = 0. * u.second,
        decimals = 3,
        description = "Total instrument time overhead between exposures."
    )
    filters: 'FiltersModel'
    optics: 'OpticsModel'
    detector: 'DetectorModel'
    telescope: 'TelescopeModel'
    site: 'SiteModel'
    default: bool = False

    cache: Optional['CacheModel'] = Field(default=None)

    @model_validator(mode="after")
    def _update_cache(self):
        # Compute extra parameters during initialization
        area = self.telescope.collecting_area - self.obstruction_area

        # Transmission peaks (essentially to check that some flux goes through)
        tpeaks: dict[str, float] = {}
        # Instrumental magnitude zero-points in the AB system
        zp_abmags: dict[str, float] = {}
        # Filter emissions and transmissions
        transmissions : dict[str, TransmissionModel] = {}  #type: ignore[annotation-unchecked]
        emissions_ct : dict[str, u.Quantity[u.ct/u.s]] = {}  #type: ignore[annotation-unchecked]
        for mirror_status in self.telescope.transmissions:
            upstream_transmission = 1.
            mirror_transmission = self.telescope.transmissions[mirror_status]
            mirror_emission = self.telescope.emissions[mirror_status]
            # Pre-filter list of transmissions
            transmission_list = [
                mirror_transmission,
                *self.optics.transmissions.values()
            ]
            upstream_emission = SourceSpectrum(ConstFlux1D, amplitude=0.)
            emission_list = [
                mirror_emission,
                *self.optics.emissions.values()
            ]
            for i, v in enumerate(transmission_list):
                emission = emission_list[i].spectral
                transmission = transmission_list[i].spectral
                upstream_transmission *= transmission
                upstream_emission = upstream_emission * transmission + emission
            for f in self.filters.transmissions:
                filter = self.filters.transmissions[f]
                filter_transmission = filter.spectral
                filter_emission = self.filters.emissions[f].spectral
                transmission = upstream_transmission * filter_transmission
                emission = upstream_emission * transmission + filter_emission
                transmission *= self.detector.transmissions["0"].spectral
                emission *= self.detector.transmissions["0"].spectral
                wave, response = spectral_to_arrays(transmission)
                # Configuration ID includes mirror status ID and filter ID
                config_id = f"{mirror_transmission.id}+{filter.id}" \
                    if mirror_transmission.id != "" \
                    else filter.id
                 # Compute instrumental magnitude zero-point
                tpeaks[config_id] = transmission.tpeak()
                zp_abmags[config_id] = u.Magnitude(
                    self.detector.gain.value / \
                    Observation(
                        abphotsys.spectrum,
                        transmission
                    ).countrate(area=area, binned=False)
                ) if tpeaks[config_id] > 0. else -100. * u.mag
                transmissions[config_id] = TransmissionModel(
                    id = config_id,
                    name = filter.name,
                    description = filter.description,
                    vars = filter.vars,
                    wave = wave,
                    response = response,
                    spectral = transmission
                )
                # Compute emission countrate
                emissions_ct[config_id] = Observation(
                    emission,
                    transmission,
                    force='taper'
                ).countrate(area=area).value if tpeaks[config_id] > 0. else 0.
            self.cache = CacheModel(
                tpeaks=tpeaks,
                zp_abmags=zp_abmags,
                transmissions=transmissions,
                emissions_ct=emissions_ct
            )
        return self

    model_config = ConfigDict(arbitrary_types_allowed=True)



class OpticsModel(BaseModel):
    '''
    Pydantic model for optics.
    '''
    transmissions: dict[str, 'TransmissionModel']
    emissions: dict[str, 'SBSEDModel']



class FiltersModel(OpticsModel):
    '''
    Pydantic model for a filter set.
    '''
    pass



class SBSEDModel(BaseModel):
    '''
    Pydantic model for a Surface Brightness Spectral Energy Distribution (SBSED).
    '''
    id: str
    name: str
    description: str
    vars: dict[str, float|str] = {}
    wave: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "nm",
        ge = 100. * u.nm,
        le = 100. * u.micron,
        min_shape = (2),
        max_shape = (100000),
        decimals = 4
    ) | None = None
    sbsed:  AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "Jy / arcsec2",
        ge = 0. * u.Jy / u.arcsec**2,
        min_shape = (2),
        max_shape = (100000),
        decimals = 6
    ) | None = None
    spectral: SourceSpectrum = Field(exclude=True)
    default: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)



class SEDModel(BaseModel):
    '''
    Pydantic model for a Spectral Energy Distribution (SED).
    '''
    id: str
    name: str
    description: str
    vars: dict[str, float] = {}
    wave: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "nm",
        ge = 100. * u.nm,
        le = 100. * u.micron,
        min_shape = (2),
        max_shape = (100000),
        decimals = 4
    ) | None = None
    sed:  AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "Jy",
        ge = 0. * u.Jy,
        min_shape = (2),
        max_shape = (100000),
        decimals = 6
    ) | None = None
    spectral: SourceSpectrum = Field(exclude=True)
    default: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)



class SiteModel(BaseModel):
    '''
    Pydantic model for an observing site.
    '''
    id: str
    name: str
    description: str
    sky_transmissions: dict[str, 'TransmissionModel']
    sky_emissions: dict[str, 'SBSEDModel']
    default: bool = False



class TelescopeModel(BaseModel):
    '''
    Pydantic model for a telescope.
    '''
    id: str
    name: str
    description: str
    collecting_area: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "m**2",
        gt = 0. * u.m**2,
        decimals = 4,
        description = "Full collecting area, ignoring obstructions."
    )
    obstruction_area: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "m**2",
        gt = 0. * u.m**2,
        decimals = 4,
        description = "Minimum obstruction area."
    )
    transmissions: dict[str, 'TransmissionModel']
    emissions: dict[str, 'SBSEDModel']
    default: bool = False



class TransmissionModel(BaseModel):
    '''
    Pydantic model for a transmission curve (with wavelength).
    '''
    id: str
    name: str
    description: str = ""
    vars: Optional[dict[str, float | str]] = None
    wave_range: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "nm",
        gt = [0., 0.] * u.nm,
        min_shape = (2),
        max_shape = (2),
        decimals = 4,
        description = "Instrument minimum and maximum wavelengths."
    ) | None = None
    wave: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "nm",
        ge = 100. * u.nm,
        le = 100. * u.micron,
        min_shape = (2),
        max_shape = (100000),
        decimals = 3
    ) | None = None
    response: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "",
        ge = -100.,
        le = 100.,
        min_shape = (2),
        max_shape = (100000),
        decimals = 4
    ) | None = None
    spectral: Optional[SpectralElement] = Field(default=None, exclude=True)
    default: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)


