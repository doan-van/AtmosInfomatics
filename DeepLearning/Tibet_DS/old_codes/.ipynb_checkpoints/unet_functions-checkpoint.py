#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import xarray as xr
import tensorflow as tf 
from tensorflow.keras.layers import (Activation, BatchNormalization, Concatenate, Conv2D,
                                     Conv2DTranspose, Input, MaxPool2D)
from tensorflow.keras.models import Model
import datetime as dt


# https://www.tensorflow.org/api_docs/python/tf/keras/layers/Conv2D


def z_norm_data(data, mu=None, std=None, dims=None, return_stat=False):
    """
    Perform z-score normalization on the data
    :param data: the data-array
    :param mu: the mean used for normalization (set to False if calculation from data is desired)
    :param std: the standard deviation used for normalization (set to False if calculation from data is desired)
    :param dims: list of dimension over which statistical quantities for normalization are calculated
    :param return_stat: flag if normalization statistics are returned
    :return: the normalized data
    """
    if mu is None and std is None:
        if not dims:
            dims = list(data.dims)
        mu = data.mean(dim=dims)
        std = data.std(dim=dims)
        
    data_out = (data-mu)/std
    
    if return_stat:
        return data_out, mu, std
    else:
        return data_out   
    
    

def preprocess_data_for_unet(dataset, daytime=12, opt_norm={}):
    """
    Preprocess the data for feeding into the U-net, i.e. conversion to data arrays incl. z-score normalization
    :param dataset: the dataset obtained from the database
    :param daytime: daytime in UTC for temporal slicing
    :param opt_norm: dictionary holding data for z-score normalization of data ("mu_in", "std_in", "mu_tar", "std_tar")
    :return: normalized data ready to be fed to U-net model
    """
    norm_dims_t = ["time"]                   # normalization of 2m temperature for each grid point
    norm_dims_z = ["time", "lat", "lon"]     # 'global' normalization of surface elevation
    
    # slice the dataset
    dsf = dataset.sel(time=dt.time(daytime))
    
    # retrieve and normalize input and target data
    if not opt_norm:
        t2m_in, t2m_in_mu, t2m_in_std  = z_norm_data(dsf["t2m_in"], dims=norm_dims_t, return_stat=True)
        t2m_tar, t2m_tar_mu, t2m_tar_std = z_norm_data(dsf["t2m_tar"], dims=norm_dims_t, return_stat=True)
    else: 
        t2m_in = z_norm_data(dsf["t2m_in"], mu=opt_norm["mu_in"], std=opt_norm["std_in"])
        t2m_tar = z_norm_data(dsf["t2m_tar"], mu=opt_norm["mu_tar"], std=opt_norm["std_tar"])
        
    z_in, z_tar = z_norm_data(dsf["z_in"], dims=norm_dims_z), z_norm_data(dsf["z_tar"], dims=norm_dims_z)

    in_data = xr.concat([t2m_in, z_in, z_tar], dim="variable")
    tar_data = xr.concat([t2m_tar, z_tar], dim="variable")

    # re-order data
    in_data = in_data.transpose("time",...,"variable")
    tar_data = tar_data.transpose("time",...,"variable")
    if not opt_norm:
        opt_norm = {"mu_in": t2m_in_mu, "std_in": t2m_in_std,
                    "mu_tar": t2m_tar_mu, "std_tar": t2m_tar_std}
        return in_data, tar_data, opt_norm
    else:
        return in_data, tar_data
    
    
    

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
    if l_batch_normalization:
        x = BatchNormalization()(x)
    x = Activation(activation)(x)
    
    return x

def conv_block_n(inputs, num_filters, n=2, kernel=(3,3), padding="same", activation="relu", 
                     kernel_init="he_normal", l_batch_normalization=True):
    """
    Sequential application of two convolutional layers (using conv_block).
    """
    
    x = conv_block(inputs, num_filters, kernel, padding, activation,
                   kernel_init, l_batch_normalization)
    for i in np.arange(n-1):
        x = conv_block(x, num_filters, kernel, padding, activation,
                       kernel_init, l_batch_normalization)
    
    return x

def encoder_block(inputs, num_filters, kernel_maxpool: tuple=(2,2), l_large: bool=True):
    """
    One complete encoder-block used in U-net
    """
    if l_large:
        x = conv_block_n(inputs, num_filters, n=2)
    else:
        x = conv_block(inputs, num_filters)
        
    p = MaxPool2D(kernel_maxpool)(x)
    
    return x, p

def decoder_block(inputs, skip_features, num_filters, kernel: tuple=(3,3), strides_up: int=2, padding: str= "same", 
                  activation="relu", kernel_init="he_normal", l_batch_normalization: bool=True):
    """
    One complete decoder block used in U-net (reverting the encoder)
    """
    
    x = Conv2DTranspose(num_filters, (strides_up, strides_up), strides=strides_up, padding="same")(inputs)
    x = Concatenate()([x, skip_features])
    x = conv_block_n(x, num_filters, 2, kernel, padding, activation, kernel_init, l_batch_normalization)
    
    return x





def build_unet(input_shape, channels_start=56, z_branch=False):
    
    inputs = Input(input_shape)
    
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
    if z_branch:
        output_z = Conv2D(1, (1, 1), kernel_initializer="he_normal", name="output_z")(d3)

        model = Model(inputs, [output_temp, output_z], name="t2m_downscaling_unet_with_z")
    else:    
        model = Model(inputs, output_temp, name="t2m_downscaling_unet")
    
    return model



# define a earning-rate scheduler
def lr_scheduler(epoch, lr):
  if epoch < 5:
    return lr
  elif epoch >= 5 and epoch < 30:
    return lr * tf.math.exp(-0.1)
  elif epoch >= 30:
    return lr







