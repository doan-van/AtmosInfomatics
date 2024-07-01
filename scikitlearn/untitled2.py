#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 14:53:12 2024

@author: doan
"""

import xarray as xr

for y in range(1991,2024)[:1]:
    f = '/Volumes/ERA5_DL/'+str(y)+'_2t_era5_land.nc'
    ds = xr.open_dataset(f)
    jp = ds.sel(longitude=slice(130 ,145), latitude=slice(41, 30))
    tb = ds.sel(longitude=slice(68 ,110), latitude=slice(41, 25))
    
    odir = 'era5landtemp/'
    jp.to_netcdf(odir + '/jp_'+str(y)+'.nc')   
    tb.to_netcdf(odir + '/tb_'+str(y)+'.nc')
    
    
    
    
    