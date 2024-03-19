#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 12:22:23 2023

@author: doan
"""


import xarray as xr
import pandas as pd
import numpy as np
import glob, os, sys





for y in range(1940,2023)[:0]:
    ifile = 'data/'+str(y)+'.nc'
    ds = xr.open_dataset(ifile)


if 0:
    ifiles = sorted(glob.glob('data/*nc'))[:]
    
    ds = xr.open_mfdataset(ifiles)
    do = xr.Dataset()
    do['t2m'] = ds.t2m.groupby('time.month').mean() - 273.15
    do['pr'] = ds.tp.groupby('time.month').sum() * 1000
    #da = ds.groupby('time.month').mean()
    do.to_netcdf('climmean.nc')

lm = xr.open_dataset('landmask.nc').lsm[0] > 0.
ds = xr.open_dataset('climmean.nc').where(lm.values)
t = ds.t2m.where(lm.values)
p = ds.pr.where(lm.values)

py = p.sum(dim='month').where(lm.values)
pmin = p.min(dim='month').where(lm.values)
pmax = p.max(dim='month').where(lm.values)


ttrop = (t>=18).all(dim='month')

Af = ( ttrop & (p >= 60).all(dim='month'))
Am = ( ttrop & (pmin >= 100 - py / 25) & (pmin < 60))
As = ( ttrop & (pmin  < 100 - py / 25) & (pmin < 60))








