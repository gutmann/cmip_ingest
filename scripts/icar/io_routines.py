import subprocess,os,glob
import gc,sys
import numpy as np
import netCDF4
from bunch import Bunch
import datetime
# import mygis

from cdo import Cdo

global cdo
cdo = None # don't initialize the climate data operators if they aren't going to be used.


g = 9.81
atmvarlist = ["ta","hus","ua","va"]
icar_atm_var = ["t","qv","u","v"]

# from mygis, modified to work with netCDF4
def read_nc(filename,var="data",proj=None,returnNCvar=False):
    '''read a netCDF file and return the specified variable

    output is a structure :
        data:raw data as an array
        proj:string representation of the projection information
        atts:data attribute dictionary (if any)
    if (returnNCvar==True) then the netCDF4 file is note closed and the netCDF4
        representation of the variable is returned instead of being read into
        memory immediately.
    '''
    d = netCDF4.Dataset(filename, mode='r',format="nc")
    outputdata=None
    if var != None:
        data=d.variables[var]
        attributes=d.variables[var].__dict__
        if returnNCvar:
            outputdata=data
        else:
            # outputdata=data[:]
            ntimes=365*4
            if len(data.shape)>2:
                outputdata=data[:ntimes,...]
            else:
                outputdata=data[:]
    outputproj=None
    if proj!=None:
        projection=d.variables[proj]
        outputproj=str(projection)


    if returnNCvar:
        return Bunch(data=outputdata,proj=outputproj,ncfile=d,atts=attributes)
    d.close()
    return Bunch(data=outputdata,proj=outputproj,atts=attributes)

def find_atm_file(time,varname,info):
    file_base= info.atmdir+info.atmfile
    file_base= file_base.replace("_GCM_",info.gcm_name)
    file_base= file_base.replace("_VAR_",varname)
    file_base= file_base.replace("_Y_",str(time.year))
    file_base= file_base.replace("_EXP_",info.experiment)
    atm_file = file_base.replace("_ENS_",info.ensemble)

    print(atm_file)
    filelist = glob.glob(atm_file)
    filelist.sort()
    return filelist

def find_sst_file(time, info):
    file_base = info.atmdir + info.atmfile
    file_base = file_base.replace("_GCM_",info.gcm_name)
    file_base = file_base.replace("_VAR_","tos")
    file_base = file_base.replace("6hrLev","day")
    file_base = file_base.replace("_Y_","*") #str(time.year))
    file_base = file_base.replace("_EXP_",info.experiment)
    sst_file  = file_base.replace("_ENS_",info.ensemble)

    print(sst_file)
    filelist = glob.glob(sst_file)
    filelist.sort()
    output_file = None
    for f in filelist:
        # e.g. tos_day_CanESM2_historical_r1i1p1_19710101-19801231.nc
        start_year = int(f.split("/")[-1].split("_")[5][:4])
        print(start_year)
        end_year = int(f.split("/")[-1].split("_")[5].split("-")[1][:4])
        if (time.year >= start_year) and (time.year <= end_year):
            output_file = f

    start_year = int(output_file.split("/")[-1].split("_")[5][:4])

    print(time)
    return output_file, int((time - datetime.datetime(start_year, 1,1)).days)


def load_atm(time,info):
    """Load atmospheric variable from a netcdf file"""

    outputdata=Bunch()

    for s,v in zip(icar_atm_var,atmvarlist):
        atmfile_list=find_atm_file(time,v,info)
        for atmfile in atmfile_list:
            nc_data=read_nc(atmfile,v)#,returnNCvar=True)
            newdata=nc_data.data[:,:,info.ymin:info.ymax,info.xmin:info.xmax]
            if s in outputdata:
                outputdata[s]=np.concatenate([outputdata[s],newdata])
            else:
                outputdata[s]=newdata

    outputdata.ntimes=0
    for atmfile in atmfile_list:
        varname="ps"
        nc_data=read_nc(atmfile,varname)
        newdata=nc_data.data[:,info.ymin:info.ymax,info.xmin:info.xmax]
        if varname in outputdata:
            outputdata[varname]=np.concatenate([outputdata[varname],newdata])
        else:
            outputdata[varname]=newdata

        varname="p"
        newdata=info.read_pressure(atmfile)[:,:,info.ymin:info.ymax,info.xmin:info.xmax]
        if varname in outputdata:
            outputdata[varname]=np.concatenate([outputdata[varname],newdata])
        else:
            outputdata[varname]=newdata

        outputdata.ntimes = outputdata.p.shape[0]

    # outputdata.times=info.read_time(atmfile)
    try:
        d = netCDF4.Dataset(atmfile_list[0], mode='r',format="nc")
        calendar = d.variables["time"].calendar
        # calendar = mygis.read_attr(atmfile_list[0], "calendar", varname="time")
    except (KeyError, IndexError) as e:
        calendar = None

    outputdata.calendar = calendar

    return outputdata

def load_sfc(time,info):
    """docstring for load_sfc"""
    outputdata = Bunch()
    basefile = glob.glob(info.orog_file.replace("_GCM_",info.gcm_name))[0]
    outputdata.hgt = read_nc(basefile,"orog").data[info.ymin:info.ymax,info.xmin:info.xmax]

    print(time)
    sstfile, timeidx = find_sst_file(time, info)
    # cdo griddes va_6hrLev_CCSM4_historical_r6i1p1_1980100100-1980123118.nc  > grid.txt
    # subprocess.call(["cdo","griddes","{gridfile}  > grid.txt".format(gridfile=basefile)])
    # cdo -f nc -s remapcon,grid.txt tos_day_CCSM4_historical_r6i1p1_19700101-19891231.nc tos2_day_CCSM4_historical_r6i1p1_19700101-19891231.nc
    # subprocess.call(["cdo","-f nc", "-s remapcon,grid.txt {input_sst} {regridded_sst}".format(input_sst=sstfile, regridded_sst="regridded_"+sstfile)])

    global cdo
    if cdo is None:
        cdo = Cdo()
    cdo.griddes("-f "+basefile+" >grid.txt")
    print("regridding:"+sstfile)
    cdo.remapcon("grid.txt ", input=sstfile, output="regridded_"+sstfile, options="-f nc")
    sstfile = "regridded_"+sstfile
    outputdata.sst = read_nc(sstfile,"tos").data[timeidx,info.ymin:info.ymax,info.xmin:info.xmax]

    outputdata.land = np.zeros(outputdata.hgt.shape)
    basefile = glob.glob(info.sftlf_file.replace("_GCM_",info.gcm_name))[0]
    landfrac = read_nc(basefile,"sftlf").data[info.ymin:info.ymax,info.xmin:info.xmax]
    outputdata.land[landfrac>=0.5] = 1

    return outputdata

def load_data(time,info):
    """docstring for load_data"""
    print(time)
    atm=load_atm(time,info)
    sfc=load_sfc(time,info)
    return Bunch(sfc=sfc,atm=atm)
