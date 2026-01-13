"""
Image simulation module
"""
# Copyright CFHT
# Licensed under the MIT licence

from typing import Literal

from astropy import units as u  #type: ignore[import-untyped]
from base64 import b64encode
from io import BytesIO
from PIL.Image import fromarray
import numpy as np
from scipy.optimize import brentq, minimize_scalar
from synphot import Observation, SpectralElement  #type: ignore[import-untyped]

from .models.types import PhotometryID, SourceID



class Image(object):
    def __init__(
            self,
            source: SourceID='star',
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
            full_well: float=1e6,
            range: int=65536,
            bias: float=0.,
            photometry: PhotometryID='model_fitting',
            aperture: float=3.,
            oversamp: int=1,) -> np.ndarray:

        self.pixel = pixel
        self.flux = flux
        self.bkg = bkg
        self.ron = ron
        self.var_flux = flux
        self.var_bkg = bkg
        self.var_ron = ron*ron
        self.gain = gain
        self.oversamp = oversamp
        self.photometry = photometry
        self.saturation = min(range - 1. - bias, full_well / gain)

        # Rasterize the PSF
        if psf_beta <= 1.:
            raise ValueError("Moffat beta must be > 1.")

        # Compute the square of the alpha parameter from the FWHM
        alpha2 = u.Quantity(psf_fwhm)**2 / (4. * (2.**(1./psf_beta) - 1.)) \
            / (pixel[0] * pixel[1]) * (oversamp * oversamp)

        # Create PSF raster
        raster_size = [image_size[0] * oversamp, image_size[1] * oversamp]
        yx = np.mgrid[
            -raster_size[0]//2:raster_size[0] - raster_size[0]//2,
            -raster_size[1]//2:raster_size[1] - raster_size[1]//2
        ].astype(np.float32)
        r2 = yx[0]**2 + yx[1]**2
        self.r2 = r2
        moffat = np.power(1. + r2 / alpha2.value, -psf_beta) 

        # Truncate inside a disk
        self.mask_r2 = r2[0, raster_size[1]//2]
        self.mask = r2 <= self.mask_r2
        moffat *= self.mask
        self.psf = moffat / moffat.sum()

        # Generate star of galaxy image
        self.image = self.sersic(
            re=sersic_radius, n=sersic_index
        ) if source == 'galaxy' else self.psf

        # Create photometry measurement aperture
        if self.photometry != 'model_fitting':
            if self.photometry == 'fixed_aperture':
                # User-provided aperture diameter
                r2max = aperture**2 * (u.arcsec / u.pix)**2 \
                    / (self.pixel[0] * self.pixel[1])
            elif self.photometry == 'large_aperture':
                # Aperture enclosing 96% of the flux
                r2max = brentq(
                    f = lambda r2: np.sum((self.r2 <= r2) * self.image) - 0.96,
                    a=0.,
                    b=self.mask_r2,
                    xtol=1e-3,
                    maxiter=100
                ) 
            elif self.photometry == 'optimal_aperture':
                r2max = 0.
            self.aperture = r2 < r2max


    def snr(self, t: float=1.) -> float:
        # Compute the "noise variance image"
        img2 = self.image**2
        var_tot = self.var_ron + (self.var_bkg + self.var_flux * self.image) * t
        if self.photometry == 'optimal_aperture':
            # (Re-)compute optimal aperture
            res = minimize_scalar(
                fun = lambda r2: - self.snr_aper(
                    self.flux * t,
                    self.image,
                    var_tot,
                    self.r2 < r2,
                ),
                bounds=(0., self.mask_r2),
                method='bounded'
            )
            # Return SNR at optimal aperture
            return -res.fun
        elif self.photometry == 'model_fitting':
            # Return model-fitting SNR
            return self.flux * t * np.sqrt(
                np.sum(img2 / var_tot + img2 / (2. * var_tot**2))
            )
        else:
            # Return SNR for a predefined aperture
            return self.snr_aper(
                self.flux * t,
                self.image,
                var_tot,
                self.aperture
            )

    def snr_aper(
            self,
            flux: float,
            obj: np.ndarray,
            var: np.ndarray,
            aper: np.ndarray) -> float:
        return flux * np.sum(obj * aper) / np.sqrt(np.sum(var * aper))


    def delta_snr2(self, t: float, snr: float) -> float:
        return self.snr(t=t)**2 - snr**2


    def etime_max(self, snr:float) -> float:
        # Find exposure time range for root finding
        t_high = 1.
        while (tsnr:=self.snr(t_high)) < snr and tsnr < 1.e12:
            t_high *= 2.
        return t_high


    def etime(self, snr: float) -> float:
        return brentq(
            f=self.delta_snr2,
            a=0.,
            b=self.etime_max(snr),
            args=(snr),
            xtol=1e-6,
            maxiter=100
        )


    def etime_bkg_sat(self) -> float:
        return self.saturation / self.bkg


    def etime_source_sat(self) -> float:
        return self.saturation / self.max()


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
        ) * self.mask
        return sersic / np.sum(sersic)


    def max(self) -> float:
        return self.flux * self.image.max() + self.bkg


    def gif(self, etime: float, exposures: int=1, frames: int=10) -> str:
        # Initialize random generator
        rng = np.random.default_rng()
        # Use the PSF as a template image and generate a noiseless image
        noiseless = (self.flux * np.array([self.image] * frames) + self.bkg) * etime
        # Generate Poisson + Gaussian noise realizations
        # We add a 3 sigma offset above the background to prevent negative values
        sigmas = 3.*(self.ron*self.ron + self.bkg*etime)**0.5 / np.sqrt(exposures)
        offset = sigmas - self.bkg * etime
        nmax = (noiseless.max() + offset + sigmas)  / self.gain
        noisy = np.round(
            exposures * (
                rng.poisson(lam=noiseless*exposures) / exposures + rng.normal(
                    loc=offset,
                    scale=self.ron / np.sqrt(exposures),
                    size=noiseless.shape
                )
            ) / self.gain
        ) / exposures
        # Normalize to a max of 1
        noisy[noiseless < 0.] = 0.
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


