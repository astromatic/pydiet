"""
Backend functions that gather data from files.
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from os import PathLike, scandir
from os.path import basename, exists, isabs, join
from pathlib import Path

# Manage TOML library for Python versions < 3.11
import sys
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
import warnings

from typing import Any, IO, Optional
from astropy.table import QTable  #type: ignore[import-untyped]
from astropy import units as u  #type: ignore[import-untyped]
from astropy.modeling.models import Const1D  #type: ignore[import-untyped]
from astropy.utils.exceptions import AstropyUserWarning  #type: ignore[import-untyped]
from pydantic import BaseModel, Field
from specutils import Spectrum  #type: ignore[import-untyped]
from synphot import (  #type: ignore[import-untyped]
    SourceSpectrum,
    SpectralElement,
    ThermalSpectralElement
) #type: ignore[import-untyped]

from .. import package
from .config import override, settings
from .models.dataconfig import (
    DataConfigModel,
    DetectorConfigModel,
    EmissionConfigModel,
    FiltersConfigModel,
    OpticsConfigModel,
    TransmissionConfigModel
)
from .models.instrument import (
    DetectorModel,
    FiltersModel,
    InstrumentModel,
    OpticsModel,
    SBSEDModel,
    SiteModel,
    TelescopeModel,
    TransmissionModel
)

def add_trans(self, other):
    """Add ``self`` with ``other``."""
    self._validate_other_mul_div(other)
    result = self.__class__(self.model + other.model)
    self._merge_meta(self, other, result)
    return result


SpectralElement.__add__ = add_trans


def get_data_config(data_config: Optional[str] = None) -> DataConfigModel:
    """
    Return data configuration model.

    Examples
    --------

    >>> from .datafiles import get_data_config
    >>> conf = get_data_config()

    Parameters
    ----------
    data_config: str, optional
        Data configuration filename (defaults to "data_config" setting).

    Returns
    -------
    data_config_model: ~pydantic.BaseModel
        Pydantic data configuration model.
    """
    data_config = override("data_config", data_config)
    assert data_config is not None # This is to make mypy happy
    with open(data_config, "rb") as f:
        data = tomllib.load(f)
    assert data is not None # This is to make mypy happy
    # if "path" value is not absolute, assume it is relative to pkg root dir
    if not isabs(data['path']):
        data['path'] = join(package.root_dir, data['path'])
    data_config_model = DataConfigModel.model_validate(data)
    return data_config_model


def get_data_file(filename: IO[bytes] | PathLike | str):
    """
    Return table data from a file (FITS binary table format by preference).

    Parameters
    ----------
    filename: IO[bytes] | PathLike | str
        Data file, filename or stream.

    Returns
    -------
    table: ~astropy.table.QTable
        Astropy table with quantities.
    """
    return QTable.read(filename)


def get_default(d: dict) -> Any:
    """
    Return default model from dictionary of models.

    Parameters
    ----------
    d: dict
        Input dictionary.

    Returns
    -------
    default: Any
        Default model or quantity.
    """
    lst = [val for val in d.values() if val.default]
    return lst[0] if len(lst) > 0 else list(d.values())[0]


def get_detector(
        parent_dir: str,
        detector_config: DetectorConfigModel) -> DetectorModel:
    """
    Return detector model.

    Parameters
    ----------
    parent_dir: str
        Parent directory.
    detector: ~pydantic.BaseModel
        Pydantic detector configuration model.

    Returns
    -------
    detector_model: ~pydantic.BaseModel
        Pydantic detector model.
    """
    transmissions = get_transmissions(
            join(parent_dir, detector_config.path),
            detector_config.transmission
    )
    emissions = get_emissions(
            join(parent_dir, detector_config.path),
            detector_config.emission
    )
    return DetectorModel(
        gain = detector_config.gain,
        ron = detector_config.ron,
        scale = detector_config.scale,
        transmissions = transmissions,
        emissions = emissions
    )


def get_emission(
        file: IO | PathLike | str,
        id: str,
        name: str="",
        description: str="",
        vars: dict[str, float | str]={},
        default: bool=False) -> SBSEDModel:
    """
    Return emission model.

    Parameters
    ----------
    file: IO[bytes] | PathLike | str
        Emission filename.
    id: str
        Emission ID.
    name: str, optional
        Emission name.
    description: str, optional
        Emission description string.
    vars: dict, optional
        Emission dependency parameters
    default: bool, optional
        True if default model.

    Returns
    -------
    emission_model: ~pydantic.BaseModel
        Pydantic surface brightness spectral energy distribution model.
    """
    data = get_data_file(file)
    wave = u.Quantity(data['WAVELENGTH'])
    sed = u.Quantity(data['PHOTLAM']).to(
        u.Jy / u.arcsec**2,
        equivalencies=u.spectral_density(wave)
    )
    # Instantiate the model
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=".*negative flux or throughput.*",
            category=AstropyUserWarning,
        )
        emission = SBSEDModel(
            id = id,
            name = name,
            description = description,
            vars = vars,
            # We drop the surface part as Spectrum does cannot deal with SBs.
            spectral = SourceSpectrum.from_spectrum1d(
                Spectrum(
                    spectral_axis = wave,
                    flux = sed * u.arcsec**2
                ),
                keep_neg=False
            ),
            default=default
        )
    return emission


def get_emission_from_transmission(
        transmission: TransmissionModel,
        temperature: u.Quantity['temperature'],  #type: ignore[name-defined]
        blackbody_fraction: float,
        id: str) -> SBSEDModel:
    """
    Return emission model based on a transmission model.

    Parameters
    ----------
    transmission: ~pydantic.BaseModel
        Pydantic device transmission model.
    temperature: ~astropy.units.Quantity['temperature']
        Device temperature.
    id: str
        Device emission ID.

    Returns
    -------
    emission_model: ~pydantic.BaseModel
        Pydantic surface brightness spectral energy distribution model.
    """
    flat = SpectralElement(Const1D, amplitude=1.)
    assert transmission.spectral != None    # Make mypy happy
    emission = SBSEDModel(
        id = id,
        name = f"{transmission.name} emission",
        description = f"Blackbody emission at {temperature.to(u.K).value:.1f} K",
        # Thermal source spectral flux with Blackbody spectrum over 1 arcsec2
        spectral = ThermalSpectralElement(
            # Add contribution from pure bb fraction and emissivity law
            flat + (blackbody_fraction - 1.) * transmission.spectral,
            temperature=temperature,
            beam_fill_factor=1.
        ).thermal_source(),
        default=transmission.default
    )
    return emission


def get_emissions(
        parent_dir: str,
        emission_config: EmissionConfigModel,
        transmissions: dict[str, TransmissionModel] | None = None
        ) -> dict[str, SBSEDModel]:
    """
    Return dictionary of emission models.

    Parameters
    ----------
    parent_dir: str
        Parent directory.
    emission_config: ~pydantic.BaseModel
         Pydantic emission configuration model.
    transmissions: dict[str, ~pydantic.BaseModel], optional
        Dictionary of Pydantic transmission models.

    Returns
    -------
    emission_models:  dict[str, ~pydantic.BaseModel]
        Dictionary of Pydantic surface brightness SED models.
    """
    emissions : dict[str, SBSEDModel] = {}
    for file_config in emission_config.files:
        key = file_config.id if file_config.id != '' else str(len(emissions))
        emissions[key] = get_emission(
            file=join(parent_dir, emission_config.path, file_config.file),
            id=key,
            name=file_config.name,
            description = file_config.description,
            vars = file_config.vars,
            default=file_config.default
        )
    # No emission files: we use a blackbody with emissivity from transmission
    if len(emission_config.files) == 0 and transmissions is not None:
        temperatures = emission_config.temperatures
        bb_fractions = emission_config.blackbody_fractions
        for t, key in enumerate(transmissions):
            emissions[key] = get_emission_from_transmission(
                transmissions[key],
                temperature=temperatures[t] if t < len(temperatures) \
                    else temperatures[-1],  # Use last temperature if missing
                blackbody_fraction=bb_fractions[t] if t < len(bb_fractions) \
                    else bb_fractions[-1],  # Use last bb_fraction if missing
                id=key
            )
    return emissions


def get_filters(
        parent_dir: str,
        filters_config: FiltersConfigModel) -> FiltersModel:
    """
    Return filter set model.

    Parameters
    ----------
    parent_dir: str
        Parent directory.
    filters_config: ~pydantic.BaseModel
        Pydantic filter set configuration model.

    Returns
    -------
    filters_model: ~pydantic.BaseModel
        Filter set Pydantic model.
    """
    path = join(parent_dir, filters_config.path)
    transmissions = get_transmissions(path, filters_config.transmission)
    # For emissions we may have to use transmission curves
    emissions = get_emissions(
        path,
        filters_config.emission,
        transmissions
    )
    return FiltersModel(
        transmissions=transmissions,
        emissions=emissions
    )


def get_instruments(
        data_config: DataConfigModel) -> dict:
    """
    Return dictionary of instrument models.

    Parameters
    ----------
    data_config: ~pydantic.BaseModel
        Data configuration model.

    Returns
    -------
    instrument_models: dict[str, ~pydantic.BaseModel]
        Dictionary of Pydantic instrument models.
    """
    # Start by gathering the provided sites and telescopes
    sites = get_sites(data_config)
    telescopes = get_telescopes(data_config)
    instruments = {}
    for instrument in data_config.instruments:
        path = join(data_config.path, instrument.path)
        # Instantiate the model
        instruments[instrument.id] = InstrumentModel(
            id = instrument.id,
            name = instrument.name,
            description = instrument.description,
            wavelength_range = instrument.wavelength_range,
            obstruction_area = instrument.obstruction_area,
            overhead = instrument.overhead,
            psf_beta = instrument.psf_beta,
            optics = get_optics(path, instrument.optics),
            filters = get_filters(path, instrument.filters),
            detector = get_detector(path, instrument.detector),
            telescope = telescopes[instrument.telescope_id],
            site = sites[instrument.site_id],
            default = instrument.default
        )
    return instruments


def get_optics(
        parent_dir: str,
        optics_config: OpticsConfigModel) -> OpticsModel:
    """
    Return optics model.

    Parameters
    ----------
    parent_dir: str
        Parent directory.
    optics_config: ~pydantic.BaseModel
        Pydantic optics configuration model.

    Returns
    -------
    optics_model: ~pydantic.BaseModel
        Pydantic optics model.
    """
    path = join(parent_dir, optics_config.path)
    transmissions = get_transmissions(path, optics_config.transmission)
    # For emissions we may have to use transmission curves
    emissions = get_emissions(
        path,
        optics_config.emission,
        transmissions
    )
    return OpticsModel(
        transmissions=transmissions,
        emissions=emissions
    )


def get_sites(data_config: DataConfigModel) -> dict[str, SiteModel]:
    """
    Return dictionary of site models.

    Parameters
    ----------
    data_config: ~pydantic.BaseModel
        Pydantic data configuration model.

    Returns
    -------
    site_models: dict[str, ~pydantic.BaseModel]
        Dictionary of Pydantic site models.
    """
    sites = {}
    for site in data_config.sites:
        path = join(data_config.path, site.path)
        # Instantiate the model
        sites[site.id] = SiteModel(
            id = site.id,
            name = site.name,
            description = site.description,
            sky_transmissions = get_transmissions(path, site.transmission),
            sky_emissions = get_emissions(path, site.emission),
            default = site.default
        )
    return sites


def get_telescopes(data_config: DataConfigModel) -> dict[str, TelescopeModel]:
    """
    Return dictionary of telescope models.

    Parameters
    ----------
    data_config: ~pydantic.BaseModel
        Pydantic data configuration model.

    Returns
    -------
    telescope_models: dict[str, ~pydantic.BaseModel]
        Dictionary of Pydantic telescope models.
    """
    telescopes = {}
    for telescope in data_config.telescopes:
        path = join(data_config.path, telescope.path)
        # Instantiate the model
        transmissions = get_transmissions(path, telescope.transmission)
        emissions = get_emissions(path, telescope.emission, transmissions)
        telescopes[telescope.id] = TelescopeModel(
            id = telescope.id,
            name = telescope.name,
            description = telescope.description,
            collecting_area = telescope.collecting_area,
            obstruction_area = telescope.obstruction_area,
            transmissions = transmissions,
            emissions = emissions,
            default = telescope.default
        )
    return telescopes


def get_transmission(
        file: IO | PathLike | str,
        id: str,
        name: str="",
        description: str="",
        vars: dict[str, float | str]={},
        default: bool=False
    ) -> TransmissionModel:
    """
    Return transmission model.

    Parameters
    ----------
    file: IO[bytes] | PathLike | str
        Transmission filename.
    id: str
        Transmission ID.
    name: str, optional
        Transmission name.
    description: str, optional
        Transmission description string.
    vars: dict, optional
        Transmission dependency parameters
    default: bool, optional
        True if default model.

    Returns
    -------
    transmission_model: ~pydantic.BaseModel
        Pydantic transmission model.
    """
    data = get_data_file(file)
    # Instantiate the model
    wave = u.Quantity(data['WAVELENGTH'])
    response = u.Quantity(data['THROUGHPUT'])
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=".*negative flux or throughput.*",
            category=AstropyUserWarning,
        )
        transmission = TransmissionModel(
            id = id,
            name = name,
            description = description,
            vars = vars,
            # Apply tapering to filters to avoid possible spurious spectral leaks
            spectral = SpectralElement.from_spectrum1d(
                Spectrum(spectral_axis=wave, flux=response),
                keep_neg=False
            ).taper(),
            default=default
        )
    return transmission


def get_transmissions(
        parent_dir: str,
        transmission_config: TransmissionConfigModel) -> dict[str, TransmissionModel]:
    """
    Return dictionary of transmission models.

    Parameters
    ----------
    parent_dir: str
        Parent directory.
    transmission_config: ~pydantic.BaseModel
         Pydantic transmission configuration model.

    Returns
    -------
    transmission_models:  dict[str, ~pydantic.BaseModel]
        Dictionary of Pydantic transmission models.
    """
    transmissions : dict[str, TransmissionModel] = {}
    for file_config in transmission_config.files:
        key = file_config.id if file_config.id != '' else str(len(transmissions))
        transmissions[key] = get_transmission(
            file=join(parent_dir, transmission_config.path, file_config.file),
            id=file_config.id,
            name=file_config.name,
            description=file_config.description,
            vars=file_config.vars,
            default=file_config.default
        )
    return transmissions


def get_webapi_instruments(instruments: dict[str, InstrumentModel]) -> dict[str, InstrumentModel]:
    """
    Return dictionary of filtered instrument models for the web API.

    Parameters
    ----------
    instruments: dict[str, ~pydantic.BaseModel]
        Dictionary of Pydantic instrument models.

    Returns
    -------
    instrument_models: dict[str, ~pydantic.BaseModel]
        Dictionary of Pydantic instrument models.
    """
    winstruments = {}
    for instrument in instruments:
        winstruments[instrument] = instruments[instrument].copy(exclude={
            'site': {'sky_emissions', 'sky_transmissions'},
            'cache': True
        })
    return winstruments

