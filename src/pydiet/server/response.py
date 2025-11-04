"""
Computation module
"""
# Copyright CFHT
# Licensed under the MIT licence

from math import pi, sqrt
from typing import Literal

from astropy import units as u  #type: ignore[import-untyped]
from base64 import b64encode
from io import BytesIO
from PIL.Image import fromarray
import numpy as np
from pydantic import BaseModel, Field
from scipy.optimize import brentq
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



class Image(object):
    def __init__(
            self,
            source: Literal['pointsource', 'galaxy', 'extended']='star',
            psf_fwhm: u.Quantity['angle']=1.*u.arcsec, #type: ignore[name-defined],
            psf_beta: float=3.2,
            sersic_radius: u.Quantity['angle']=1.*u.arcsec, #type: ignore[name-defined]
            sersic_index: float=1.,
            pixel: [u.Quantity['solid angle'],
                u.Quantity['solid angle']]=[0.2*u.arcsec,0.2*u.arcsec],
            image_size: [int, int] = [64, 64],
            flux: float=1.,
            bkg: float=0.,
            ron: float=0.,
            gain: float=1.,
            oversamp: int=1) -> np.ndarray:

        self.pixel = pixel
        self.flux = flux
        self.bkg = bkg
        self.ron = ron
        self.var_flux = flux
        self.var_bkg = bkg
        self.var_ron = ron*ron
        self.gain = gain
        self.oversamp = oversamp

        # Rasterize the PSF
        if psf_beta <= 1.:
            raise ValueError("Moffat beta must be > 1.")
        # Compute the square of the alpha parameter from the FWHM
        alpha2 = u.Quantity(psf_fwhm)**2 / (4. * (2.**(1./psf_beta) - 1.)) \
            / (pixel[0] * pixel[1]) * (oversamp * oversamp)

        # Create raster
        raster_size = [image_size[0] * oversamp, image_size[1] * oversamp]
        yx = np.mgrid[
            -raster_size[0]//2:raster_size[0] - raster_size[0]//2,
            -raster_size[1]//2:raster_size[1] - raster_size[1]//2
        ].astype(np.float32)
        r2 = yx[0]**2 + yx[1]**2
        self.r2 = r2
        moffat = np.power(1. + r2 / alpha2.value, -psf_beta) 
        # Truncate inside a disk
        mask = r2 <= r2[0, raster_size[1]//2]
        moffat *= mask
        self.psf = moffat / moffat.sum()
        self.image = self.sersic(
            re=sersic_radius, n=sersic_index
        ) if source == 'galaxy' else self.psf


    def snr(self, t: float=1.) -> float:
        # Compute the "noise variance image"
        img2 = self.image**2
        var_tot = self.var_ron + (self.var_bkg + self.var_flux * self.image) * t
        # Return SNR
        return self.flux * t * np.sqrt(
            np.sum(img2 / var_tot + img2 / (2. * var_tot**2))
        )


    def delta_snr2(self, t: float, snr: float) -> float:
        return self.snr(t)**2 - snr**2


    def etime_max(self, snr:float) -> float:
        # Find exposure time range for root finding
        t_high = 1.
        while (tsnr:=self.snr(t_high)) < snr and tsnr < 1.e12:
            t_high *= 2.
        return t_high


    def etime(self, snr:float) -> float:
        return brentq(self.delta_snr2, 0., self.etime_max(snr), args=snr, xtol=1e-6, maxiter=100)


    def sersic(
            self,
            re: u.Quantity['angle']=1.*u.arcsec,
            n: float=1.) -> np.ndarray:
        # Model validity limits
        if n < 0.36:
            n = 0.36
        # R_e normalization from Ciotti & Bertin 1999
        bn = 2.* n - 0.333333 + 9.8765e-3*n**(-1) + 1.8029e-3 * n**(-2) \
            + 1.1409e-4 * n**(-3) - 7.151e-5 * n**(-4)
        inv2n = 0.5 / n
        invre2 = (
            (self.pixel[0] * self.pixel[1]) / (self.oversamp**2 * re**2)
        ).value
        sersic = np.exp(-bn * (np.power(self.r2 * invre2, inv2n) - 1.))
        sersic = np.fft.irfft2(
            np.fft.rfft2(sersic) * np.fft.rfft2(np.fft.fftshift(self.psf))
        )
        return sersic / np.sum(sersic)


    def get_gif(self, etime: float, frames: int=10) -> str:
        # Initialize random generator
        rng = np.random.default_rng()
        # Use the PSF as a template image and generate a noiseless image
        noisy = (self.flux * np.array([self.image] * frames) + self.bkg) * etime
        # Generate Poisson + Gaussian noise realizations
        # We add a 3 sigma offset above the background to prevent negative values
        sigmas = 3.*(self.ron*self.ron + self.bkg*etime)**0.5
        offset = sigmas - self.bkg * etime
        nmax = (noisy.max() + offset + sigmas)  / self.gain
        noisy = np.round(
            (
                rng.poisson(lam=noisy) + rng.normal(
                    loc=offset,
                    scale=self.ron,
                    size=noisy.shape
                )
            ) / self.gain
        )
        # Normalize to a max of 1
        noisy[noisy < 0.] = 0.
        noisy /= nmax
        noisy[noisy > 1.] = 1.
        # Apply sRGB gamma correction and convert to 0...255 unsigned integers
        noisy = (
            np.where(
                noisy <= 0.0031308,
                12.92 * noisy,
                1.055 * np.power(noisy, 1/2.4) - 0.055
            ) * 255.
        ).astype(np.uint8)
        
        # Create image buffer
        buffer = BytesIO()
        # Save GIF to buffer and append the rest of the animation
        fromarray(noisy[0], mode="L").save(
            buffer,
            format='GIF',
            save_all=True,
            append_images=[fromarray(im) for im in noisy[1:]],
            duration=100,
            loop=0
        )
        buffer.seek(0)
        # Encode GIF as base64
        gif_base64 = b64encode(buffer.read()).decode("utf-8")
        return f"data:image/gif;base64,{gif_base64}"



def spectrum_at_airmass(
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
    total_resp = detector_resp * filter_resp * optics_resp * telescope_resp \
        * q.transparency * atmo_resp
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

    # Compute total number of reference source electrons
    flux = (ct_ref * gain).value * 10.**(-0.4*q.brightness)

    # Compute number of background electrons per pixel per second
    bkg = (ct_skysb * gain * (detector.scale[0] * detector.scale[1])).value

    # Compute number of background electrons per pixel
    # Use 'counts' instead of electrons for the RON for compatibility with synphot
    ron = detector.ron.to('electron').value

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
        ron=ron,
        gain=gain
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
            filter = filter.name,
            compute = q.compute,
            zp = zp.value,
            etime = etime,
            etime_skysat = etime * 100.,
            etime_sourcesat = etime * 10.,
            snr = snr,
            sky_mag = mag_skysb.value,
            cutout = img.get_gif(etime) if ui else None
    )


