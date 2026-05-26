#!/usr/bin/python3
"""
Script for simulating the degration of mirror reflectance with time, following
the model and fitted parameters of Okita et al. 2019 (PASJ 71, 32):
https://ui.adsabs.harvard.edu/abs/2019PASJ...71...32O
"""
# Author: Emmanuel Bertin DAp/CEA/AIM/OSUPS
# Copyright (c) 2026 DAp/CEA/AIM/OSUPS/UParisSaclay
# Licensed under the MIT licence
import argparse

from astropy.io import fits
import astropy.units as u
from astropy.table import QTable
import numpy as np

def degrade_mirror(
        wave: u.nm,
        t: u.yr = 1. * u.yr,
        A: u.yr**(-1) = 0.023 / u.yr,
        sigma_0: u.AA = 10. * u.AA,
        S: u.AA / u.yr = 40. * u.AA / u.yr,
        cos2theta_i: float = 0.9974) -> np.ndarray:
    """
    Compute the relative mirror reflectance with wavelength caused by
    the degradation of the mirror coating with time, following the model and
    fitted parameters of Okita et al. 2019 (PASJ 71, 32):
    https://ui.adsabs.harvard.edu/abs/2019PASJ...71...32O

    Parameters
    ----------
    wave: ~astropy.units.Quantity['nm']
        Array of wavelengths
    t: ~astropy.units.Quantity['yr'], optional
        Time since last mirror re-coating.
    A: ~astropy.units.Quantity['yr**(-1)'], optional
        Achromatic loss rate.
    sigma_0: ~astropy.units.Quantity['AA'], optional
        Initial RMS surface roughness.
    S: ~astropy.units.Quantity['AA/yr'], optional
        RMS surface roughness increase rate.
    cos2theta_i: float, optional
        <(cos theta_i)**2>, where theta_i is the incidence angle.

    Returns
    -------
    R: ~numpy.ndarray
        Relative reflectance caused by mirror coating degradation
    """
    alpha = np.exp(- A * t)
    sigma = sigma_0 + S * t
    return alpha * np.exp(-cos2theta_i * (4 * np.pi * sigma / wave)**2)
    

default_A = 0.023
default_cos2theta_i = 0.9974
default_s = 10.
default_S = 40.
default_t = 1.


def main() -> int:
    """
    Compute degraded reflectance table from pristine reflectance table.
    """

    parser = argparse.ArgumentParser(
        description="Compute degraded reflectance table from pristine reflectance table."
    )
    parser.add_argument(
        'input',
        metavar='<input table>',
        nargs=1,
        help="Input mirror reflectance table"
    )
    parser.add_argument(
        'output',
        metavar='<output table>',
        nargs=1,
        help="Output mirror reflectance table"
    )
    parser.add_argument(
        '-A', '--achromatic-rate',
        type=float,
        default=default_A,
        help=f"Achromatic loss rate  (default: {default_A}) per year"
    )
    parser.add_argument(
        '-c', '--cos2theta_i',
        type=float,
        default=default_cos2theta_i,
        help=f"<(cos theta_i)**2>, with theta_i incidence angle (default: {default_cos2theta_i})"
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help="Run quietly"
    )
    parser.add_argument(
        '-s', '--sigma_0',
        type=float,
        default=default_s,
        help=f"Initial RMS surface roughness (default: {default_s}) in Å"
    )
    parser.add_argument(
        '-S', '--S',
        type=float,
        default=default_S,
        help=f"RMS surface roughness increase rate (default: {default_S}) in Å/yr"
    )
    parser.add_argument(
        '-t', '--time',
        type=float,
        default=default_t,
        help=f"Time since last mirror re-coating (default: {default_t}) in years"
    )


    args = vars(parser.parse_args())
    quiet = args['quiet']

    mirror = QTable.read(args['input'][0])
    mirror['THROUGHPUT'] *= degrade_mirror(
        wave=mirror['WAVELENGTH'],
        t=args['time'] * u.yr,
        A=args['achromatic_rate'] / u.yr,
        sigma_0=args['sigma_0'] * u.AA,
        S=args['S'] * u.AA / u.yr,
        cos2theta_i=args['cos2theta_i']
    )
    mirror.meta['FILTER'] = f"{mirror.meta['FILTER']} {args['time']} " \
        f"{'year' if args['time'] == 1. else 'years'} after re-coating"

    if not quiet:
        mirror.info()
    fits.table_to_hdu(
        mirror,
        character_as_bytes=True
    ).writeto(args['output'][0], overwrite=True)

    if not quiet:
        print("Done.")

    return 0 # success

if __name__ == "__main__":
    exit(main())

