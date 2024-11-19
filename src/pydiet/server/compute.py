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
from .models.types import InstrumentID


def etc_response(instrument: InstrumentID, q: ETCQueryModel) -> ETCResponseModel:
    if q.compute == 'etime':
        etime = (10.**(0.4*(q.brightness-26.))) * 10. * q.snr**2
        return ETCResponseModel(
            compute = q.compute,
            etime = etime,
            etime_skysat = etime * 100.,
            etime_sourcesat = etime * 10.,
            snr = q.snr
        )
    else:
        return ETCResponseModel(
            compute = q.compute,
            etime = q.etime,
            etime_skysat = q.etime * 100.,
            etime_sourcesat = q.etime * 10.,
            snr = sqrt(0.1 * (10.**(0.4*(26.-q.brightness))) * q.etime)
        )


def make_image(instrument: InstrumentID, r: ETCResponseModel):
    '''
    Simulate an astronomical image of a point-source
    '''
    print(r)
    # Pixel size in arcsec
    pixsize = 0.186 if instrument == 'megacam' else 0.307
    # Compute point source image
    y,x = np.mgrid[-shape[0]//2:shape[0]//2,-shape[1]//2:shape[1]//2] * pixsize
    sigma2 = (fwhm / 2.35) ** 2
    psf = np.exp( - (x*x + y*y) / (2 * sigma2))
    # Add point-source plus background plus realization of Gaussian noise
    image = r.snr * psf + np.random.normal(size=shape)
    # Normalize and encode to PNG format
    mini = np.min(image)
    maxi = np.max(image)
    res, png = imencode('.png', 255.0 * (image - mini) / (maxi - mini))
    return png

