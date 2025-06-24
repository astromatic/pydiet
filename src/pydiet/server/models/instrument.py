"""
Data models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from typing import Annotated, Dict

from astropy import units as u  #type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, Field
from synphot import SourceSpectrum, SpectralElement #type: ignore[import-untyped]

from ... import package
from ..types import AnnotatedQuantity


class DetectorModel(BaseModel):
    '''
    Pydantic model for an instrument detector (e.g., CMOS or CCD).
    '''
    gain: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "electron / adu",
        gt = 0. * u.electron / u.adu,
        decimals = 4
    )
    ron: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "electron",
        ge = 0. * u.electron,
        decimals = 4
    )
    scale: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "arcsec/pix",
        gt = [0., 0.] * u.arcsec / u.pix,
        min_shape = (2),
        max_shape = (2),
        decimals = 4,
        description = "Angular pixel scale along each axis."
    )
    qes: Dict[str, 'TransmissionModel']



class InstrumentModel(BaseModel):
    '''
    Pydantic model for a PyDIET instrument.
    '''
    id: str
    name: str
    description: str
    filters: Dict[str, 'TransmissionModel']
    optics: Dict[str, 'TransmissionModel']
    detector: 'DetectorModel'
    telescope: 'TelescopeModel'
    site: 'SiteModel'
    default: bool = False



class SBSEDModel(BaseModel):
    '''
    Pydantic model for a Surface Brightness Spectral Energy Distribution (SBSED).
    '''
    id: str
    name: str
    description: str
    wave: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "nm",
        ge = 100. * u.nm,
        le = 100. * u.micron,
        min_shape = (2),
        max_shape = (20000),
        decimals = 4
    )
    sbsed:  AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "Jy / arcsec2",
        ge = 0. * u.Jy / u.arcsec**2,
        min_shape = (2),
        max_shape = (20000),
        decimals = 6
    )
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
    wave: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "nm",
        ge = 100. * u.nm,
        le = 100. * u.micron,
        min_shape = (2),
        max_shape = (20000),
        decimals = 4
    )
    sed:  AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "Jy",
        ge = 0. * u.Jy,
        min_shape = (2),
        max_shape = (20000),
        decimals = 6
    )
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
        decimals = 4
    )
    obstruction_area: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "m**2",
        gt = 0. * u.m**2,
        decimals = 4
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
    wave: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "nm",
        ge = 100. * u.nm,
        le = 100. * u.micron,
        min_shape = (2),
        max_shape = (20000),
        decimals = 3
    )
    response: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "",
        ge = -100.,
        le = 100.,
        min_shape = (2),
        max_shape = (20000),
        decimals = 4
    )
    spectral: SpectralElement = Field(exclude=True)
    default: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)


