import numpy as np
import xarray as xr

def vcoord(ds):
    """compute the vertical coordinate in space and time for a given file"""
    # raise ValueError("ACCESS style model computes Z not P...")
    na = np.newaxis
    a = ds["lev"].values[na,:,na,na]
    b = ds["b"].values[na,:,na,na]
    orog = ds["orog"].values
    z = a + b * orog

    z_attrs = {"standard_name":"elevation",
                      "units":"m"}

    output_data = ds["ta"].copy().load()
    output_data.name = "z"
    output_data.attrs = z_attrs
    output_data.values[:] = z

    return output_data
