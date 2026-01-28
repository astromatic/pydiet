#! /usr/bin/python3
"""
Example script using the PyDIET library for computing ETC estimates locally
"""
# Author: Emmanuel Bertin DAp/CEA/AIM/OSUPS
# Copyright (c) 2026 DAp/CEA/AIM/OSUPS/UParisSaclay
# Licensed under the MIT licence
import argparse
from os import path
from pprint import pprint

from astropy.io import ascii, fits  #type: ignore[import-untyped]
import astropy.units as u  #type: ignore[import-untyped]
import numpy as np

from pydiet.server.models import (
    ETCQueryModel,
    FileConfigModel,
    FiltersConfigModel,
    FiltersModel,
    TransmissionConfigModel
)

from pydiet.server import data, response
from pydiet.server.datafiles import (
    get_emission_from_transmission,
    get_transmission
)

def main() -> int:
    """
    Load a filter curve and return ETC estimates.
    """

    default_airmass = 1.
    default_brightness = 20.
    default_format = 'fits'
    default_fwhm = '0.7'
    default_instrument = 'megacam'
    default_sky = 'dark'
    default_snr = 10.
    default_unit = 'abmag'
    default_multiply = 1.

    parser = argparse.ArgumentParser(
        description="Client script for using locally the PyDIET ETC"
    )
    parser.add_argument(
        'input',
        metavar='<input filter transmission>',
        nargs=1,
        help="Input filter transmission table."
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
        choices=['abmag', 'vegamag', 'fmujy'],
        default=default_unit,
        help=f"Flux unit (default: {default_unit})"
    )
    parser.add_argument(
        '-V', '--version',
        action='version',
        version='1.0'
    )

    args = vars(parser.parse_args())

    input_name = args['input'][0]
    airmass = args['airmass']
    brightness = args['brightness']
    format = args['format']
    fwhm = args['fwhm']
    instrument = args['instrument']
    quiet = args['quiet']
    sky = args['sky']
    snr = args['snr']
    unit = args['unit']


    # Add filter transmission
    transmission = get_transmission(file=input_name, id='custom')
    # Add filter emission based on transmission (and dummy temperature/area)
    emission = get_emission_from_transmission(
        transmission,
        temperature=273. * u.K,
        area=0.1 * u.m**2,
        id='custom'
    )
    #data.instruments[instrument].transmissions['custom'] = transmission
    instrumodel = data.instruments[instrument]
    # Update Filter list
    filters = instrumodel.filters
    instrumodel.filters = FiltersModel(
        transmissions = filters.transmissions | {'custom' : transmission},
        emissions = filters.emissions | {'custom' : emission}
    )
    instrumodel._update_transmissions()
    result = response.get_response(
        ETCQueryModel(
            instrument=instrument,
            filter='custom',
            airmass=airmass,
            brightness=brightness,
            fwhm=fwhm,
            sky=sky,
            snr=snr,
            unit=unit
        )
    )
    pprint(result.model_dump())

    #if not quiet:
    #    print("Done.")

    return 0 # success

if __name__ == "__main__":
    exit(main())

