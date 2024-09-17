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

T_COMPUTE = Literal['etime', 'snr']
T_INSTRUMENT = Literal['megacam', 'wircam']
T_MEGACAM_FILTER = Literal['u', 'g', 'r', 'i', 'z']
T_WIRCAM_FILTER = Literal['Y', 'J', 'H', 'K']
T_FILTER = Literal[T_MEGACAM_FILTER, T_WIRCAM_FILTER]

class ETCQueryModel(BaseModel):
    airmass: float=Field(
        default=1.2,
        ge=1.,
        description="Observation airmass"
        )
    brightness: float=Field(
        default=20.,
        ge=-100.,
        le=100.,
        description="Source brightness"
        )
    compute: T_COMPUTE
    etime: float=Field(
        default=20.,
        ge=0.,
        le=1e30,
        description="Required exposure time"
        )
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
        gt=0.,
        description="Required source Signal-to-Noise Ratio"
        )
    source: Literal['pointsource', 'galaxy', 'extended']
    transparency: float=Field(
        default=1.,
        gt=0.,
        le=1.,
        description="Sky transparency"
        )
    unit: Literal['mag', 'flux']


class ETCResponseModel(BaseModel):
    compute: T_COMPUTE
    etime: float=Field(
        default=1.,
        ge=0.,
        lt=1e30,
        description="Estimated exposure time"
    )
    etime_skysat: float=Field(
        default=0.,
        ge=0.,
        lt=1e30,
        description="Estimated exposure time for sky background saturation"
    )
    etime_sourcesat: float=Field(
        default=0.,
        ge=0.,
        lt=1e30,
        description="Estimated exposure time for source saturation"
    )
    snr: float=Field(
        default=10.,
        ge=0.,
        lt=1e30,
        description="Estimated source Signal-to-Noise Ratio"
    )


def etc_response(instrument: T_INSTRUMENT, q: ETCQueryModel) -> ETCResponseModel:
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


def make_image(instrument: T_INSTRUMENT, r: ETCResponseModel):
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

