"""
Functions that gather data from files.
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from os import scandir
from os.path import basename, exists, isabs, join

# Manage TOML library for Python versions < 3.11
import sys
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from typing import Any, Optional
from astropy.table import QTable #type: ignore[import-untyped]
from astropy import units as u #type: ignore[import-untyped]
from pydantic import BaseModel, Field
from specutils import Spectrum #type: ignore[import-untyped]
from synphot import (
    BlackBody1D,
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
    SEDModel,
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


def get_data_file(filename: str):
    return QTable.read(filename)


def get_default(d: dict) -> Any:
    lst = [val for val in d.values() if val.default]
    return lst[0] if len(lst) > 0 else list(d.values())[0]


def get_detector(
        parent_dir: str,
        detector: DetectorConfigModel) -> DetectorModel:
    # Instantiate the model
    transmissions = get_transmissions(
            join(parent_dir, detector.path),
            detector.transmission
    )
    emissions = get_emissions(
            join(parent_dir, detector.path),
            detector.emission
    )
    return DetectorModel(
        gain = detector.gain,
        ron = detector.ron,
        scale = detector.scale,
        transmissions = transmissions,
        emissions = emissions
    )


def get_emissions(
        parent_dir: str,
        emission_config: EmissionConfigModel,
        transmissions: dict[str, TransmissionModel] | None = None,
        sb = False) -> dict[str, SBSEDModel | SEDModel]:
    emissions : dict[str, SEDModel | SBSEDModel] = {}
    for file_config in emission_config.files:
        data = get_data_file(
            join(parent_dir, emission_config.path, file_config.file)
        )
        wave = u.Quantity(data['WAVELENGTH'])
        sed = u.Quantity(data['PHOTLAM']).to(
            u.Jy / u.arcsec**2,
            equivalencies=u.spectral_density(wave)
        ) if sb else u.Quantity(data['PHOTLAM'])
        # Instantiate the model
        key = file_config.id if file_config.id != '' else str(len(emissions))
        emissions[key] = SBSEDModel(
            id = key,
            name = file_config.name,
            description = file_config.description,
            vars = file_config.vars,
            # We drop the surface part as Spectrum does cannot deal with SBs.
            spectral = SourceSpectrum.from_spectrum1d(
                Spectrum(
                    spectral_axis = wave,
                    flux = sed * u.arcsec**2
                ),
                keep_neg=False
            )
        ) if sb else SEDModel(
            id = key,
            name = file_config.name,
            description = file_config.description,
            vars = file_config.vars,
            spectral = SourceSpectrum.from_spectrum1d(
                Spectrum(
                    spectral_axis = wave,
                    flux = sed
                ),
                keep_neg=False
            )
        )
    # No emission files: we use a blackbody with emissivity from transmission
    if len(emission_config.files) == 0 and transmissions is not None:
        temperatures = emission_config.temperatures
        areas = emission_config.areas
        for t, key in enumerate(transmissions):
            transmission = transmissions[key]
            temperature = temperatures[t] if t < len(temperatures) \
                else temperatures[-1]
            area = areas[t] if t < len(areas) else areas[-1]
            # Thermal source spectral flux with Blackbody spectrum over 1 arcsec2
            bb = ThermalSpectralElement(
                BlackBody1D,
                temperature=temperature
            ).thermal_source() * area.to(u.m**2).value
            emissions[key] = SBSEDModel(
                id = key,
                name = f"{transmission.name} emission",
                description = f"Blackbody emission at {temperature.to(u.K).value:.1f} K",
                # Apply emissivity
                spectral = bb - bb * transmission.spectral
            )
    return emissions


def get_filters(
        parent_dir: str,
        filters_config: FiltersConfigModel) -> FiltersModel:
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
            obstruction_area = instrument.obstruction_area,
            overhead = instrument.overhead,
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
    sites = {}
    for site in data_config.sites:
        path = join(data_config.path, site.path)
        # Instantiate the model
        sites[site.id] = SiteModel(
            id = site.id,
            name = site.name,
            description = site.description,
            sky_transmissions = get_transmissions(path, site.transmission),
            sky_emissions = get_emissions(path, site.emission, sb=True),
            default = site.default
        )
    return sites


def get_telescopes(data_config: DataConfigModel) -> dict[str, TelescopeModel]:
    telescopes = {}
    for telescope in data_config.telescopes:
        path = join(data_config.path, telescope.path)
        # Instantiate the model
        transmissions = get_transmissions(path, telescope.transmission)
        emissions = get_emissions(
            path,
            telescope.emission,
            transmissions,
            sb=True
        )
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


def get_transmissions(
        parent_dir: str,
        transmission_config: TransmissionConfigModel) -> dict[str, TransmissionModel]:
    transmissions : dict[str, TransmissionModel] = {}
    for file_config in transmission_config.files:
        data = get_data_file(
            join(parent_dir, transmission_config.path, file_config.file)
        )
        # Instantiate the model
        wave = u.Quantity(data['WAVELENGTH'])
        response = u.Quantity(data['THROUGHPUT'])
        key = file_config.id if file_config.id != '' else str(len(transmissions))
        transmissions[key] = TransmissionModel(
            id = file_config.id,
            name = file_config.name,
            description = file_config.description,
            vars = file_config.vars,
            # Apply tapering to filters to avoid possible spurious spectral leaks
            spectral = SpectralElement.from_spectrum1d(
                Spectrum(spectral_axis=wave, flux=response),
                keep_neg=False
            ).taper()
        )
    return transmissions


def get_webapi_instruments(instruments: dict[InstrumentModel]) -> dict:
    winstruments = {}
    for instrument in instruments:
        winstruments[instrument] = instruments[instrument].copy(exclude={
            'site': {'sky_emissions', 'sky_transmissions'}
        })
    return winstruments

