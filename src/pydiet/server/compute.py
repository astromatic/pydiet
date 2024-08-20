"""
Computation module
"""
# Copyright CFHT
# Licensed under the MIT licence

from cv2 import imencode
import numpy as np
from typing import Literal

from pydantic import BaseModel, Field

class ETCQueryModel(BaseModel):
    airmass: float=Field(
        default=1.2,
        ge=1.
        )
    brightness: float=Field(
        default=20.,
        ge=-100.,
        le=100.
        )
    compute: Literal['etime', 'snr']
    filter: Literal['u', 'g', 'r', 'i', 'z']
    photometry: Literal['aperture', 'psf']
    seeing: float=Field(
        default=0.7,
        ge=0.1,
        le=100.
        )
    sky: Literal['dark', 'grey', 'bright', 'custom']
    snr: float=Field(
        default=10.,
        gt=0.
        )
    transparency: float=Field(
        default=1.,
        gt=0.,
        le=1.
        )
    type: Literal['pointsource', 'galaxy', 'extended']
    unit: Literal['mag', 'flux']



def make_image(instrument, filter, snr, fwhm=0.8, shape=[128,128]):
    '''
    Simulate an astronomical image of a point-source
    '''
    # Pixel size in arcsec
    pixsize = 0.186 if instrument == 'megacam' else 0.307
    # Compute point source image
    y,x = np.mgrid[-shape[0]//2:shape[0]//2,-shape[1]//2:shape[1]//2] * pixsize
    sigma2 = (fwhm / 2.35) ** 2
    psf = np.exp( - (x*x + y*y) / (2 * sigma2))
    # Add point-source plus background plus realization of Gaussian noise
    image = snr * psf + np.random.normal(size=shape)
    # Normalize and encode to PNG format
    mini = np.min(image)
    maxi = np.max(image)
    res, png = imencode('.png', 255.0 * (image - mini) / (maxi - mini))
    return png

