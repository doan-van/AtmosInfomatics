# ---
# jupyter:
#   jupytext:
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
# # This is code to downscale rough-resolution temperature to high-resolution one
#
# ## This is test for Himalaya and Tibet region (to see how AI handle stiff terrain is intersting case study)
#
#
# ![image.png](attachment:b8c199f7-1bf9-4d71-b636-841997d453e8.png)
#
# (https://vivitravels.com/en/guides/little-tibet-and-himalaya/)
#

# %% [markdown]
# ## first let import libaries
#
# If there is necessity to install any libraries, do it.
#
# For example
#
# conda install scipy 
#

# %%
import numpy as np
import xarray as xr
import tensorflow as tf 
# all the layers used for U-net
from tensorflow.keras.layers import (Activation, BatchNormalization, Concatenate, Conv2D,
                                     Conv2DTranspose, Input, MaxPool2D)
from tensorflow.keras.models import Model
import tensorflow.keras.utils as ku
from tensorflow.keras.optimizers import Adam
import sys

# %% [markdown]
# ## Read input files (netcdf)
#  there are three type of datasets (explained in step 1)
#
# * first we normalize data (zero-mean, standard deviation)
# * In each kind of data: 
#
# X (predictors) having four dimensions (n_sample, y_axis, x_axis, n_variables)
#
# Y (preditant) having three or four dimensions (n_sample, y_axis, x_axis, n_variables (optional) )
#  


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

print('Shape of X_train: ', X_train.shape)
print('Shape of y_train: ', y_train.shape)
print('Shape of X_validation: ', X_val.shape)
print('Shape of y_validation: ', y_val.shape)
print('Shape of X_test: ', X_test.shape)
print('Shape of y_test: ', y_test.shape)

# %% [markdown]
# ## Define encoder and decorder functions
#
# ![image.png](attachment:da131011-6b36-4ab1-8d63-99ce8d1bc94a.png)
#
#
# https://www.geeksforgeeks.org/u-net-architecture-explained/
#
# With decoder UNet become different with normal CNN
#
# ### Enconder and decoder blocks combine series of convolution, activation, concaternate blocks


# %%
def conv_block(inputs, num_filters: int, kernel: tuple = (3,3), padding: str = "same",
               activation: str = "relu", kernel_init: str = "he_normal", l_batch_normalization: bool = True):
    """
    A convolutional layer with optional batch normalization
    :param inputs: the input data with dimensions nx, ny and nc
    :param num_filters: number of filters (output channel dimension)
    :param kernel: tuple indictating kernel size
    :param padding: technique for padding (e.g. "same" or "valid")
    :param activation: activation fuction for neurons (e.g. "relu")
    :param kernel_init: initialization technique (e.g. "he_normal" or "glorot_uniform")
    """
    x = Conv2D(num_filters, kernel, padding=padding, kernel_initializer=kernel_init)(inputs)
    if l_batch_normalization: x = BatchNormalization()(x)
    x = Activation(activation)(x)
    return x


# %%
def conv_block_n(inputs, num_filters, n=2, kernel=(3,3), padding="same", activation="relu", 
                     kernel_init="he_normal", l_batch_normalization=True):
    """
    Sequential application of two convolutional layers (using conv_block).
    """
    
    x = conv_block(inputs, num_filters, kernel, padding, activation,kernel_init, l_batch_normalization)
    for i in np.arange(n-1):
        x = conv_block(x, num_filters, kernel, padding, activation,kernel_init, l_batch_normalization)
    
    return x

# %%
def encoder_block(inputs, num_filters, kernel_maxpool: tuple=(2,2), l_large: bool=True):
    """
    One complete encoder-block used in U-net
    """
    if l_large: x = conv_block_n(inputs, num_filters, n=2)
    else: x = conv_block(inputs, num_filters) 
    p = MaxPool2D(kernel_maxpool)(x)
    return x, p

# %%
def decoder_block(inputs, skip_features, num_filters, kernel: tuple=(3,3), strides_up: int=2, padding: str= "same", 
                  activation="relu", kernel_init="he_normal", l_batch_normalization: bool=True):
    """
    One complete decoder block used in U-net (reverting the encoder)
    """
    x = Conv2DTranspose(num_filters, (strides_up, strides_up), strides=strides_up, padding="same")(inputs)
    x = Concatenate()([x, skip_features])
    x = conv_block_n(x, num_filters, 2, kernel, padding, activation, kernel_init, l_batch_normalization)
    
    return x


# %% [markdown]
# ### Define learning rate (need to learn more)

# %%
# define a earning-rate scheduler
def lr_scheduler(epoch, lr):
  if epoch < 5:
    return lr
  elif epoch >= 5 and epoch < 30:
    return lr * tf.math.exp(-0.1)
  elif epoch >= 30:
    return lr

# %%
#plt.plot([ lr_scheduler(e,5*10**(-4) ) for e in range(150)])

# %% [markdown]
# ## BUILDING U-NET HERE


# %%
batch_size = 32
epochs = 150
channels_start=56 
shape_in = X_train.shape[1:]

# %%
# parameters 
callback = tf.keras.callbacks.LearningRateScheduler(lr_scheduler)

# build model    
inputs = Input(shape_in)

""" encoder """
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

# %% [markdown]
# ## RUN U-NET HERE
#
# It will take a while to train model

# %%

if 1: 
    history = unet_model.fit(x=X_train, 
                             y=y_train, 
                             batch_size=batch_size,
                             epochs=epochs, 
                             callbacks=[callback],
                             validation_data=(X_val, y_val ),
                             verbose = 1 # dont show ====== if want to show =1
                             )
    # save model to ecmwf
    unet_model.save(area+'_small')
    
    print('Finished run')

# %% [markdown]
# ## Predict and verification

# %%
unet_model.summary()

# %%

# %%

# %%
