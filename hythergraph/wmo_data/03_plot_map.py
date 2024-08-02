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
"""
Created on Sun May 24 14:03:15 2020

@author: doan
"""


# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

# %%
import numpy as np
import pandas as pd
#from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LinearSegmentedColormap, PowerNorm
import sys

# %%

# %%
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy


# %%
if 1:
    
    df = pd.read_csv('latlon.csv', index_col=0)
    lat, lon = df['latitude'].values, df['longitude'].values
    lon = np.where(lon<0, lon+360, lon)
    proj = ccrs.PlateCarree(central_longitude=150)
    #proj._threshold /= 10
    #proj = ccrs.Robinson(central_longitude=145)
    #proj = ccrs.Mollweide(central_longitude=145, globe=None)
    

    plt.figure(figsize=(10, 6))
    ax = plt.axes(projection= proj )
    
    ax.set_extent([-90, 300, -65, 75], crs=ccrs.PlateCarree())
    
    #ax.coastlines() #resolution='10m',lw=.1)
    #sys.exit()
    #ax.gridlines()
    ax.stock_img()
    ax.scatter(lon, lat, s = 1, 
               color = 'r',
               transform=ccrs.Geodetic())
    #ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.5,lw=.3)
    #ax.outline_patch.set_linewidth(.5)
    #sys.exit()
    plt.savefig('city_map.png', dpi = 100)


# %%
if 0:
    
    df = pd.read_csv('latlon.csv', index_col=4)
    
    for dx in list(df.groupby(df.index))[:]:
        country, d = dx
        print(d)
        lat, lon = d['latitude'].values, d['longitude'].values
        
        #lon = np.where(lon<0, lon+360, lon)
        proj = ccrs.PlateCarree(central_longitude=150)
    

        plt.figure(figsize=(10, 6))
        ax = plt.axes(projection= proj )
        extent = [ lon.min() - 5, lon.max()+5, lat.min() - 5, lat.max()+5]
    
        ax.set_extent(extent, crs=ccrs.PlateCarree())
    
        ax.stock_img()
        
        for i, r in d.iterrows():
            la, lo = r['latitude'], r['longitude']
            #ax.scatter(lo, la, s = 10, color = 'r',transform=ccrs.Geodetic())

            ax.text(lo, la, r['city'], 
                   color = 'r',
                   ha = 'center',
                   fontsize=12,
                   transform=ccrs.Geodetic())
            
        plt.savefig('fig/'+country+'/'+'city_map.png', dpi = 100)
        
        #ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.5,lw=.3)
        #ax.outline_patch.set_linewidth(.5)
    #sys.exit()
    #plt.savefig('city_map.png', dpi = 100)

# %%

# %%

