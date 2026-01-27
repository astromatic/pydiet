"""
Image simulation module
"""
# Copyright CFHT
# Licensed under the MIT licence

from typing import Literal, Tuple

from astropy import units as u  #type: ignore[import-untyped]
from base64 import b64encode
from io import BytesIO
from PIL.Image import fromarray
import numpy as np
from scipy.optimize import brentq, minimize_scalar  #type: ignore[import-untyped]
from synphot import Observation, SpectralElement  #type: ignore[import-untyped]

from .models.types import PhotometryID, SourceID



class Image(object):
    """
    Raster image generation class for computing exposure times and SNRs

    Examples
    --------
    >>> from astropy import units as u

    >>> img = Image(
    ...     source='point_source',
    ...     psf_fwhm=0.8 * u.arcsec,
    ...     psf_beta=3.2,
    ...     pixel=(0.186 * u.arcsec, 0.186 * u.arcsec),
    ...     flux=42.,
    ...     bkg=10.,
    ...     ron=4.,
    ...     gain=1.65,
    ...     photometry='model_fitting'
    ... )

   >>> # Compute SNR from exposure time
   >>> print(f"{img.snr(etime=10.):.1f}")
   4.6

   >>> # Compute Exposure time from SNR
   >>> print(f"{img.etime(snr=10.):.1f}")
   43.0


    Parameters
    ----------
    source: Literal['point_source', 'galaxy', 'extended'], optional
        Source type.
    psf_fwhm: ~astropy.units.Quantity['angle'], optional
        Full Width at Half Maximum of the Point Spread Function.
    psf_beta: float, optional
        Moffat beta parameter of the Point Spread Function.
    sersic_radius: ~astropy.units.Quantity['angle'], optional
        Half-light radius for Sersic galaxy profiles.
    sersic_index: float, optional
        Sersic index for galaxy profiles.
    pixel: ~astropy.units.Quantity['angle'], optional
        Pixel scale on each axis.
    image_size: Tuple[int, int], optional
        Image size in pixels on each axis.
    flux: float, optional
        Source flux in photons per second.
    bkg: float, optional
        Total background flux in photons per second per square arcsecond.
    ron: float, optional
        Detector read out noise standard deviation in electrons.
    gain: float, optional
        Detector conversion factor in e-/ADU.
    full_well: float, optional
        Detector full well in electrons.
    range: int, optional
        Digital range, in analog-to-digital converter steps.
    bias: float, optional
        Detector bias in ADUs.
    photometry: Literal['model_fitting', 'fixed_aperture', 'optimal_aperture', 'large_aperture']
        Photometric measurement type.
    aperture: float, optional
        Aperture diameter in pixels for fixed aperture photometry.
    oversamp: int, optional
        Number of oversampling sub pixels on each axis.
    """
    def __init__(
            self,
            source: SourceID='point_source',
            psf_fwhm: u.Quantity['angle']=1.*u.arcsec, #type: ignore[name-defined]
            psf_beta: float=3.2,
            sersic_radius: u.Quantity['angle']=1.*u.arcsec, #type: ignore[name-defined]
            sersic_index: float=1.,
            pixel: u.Quantity['angle']=(0.2, 0.2)*u.arcsec, #type: ignore[name-defined]
            image_size: Tuple[int, int]=(64, 64),
            flux: float=1.,
            bkg: float=0.,
            ron: float=0.,
            gain: float=1.,
            full_well: float=1e6,
            range: int=65536,
            bias: float=0.,
            photometry: PhotometryID='model_fitting',
            aperture: float=3.,
            oversamp: int=1,) -> None:

        self.source = source
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

        # Create image coordinate rasters
        raster_size = [image_size[0] * oversamp, image_size[1] * oversamp]
        yx = np.mgrid[
            -raster_size[0]//2:raster_size[0] - raster_size[0]//2,
            -raster_size[1]//2:raster_size[1] - raster_size[1]//2
        ].astype(np.float32)
        r2 = yx[0]**2 + yx[1]**2
        self.r2 = r2

        # Create truncation disk
        self.mask_r2 = r2[0, raster_size[1]//2]
        self.mask = r2 <= self.mask_r2

        self.pixel_area = (pixel[0] * pixel[1]) / oversamp**2 * u.pix**2

        if source == 'extended':
            self.image = self.extended()
            return

        # Rasterize the PSF
        if psf_beta <= 1.:
            raise ValueError("Moffat beta must be > 1.")

        # Compute the square of the alpha parameter from the FWHM
        alpha2 = u.Quantity(psf_fwhm)**2 / (4. * (2.**(1./psf_beta) - 1.)) \
            / self.pixel_area

        # Create PSF raster
        print(r2, alpha2)
        moffat = np.power(1. + r2 / alpha2, -psf_beta) 

        # Truncate inside a disk
        moffat *= self.mask
        self.psf = moffat / moffat.sum()

        # Generate star or galaxy image
        self.image = self.sersic(
            re=sersic_radius,
            n=sersic_index
        ) if source == 'galaxy' else self.psf

        # Create photometry measurement aperture
        if self.photometry != 'model_fitting':
            if self.photometry == 'fixed_aperture':
                # User-provided aperture diameter
                r2max = aperture**2 * (u.arcsec / u.pix)**2 \
                    / self.pixel_area
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


    def delta_snr2(self, etime: float, snr: float) -> float:
        return self.snr(etime=etime)**2 - snr**2


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


    def etime_max(self, snr:float) -> float:
        # Find exposure time range for root finding
        t_high = 1.
        while (tsnr:=self.snr(t_high)) < snr and tsnr < 1.e12:
            t_high *= 2.
        return t_high


    def etime_source_sat(self) -> float:
        return self.saturation / self.max()


    def extended(self) -> np.ndarray:
        return self.mask * self.pixel_area.to(u.arcsec**2).value


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


    def max(self) -> float:
        return self.flux * self.image.max() + self.bkg


    def sersic(
            self,
            re: u.Quantity['angle']=1.*u.arcsec,  #type: ignore[name-defined]
            n: float=1.) -> np.ndarray:
        # Model validity limits
        if n < 0.36:
            n = 0.36
        # R_e normalization from Ciotti & Bertin 1999
        bn = 2.* n - 0.333333 + 9.8765e-3*n**(-1) + 1.8029e-3 * n**(-2) \
            + 1.1409e-4 * n**(-3) - 7.151e-5 * n**(-4)
        inv2n = 0.5 / n
        invre2 = (self.pixel_area / re**2).value
        sersic = np.exp(-bn * (np.power(self.r2 * invre2, inv2n) - 1.))
        sersic = np.fft.irfft2(
            np.fft.rfft2(sersic) * np.fft.rfft2(np.fft.fftshift(self.psf))
        ) * self.mask
        return sersic / np.sum(sersic)


    def snr(self, etime: float=1.) -> float:
        # First treat special case of extended source
        if self.source == 'extended':
            # Compute pixel area in arcsec2
            invarea = 1. / self.pixel_area.to(u.arcsec**2).value
            return self.flux * etime / np.sqrt(
                (self.var_bkg * invarea + self.var_flux) * etime \
                + self.var_ron * invarea
            )
        # Compute the "noise variance image"
        img2 = self.image**2
        var_tot = self.var_ron + (
            self.var_bkg + self.var_flux * self.image
        ) * etime
        if self.photometry == 'optimal_aperture':
            # (Re-)compute optimal aperture
            res = minimize_scalar(
                fun = lambda r2: - self.snr_aper(
                    self.flux * etime,
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
            return self.flux * etime * np.sqrt(
                np.sum(img2 / var_tot + img2 / (2. * var_tot**2))
            )
        else:
            # Return SNR for a predefined aperture
            return self.snr_aper(
                self.flux * etime,
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


