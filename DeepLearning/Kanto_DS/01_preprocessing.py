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

# %%
import numpy as np
import xarray as xr
import pandas as pd
import sys

# %% [markdown]
# ## extract data for relevant region
#
# original data is what download from ERA5 Land
# ![image.png](attachment:1231f638-0175-43a4-8ed1-4876f32a58cd.png)
#
# it is just for reducing file size: use xarray sel
# ![image.png](attachment:b81dadf9-af29-4bca-8b63-4a8b8a43ffaf.png)
#
# get only daily mean: xarray groupby
#
# write to data/tb.nc
#
# Techniques needed:
#
# - __*xarray groupby*__ and take statistics
# - __*xarray sel*__: indecing technique in xarray
#
#

# %%

if 0: # if is just to easily comment out the processs 
    
    ds = xr.open_dataset('ERA5datadownload/download.nc')
    #tb = ds.sel(longitude = slice(65,110), latitude = slice(50,15) )
    tb0 = ds.groupby('time.date').mean() 

    times = pd.to_datetime(tb0.date.values).strftime('%Y%m%d')
    tb0.date.values[:]  = times # just want to change the format of date (not matter much this time)

    tb0.to_netcdf('data/jp.nc')
    # check plot
    #ds.t2m[0].plot()
    #tb0.t2m[0].plot() 



# %% [markdown]
# ## Make low- and high-res data and put is together
#
# this is just reference code, one can do it flexibly
#
#
#  

# %%



if 0:
    
    d1 = xr.open_dataset('data/jp.nc', engine='netcdf4')['t2m']
    print('shape of original data: ', d1.shape)
    
    # get "high-resolution data"
    # because the original data is at too high-resolution, here we reduce it (just for convenient purpose)
    # https://docs.xarray.dev/en/latest/user-guide/interpolation.html
    
    
    n_blur = 7
    # rolling https://docs.xarray.dev/en/stable/generated/xarray.DataArray.rolling.html
    d2 = d1.rolling( {'latitude':n_blur,'longitude':n_blur}, center=True).mean()
    
    print('shape of rolling data: ', d2.shape)
    
    
    d4 = d2[:, ::n_blur,::n_blur]
    
    print('shape of rolling data: ', d4.shape)
    
    d5 = d4.interp(latitude=d1.latitude, longitude = d1.longitude, method= 'nearest')
    
    # extract only Tibet area using .sel
    do = xr.Dataset( {'hi': d1, 'lo':d5} ).isel(latitude = range(30,54), longitude = range(40, 72) )
    
    #.isel( latitude = range(20, 50)  )
    #.sel(longitude = slice(75,97.25), latitude = slice(42.75,26) )
    
    print(do)
    do.to_netcdf('data/kanto_input.nc')
    
    
    

# %%
#do['lo'][0].plot()

# %%
#do['hi'][0].plot()

# %% [markdown]
# ## Divide data into three sets
# - training
# - validating
# - testing
#
# Here random selection is used.
#
# 70% of data is used for training
#
# 60% of remaining 30% is used for validation
#
# 40% of remaining 30% is used for testing
#
# __there is no any rules how to divide, this is just a showcase__
#
# __data is then writen into three seperate files__
#
#
# ### techniques used
#
# > random
# > 
# > numpy .setdiff1d
# >
# > numpy .unique
# >
# > numpy .union1d
# >
# > xarray .isel (different with .sel)


# %%
area = 'kanto'
dinput = xr.open_dataset('data/'+area+'_input.nc')

# %%
dinput.lo[0].plot()
#n = 365
n = dinput['hi'].shape[0]
print('we have ', n, 'sample')

# %%
# separate data to three part: 1) training; 2) validation; 3) test
ii = np.arange(n)
n_train = int(round(.7*n))
print('extract: ', n_train, 'for training')

# %%
import random
itrain=[]
while len(itrain) !=  n_train :
   r=random.randint(0,n-1)
   if r not in itrain: itrain.append(r)

# %%
print( 'check len of training data: ', len(np.unique(itrain)), len(itrain))
print('get 70% of whole data to train: ', len(itrain))

# %%
i2 = np.setdiff1d(ii, itrain)
print('then we have remaining ', len(i2))

# %%
n_vt = len(i2)
n_val = int(round(.6*n_vt))

# %%
j1=[]
while len(j1) !=  n_val :
    r=random.randint(0, n_vt - 1)
    if r not in j1: j1.append(r)


# %%
ival = i2[j1]
itest = np.setdiff1d(i2, ival)

# %%
print(np.unique(np.union1d(itrain, np.union1d(ival, itest))).shape)
print(len(itrain) + len(ival) + len(itest))
# -

# %%

# %%
dtrain0 = dinput.isel(date=itrain)
dval0 = dinput.isel(date=ival)
dtest0 = dinput.isel(date=itest)


# =====
dtrain0.to_netcdf('data/'+area+'_train.nc')
dval0.to_netcdf('data/'+area+'_val.nc')
dtest0.to_netcdf('data/'+area+'_test.nc')















# %%
