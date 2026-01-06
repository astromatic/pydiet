"""
Computation module
"""
# Copyright CFHT
# Licensed under the MIT licence

from math import pi, sqrt

from astropy import units as u  #type: ignore[import-untyped]
from pydantic import BaseModel, Field
from synphot import Observation, SpectralElement  #type: ignore[import-untyped]

from .image import Image
from .models import (
    ETCQueryModel,
    ETCResponseModel,
    SBSEDModel,
    SEDModel,
    TransmissionModel
)
from .models.types import SkyID
from .data import instruments
from .photsys import PhotSys


def spectrum_from_airmass(
        models: dict[str, SBSEDModel | SEDModel | TransmissionModel],
        sky: SkyID|None = None,
        am: float = 1.) -> SpectralElement:
    # Build a dictionary of emission or transmission spectra
    am_spectra = {
        models[m].vars['am'] : models[m].spectral for m in models \
        if sky is None or models[m].vars['sky']==sky
    }
    ams = sorted(list(am_spectra.keys()))
    # bracket the requested airmass for interpolation
    aml = ams[0]
    amp = ams[-1]
    for a in ams:
        if a >= am:
            amp = a
            break
        else:
            aml = a
    # Linear interpolation
    fac = (am - aml) / (amp - aml) if am < amp else 1.
    return am_spectra[aml] * (1. - fac) +  am_spectra[amp] * fac


def get_response(q: ETCQueryModel, ui: bool=False) -> ETCResponseModel:
    instrument = instruments[q.instrument]
    telescope = instrument.telescope
    detector = instrument.detector
    transmission = instrument.transmissions[q.filter]

    # Multiply Total instrument transmission with atmospheric transmission
    transmission_spec = transmission.spectral * spectrum_from_airmass(
        instrument.site.sky_transmissions,
        am=q.airmass
    ) * q.transparency

    # Compute effective collecting area, compensating for possible obstruction
    area = instrument.telescope.collecting_area - instrument.obstruction_area

    # Make virtual observation
    # Actual source
    photsys = PhotSys(q.unit)
    observation = Observation(photsys.spectrum, transmission_spec)

    # Compute ref source count rate to get effective zero-point
    gain = detector.gain.value
    ct_ref = observation.countrate(area=area, binned=False) / gain
    zp = u.Magnitude(1. * u.ct / u.s) - u.Magnitude(ct_ref)

    # Compute total number of reference source electrons
    flux = (ct_ref * gain).value * photsys.flux(q.brightness)

    # Sky background
    # Atmospheric emission
    if q.sky == 'specify':
        sky_photsys = PhotSys(q.sky_unit)
        sky_spectrum = sky_photsys.spectrum
        sky_flux = sky_photsys.flux(q.sky_brightness)
        if sky_spectrum is not None:
            # If in Jy per str, convert to arcsec2
            if q.sky_unit == 'fmegajy':
                sky_flux *= 2.350e-11
            sky_spectrum *= sky_flux
    else:
        sky_spectrum = spectrum_from_airmass(
            instrument.site.sky_emissions,
            sky=q.sky,
            am=q.airmass
        )
    if sky_spectrum is not None:
        # Compute background count rate to get background surface brightness
        bkg_observation = Observation(
            sky_spectrum,
            transmission.spectral,
            force='extrap'
        )
        print(instrument.emissions_ct[q.filter], bkg_observation.countrate(area=area, binned=False))
        ct_bkgsb = (
            bkg_observation.countrate(area=area, binned=False) \
            + instrument.emissions_ct[q.filter] * u.ct / u.s
            ) / gain
        mag_bkgsb = zp + u.Magnitude(ct_bkgsb)
        if mag_bkgsb.value < -100. :
            mag_bkgsb = u.Quantity('100 mag')
        if mag_bkgsb.value > 100.:
            mag_bkgsb = u.Quantity('100 mag')

        # Compute number of background electrons per pixel per second
        # We explicitely assume that counts are per arcsec2
        bkg = (ct_bkgsb * gain * (
            detector.scale[0].to(u.arcsec / u.pix)
            * detector.scale[1].to(u.arcsec / u.pix)
        )).value
    else:
        # Counts directly provided by user
        bkg = sky_flux

    # Instantiate image model
    img = Image(
        source=q.source,
        psf_fwhm=q.seeing * u.arcsec,
        psf_beta=3.2,
        sersic_radius=q.sersic_radius,
        sersic_index=q.sersic_index,
        pixel=detector.scale,
        flux=flux,
        bkg=bkg,
        # Use RON 'counts' instead of electrons for compatibility with synphot
        ron=detector.ron.to('electron').value,
        gain=gain,
        photometry=q.photometry,
        aperture=q.aperture
    )


    if q.compute == 'etime':
        snr = q.snr
        # Compute exposure time (solution to a second degree equation) in s
        etime = img.etime(snr)
    else:
        etime = q.etime
        snr = img.snr(etime)


    return ETCResponseModel(
            instrument = instrument.name,
            filter = transmission.name,
            compute = q.compute,
            zp = zp.value,
            etime = etime,
            etime_skysat = etime * 100.,
            etime_sourcesat = etime * 10.,
            snr = snr,
            sky_mag = mag_bkgsb.value,
            cutout = img.get_gif(etime) if ui else None
    )


