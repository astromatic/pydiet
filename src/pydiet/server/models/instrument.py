"""
Data models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from typing import Annotated, Dict

from astropy import units as u  #type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, Field
from synphot import SpectralElement

from ... import package
from ..types import AnnotatedQuantity


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



class FilterModel(BaseModel):
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
    pixel: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "arcsec**2",
        gt = [0., 0.] * u.arcsec**2,
        min_shape = (2),
        max_shape = (2),
        decimals = 4
    )
    qes: Dict[str, 'FilterModel']



class TelescopeModel(BaseModel):
    '''
    Pydantic model for the telescope.
    '''
    id: str
    name: str
    description: str
    area: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "m**2",
        gt = 0. * u.m**2,
        decimals = 4
    )
    transmissions: Dict[str, 'FilterModel']
    emissions: Dict[str, 'SBSEDModel']
    default: bool = False



class SiteModel(BaseModel):
    '''
    Pydantic model for the observing site.
    '''
    id: str
    name: str
    description: str
    sky_transmissions: Dict[str, 'FilterModel']
    sky_emissions: Dict[str, 'SBSEDModel']
    default: bool = False



class InstrumentModel(BaseModel):
    '''
    Pydantic model for a PyDIET instrument.
    '''
    id: str
    name: str
    description: str
    filters: Dict[str, 'FilterModel']
    optics: Dict[str, 'FilterModel']
    detector: DetectorModel
    telescope: TelescopeModel
    site: SiteModel
    default: bool = False


