#!/usr/bin/env python
import os,traceback,sys
import config

import cftime
import xarray as xr

def interp_on_axis(input, dim_to_match):
    return input.reindex_like(dim_to_match, method='nearest')


def dims_match(c1,c2):
    if len(c1) != len(c2): return False

    if (np.abs(c1 - c2).max() > 1e-10): return False

    return True

# having trouble figureing out how to make xarray do what I want...
# def linear_interp(data, ds, dim):
#
#     c1 = data[dim].values
#     c2 = ds[dim].values
#
#     if dims_match(c1,c2):
#         return data
#
#     else:
#         # make it a list so it is mutable
#         dims = list(data.dims)
#         dims[dim] = ds[dim]
#
#         new_data = xr.DataArray()
#         new_data.attrs = data.attrs
#
#         start_point = 0
#         end_point = 1
#         for i in range(len(ds[dim])):
#             if
#
#         return new_data
#

def interpolate_data(data, ds):
    for dim in data.dims:
        data = interp_on_axis(data, ds[dim])

    print("WARNING: interpolation only occurs using nearest neighbor this may not be appropriate")
    return data
    # data = linear_interp(data, ds, "lon")
    # data = linear_interp(data, ds, "lat")


def load_base_data(info):

    if (info.verbose): print("Loading: "+info.atmdir + "/" + info.atmfile)

    ds = xr.open_mfdataset(info.atmdir + "/" + info.atmfile.format(info.base_vars[0]))

    for v in info.base_vars[1:]:
        this_data = xr.open_mfdataset(info.atmdir + "/" + info.atmfile.format(v))
        data = interpolate_data(this_data[v], ds)
        ds[v] = data

    # for example, this could do:
    # ds = xr.open_mfdataset(["hus_6hrLev_CanESM2_historical_r1i1p1_198001010000-198012311800.nc",
    #                     "ta_6hrLev_CanESM2_historical_r1i1p1_198001010000-198012311800.nc",
    #                     "ua_6hrLev_CanESM2_historical_r1i1p1_198001010000-198012311800.nc",
    #                     "va_6hrLev_CanESM2_historical_r1i1p1_198001010000-198012311800.nc",
    #                     "orog_fx_CanESM2_historical_r0i0p0.nc",
    #                     "sftlf_fx_CanESM2_historical_r0i0p0.nc"])
    # perhaps as :
    # ds = xr.open_mfdataset("*CanESM2*.nc")

    if (info.verbose): print("Loading base file metadata (this could take a while)")

    # Time objects have to be defined with the calendar used in the input GCM
    start_time = ds.time.values[0]

    if start_time.calendar == "360_day":
        start_date = cftime.Datetime360Day(*info.start_date.timetuple())
        end_date = cftime.Datetime360Day(*info.end_date.timetuple())

    elif start_time.calendar == "noleap":
        start_date = cftime.DatetimeNoLeap(*info.start_date.timetuple())
        end_date = cftime.DatetimeNoLeap(*info.end_date.timetuple())

    else:
        start_date = cftime.Datetime(*info.start_date.timetuple())
        end_date = cftime.Datetime(*info.end_date.timetuple())


    # subset the dataset in space and time
    return ds.sel(time= slice(start_date, end_date),
                  lat = slice(info.lat[0], info.lat[1]),
                  lon = slice(info.lon[0], info.lon[1]))


def add_regridded_data(ds, info, regrid_file_search, regrid_var_name):
    # tos_file = get_tos_file(info, years)
    # if tos files have not been regridded:
    # use CDO to regrid tos
    # regridded_files = regrid_files(regrid_file_search, regrid_var_name)

    # tos = xr.open_mfdataset("regridded_tos_day_CanESM2_historical_r1i1p1_19710101-19801231.nc")
    new_data = xr.open_mfdataset(regridded_files)

    # convert daily data into 6hrly if necessary
    time_filled = new_data[regrid_var_name].reindex_like(ds['time'], method='nearest')
    # note reindex_like automatically subsets tos to the same timesteps as ds, e.g. time=slice(info.start_time, info.end_time)

    # dilate tos to fill missing data along coasts?

    subset_data = time_filled.sel(lat = slice(info.lat[0], info.lat[1]),
                                  lon = slice(info.lon[0], info.lon[1]))

    ds[regrid_var_name] = subset_data
    ds[regrid_var_name].values = subset_data.values # not clear why this is needed, but the actual data don't seem to copy over otherwise

    return ds


def add_derived_data(ds, info):

    # this function is defined for each GCM and is set up in config?
    vert_coord = info.read_vcoord(ds) # note this could be pressure or height
    ds[vert_coord.name] = vert_coord

    return ds



def simple_ingest(info):

    ds = load_base_data(info)

    # ds = add_regridded_data(ds, info, info.tos_file_search, info.tos_var)

    # mostly loads vertical coordinate, needs to apply a GCM specific equation
    ds = add_derived_data(ds, info)

    # years loop might have to be outside all of the loading and regridding to save memory?
    years = range(info.start_date.year, info.end_date.year+1)
    for y in years:
        start_date = "{}-01-01".format(y)
        end_date = "{}-01-01".format(y+1)

        current_data = ds.sel(time=slice(start_date, end_date))

        ps = current_data["hus"][:,0].copy().load()
        ps.name="surface_pressure"
        ps.values[:] = 1022 * 100
        pressure_attrs = {"standard_name":"surface_pressure",
                          "units":"Pa"}
        ps.attrs = pressure_attrs

        current_data[ps.name] = ps

        current_data.to_netcdf(info.output_file.format(y)+".nc")


if __name__ == '__main__':
    try:
        info = config.parse()
        # config.update_info(info)

        exit_code = simple_ingest(info)

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
