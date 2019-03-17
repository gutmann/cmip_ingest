import numpy as np

import mygis
from bunch import Bunch

def vcoord(filename):
    """compute the vertical coordinate in space and time for a given file"""
    na=np.newaxis
    a = mygis.read_nc(filename,"lev").data[na,:,na,na]
    b = mygis.read_nc(filename,"b").data[na,:,na,na]
    orog= mygis.read_nc(filename,"orog").data
    z= a+b*orog
    return z

def xr_vcoord(ds):
    """compute the vertical coordinate in space and time for a given file"""
    raise ValueError("ACCESS style model computes Z not P...")
    na=np.newaxis
    a = ds["lev"].values[na,:,na,na]
    b = ds["b"].values[na,:,na,na]
    orog= mds["orog"].values
    z= a+b*orog

    z_attrs = {"standard_name":"elevation",
                      "units":"m"}
    output_data = ds["ta"].copy()
    output_data.attrs = z_attrs
    output_data.values = z

    return output_data
