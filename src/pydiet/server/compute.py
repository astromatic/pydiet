"""
Computation module
"""
# Copyright CFHT
# Licensed under the MIT licence

from math import sqrt
from typing import Literal

from astropy import units as u  #type: ignore[import-untyped]
from cv2 import imencode
import numpy as np
from pydantic import BaseModel, Field
from synphot import Observation  #type: ignore[import-untyped]

from .models import ETCQueryModel, ETCResponseModel
from .data import instruments, ab_spectrum, st_spectrum, vega_spectrum

ref_spectra = {
    'abmag': ab_spectrum,
    'vegamag': vega_spectrum,
    'flambda': st_spectrum,
    'fnu': ab_spectrum,
    'fjansky': ab_spectrum
}


def etc_response(q: ETCQueryModel) -> ETCResponseModel:
    instrument = instruments[q.instrument.value]
    # Detector transmission
    detector = instrument.detector
    detector_resp = 1.
    qes = detector.qes
    for qe in qes:
        detector_resp *= qes[qe].spectral
    # Filter transmission
    filter = instrument.filters[q.filter]
    # Apply tapering to filters to avoid possible spurious spectral leaks
    filter_resp = filter.spectral.taper()
    # Optics transmission
    optics_resp = 1.
    optics = instrument.optics
    for optic in optics:
        optics_resp *= optics[optic].spectral
    # Telescope transmission
    telescope = instrument.telescope
    telescope_resp = 1.
    transmissions = telescope.transmissions
    for transmission in transmissions:
        telescope_resp *= transmissions[transmission].spectral
    # Atmospheric transmission
    airmass = q.airmass
    airmasses = instrument.site.sky_transmissions.keys()
    print(airmasses)
    atmo_resp = instrument.site.sky_transmissions['am1.2'].spectral
    # Effective transmission
    total_resp = detector_resp * filter_resp * optics_resp * telescope_resp * atmo_resp
    total_resp.to_fits("resp.fits", overwrite=True)
    ref_spectrum = ref_spectra[q.unit]
    sky_spectrum = instrument.site.sky_emissions['am1.0'].spectral
    observation = Observation(ref_spectrum, total_resp)
    sky_observation = Observation(sky_spectrum, total_resp, force='extrap')
    area = telescope.collecting_area - instrument.obstruction_area
    ct = observation.countrate(area=area, binned=False) / detector.gain.value
    zp = u.Magnitude(1. * u.ct / u.s) - u.Magnitude(ct)
    ct_sky = sky_observation.countrate(area=area, binned=False) / detector.gain.value
    mag_sky =  zp + u.Magnitude(ct_sky)
    print(zp, mag_sky)
    if q.compute == 'etime':
        etime = (10.**(0.4*(q.brightness-26.))) * 10. * q.snr**2
        return ETCResponseModel(
            instrument = q.instrument,
            compute = q.compute,
            zp = zp,
            etime = etime,
            etime_skysat = etime * 100.,
            etime_sourcesat = etime * 10.,
            snr = q.snr
        )
    else:
        return ETCResponseModel(
            instrument = q.instrument,
            compute = q.compute,
            zp = zp,
            etime = q.etime,
            etime_skysat = q.etime * 100.,
            etime_sourcesat = q.etime * 10.,
            snr = sqrt(0.1 * (10.**(0.4*(26.-q.brightness))) * q.etime)
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

