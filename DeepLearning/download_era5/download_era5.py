#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 19 17:37:28 2023
https://codes.ecmwf.int/grib/param-db/

@author: doan
"""


#import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
import os, sys, glob
from collections import namedtuple
import xarray as xr
#import mpl_toolkits.basemap
#===========================



#dates = pd.date_range('2009-01-01','2023-02-01', freq='MS')
#dates = pd.date_range('2020-07-01','2023-02-01', freq='MS')

dates = pd.date_range('2012-12-01','2013-02-01', freq='MS')[:]


dates = pd.date_range('1980-01-01','2024-02-01', freq='MS')[::-1][:]


if 1:
    
    print('download_japan')
    import cdsapi
    c = cdsapi.Client()

    dom = 'jp'
    area = '46/128/30/150' # NWSE
    odir = 'era5_hrldas/' +dom
    if not os.path.exists(odir): os.makedirs(odir) 
    n = 0
    
    for i, (d, d1) in enumerate( zip( dates[n:-1], dates[n+1:])):
        ed = d1 - pd.Timedelta('1 day')
        print(d)    
        date = '/'.join([ a.strftime('%Y%m%d') for a in pd.date_range(d,ed, freq='D')])
        dateland = d.strftime('%Y%m%d') +'/'+ed.strftime('%Y%m%d')

        ofile = odir + '/' + d.strftime('%Y%m.nc')
        print(ofile)

        year = [ d.strftime('%Y') ]
        month =  [ d.strftime('%m') ]
        day = list(range(1,32))
        if 1:
            c.retrieve(
                'reanalysis-era5-single-levels',
                {   'product_type':'reanalysis',
                    'format': 'netcdf',
                    'variable': [
                        '2m_temperature', 'total_precipitation',
                    ],
                    'year':  year,
                    'month': month,
                    'day': day,
                    'time': [0,3,6,9,12,15,18,21 ],
                    'area':area,
                    #'grid': [1, 1],
                },
                ofile)














#==================================================================:::
# This script is to download ERA5 data used for HRLDAS downscaling :::
#==== monthly basic

if 0: # download era5

    print('download_x')
    import cdsapi
    c = cdsapi.Client()


    #dom = 'global'
    #area = '90/-180/-90/180' # NWSE
    #odir0 = '/media/doan/Backup_disk/share_DATA/era5_hrldas/' +dom
    
    dom = 'dbsh'
    area = '25/98/17/110' # NWSE
    odir0 = 'era5_hrldas/' +dom
    
    
    #dom = 'asia'
    #area = '46/90/-15/150' # NWSE
    #odir0 = '/media/doan/Backup_disk/share_DATA/era5_hrldas/' +dom
    
    
    by = '1' # each hour
    n = 0
    for i, (d, d1) in enumerate( zip( dates[n:-1], dates[n+1:])):
        ed = d1 - pd.Timedelta('1 day')
        print(d)    
        date = '/'.join([ a.strftime('%Y%m%d') for a in pd.date_range(d,ed, freq='D')])
        dateland = d.strftime('%Y%m%d') +'/'+ed.strftime('%Y%m%d')

        if 1:
            
            pair = namedtuple("pair", ["long", "short"])
            variables = [pair("surface_solar_radiation_downwards", "ssrd"), 
                         pair("surface_thermal_radiation_downwards", "strd"),
                         pair("surface_pressure", "sp"), 
                         pair("total_precipitation", "tp"), 
                         #===================================================
                         pair('skin_temperature', 'skt'),     # for setup file
                         pair('snow_depth','sde'),  # for setup file
                         pair('soil_temperature_level_1', 'stl1'),  # for setup file
                         pair('soil_temperature_level_2', 'stl2'),  # for setup file
                         pair('soil_temperature_level_3', 'stl3'), 
                         pair('soil_temperature_level_4', 'stl4'),
                         pair('volumetric_soil_water_layer_1', 'swvl1'), 
                         pair('volumetric_soil_water_layer_2', 'swvl2'), 
                         pair('volumetric_soil_water_layer_3', 'swvl3'), 
                         pair('volumetric_soil_water_layer_4', 'swvl4'),
                         pair('2m_dewpoint_temperature', '2d'),
                         pair('2m_temperature', '2t')
                         ]
            
            # end prepare
            for var in variables[:]:
                odir = odir0 + '/land/' + var.short + '/'
                if not os.path.exists(odir): os.makedirs(odir) 
                lev = '0'
                ofile = odir + var.short + '_lev'+lev+'_'+d.strftime('%Y%m.nc')
                
                print(ofile, date)
        
                c.retrieve(
                'reanalysis-era5-single-levels',
                {
                    'product_type':'reanalysis',
                    'format': 'netcdf', #dformat,
                    'variable':var.long, 
                    'date':dateland,
                    'area':area,
                    'time':'00/to/23/by/'+by,
                },
                ofile )
    
    
    
        if 1:
            pair = namedtuple("pair", ["long", "short", "id"])
            variables = [
                         pair("Temperature", "t","130"), 
                         pair("U component of wind", "u","131"),
                         pair("V component of wind", "v","132"), 
                         pair("Specific humidity", "q","133"), 
                         #pair('Geopotential', 'z', '129')
                         ]
            

            for var in variables[:]:
                odir = odir0 + '/air/' + var.short + '/'
                if not os.path.exists(odir): os.makedirs(odir) 
                
                levelist = '136'
                lev = levelist
                ofile = odir + var.short + '_lev'+lev+'_'+d.strftime('%Y%m.nc')
                
                print(ofile, date)
                c.retrieve('reanalysis-era5-complete', { # Requests follow MARS syntax
                                                         # Keywords 'expver' and 'class' can be dropped. They are obsolete
                                                         # since their values are imposed by 'reanalysis-era5-complete'
                        'date'    : date, 
                        'levelist': levelist,               # 1 is top level, 137 the lowest model level in ERA5. Use '/' to separate values.
                        'levtype' : 'ml',
                        'param'   : var.id,                 # Full information at https://apps.ecmwf.int/codes/grib/param-db/
                                                            # The native representation for temperature is spherical harmonics
                        'stream'  : 'oper',                  # Denotes ERA5. Ensemble members are selected by 'enda'
                        'time'    : '00/to/23/by/1',         # You can drop :00:00 and use MARS short-hand notation, instead of '00/06/12/18'
                        'type'    : 'an',
                        'grid'    : '0.1/0.1',               # Latitude/longitude. Default: spherical harmonics or reduced Gaussian grid
                        'format'  : 'netcdf',                # Output needs to be regular lat-lon, so only works in combination with 'grid'!
                        'area':area,
                    }, 
                           ofile)

















