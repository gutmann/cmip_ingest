import numpy as np

def vcoord(ds):
    """compute the vertical coordinate in space and time for a given file"""
    na=np.newaxis
    ap= ds["ap"].values[na,:,na,na]
    b = ds["b"].values[na,:,na,na]
    ps= ds["ps"].values[:,na,:,:]
    p= ap+b*ps

    pressure_attrs = {"standard_name":"air_pressure",
                      "units":"Pa"}
    output_data = ds["ta"].copy()
    output_data.name = "pressure"
    output_data.attrs = pressure_attrs
    output_data.values = p

    return output_data
