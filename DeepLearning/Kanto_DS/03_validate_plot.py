#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
import tensorflow as tf 

import cartopy
import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
import os, glob, sys


# %%
area = 'kanto'
dtrain0 = xr.open_dataset('data/'+area+'_train.nc')
dval0 = xr.open_dataset('data/'+area+'_val.nc')
dtest0 = xr.open_dataset('data/'+area+'_test.nc')


# %%
# normalize data 
def datnorm(d): 
    return (d - d.mean()) / d.std() 


# %%
# normalize data
dtrain, dval, dtest = datnorm(dtrain0), datnorm(dval0), datnorm(dtest0)

# %%
int_data = dtrain['lo'].values
X_train = np.expand_dims(int_data,3)
y_train = dtrain['hi'].values

# %%
X_val = np.expand_dims(dval['lo'].values,3)
y_val = dval['hi'].values

# %%
X_test = np.expand_dims(dtest['lo'].values,3)
y_test = dtest['hi'].values

# %%

if 1: 
    # load model and run
    xmodel = tf.keras.models.load_model(area+'_small') 
    
    #print(xmodel.summary())
    
    y_pred_val = xmodel.predict(X_val, verbose=1)
    y_pred_test = xmodel.predict(X_test, verbose=1) 

    # return values to Kelvin 
    x1, x2 = dtest0.mean()['hi'], dtest0.std()['hi']
    y_pred_test_r = y_pred_test*x2.values + x1.values

    x1, x2 = dval0.mean()['hi'], dval0.std()['hi']
    y_pred_val_r = y_pred_val*x2.values + x1.values
    

    do = xr.Dataset( )
    do['pred'] = ( ('dat', 'latitude', 'longitude'), y_pred_test_r.squeeze())  
    do.coords['latitude'] = dtest0.latitude
    do.coords['longitude'] = dtest0.longitude
    do['real'] = dtest0['hi']

    dv = xr.Dataset( )
    dv['pred'] = ( ('dat', 'latitude', 'longitude'), y_pred_val_r.squeeze())  
    dv.coords['latitude'] = dval0.latitude
    dv.coords['longitude'] = dval0.longitude
    dv['real'] = dval0['hi']

    odir = 'output/'
    if not os.path.exists(odir): os.makedirs(odir)
    do.to_netcdf(odir+'prediction.nc')
    dv.to_netcdf(odir+'validation.nc')
    do.close()
    dv.close()
    
    #do.pred[0].plot()
    #plt.show()
    #dtest0['hi'][0].plot()
    #plt.show()
    #bias = do.pred - dtest0.hi.values
    #bias[0].plot()
    #print(bias.mean())   

    print(do)
    print(dv)
    
    do['real'][0].plot()
    plt.show()
    do['pred'][0].plot()

# %%
if 1:


    lat, lon = do.latitude.values, do.longitude.values
    ntime = 0
    zz = [ dtest0['lo'][ntime] - 273.15, do['pred'][ntime] - do['real'][ntime], 
          do['pred'][ntime]-273.15, do['real'][ntime]-273.15 ] 
    
    
    lat2d, lon2d = np.meshgrid(lon, lat)

    
    fig = plt.figure(figsize=(8,8))
    
    level = np.arange(0., 20., .5)
    levels = [ level,  np.linspace(-5, 5, 6), level, level ] 
    
    
    for i in range(4):
        
        ax = plt.axes( [ [.1, .6, .1, .6 ][i] , 
                        [.6,.6,.1,.1][i], 
                        .4, .4 ], projection = ccrs.PlateCarree())
        
        z = zz[i]
        print(z.max())
    
        cm1 = 'viridis'
        cmap = [ plt.colormaps[ cm ] for cm in [cm1, 'bwr', cm1, cm1] ][i]
        
        norm = mpl.colors.BoundaryNorm(levels[i], cmap.N)  
        t = ax.pcolormesh(lat2d, lon2d, z, cmap=cmap, norm=norm)
    
        #cax = fig.add_axes([0.92, 0.3, 0.02, 0.4])
        #cbar = plt.colorbar(orientation="vertical", ticks=lvl[1::2])
        #cbar.ax.tick_params(labelsize=12)
    
    
        fig.colorbar(t, orientation='horizontal')
    
        ax.text( .0, 1.02, 
                ['Low resolution', 'Error (High-res  prediction minus high-res real)', 'High resolution (prediction)', 'High resolution (real)' ][i], 
                fontsize = 15, 
                fontweight = 'bold',
                transform = ax.transAxes)

# %%
