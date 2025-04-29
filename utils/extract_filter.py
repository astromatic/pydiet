#! /usr/bin/python3
"""
Script for converting filter response curves on
https://www.cfht.hawaii.edu/Instruments/Filters/megaprimenew.html
to a format that PyDIET understands
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

def main() -> int:
    """
    Run inference on the provided images.
    """

    default_filter = ''
    default_airmass = 1.
    default_format = 'fits'
    default_instrument = "MegaPrime"
    default_multiply = 1.
    default_origin = "PyDIET table converter"
    default_telescope = "CFHT"
    default_type = "THROUGHPUT"
    default_unit = ""
    default_wunit = "nm"

    parser = argparse.ArgumentParser(
        description="Convert response curves and SEDs for use with PyDIET"
    )
    parser.add_argument(
        'input',
        metavar='input table',
        nargs=1,
        help="Input CFHT table."
    )
    parser.add_argument(
        'output',
        metavar='output table',
        nargs=1,
        help="Input CFHT table."
    )
    parser.add_argument(
        '-a', '--airmass',
        type=float,
        default=default_multiply,
        help=f"Airmass  (default: {default_airmass})"
    )
    parser.add_argument(
        '-f', '--filter',
        type=str,
        default=default_filter,
        help=f"Filter name (default: {default_filter})"
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
        '-m', '--multiply',
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
        '-R', '--rows',
        action='store_true',
        help="Read table as rows instead of columns"
    )
    parser.add_argument(
        '-T', '--telescope',
        type=str,
        default=default_telescope,
        help=f"Telescope applicable to the data (default: {default_telescope})"
    )
    parser.add_argument(
        '-t', '--type',
        type=str,
        default=default_type,
        help=f"Response type  (default: {default_type})"
    )
    parser.add_argument(
        '-u', '--unit',
        type=str,
        default=default_unit,
        help=f"Astropy unit for curve (default: {default_unit})"
    )
    parser.add_argument(
        '-V', '--version',
        action='version',
        version=1.0
    )
    parser.add_argument(
        '-w', '--wunit',
        type=str,
        default=default_wunit,
        help=f"Astropy unit for wavelength (default: {default_wunit})"
    )
    parser.add_argument(
        '-z', '--zero',
        action='store_true',
        help="Zero negative values"
    )

    args = vars(parser.parse_args())

    output_airmass = args['airmass']
    output_filter = args['filter']
    output_format = args['format']
    output_instrument = args['instrument']
    output_origin = args['origin']
    output_telescope = args['telescope']
    output_type = args['type']
    multiply = args['multiply']
    rows = args['rows']	
    unit = args['unit']
    wunit = args['wunit']
    quiet = args['quiet']
    zero = args['zero']	
    input_name = args['input']
    output_name = args['output']

    if input_name[0].endswith(".fits"):
        input_table = Table(fits.getdata(input_name[0]), names=('col1', 'col2'))
    else:
        input_table = ascii.read(input_name[0])
    if rows:
        wave = u.Quantity(list(input_table[0]), wunit).to(u.nm)
        resp = u.Quantity(
            multiply * np.array(list(input_table[1])),
            unit=unit
        )
    else:
        wave = u.Quantity(input_table['col1'], wunit)
        resp = u.Quantity(
            multiply * np.mean(
                np.array([input_table[col] for col in input_table.columns[1:]]),
                axis=0
            ),
            unit=unit
        )
    if zero:
        resp[resp<0.] = 0.
    # Sort by increasing wavelength
    sindex = np.argsort(wave)
    wave = wave[sindex]
    resp = resp[sindex]
    output_table = Table()
    output_table['WAVELENGTH'] = wave
    output_table[output_type] = resp
    output_table.meta = {
        "airmass": output_airmass,
        "date": datetime.now().isoformat(),
        "filter": output_filter,
        "instrume": output_instrument,
        "origin": output_origin,
        "telescop": output_telescope
        }
    print(output_table.info)
    output_table.write(output_name[0], format=output_format, overwrite=True)
    if not quiet:
        print("Done.")

    return 0 # success

if __name__ == "__main__":
    exit(main())

