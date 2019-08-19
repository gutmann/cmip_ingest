#!/usr/bin/env python

"""
SYNOPSIS

    download_icar.py [-h] [-model [MODEL]] [-run [RUN]] [-scen [SCEN]]
                        [-start [START]] [-end [END]] [-v] [--verbose]

DESCRIPTION

    Script to download data CMIP5 forcing data for ICAR by selecting model,

EXAMPLES

    download_icar.py -model CanESM2 -scen historical -start 19500101 -end 19600101

EXIT STATUS

    TODO: List exit codes

AUTHOR

    Ethan Gutmann - gutmann@ucar.edu

LICENSE

    This script is in the public domain.

VERSION
    1.0

"""
from __future__ import absolute_import, print_function, division

import sys
import os
import traceback
import argparse

global verbose
verbose=False


from download import get_dataset

# If it is possible to get all of the MPI data (with divergence / vorticity winds) these can be converted
#  to u and v winds using something like "cdo -s -r -f nc setreftime,1860-01-01,00:00 -settunits,day -sp2gp -dv2uv input.grb output.nc"
#
#  to remap a rotated pole (e.g. ocean temperatures) first create a cdo grid description:
#   cdo griddes sample_file.nc  > grid.txt
#  then remap to it
#   cdo -f nc -s remapcon,grid.txt rotated_pole_data.nc output_data.nc

# 6 Hourly, high res download
core_variables = [{"var_name":"va", "domain":"atmos", "interval":"6hr"},
                  {"var_name":"ua", "domain":"atmos", "interval":"6hr"},
                  {"var_name":"ta", "domain":"atmos", "interval":"6hr"},
                  # {"var_name":"ps", "domain":"atmos", "interval":"6hr"},
                  {"var_name":"hus", "domain":"atmos", "interval":"6hr"},
                  {"var_name":"prc", "domain":"atmos", "interval":"3hr"},
                  {"var_name":"tos", "domain":"ocean", "interval":"day"},
                  {"var_name":"orog", "domain":"atmos", "interval":"fx"},
                  {"var_name":"sftlf", "domain":"atmos", "interval":"fx"},
                  ]

# daily, low time resolution download
# core_variables = [{"var_name":"va", "domain":"atmos", "interval":"day"},
#                   {"var_name":"ua", "domain":"atmos", "interval":"day"},
#                   {"var_name":"ta", "domain":"atmos", "interval":"day"},
#                   {"var_name":"ps", "domain":"atmos", "interval":"day"},
#                   {"var_name":"hus", "domain":"atmos", "interval":"day"},
#                   {"var_name":"zg", "domain":"atmos", "interval":"day"},
#                   {"var_name":"prc", "domain":"atmos", "interval":"day"},
#                   {"var_name":"tos", "domain":"ocean", "interval":"day"},
#                   {"var_name":"orog", "domain":"atmos", "interval":"fx"},
#                   {"var_name":"sftlf", "domain":"atmos", "interval":"fx"},
#                   ]



def main(model="CCSM4", run="r6i1p1", scenario="historical", start_date="19800101", end_date="19810101"):

    for v in core_variables:
        print(v)
        try:
            get_dataset.download(model=model, run=run, scenario=scenario, start_time=start_date, end_time=end_date, **v)
        except Exception as e:
            print("Error: ")
            print(e)

if __name__ == '__main__':
    # main()
    try:
        parser= argparse.ArgumentParser(description='Download ICAR data from CMIP5 FTP archive. ',
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('-model', dest="model", nargs="?", action='store', default="CanESM2",     help="CMIP5 Model name (e.g. CCSM4, CanESM2, ...)")
        parser.add_argument('-run',   dest="run",   nargs="?", action='store', default="r1i1p1",      help="run, initialization, physics member (e.g. r1i1p1)")
        parser.add_argument('-scen',  dest="scen",  nargs="?", action='store', default="historical",  help="scenario (e.g. historical, rcp85)")
        parser.add_argument('-start', dest="start", nargs="?", action='store', default="19800101",    help="run, initialization, physics member (e.g. r1i1p1)")
        parser.add_argument('-end',   dest="end",   nargs="?", action='store', default="19810101",    help="run, initialization, physics member (e.g. r1i1p1)")
        parser.add_argument('-v', '--version',action='version',
                version='CMIP5 ICAR ingest 1.0')
        parser.add_argument ('--verbose', action='store_true',
                default=False, help='verbose output', dest='verbose')
        args = parser.parse_args()

        verbose = args.verbose

        exit_code = main(model=args.model, run=args.run, scenario=args.scen, start_date=args.start, end_date=args.end)

        if exit_code is None:
            exit_code = 0
        sys.exit(exit_code)
    except KeyboardInterrupt as e: # Ctrl-C
        raise e
    except SystemExit as e: # sys.exit()
        raise e
    except Exception as e:
        print('ERROR, UNEXPECTED EXCEPTION')
        print(str(e))
        traceback.print_exc()
        os._exit(1)
