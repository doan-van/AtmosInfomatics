#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  8 14:57:28 2024

@author: doan
"""

import numpy as np
import xarray as xr
#import ecubevis as ecv
#import climetlab as cml
import tensorflow as tf 
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
# all the layers used for U-net
from tensorflow.keras.layers import (Activation, BatchNormalization, Concatenate, Conv2D,
                                     Conv2DTranspose, Input, MaxPool2D)
from tensorflow.keras.models import Model
import tensorflow.keras.utils as ku
from tensorflow.keras.optimizers import Adam
import sys
from unet_functions import build_unet, lr_scheduler, preprocess_data_for_unet, encoder_block, decoder_block, conv_block




# =======
# preparing data
if 0:
    ds = xr.open_dataset('/Users/doan/Desktop/2023_2t_era5_land.nc')
    tb = ds.sel(longitude = slice(65,110), latitude = slice(50,15) )
    tb0 = tb.groupby('time.date').mean()
    tb0.date.values[:]  = pd.to_datetime(tb0.date.values).strftime('%Y%m%d')  #pd.to_datetime(tb0.date.values)
    tb0.to_netcdf('tb.nc')


#ifile = '/Users/doan/Desktop/2023_2t_era5_land.nc'
#ds = xr.open_dataset(ifile)['t2m']

ds = xr.open_dataset('tb.nc')['t2m']

n = 7
d1 = ds.interp(latitude=ds.latitude[::n], longitude = ds.longitude[::n])
d2 = d1.rolling( {'latitude':7,'longitude':7}, center=True).mean()

#d3 = xr.Dataset( {'hi': d1, 'lo':d2} ).sel(longitude = slice(73,100), latitude = slice(40,25) )
d3 = xr.Dataset( {'hi': d1, 'lo':d2} ).sel(longitude = slice(74,96), latitude = slice(41.75,25) )


# separate data to three part: 1) training; 2) validation; 3) test
n = ds.shape[0]
ii = np.arange(n)
i1 = np.random.randint(n, size=int(.7*n))
i2 = np.setdiff1d(ii, i1)
j1 = np.random.randint(i2.size, size=int(.6*i2.size))
i21 = i2[j1]
i22 = np.setdiff1d(i2, i21)

#np.unique(np.union1d(i1, np.union1d(i21, i22))).shape

dtrain0 = d3.isel(date=i1)
dval0 = d3.isel(date=i21)
dtest0 = d3.isel(date=i22)


# normalize data

drs = []
for d in [dtrain0, dval0, dtest0 ]:
    #xmin, xrange = d.min(), d.max() - d.min()
    #drs.append( (d - xmin) / xrange)
    x1, x2 = d.mean(), d.std()
    drs.append( (d - x1) / x2 )


dtrain, dval, dtest = drs

int_data = dtrain.lo.values
X_train = np.expand_dims(int_data,3)
y_train = dtrain.hi.values

X_val = np.expand_dims(dval.lo.values,3)
y_val = dval.hi.values

X_test = np.expand_dims(dtest.lo.values,3)
y_test = dtest.hi.values


# running unet using unet_functions
rununet = 1
if rununet:
    
    #shape_in = (96, 128, 3)
    # parameters 
    batch_size = 32
    epochs = 150
    
    
    shape_in = X_train.shape[1:]
        
    callback = tf.keras.callbacks.LearningRateScheduler(lr_scheduler)
    
    # build model    
    inputs = Input(shape_in)
    
    """ encoder """
    channels_start=56
    #channels_start=16
    
    s1, e1 = encoder_block(inputs, channels_start, l_large=True)
    s2, e2 = encoder_block(e1, channels_start*2, l_large=False)
    s3, e3 = encoder_block(e2, channels_start*4, l_large=False)
    
    """ bridge encoder <-> decoder """
    b1 = conv_block(e3, channels_start*8)
    
    """ decoder """
    d1 = decoder_block(b1, s3, channels_start*4)
    
    
    d2 = decoder_block(d1, s2, channels_start*2)
    d3 = decoder_block(d2, s1, channels_start)
    
    output_temp = Conv2D(1, (1,1), kernel_initializer="he_normal", name="output_temp")(d3)
    
    unet_model= Model(inputs, output_temp, name="t2m_downscaling_unet")
    
    #ku.plot_model(unet_model, show_shapes=True)
    
    unet_model.compile(optimizer=Adam(learning_rate=5*10**(-4)), loss="mae")
    
    if 1:
        history = unet_model.fit(x=X_train, 
                                 y=y_train, 
                                 batch_size=batch_size,
                                 epochs=epochs, 
                                 callbacks=[callback],
                                 validation_data=(X_val, y_val )
                                 )
            
        # save model to ecmwf
        
        unet_model.save('tb_small')
    



if 1: # loead model and run
    xmodel = tf.keras.models.load_model('tb_small') 
    # get the test data first
    print(xmodel.summary())
    
    
    #y_pred_val = xmodel.predict(X_val, verbose=1)
    y_pred_test = xmodel.predict(X_test, verbose=1) 
    
    
    x1, x2 = dtest0.mean()['hi'], dtest0.std()['hi']
    y_pred_test_r = y_pred_test*x2.values + x1.values
    
    do = xr.Dataset( )
    do['pred'] = ( ('dat', 'latitude', 'longitude'), y_pred_test_r.squeeze())  
    do.coords['latitude'] = dtest0.latitude
    do.coords['longitude'] = dtest0.longitude
    
    
    do.pred[0].plot()
    plt.show()
    dtest0['hi'][0].plot()
    plt.show()
    bias = do.pred - dtest0.hi.values
    bias[0].plot()
    print(bias.mean())    
    
    
    
    

        

    


    
    











