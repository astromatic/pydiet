#! /usr/bin/python3
"""
Client script for harvesting results from the PyDIET ETC.
"""
# Author: Emmanuel Bertin DAp/CEA/AIM/OSUPS
# Copyright (c) 2024, 2025 DAp/CEA/AIM/OSUPS/UParisSaclay
# Licensed under the MIT licence
import argparse
import json
from typing import Literal
from urllib import error, request
from urllib.parse import urljoin

from astropy.io import ascii, fits #type: ignore
from astropy.table import Table  #type: ignore
import astropy.units as u #type: ignore
import numpy as np


def query_url(url: str, query: str):
    """
    Fetch a TODO item from the JSONPlaceholder API and return it as a dict.
    """
    full_url = urljoin(url, query)
    try:
        with request.urlopen(full_url, timeout=5) as response:
            # Read response body as bytes and decode to str
            data = response.read().decode("utf-8")
            return json.loads(data)  # Parse JSON string into dict
    except error.HTTPError as e:
        print(f"HTTP error: {e.code} {e.reason}")
    except error.URLError as e:
        print(f"Network error: {e.reason}")
    except json.JSONDecodeError:
        print("Error: Response was not valid JSON.")
    return None


def main() -> int:
    """
    Convert the input response/emission curve.
    """

    default_airmass = 1.
    default_brightness = 20.
    default_format = 'fits'
    default_fwhm = '0.7'
    default_instrument = 'megacam'
    default_sky = 'dark'
    default_snr = 10.
    default_unit = 'abmag'
    default_url = "http://127.0.0.1:8010/api/"
    default_multiply = 1.

    parser = argparse.ArgumentParser(
        description="Client script for harvesting results from the PyDIET ETC"
    )
    parser.add_argument(
        '-a', '--airmass',
        type=float,
        default=default_airmass,
        help=f"Airmass  (default: {default_airmass})"
    )
    parser.add_argument(
        '-b', '--brightness',
        type=float,
        default=default_brightness,
        help=f"Brightness  (default: {default_brightness})"
    )
    parser.add_argument(
        '-f', '--format',
        type=str,
        default=default_format,
        help=f"Output AstroPy table format (default: {default_format})"
    )
    parser.add_argument(
        '-F', '--fwhm',
        type=float,
        default=default_fwhm,
        help=f"Seeing FWHM (default: {default_fwhm})"
    )
    parser.add_argument(
        '-i', '--instrument',
        type=str,
        default=default_instrument,
        help=f"Instrument applicable to the data (default: {default_instrument})"
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help="Run quietly"
    )
    parser.add_argument(
        '-s', '--sky',
        choices=['dark', 'grey', 'bright'],
        default=default_sky,
        help=f"Sky brightness (default: {default_sky})"
    )
    parser.add_argument(
        '-S', '--snr',
        type=float,
        default=default_snr,
        help=f"SNR  (default: {default_snr})"
    )
    parser.add_argument(
        '-u', '--unit',
        choices=['abmag', 'vegamag', 'flambda', 'fnu', 'fjansky'],
        default=default_unit,
        help=f"Flux unit (default: {default_unit})"
    )
    parser.add_argument(
        '-U', '--url',
        type=str,
        default=default_url,
        help=f"URL of the PyDIET API (default: {default_url})"
    )
    parser.add_argument(
        '-V', '--version',
        action='version',
        version='1.0'
    )

    args = vars(parser.parse_args())

    airmass = args['airmass']
    brightness = args['brightness']
    format = args['format']
    fwhm = args['fwhm']
    instrument = args['instrument']
    quiet = args['quiet']
    sky = args['sky']
    snr = args['snr']
    unit = args['unit']
    url = args['url']

    instruments = query_url(url, "instruments")
    if instruments is None:
        return 1
    filters = instruments[instrument]["filters"]
    for f in filters:
        r = query_url(
            url,
            f"{instrument}?compute=etime&source=pointsource&snr={snr}&"
            f"filter={f}&brightness={brightness}&unit={unit}&photometry=psf&"
            f"sky={sky}&airmass={airmass}&transparency=1.0&seeing={fwhm}"
        )
        if r is None:
            return 1
        print(
            f"{r['filter']:10s}:    "
            f"Zero-point = {r['zp']:6.2f} | Background = {r['sky_mag']:6.2f} | Exp.time = {r['etime']:6.2f}"
        )
    if not quiet:
        print("Done.")

    return 0 # success

if __name__ == "__main__":
    exit(main())

