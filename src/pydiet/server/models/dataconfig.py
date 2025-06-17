"""
Data models
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from astropy import units as u  #type: ignore[import-untyped]
from pydantic import BaseModel, DirectoryPath

from ..types import AnnotatedQuantity


class FileConfigModel(BaseModel):
    '''
    Pydantic model for datafile configuration.
    '''
    default: bool = False
    id: str = 'file'
    name: str = "File"
    description: str = ""
    file: str



class FilesConfigModel(BaseModel):
    '''
    Pydantic model for transmission curve data configuration.
    '''
    path: str
    files: list[FileConfigModel]



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
    transmission: FilesConfigModel
    emission: FilesConfigModel



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
    transmission: FilesConfigModel
    emission: FilesConfigModel


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
    transmission: FilesConfigModel



class OpticsConfigModel(BaseModel):
    '''
    Pydantic model for the intrument optics data configuration model.
    '''
    path: str
    transmission: FilesConfigModel
    emission: FilesConfigModel



class InstrumentConfigModel(BaseModel):
    '''
    Pydantic model for the instrument data configuration model.
    '''
    default: bool = False
    id: str
    name: str
    description: str
    path: str
    obstruction_area:  AnnotatedQuantity(    #type: ignore[valid-type]
        default = None,
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
    site_id: str
    telescope_id: str
    optics: OpticsConfigModel
    filters: FilesConfigModel
    detector: DetectorConfigModel



class DataConfigModel(BaseModel):
    '''
    Pydantic model for the data configuration
    '''
    path: DirectoryPath
    sites: list['SiteConfigModel']
    telescopes: list['TelescopeConfigModel']
    instruments: list['InstrumentConfigModel']

