#! /usr/bin/python3
"""
Script for downloading an atmospheric emission curve from ESO's SkyCalc:
https://skycalc-ipy.readthedocs.io
"""
# Author: Emmanuel Bertin DAp/CEA/AIM/OSUPS
# Copyright (c) 2024, 2025 DAp/CEA/AIM/OSUPS/UParisSaclay
# Licensed under the MIT licence
import argparse
from datetime import datetime

from astropy.io import ascii, fits #type: ignore
from astropy.table import Table  #type: ignore
import astropy.units as u #type: ignore
import numpy as np
from skycalc_ipy import SkyCalc

def main() -> int:
    """
    Get atmospheric emission curve.
    """
    default_min_wavelength = 300.
    default_max_wavelength = 5000.
    default_wavelength_step = 0.1
    default_airmass = 1.
    default_format = 'fits'
    default_instrument = "MegaPrime"
    default_moon_phase = 180.
    default_moon_separation = 45.
    default_multiply = 1.
    default_origin = "ESO SkyCalc"
    default_telescope = "CFHT"

    parser = argparse.ArgumentParser(
        description="Convert response curves and SEDs for use with PyDIET"
    )
    parser.add_argument(
        'output',
        metavar='output table',
        nargs=1,
        help="Output table"
    )
    parser.add_argument(
        '-a', '--airmass',
        type=float,
        default=default_airmass,
        help=f"Airmass  (default: {default_airmass})"
    )
    parser.add_argument(
        '-e', '--exclude-all-but-moon',
        action='store_true',
        help="Exclude all contributions except that of the Moon"
    )
    parser.add_argument(
        '-F', '--format',
        type=str,
        default=default_format,
        help=f"Output AstroPy table format (default: {default_format})"
    )
    parser.add_argument(
        '-i', '--instrument',
        type=str,
        default=default_instrument,
        help=f"Instrument applicable to the data (default: {default_instrument})"
    )
    parser.add_argument(
        '--min-wavelength',
        type=float,
        default=default_min_wavelength,
        help=f"Minimum wavelength in nm (default: {default_min_wavelength})"
    )
    parser.add_argument(
        '--max-wavelength',
        type=float,
        default=default_max_wavelength,
        help=f"Maximum wavelength in nm (default: {default_max_wavelength})"
    )
    parser.add_argument(
        '-m', '--moon',
        action='store_true',
        help="Include Moon"
    )
    parser.add_argument(
        '-p', '--moon-phase',
        type=float,
        default=default_moon_phase,
        help=f"Moon phase in degrees (default: {default_moon_phase})"
    )
    parser.add_argument(
        '--multiply',
        type=float,
        default=default_multiply,
        help=f"Multiplication factor  (default: {default_multiply})"
    )
    parser.add_argument(
        '-o', '--origin',
        type=str,
        default=default_origin,
        help=f"Origin of the data  (default: {default_origin})"
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help="Run quietly"
    )
    parser.add_argument(
        '-s', '--wavelength-step',
        type=float,
        default=default_wavelength_step,
        help=f"Wavelength step in nm (default: {default_wavelength_step})"
    )
    parser.add_argument(
        '-S', '--moon-separation',
        type=float,
        default=default_moon_separation,
        help=f"Moon separation with target in degrees (default: {default_moon_separation})"
    )
    parser.add_argument(
        '-T', '--telescope',
        type=str,
        default=default_telescope,
        help=f"Telescope applicable to the data (default: {default_telescope})"
    )
    parser.add_argument(
        '-V', '--version',
        action='version',
        version='1.0'
    )

    args = vars(parser.parse_args())

    airmass = args['airmass']
    format = args['format']
    instrument = args['instrument']
    origin = args['origin']
    moon= args['moon']
    moon_phase = args['moon_phase'] % 360.
    moon_separation = args['moon_separation']
    telescope = args['telescope']
    exclude = args['exclude_all_but_moon']
    multiply = args['multiply']
    quiet = args['quiet']
    name = args['output']

    skycalc = SkyCalc()
    skycalc['observatory'] = '3060m'
    skycalc['pwv'] = -1
    skycalc['airmass'] = airmass
    skycalc['wgrid_mode'] = 'fixed_wavelength_step'
    skycalc['wmin'] = args['min_wavelength']
    skycalc['wmax'] = args['max_wavelength']
    skycalc['wdelta'] = args['wavelength_step']
    skycalc['moon_target_sep'] = args['moon_separation']
    skycalc['moon_sun_sep'] = moon_phase
    skycalc['incl_moon'] = 'Y' if moon else 'N'
    if exclude:
        skycalc['incl_starlight'] = 'N'
        skycalc['incl_zodiacal'] = 'N'
        skycalc['incl_loweratm'] = 'N'
        skycalc['incl_upperatm'] = 'N'
        skycalc['incl_airglow'] = 'N'

    skycalc.validate_params()
    
    table = skycalc.get_sky_spectrum()
    output_table = Table()
    output_table['WAVELENGTH'] = table['lam']
    output_table['PHOTLAM'] = multiply * table['flux']
    output_table.meta = {
        "airmass": airmass,
        "date": datetime.now().isoformat(),
        "filter": "Atmosphere",
        "instrume": instrument,
        "origin": origin,
        "telescop": telescope,
        "moonup": moon,
        "moonphas": (moon_phase if moon_phase <= 180. else moon_phase-360.) / 180.,
        "moonangl": moon_separation
        
        }
    if not quiet:
        print(output_table.info)
    output_table.write(name[0], format=format, overwrite=True)
    if not quiet:
        print("Done.")

    return 0 # success

if __name__ == "__main__":
    exit(main())

