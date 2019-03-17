import numpy as np

import mygis
from bunch import Bunch

def vcoord(filename):
    """compute the vertical coordinate in space and time for a given file"""
    na=np.newaxis
    a = mygis.read_nc(filename,"a").data[na,:,na,na]
    b = mygis.read_nc(filename,"b").data[na,:,na,na]
    p0= mygis.read_nc(filename,"p0").data
    ps= mygis.read_nc(filename,"ps").data[:,na,:,:]
    p= a*p0+b*ps
    return p

def xr_vcoord(ds):
    """compute the vertical coordinate in space and time for a given file"""
    na=np.newaxis
    a = ds["a"].values[na,:,na,na]
    b = ds["b"].values[na,:,na,na]
    p0= ds["p0"].values
    ps= ds["ps"].values[:,na,:,:]
    p= a*p0+b*ps

    pressure_attrs = {"standard_name":"air_pressure",
                      "units":"Pa"}
    output_data = ds["ta"].copy()
    output_data.attrs = pressure_attrs
    output_data.values = p

    return output_data
