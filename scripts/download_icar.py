#!/usr/bin/env python

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
    main(model="CanESM2", run="r1i1p1", scenario="historical")
