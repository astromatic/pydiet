"""
Data models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from typing import Annotated, Dict

from astropy import units as u  #type: ignore[import-untyped]
import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator
from synphot import (
    BlackBody1D,
    ConstFlux1D,
    Observation,
    SourceSpectrum,
    SpectralElement
)
from synphot.spectrum import BaseSpectrum

from ... import package
from ..types import AnnotatedQuantity


def spectral_to_arrays(spectral: BaseSpectrum) -> (np.ndarray,np.ndarray):
    w = spectral.waveset
    x = spectral(w)

    # Trim extra 0 values at beginning and at the end
    idx = np.where(x.value != 0.)[0]
    start = idx[0] - 1 if idx[0] > 0 else 0
    end = idx[-1] + 2 if idx[-1] < w.size - 1 else w.size
    w = w[start:end]
    x = x[start:end]

    return w, x



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
    transmissions: Dict[str, 'TransmissionModel']
    emissions: Dict[str, 'SBSEDModel']



class InstrumentModel(BaseModel):
    '''
    Pydantic model for a PyDIET instrument.
    '''
    id: str
    name: str
    description: str
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

    transmissions: dict = Field(default=None)
    emissions_ct: dict = Field(default=None)

    @model_validator(mode="after")
    def _compute(self):
        # Compute extra parameters during initialization
        # Filter emissions and transmissions
        upstream_transmission = 1.
        upstream_emission = SourceSpectrum(ConstFlux1D, amplitude=0.)
        # Pre-filter list of transmissions
        transmissions = self.telescope.transmissions | self.optics.transmissions
        emissions = self.telescope.emissions | self.optics.emissions
        for t in transmissions:
            emission = emissions[t].spectral
            transmission = transmissions[t].spectral
            upstream_transmission *= transmission
            upstream_emission = upstream_emission * transmission + emission
        self.transmissions : dict[str, TransmissionModel] = {}
        self.emissions_ct : dict[str, u.Quantity[u.ct/u.s]] = {}
        filter_transmissions = self.filters.transmissions
        filter_emissions = self.filters.emissions
        for f in filter_transmissions:
            filter = filter_transmissions[f]
            filter_transmission = filter_transmissions[f].spectral
            filter_emission = filter_emissions[f].spectral
            transmission = upstream_transmission * filter_transmission
            emission = upstream_emission * transmission + filter_emission
            transmission *= self.detector.transmissions["0"].spectral
            emission *= self.detector.transmissions["0"].spectral
            wave, response = spectral_to_arrays(filter_transmission)
            # Compute countrate
            observation = Observation(emission, transmission)
            self.transmissions[f] = TransmissionModel(
                id = filter.id,
                name = filter.name,
                description = filter.description,
                vars = filter.vars,
                wave = wave,
                response = response,
                spectral = filter_transmission
            )
            self.emissions_ct[f] = observation.countrate(area=1*u.m**2).value
            
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
    sky_transmissions: Dict[str, 'TransmissionModel']
    sky_emissions: Dict[str, 'SBSEDModel']
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
    transmissions: Dict[str, 'TransmissionModel']
    emissions: Dict[str, 'SBSEDModel']
    default: bool = False



class TransmissionModel(BaseModel):
    '''
    Pydantic model for a transmission curve (with wavelength).
    '''
    id: str
    name: str
    description: str
    vars: dict[str, float]
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
    spectral: SpectralElement = Field(exclude=True)
    default: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)


