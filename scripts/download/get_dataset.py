from ftplib import FTP
import netrc

import xarray as xr

# example_url :
# "ftp://ftp.ceda.ac.uk/badc/cmip5/data/cmip5/output1/NOAA-GFDL/GFDL-ESM2M/rcp85/6hr/atmos/6hrLev/r1i1p1/latest/va/va_6hrLev_GFDL-ESM2M_rcp85_r1i1p1_2096010100-2100123123.nc"

ftpsite = "ftp.ceda.ac.uk"
base_directory = "badc/cmip5/data/cmip5/output1"

dir_template = "{institute}/{model}/{scenario}/{interval}/{domain}/{interval_subdir}/{run}/latest/{var_name}"

int_subdict = {"3hr":"3hr",
               "6hr":"6hrLev",
               "day":"day",
               "mon":"{domain_letter}mon",
               "fx":"fx"}

from download.models import institute_dict

def list_models(ftp, level_format="6hrLev", interval="6hr", test_var="hus"):
    """Prints a list of model/scenario/run combinations that have the requested data"""
    # aternatives: level_format = "6hrPlev", test_var="ta"
    # aternatives: level_format = "day", interval="day"

    ftp.cwd("/"+base_directory)
    # loop over all institutes
    inst = ftp.nlst()
    for i in inst:
        ftp.cwd(i)
        # loop over all models from this institute
        models = ftp.nlst()
        for m in models:
            ftp.cwd(m)
            # loop over scenarios from this model
            scenarios = ftp.nlst()
            for s in scenarios:
                # for all RCP scenarios try to CD into the requested sub-directory
                if s[:3] == "rcp":
                    try:
                        ftp.cwd(s+"/{}/atmos/{}/".format(interval, level_format))
                        # loop through all model runs (e.g. r1i1p1)
                        runs = ftp.nlst()
                        for r in runs:
                            try:
                                ftp.cwd(r+"/latest/")
                                vars = ftp.nlst()
                                # if the requested test_var is present, print the institute, model, scenario, run
                                if test_var in vars:
                                    print(" ".join([i,m,s,r]))

                            # if anything went wrong with this run, catch the error and reset the directory position
                            except Exception as e:
                                ftp.cwd("/"+base_directory+"/"+i+"/"+m)
                                ftp.cwd(s+"/{}/atmos/{}/".format(interval, level_format))
                                # print(e)

                            ftp.cwd("../..")
                        ftp.cwd("../../../../")

                    # if anything went wrong with this institute/model/scenario, catch the error and reset the directory position
                    except Exception as e:
                        ftp.cwd("/"+base_directory+"/"+i+"/"+m)

            ftp.cwd("../")
        ftp.cwd("../")

def get_auth(filename=None):
    """Read authentication information stored in .netrc file"""
    username = None
    password = None

    auth = netrc.netrc(filename)
    username, account, password = auth.hosts[ftpsite]

    return username, password


def construct_directory_name(model, var_name, run="r1i1p1", institute=None,
                             domain="atmos", interval="6hr", scenario="rcp85"):
    """Construct a string with the sub-directory name needed to download data from"""

    if institute is None:
        institute = institute_dict[model]

    sub_interval = int_subdict[interval].format(domain_letter=domain[0].upper())

    dir = dir_template.format(model=model,
                            var_name=var_name,
                            run=run,
                            institute=institute,
                            interval_subdir=sub_interval,
                            domain=domain,
                            interval=interval,
                            scenario=scenario)
    return dir


def download(model, var_name, run="r1i1p1", institute=None,
            domain="atmos", interval="6hr",
            start_time="20900101", end_time="21000101",
            scenario="rcp85"):
    """Download a requested variable from the CEDA ftp site"""

    if interval is "fx":
        run="r0i0p0"

    # setup the ftp connection
    ftp = FTP(ftpsite)

    # login
    u,p = get_auth()
    result = ftp.login(user=u, passwd=p)
    if result[:3] != "230":
        raise Exception("Unable to connect to: "+ftpsite)

    # cd into the CMIP directory
    result = ftp.cwd(base_directory)
    if result[:3] != "250":
        raise Exception("Unable to cd into base directory: "+base_directory)


    # cd into the directory containing the requested dataset
    data_directory = construct_directory_name(model, var_name, run=run, institute=institute,
                                              domain=domain, interval=interval, scenario=scenario)
    result = ftp.cwd(data_directory)
    if result[:3] != "250":
        raise Exception("Unable to cd into data directory: "+data_directory)

    # get a list of all files in the current directory
    files = ftp.nlst()
    # loop through files checking to see if they should be downloaded
    for f in files:

        if interval is "fx":
            print("Downloading: "+f)
            ftp.retrbinary("RETR "+f, open(f, 'wb').write)

        else:
            # note, example filename = ps_6hrLev_CCSM4_rcp85_r6i1p1_2100010100-2100123118.nc
            # [-1] gets "2100010100-2100123118.nc"
            # [:-3] strips off the .nc
            file_dates = f.split("_")[-1][:-3]

            # then strip out the start and end dates
            # with the strings cut to the size of the input data they will be compared to
            file_start_date = file_dates.split("-")[0][:len(end_time)]
            file_end_date = file_dates.split("-")[1][:len(start_time)]

            # if the current file over laps the time period requested, then we will download it
            if (int(file_start_date) < int(end_time)) and (int(file_end_date) > int(start_time)):
                print("Downloading: "+f)
                ftp.retrbinary("RETR "+f, open(f, 'wb').write)

    # close the ftp connection
    ftp.quit()
