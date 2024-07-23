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

# %% [markdown]
# # This code to check u-net model
#

# %%
import tensorflow as tf
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

# %%

# %%
area = 'kanto'
dtest0 = xr.open_dataset('data/'+area+'_test.nc')

# normalize data
dtest = ( dtest0 - dtest0.mean() ) / dtest0.std()


# %%
X_test = np.expand_dims(dtest.lo.values,3)
y_test = dtest.hi.values

# %%


# %%
# load model and run
xmodel = tf.keras.models.load_model(area+'_small') 
xmodel.summary()

# %% [markdown]
# ## Look at procesess 
# to see each layers
#
# what they do
#
#

# %%
import json
summary = str(xmodel.to_json())
a = json.loads(summary)
al = a['config']['layers']

xlayers = xmodel.layers
n_xlayers = len(xlayers)

for i in range( n_xlayers )[:]:    
    print(i, 
          al[i]['class_name'], 
          al[i]['config']['name'], 
          al[i]['inbound_nodes']
          )

# %% [markdown]
# ### Low how they behave?

# %%
xlayers = xmodel.layers

l0 = X_test  # 0 layer = input layer
layx = {0:l0}  # python dictionary type

for i in range(n_xlayers)[1:]:
    
    layer = xmodel.layers[i]
    if i == 20:  # this is concatenate layer 
        l0 = layer( (layx[i-1], layx[14] ) )

    elif i == 28: # this is concatenate layer 
        l0 = layer( (layx[i-1], layx[10] ) )

    elif i == 36: # this is concatenate layer 
        l0 = layer( (layx[i-1], layx[6] ) )        
        
    else: l0 = layer(l0)
    
    layx[i] = l0

# %%
X_test.shape


# %%
plt.imshow(X_test[0])

# %%
layx[43][0]

plt.imshow( layx[43][0] )

# %%


for ilay in list(layx.keys())[1:2]:
    l0 = layx[ilay]
    #print(ilay, len(layer))
    #print(l0.shape) # the first image from X_test

    lshape = l0[0].shape
    for k in range(lshape[-1])[:]:
        print(k)
        b = l0[0,:,:,k]
        plt.imshow(b)
        plt.show()


# %%
print(layx.keys())

# %%

xlayers = xmodel.layers

l0 = X_test  # 0 layer = input layer
layx = {0:l0}  # python dictionary type

for i in range(n_xlayers)[1:]:
    
    layer = xmodel.layers[i]
    if i == 20:  # this is concatenate layer 
        l0 = layer( (layx[i-1], layx[14] ) )

    elif i == 28: # this is concatenate layer 
        l0 = layer( (layx[i-1], layx[10] ) )

    elif i == 36: # this is concatenate layer 
        l0 = layer( (layx[i-1], layx[6] ) )        
        
    else: l0 = layer(l0)
    
    lshape = l0[0].shape
    for k in range(lshape[-1])[:0]:
        print(k)
        b = l0[0,:,:,k]
        plt.imshow(b)
        plt.show()
        
    layx[i] = l0
    
    print(i, al[i]['class_name'])
    if al[i]['class_name'] == 'Conv2D':
        print(i, layer.name, ': ', len(layer.weights) )
        w = layer.weights
        print(w[0].shape)
        #plt.imshow(w[0][:,:,0,0])
        #plt.show()
    
    
    
    #for w in layer.get_weights():
    #    print(w)

# %%

