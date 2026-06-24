"""
Data models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from typing import Annotated
from astropy import units as u  #type: ignore[import-untyped]
from pydantic import BaseModel, DirectoryPath, Field

from ..types import AnnotatedQuantity


class FileConfigModel(BaseModel):
    '''
    Pydantic model for transmission curve configuration.
    '''
    default: bool = False
    id: str = ''
    name: str = ""
    description: str = ""
    vars: dict[str, float|str] = {}
    file: str



class EmissionConfigModel(BaseModel):
    '''
    Pydantic model for emission curve set configuration.
    '''
    path: str = ""
    temperatures: list[AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "K",
        gt = 0. * u.K,
        decimals = 2,
        description  = "Device temperature."
    )] = [283 * u.K]
    blackbody_fractions: list[Annotated[float, Field(
        ge = 0.,
        le = 1.,
        description="Fraction of the pupil that behaves as a pure black body."
    )]] = Field(default_factory=lambda: [0.])
    files: list[FileConfigModel] = []



class TransmissionConfigModel(BaseModel):
    '''
    Pydantic model for transmission curve set configuration.
    '''
    path: str = ""
    files: list[FileConfigModel] = []



class SiteConfigModel(BaseModel):
    '''
    Pydantic model for the observing site data configuration model.
    '''
    default: bool = False
    id: str
    name: str
    description: str
    path: str
    altitude:  AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "m",
        ge = -1000. * u.m,
        decimals = 3,
        description = "Altitude of the observation site."
    )
    transmission: TransmissionConfigModel
    emission: EmissionConfigModel



class TelescopeConfigModel(BaseModel):
    '''
    Pydantic model for the telescope data configuration model.
    '''
    default: bool = False
    id: str
    name: str
    description: str
    path: str
    collecting_area:  AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "m2",
        gt = 0. * u.m**2,
        decimals = 3,
        description = "Full collecting area, including possible mirror hole and spider branches."
    )
    obstruction_area:  AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "m2",
        gt = 0. * u.m**2,
        decimals = 3,
        description = "Default obstruction area (only used if not specified for the instrument)."
    )
    transmission: TransmissionConfigModel
    emission: EmissionConfigModel



class DetectorConfigModel(BaseModel):
    '''
    Pydantic model for the detector data configuration model.
    '''
    path: str
    gain:  AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "electron/adu",
        gt = 0. * u.electron / u.adu,
        decimals = 3,
        description = "Average gain (conversion factor) in electrons per ADU."
    )
    ron:  AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "electron",
        ge = 0. * u.electron,
        decimals = 3,
        description = "Total readout noise in electrons."
    )
    scale: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "arcsec/pix",
        gt = [0., 0.] * u.arcsec / u.pix,
        min_shape = (2),
        max_shape = (2),
        decimals = 4,
        description = "Angular pixel scale along each axis."
    )
    transmission: TransmissionConfigModel
    emission: EmissionConfigModel



class OpticsConfigModel(BaseModel):
    '''
    Pydantic model for the intrument optics data configuration model.
    '''
    path: str
    transmission: TransmissionConfigModel
    emission: EmissionConfigModel



class FiltersConfigModel(OpticsConfigModel):
    '''
    Pydantic model for the intrument filters data configuration model.
    '''
    pass



class InstrumentConfigModel(BaseModel):
    '''
    Pydantic model for the instrument data configuration model.
    '''
    default: bool = False
    id: str
    name: str
    description: str
    path: str
    wavelength_range: AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "nm",
        gt = [0., 0.] *u. nm,
        min_shape = (2),
        max_shape = (2),
        decimals = 4,
        description = "Instrument minimum and maximum wavelengths."
    )
    obstruction_area:  AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "m2",
        gt = 0. * u.m**2,
        decimals = 3,
        description = "Obstruction area for this particular instrument."
    )
    overhead:  AnnotatedQuantity(    #type: ignore[valid-type]
        unit = "s",
        ge = 0. * u.second,
        decimals = 3,
        description = "Total instrument time overhead between exposures."
    )
    psf_beta: float = Field(
        default = 3.2,
        ge = 0.,
        le = 10.,
        description="Moffat beta parameter of the instrument PSF model."
    )
    site_id: str
    telescope_id: str
    optics: OpticsConfigModel
    filters: FiltersConfigModel
    detector: DetectorConfigModel



class DataConfigModel(BaseModel):
    '''
    Pydantic model for the data configuration
    '''
    path: DirectoryPath
    sites: list['SiteConfigModel']
    telescopes: list['TelescopeConfigModel']
    instruments: list['InstrumentConfigModel']

