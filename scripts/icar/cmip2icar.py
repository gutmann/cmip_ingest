#!/usr/bin/env python
import os,traceback,sys
import config
import io_routines
import output
import convert

def main(info):

    for k in info.keys():
        if k!="times" and k!="lat_data" and k!="lon_data":
            print(k,info[k])

    print(info.times[0],info.times[-1])

    curyear = info.times[0].year
    lastyear = info.times[0].year-1

    for curtime in info.times:
        if curtime.year > lastyear:
            raw_data = io_routines.load_data(curtime, info)
            processed_data = convert.cmip2icar(raw_data)
            output.write_file(curtime, info, processed_data)
            lastyear = curtime.year




if __name__ == '__main__':
    try:
        info=config.parse()
        config.update_info(info)

        exit_code = main(info)
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


def simple_ingest(info):
    # for year in years:
    #     files_to_open = get_files(info, year)
    #     ds = xr.open_mfdataset(files_to_open)
    ds = xr.open_mfdataset(["hus_6hrLev_CanESM2_historical_r1i1p1_198001010000-198012311800.nc",
                            "ta_6hrLev_CanESM2_historical_r1i1p1_198001010000-198012311800.nc",
                            "ua_6hrLev_CanESM2_historical_r1i1p1_198001010000-198012311800.nc",
                            "va_6hrLev_CanESM2_historical_r1i1p1_198001010000-198012311800.nc",
                            "orog_fx_CanESM2_historical_r0i0p0.nc",
                            "sftlf_fx_CanESM2_historical_r0i0p0.nc"])

    # tos_file = get_tos_file(info, years)
    # if tos files have not been regridded:
    # use CDO to regrid tos
    tos = xr.open_mfdataset("regridded_tos_day_CanESM2_historical_r1i1p1_19710101-19801231.nc")
    tos_filled = tos["tos"].reindex_like(ds['time'], method='nearest')
    ds["tos"] = tos_filled
    ds["tos"].values = tos_filled.values # not clear why this is needed, but the actual data don't seem to copy over otherwise

    # add z variables
    # add p variables
    # dilate tos?
    # convert, e.g. t to potential t, modify variable attributes

    # alternative strategy :
    # ds = xr.open_mfdataset("*")
    for y in years:
        start_date = "{}-01-01".format(y)
        end_date = "{}-01-01".format(y+1)
        current_data = ds.sel(time=slice(start_date, end_date))


    # ds.to_netcdf(info.output_file.format(year))
