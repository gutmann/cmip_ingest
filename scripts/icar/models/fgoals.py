import numpy as np

def vcoord(ds):
    """compute the vertical coordinate in space and time for a given file"""
    na=np.newaxis
    ptop = ds["ptop"].values
    sigma = ds["lev"].values[na,:,na,na]
    ps= mds["ps"].values[:,na,:,:]
    p= ptop + sigma * (ps - ptop)

    pressure_attrs = {"standard_name":"air_pressure",
                      "units":"Pa"}
    output_data = ds["ta"].copy()
    output_data.name = "pressure"
    output_data.attrs = pressure_attrs
    output_data.values = p

    return output_data
