import numpy as np
import xarray as xr
import pandas as pd
print('===')
# ## Prepare input data for Unet
# =======
# preparing data

if 0:
    ds = xr.open_dataset('/Users/doan/Desktop/2023_2t_era5_land.nc')
    tb = ds.sel(longitude = slice(65,110), latitude = slice(50,15) )
    tb0 = tb.groupby('time.date').mean()
    tb0.date.values[:]  = pd.to_datetime(tb0.date.values).strftime('%Y%m%d')  #pd.to_datetime(tb0.date.values)
    tb0.to_netcdf('data/tb.nc')


# Put data together
if 0:
    
    ds = xr.open_dataset('data/tb.nc')['t2m']
    print('shape of original data: ', ds.shape)
    
    
    # get "high-resolution data"
    # because the original data is at high-resolution, here reduce it
    n_int = 7
    # https://docs.xarray.dev/en/latest/user-guide/interpolation.html
    d1 = ds.interp(latitude=ds.latitude[::n_int], longitude = ds.longitude[::n_int])
    
    
    print('shape of interpolated data: ', d1.shape)
    
    n_blur = 7
    # rolling https://docs.xarray.dev/en/stable/generated/xarray.DataArray.rolling.html
    d2 = d1.rolling( {'latitude':n_blur,'longitude':n_blur}, center=True).mean()
    
    print('shape of rolling data: ', d2.shape)
    
    
    d4 = d2[:, ::n_blur,::n_blur]
    
    print('shape of rolling data: ', d4.shape)
    
    d5 = d4.interp(latitude=d1.latitude, longitude = d1.longitude, method= 'nearest')
    
    # extract only Tibet area using .sel
    do = xr.Dataset( {'hi': d1, 'lo':d5} ).sel(longitude = slice(75,97.25), latitude = slice(42.75,26) )
    
    print(do)
    do.to_netcdf('data/tb_input.nc')
    
    
    
    
    
    
dinput = xr.open_dataset('data/tb_input.nc')

dinput.lo[0].plot()
#n = 365
n = dinput['hi'].shape[0]
print('we have ', n, 'sample')

# separate data to three part: 1) training; 2) validation; 3) test
ii = np.arange(n)
n_train = int(round(.7*n))
print('extract: ', n_train, 'for training')

import random
itrain=[]
while len(itrain) !=  n_train :
   r=random.randint(0,n-1)
   if r not in itrain: itrain.append(r)

print( 'check len of training data: ', len(np.unique(itrain)), len(itrain))
print('get 70% of whole data to train: ', len(itrain))

i2 = np.setdiff1d(ii, itrain)
print('then we have remaining ', len(i2))

n_vt = len(i2)
n_val = int(round(.6*n_vt))

j1=[]
while len(j1) !=  n_val :
    r=random.randint(0, n_vt - 1)
    if r not in j1: j1.append(r)


ival = i2[j1]
itest = np.setdiff1d(i2, ival)

print(np.unique(np.union1d(itrain, np.union1d(ival, itest))).shape)
print(len(itrain) + len(ival) + len(itest))
# -



# +
dtrain0 = dinput.isel(date=itrain)
dval0 = dinput.isel(date=ival)
dtest0 = dinput.isel(date=itest)


# =====
dtrain0.to_netcdf('data/tb_train.nc')
dval0.to_netcdf('data/tb_val.nc')
dtest0.to_netcdf('data/tb_test.nc')














