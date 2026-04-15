"""
Computation module
"""
# Copyright CFHT
# Licensed under the MIT licence

from math import pi, sqrt
from os import PathLike
from typing import IO, Optional

from astropy import units as u  #type: ignore[import-untyped]
from pydantic import BaseModel, Field
from synphot import Observation, SpectralElement  #type: ignore[import-untyped]

from .image import Image
from .models import (
    ETCQueryModel,
    ETCResponseModel,
    FiltersModel,
    SBSEDModel,
    SEDModel,
    TransmissionModel,
    spectral_to_arrays
)
from .models.types import SkyID
from .data import instruments
from .datafiles import (
    get_emission_from_transmission,
    get_transmission
)
from .photsys import PhotSys


def spectrum_from_airmass(
        models: dict[str, SBSEDModel | SEDModel | TransmissionModel],
        sky: SkyID|None = None,
        am: float = 1.) -> SpectralElement:
    # Build a dictionary of emission or transmission spectra
    am_spectra = {
        model.vars['am'] : model.spectral  #type: ignore[index]
        for model in models.values()
        if sky is None or model.vars['sky'] == sky  #type: ignore[index]
    }
    ams = sorted(list(am_spectra.keys()))
    # bracket the requested airmass for interpolation
    aml = float(ams[0])
    amp = float(ams[-1])
    for aa in ams:
        a = float(aa)
        if a >= am:
            amp = a
            break
        else:
            aml = a
    # Linear interpolation
    fac = (am - aml) / (amp - aml) if am < amp else 1.
    return am_spectra[aml] * (1. - fac) +  am_spectra[amp] * fac  #type: ignore[operator]


def get_response(
        q: ETCQueryModel,
        filter: Optional[IO[bytes] | PathLike | str]=None,
        ui: bool=False) -> ETCResponseModel:
    if filter is not None:
        # Read the uploaded filter transmission file
        filter_transmission = get_transmission(filter, id='upload')
        # Compute filter emission based on transmission (and dummy temperature/area)
        emission = get_emission_from_transmission(
            filter_transmission,
            temperature=273. * u.K,
            id='upload'
        )
        # Make a copy of the instrument while adding the uploaded filter
        filters = instruments[q.instrument].filters
        instrument = instruments[q.instrument].model_copy(
            update={
                'filters': FiltersModel(
                    transmissions = filters.transmissions | {
                        'upload' : filter_transmission
                    },
                    emissions = filters.emissions | {'upload' : emission}
                )
            }
        )
        # Update composite transmissions and emission curves
        instrument._update_transmissions()
    else:
        instrument = instruments[q.instrument]

    telescope = instrument.telescope
    detector = instrument.detector
    instrument_transmission = instrument.transmissions[q.filter]

    # Multiply Total instrument transmission with atmospheric transmission
    atmosphere_spec = spectrum_from_airmass(
        instrument.site.sky_transmissions,
        am=q.airmass
    ) * q.transparency
    full_spec = instrument_transmission.spectral * atmosphere_spec
    # Compute effective collecting area, compensating for possible obstruction
    area = instrument.telescope.collecting_area - instrument.obstruction_area

    # Make virtual observation
    gain = detector.gain.value
    tpeak = full_spec.tpeak()
    lambda_pivot = full_spec.pivot()
    dlambda_rect = full_spec.rectwidth()
    # Actual source
    photsys = PhotSys(q.unit, lambda_pivot, dlambda_rect)
    if tpeak > 0.:
        if photsys.spectrum is None:
            ct_ref = photsys.photon_rate() / gain * u.ct / u.s
        else:
            observation = Observation(photsys.spectrum, full_spec)
            # Compute ref source count rate to get effective zero-point
            ct_ref = observation.countrate(area=area, binned=False) / gain
        zp = u.Magnitude(1. * u.ct / u.s) - u.Magnitude(ct_ref)
    else:
        ct_ref = 0. * u.ct / u.s
        zp = -100. * u.mag
    # Compute total number of reference source electrons (photons per second)
    photon_rate = (ct_ref * gain).value * photsys.photon_rate(q.brightness)

    # Sky background
    # Atmospheric emission
    if q.sky == 'specify':
        sky_photsys = PhotSys(q.sky_unit, lambda_pivot, dlambda_rect)
        sky_spectrum = sky_photsys.spectrum
        sky_photon_rate = sky_photsys.photon_rate(q.sky_brightness)
        if sky_spectrum is not None:
            # If in Jy per str, convert to arcsec2
            if q.sky_unit == 'fmegajy':
                sky_photon_rate *= 2.350e-11
            sky_spectrum *= sky_photon_rate
    else:
        sky_spectrum = spectrum_from_airmass(
            instrument.site.sky_emissions,
            sky=q.sky,
            am=q.airmass
        )
    if sky_spectrum is not None:
        # Compute background count rate to get background surface brightness
        if tpeak > 0.:
            bkg_observation = Observation(
                sky_spectrum,
                instrument_transmission.spectral,
                force='extrap'
            )
            # Add instrumental thermal background
            ct_bkgsb = (
                bkg_observation.countrate(area=area, binned=False) \
                + instrument.emissions_ct[q.filter] * u.ct / u.s
                ) / gain
            mag_bkgsb = zp + u.Magnitude(ct_bkgsb)
        else:
            ct_bkgsb = 0. * u.ct / u.s
            mag_bkgsb = 100. * u.mag
        if mag_bkgsb.value < -100. :
            mag_bkgsb = u.Quantity('100 mag')
        if mag_bkgsb.value > 100.:
            mag_bkgsb = u.Quantity('100 mag')

        # Compute number of background electrons per pixel per second
        # We explicitely assume that counts are per arcsec2
        bkg_rate = (ct_bkgsb * gain * (
            detector.scale[0].to(u.arcsec / u.pix)
            * detector.scale[1].to(u.arcsec / u.pix)
        )).value
    else:
        # Counts directly provided by user
        bkg_rate = sky_photon_rate

    # Instantiate image model
    img = Image(
        source=q.source,
        psf_fwhm=q.seeing * u.arcsec,
        psf_beta=3.2,
        sersic_radius=q.sersic_radius,
        sersic_index=q.sersic_index,
        pixel=detector.scale,
        rate=photon_rate,
        bkg_rate=bkg_rate,
        # Use RON 'counts' instead of electrons for compatibility with synphot
        ron=detector.ron.to_value('electron'),
        gain=gain,
        photometry=q.photometry,
        aperture=q.aperture
    )

    sexposures = sqrt(q.exposures * 2. / pi) if \
        q.stacking == 'median' and q.exposures > 2 else sqrt(q.exposures)
       
    if q.compute == 'etime':
        snr = q.snr / sexposures
        # Compute exposure time (solution to a second degree equation) in s
        etime = img.etime(snr)
    else:
        etime = q.etime
        snr = img.snr(etime)

    if ui:
        full_wave, full_response = spectral_to_arrays(full_spec)
        atmosphere_wave, atmosphere_response = spectral_to_arrays(atmosphere_spec)

    return ETCResponseModel(
            instrument = instrument.name,
            filter = instrument_transmission.name,
            compute = q.compute,
            zp = zp.value,
            snr = snr * sexposures,
            etime = etime,
            etime_skysat = img.etime_bkg_sat(),
            etime_sourcesat = img.etime_source_sat(),
            ttime = q.exposures * (etime + instrument.overhead.to_value(u.s)),
            sky_mag = mag_bkgsb.value,
            lambda_pivot = lambda_pivot.to_value(u.nm),
            bandwidth_rect = dlambda_rect.to_value(u.nm),
            cutout = img.gif(etime, exposures=q.exposures) if ui else None,
            filter_transmission = TransmissionModel(
                id = instrument_transmission.id,
                name = instrument_transmission.name,
                wave_range = instrument.wavelength_range,
                wave = full_wave,
                response = full_response
            ).model_dump_json(
                exclude={'spectral'}
            ) if ui else None,
            atmosphere_transmission =  TransmissionModel(
                id = 'atmosphere',
                name = "Atmosphere",
                wave_range = instrument.wavelength_range,
                wave = atmosphere_wave,
                response = atmosphere_response
            ).model_dump_json() if ui else None
    )


