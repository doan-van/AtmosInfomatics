# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # this script is to calculate drought index from climate data
# ##
#
# https://climate-indices.readthedocs.io/en/latest/
#
#

# %%
import sys, glob
import numpy as np
import xarray as xr
import pandas as pd
sys.path.insert(0, "climindices/src")
from climate_indices import compute, indices, utils
from climate_indices.compute import scale_values, Periodicity
#==================

# %%


# %%
#==================
# compute spi spei
if 0:
    ifiles = sorted(glob.glob('download/era/data/*.nc') )
    
    ds = xr.open_mfdataset(ifiles) #['tp']
    do = ds.isel(longitude = np.arange(0,360,2), latitude = np.arange(0,181,2) )
    do.to_netcdf('era5_2deg.nc')

# %%

# %%
tp = xr.open_dataset('era5_2deg.nc')['tp'][:,::-1]

# %%
# ERA5 data
dg = tp.stack(point=('latitude', 'longitude')).groupby('point')

# %%
#dg.values

# %%
nu_year = pd.to_datetime( tp.time.values).year.unique().size
spi_args = {
        'scale': 3,
        'distribution': indices.Distribution.gamma,
        'data_start_year': 1,
        'calibration_year_initial': 1,
        'calibration_year_final': nu_year,
        'periodicity': compute.Periodicity.monthly
}

#x = dg.values.reshape(dg.shape[0], -1)
# %%
da_spi = xr.apply_ufunc(
    indices.spi,
    dg,
    dask="allowed",
    kwargs=spi_args,
)

# %%
da_spi = da_spi.unstack('point')

# %%
da_spi.to_netcdf('spi_3month.nc')

# %%
da_spi


# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

