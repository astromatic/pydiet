"""
Functions that gather data from files.
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence
from os import scandir
from os.path import basename, exists, join
import tomllib
from typing import Any, Optional
from astropy.table import QTable #type: ignore[import-untyped]
from astropy import units as u #type: ignore[import-untyped]
from pydantic import BaseModel, Field
from specutils import Spectrum1D #type: ignore[import-untyped]
from synphot import SourceSpectrum, SpectralElement #type: ignore[import-untyped]

from .. import package
from .config import override, settings
from .models.dataconfig import (
    DataConfigModel,
    DetectorConfigModel,
    FilesConfigModel
)
from .models.instrument import (
    DetectorModel,
    InstrumentModel,
    SBSEDModel,
    SEDModel,
    SiteModel,
    TelescopeModel,
    TransmissionModel
)


def get_data_config(data_config: Optional[str] = None) -> DataConfigModel:
    data_config = override("data_config", data_config)
    assert data_config is not None # This is to make mypy happy
    with open(data_config, "rb") as f:
        data = tomllib.load(f)
    assert data is not None # This is to make mypy happy
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
    return DetectorModel(
        gain = detector.gain,
        ron = detector.ron,
        scale = detector.scale,
        qes = get_transmissions(
            join(parent_dir, detector.path),
            detector.transmission
        )
    )


def get_emissions(
        parent_dir: str,
        files_config: FilesConfigModel,
        sb = False) -> dict:
    emissions = {}
    for file_config in files_config.files:
        data = get_data_file(
            join(parent_dir, files_config.path, file_config.file)
        )
        wave = u.Quantity(data['WAVELENGTH'])
        sed = u.Quantity(data['PHOTLAM']).to(
            u.Jy / u.arcsec**2,
            equivalencies=u.spectral_density(wave)
        ) if sb else u.Quantity(data['PHOTLAM'])
        # Instantiate the model
        emissions[file_config.id] = SBSEDModel(
            id = file_config.id,
            name = file_config.name,
            description = file_config.description,
            wave = wave,
            sbsed = sed,
            spectral = SourceSpectrum.from_spectrum1d(
                Spectrum1D(
                    spectral_axis = wave,
                    flux = sed * u.arcsec**2
                ),
                keep_neg=False
            )
        ) if sb else SEDModel(
            id = file_config.id,
            name = file_config.name,
            description = file_config.description,
            wave = wave,
            sed = sed,
            spectral = SourceSpectrum.from_spectrum1d(
                Spectrum1D(
                    spectral_axis = wave,
                    flux = sed
                ),
                keep_neg=False
            )
        )
    return emissions


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
            optics = get_transmissions(
                join(path, instrument.optics.path),
                instrument.optics.transmission
            ),
            filters = get_transmissions(path, instrument.filters),
            detector = get_detector(path, instrument.detector),
            telescope = telescopes[instrument.telescope_id],
            site = sites[instrument.site_id],
            default = instrument.default
        )
    return instruments


def get_sites(data_config: DataConfigModel) -> dict:
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


def get_telescopes(data_config: DataConfigModel) -> dict:
    telescopes = {}
    for telescope in data_config.telescopes:
        path = join(data_config.path, telescope.path)
        # Instantiate the model
        telescopes[telescope.id] = TelescopeModel(
            id = telescope.id,
            name = telescope.name,
            description = telescope.description,
            collecting_area = telescope.collecting_area,
            obstruction_area = telescope.obstruction_area,
            transmissions = get_transmissions(path, telescope.transmission),
            emissions = get_emissions(path, telescope.emission, sb=True),
            default = telescope.default
        )
    return telescopes


def get_transmissions(
        parent_dir: str,
        files_config: FilesConfigModel) -> dict:
    transmissions = {}
    for file_config in files_config.files:
        data = get_data_file(
            join(parent_dir, files_config.path, file_config.file)
        )
        # Instantiate the model
        wave = u.Quantity(data['WAVELENGTH'])
        response = u.Quantity(data['THROUGHPUT'])
        transmissions[file_config.id] = TransmissionModel(
            id = file_config.id,
            name = file_config.name,
            description = file_config.description,
            wave = wave,
            response = response,
            spectral = SpectralElement.from_spectrum1d(
                Spectrum1D(spectral_axis=wave, flux=response),
                keep_neg=False
            )
        )
    return transmissions

