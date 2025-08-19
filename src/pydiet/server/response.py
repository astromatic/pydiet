"""
Computation module
"""
# Copyright CFHT
# Licensed under the MIT licence

from math import pi, sqrt
from typing import Literal

from astropy import units as u  #type: ignore[import-untyped]
from cv2 import imencode
import numpy as np
from pydantic import BaseModel, Field
from synphot import Observation, SpectralElement  #type: ignore[import-untyped]

from .models import (
    ETCQueryModel,
    ETCResponseModel,
    SBSEDModel,
    SEDModel,
    TransmissionModel
)
from .models.types import SkyID

from .data import instruments, ab_spectrum, st_spectrum, vega_spectrum

ref_spectra = {
    'abmag': ab_spectrum,
    'vegamag': vega_spectrum,
    'flambda': st_spectrum,
    'fnu': ab_spectrum,
    'fjansky': ab_spectrum
}


def spectrum_at_airmass(
        models: dict[str, SBSEDModel | SEDModel | TransmissionModel],
        sky: SkyID|None = None,
        am: float = 1.) -> SpectralElement:
    # Build a dictionary of transmission spectra
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


def moffat_nea(
        fwhm: u.Quantity['angle'], #type: ignore[name-defined]
        beta: float) -> u.Quantity['solid angle']: #type: ignore[name-defined] 
    """
    Return King's Noise Equivalent Area of a Moffat function of given
    Full Width at Half-Maximum (FWHM) and beta parameters.
    See `King 1983 <https://adsabs.harvard.edu/abs/1983PASP...95..163K>`_

    Examples
    --------
    >>> from pydiet.server.compute import moffat_nea
    
    >>> moffat_nea("1 arcsec", 3.2)
    <Quantity 3.62308197 arcsec2>

    # beta values < 1 trigger a ValueError exception
    >>> moffat_nea("1 arcsec", 0.8)
    Traceback (most recent call last):
    ...
    ValueError: Moffat beta must be > 1.

    Parameters
    ----------
    fwhm: ~astropy.units.Quantity['angle']
        Angular Full-Width at Half-Maximum of the Moffat function.
    beta: float
        Moffat beta parameter (must be strictly greater than 1).

    Returns
    -------
    nea: ~astropy.units.Quantity['solid angle']
        Noise Equivalent Area as a solid angle.
    """
    if beta <= 1.:
        raise ValueError("Moffat beta must be > 1.")
    # Compute the square of the alpha parameter from the FWHM
    alpha2 = u.Quantity(fwhm)**2 / (4. * (2.**(1./beta) - 1.))
    # Integrate f(r)**2 from 0 to +infty and take the inverse
    return pi * (2. * beta - 1.) / (beta - 1.)**2. * alpha2 


def get_response(q: ETCQueryModel) -> ETCResponseModel:
    instrument = instruments[q.instrument.value]

    # Detector transmission
    detector = instrument.detector
    detector_resp = 1.
    qes = detector.qes
    for e in qes:
        detector_resp *= qes[e].spectral

    # Filter transmission
    filter = instrument.filters[q.filter]

    # Apply tapering to filters to avoid possible spurious spectral leaks
    filter_resp = filter.spectral.taper()

    # Optics transmission
    optics_resp = 1.
    optics = instrument.optics
    for o in optics:
        optics_resp *= optics[o].spectral

    # Telescope transmission
    telescope = instrument.telescope
    telescope_resp = 1.
    trans = telescope.transmissions
    for t in trans:
        telescope_resp *= trans[t].spectral

    # Atmospheric transmission
    atmo_resp = spectrum_at_airmass(
        instrument.site.sky_transmissions,
        am=q.airmass
    )
    # Effective transmission
    total_resp = detector_resp * filter_resp * optics_resp * telescope_resp * atmo_resp
    total_resp.to_fits("resp.fits", overwrite=True)
    ref_spectrum = ref_spectra[q.unit]

    # Atmospheric emission
    sky_spectrum = spectrum_at_airmass(
        instrument.site.sky_emissions,
        sky=q.sky,
        am=q.airmass
    )

    # Make virtual observation
    # Actual source
    observation = Observation(ref_spectrum, total_resp)
    # Sky background
    sky_observation = Observation(sky_spectrum, total_resp, force='extrap')

    # Compute effective collecting area, compensating for possible obstruction
    area = telescope.collecting_area - instrument.obstruction_area

    # Compute ref source count rate to get effective zero-point
    gain = detector.gain.value
    ct_ref = observation.countrate(area=area, binned=False) / gain
    zp = u.Magnitude(1. * u.ct / u.s) - u.Magnitude(ct_ref)

    # Compute background count rate to get background surface brightness
    ct_skysb = sky_observation.countrate(area=area, binned=False) / gain
    mag_skysb =  zp + u.Magnitude(ct_skysb)

    # Compute King's Noise Equivalent Area
    nea = moffat_nea(q.seeing * u.arcsec, 3.2)
    
    # Compute total number of reference source electrons over NEA
    e_ref = (ct_ref * gain).value * 10.**(-0.4*q.brightness)

    # Compute total number of background electrons over NEA
    e_sky = (ct_skysb * gain * nea).value
    # Use 'counts' instead of electrons for the RON for compatibility with synphot
    e_ron = detector.ron.to('electron').value
    e_ron_eff2 = (e_ron**2 * nea / (detector.scale[0] * detector.scale[1])).value
    if q.compute == 'etime':
        snr = q.snr
        # Compute exposure time (solution to a second degree equation) in s
        etime = (
            snr * (snr * e_sky + sqrt(
                (snr * e_sky)**2 + 4. * e_ref**2 * e_ron_eff2
            ))
        ) / (2. * e_ref**2)
    else:
        etime = q.etime
        # Compute SNR
        snr = e_ref * etime / sqrt(e_sky * etime + e_ron_eff2)
    return ETCResponseModel(
            instrument = instrument.name,
            filter = filter.name,
            compute = q.compute,
            zp = zp.value,
            etime = etime,
            etime_skysat = etime * 100.,
            etime_sourcesat = etime * 10.,
            snr = snr,
            sky_mag = mag_skysb.value
    )


def make_image(r: ETCResponseModel):
    '''
    Simulate an astronomical image of a point-source
    '''
    # Pixel size in arcsec
    pixsize = 0.186 if r.instrument == 'megacam' else 0.307
    # Compute point source image
    y,x = np.mgrid[-shape[0]//2:shape[0]//2,-shape[1]//2:shape[1]//2] * pixsize #type: ignore
    sigma2 = (fwhm / 2.35) ** 2 #type: ignore
    psf = np.exp( - (x*x + y*y) / (2 * sigma2))
    # Add point-source plus background plus realization of Gaussian noise
    image = r.snr * psf + np.random.normal(size=shape) #type: ignore
    # Normalize and encode to PNG format
    mini = np.min(image)
    maxi = np.max(image)
    res, png = imencode('.png', 255.0 * (image - mini) / (maxi - mini))
    return png

