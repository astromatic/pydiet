"""
Computation module
"""
# Copyright CFHT
# Licensed under the MIT licence

from math import sqrt
from typing import Literal

from cv2 import imencode
import numpy as np

from pydantic import BaseModel, Field

from .models import ETCQueryModel, ETCResponseModel
from .models.data import instruments


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
    filter_resp = filter.spectral
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
    atmo_resp = instrument.site.sky_transmissions['mko_transmission.am1.2'].spectral
    # Effective transmission
    effective_resp = detector_resp * filter_resp * optics_resp * telescope_resp * atmo_resp
    unit = effective_resp.unit_response(telescope.area)
    print(unit)
    if q.compute == 'etime':
        etime = (10.**(0.4*(q.brightness-26.))) * 10. * q.snr**2
        return ETCResponseModel(
            instrument = q.instrument,
            compute = q.compute,
            etime = etime,
            etime_skysat = etime * 100.,
            etime_sourcesat = etime * 10.,
            snr = q.snr
        )
    else:
        return ETCResponseModel(
            instrument = q.instrument,
            compute = q.compute,
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

