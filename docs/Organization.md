# Organizational Structure #
Code development is currently contained in the "scripts" directory.

`download/get_dataset.py` contains most of the logic to handle downloads from CEDA.

`download/models.py` contains useful look up tables to access attributes of each CMIP5 model.

`download_icar.py` contains the logic to use get_dataset to download the core variables required by ICAR.

`gard` is currently empty.

`icar` has old code for transforming raw downloaded CMIP5 datasets into ICAR input data files. This may need to be modified for the format of files downloaded from CEDA in some cases.

`lib` contains generally useful scripts, in this case `mygis.py` which is used by `icar/io_routines.py` to read and `icar/output.py` to write netcdf files.

# Requirements #
`python3`
`xarray`
`netCDF4`
`bunch`
