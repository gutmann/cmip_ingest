#!/usr/bin/env python
import os,traceback,sys
import config
import io_routines
import output
import convert


def load_base_data(info):
    file_list = []
    for v in info.base_vars:
        file_list.append(info.base_file.format(variable=v))

    for v in info.const_vars:
        file_list.append(info.const_file.format(v))

    for v in info.surface_vars:
        file_list.append(info.surface_file.format(v))

    ds = xr.open_mfdataset(file_list)

    # for example, this could do:
    # ds = xr.open_mfdataset(["hus_6hrLev_CanESM2_historical_r1i1p1_198001010000-198012311800.nc",
    #                     "ta_6hrLev_CanESM2_historical_r1i1p1_198001010000-198012311800.nc",
    #                     "ua_6hrLev_CanESM2_historical_r1i1p1_198001010000-198012311800.nc",
    #                     "va_6hrLev_CanESM2_historical_r1i1p1_198001010000-198012311800.nc",
    #                     "orog_fx_CanESM2_historical_r0i0p0.nc",
    #                     "sftlf_fx_CanESM2_historical_r0i0p0.nc"])

    if (info.verbose): print("Loading base file metadata (this could take a while)")
    return ds.sel(time= slice(info.start_time, info.end_time),
                  lat = slice(info.south, info.north),
                  lon = slice(info.west, info.east))


def add_regridded_data(ds, info, regrid_file_search, regrid_var_name):
    # tos_file = get_tos_file(info, years)
    # if tos files have not been regridded:
    # use CDO to regrid tos
    regridded_files = regridded_files(regrid_file_search, regrid_var_name)

    # tos = xr.open_mfdataset("regridded_tos_day_CanESM2_historical_r1i1p1_19710101-19801231.nc")
    new_data = xr.open_mfdataset(regridded_files)
    time_filled = new_data[regrid_var_name].reindex_like(ds['time'], method='nearest')
    # note reindex_like automatically subsets tos to the same timesteps as ds, e.g. time=slice(info.start_time, info.end_time)

    subset_data = time_filled.sel(lat = slice(info.south, info.north),
                                  lon = slice(info.west, info.east))


    ds[regrid_var_name] = subset_data
    ds[regrid_var_name].values = subset_data.values # not clear why this is needed, but the actual data don't seem to copy over otherwise

    return ds


def add_derived_data(ds, info):
    R = 8.3144621   # J/mol/K
    cp = 29.19      # J/mol/K   =1.012 J/g/K
    g = 9.81        # m/s^2


    # this function is defined for each GCM and is set up in config?
    ds[info.pressure_var] = info.read_pressure(ds)

    # exner function to convert temperature and potential temperature
    pii = (100000.0 / ds[info.pressure_var].values)**(R / cp)
    ds[info.potential_t_var] = data[info.temperature_var] * pii              # K (converted to potential temperature)

    potential_temperature_attributes = {"standard_name":"potential_temperature_of_air",
                                        "units":"K"}
    ds[info.potential_t_var].attrs = potential_temperature_attributes


    # not sure if this is necessary anymore or if calc_z can use surface pressure
    slp = units.calc_slp(data[info.ps_var].values,
                         data[info.hgt_var].values[np.newaxis,...],
                         ts = data[info.temperature_var].values[:,0,...],
                         mr = data[info.qvapor_var].values[:,0,...],
                         method = 2)

    # if z not in ds? (access supplies z instead of p...)
    ds[info.z_var] = data[info.pressure_var].copy()
    z_attributes = {"standard_name":"elevation",
                    "units":"m"}
    ds[info.z_var].attrs = z_attributes

    for z_time in range(ds[info.z_var].shape[0]):
        ds[info.z_var].values[z_time,...] = units.calc_z(slp.values[z_time],
                                              ds[info.pressure_var].values[z_time],
                                              t = ds[info.temperature_var].values[z_time],
                                              mr = ds[info.qvapor_var].values[z_time])

    return ds



def simple_ingest(info):
    # for year in years:
    #     files_to_open = get_files(info, year)
    #     ds = xr.open_mfdataset(files_to_open)
    ds = load_base_data(info)

    ds = add_regridded_data(ds, info, info.tos_file_search, info.tos_var)
    # dilate tos to fill missing data along coasts?

    ds = add_derived_data(ds)

    # convert, e.g. t to potential t, modify variable attributes

    # alternative strategy :
    # ds = xr.open_mfdataset("*")
    # years loop might have to be outside all of the loading and regridding to save memory?
    years = range(info.start_time.year, info.end_time.year+1)
    for y in years:
        start_date = "{}-01-01".format(y)
        end_date = "{}-01-01".format(y+1)
        current_data = ds.sel(time=slice(start_date, end_date))

        current_data.to_netcdf(info.output_file.format(y))

    # ds.to_netcdf(info.output_file.format(year))


if __name__ == '__main__':
    try:
        info=config.parse()
        config.update_info(info)

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
