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
#

# %%
import sys, os, glob
import pandas as pd
import json
import matplotlib.pyplot as plt


# %%
idir = 'download/'
ff = glob.glob(idir+'*.json')

# %%
a = pd.read_csv('list_id.csv', index_col=2)
print(a.head())


# %%
def plot_hythergraph(temperature_max, temperature_min, precipitation, title):
    # plotting
    # Example monthly climate data
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    lab1, lab2, lab3 = 'Max Temperature (°C)', 'Min Temperature (°C)', 'Precipitation (mm)'
    tit1 = 'Hythergraph: Monthly Temperature and Precipitation\n'
    xlab, ylab1, ylab2 = 'Month', 'Temperature (°C)', 'Precipitation (mm)'


    # Create figure and axis
    fig = plt.figure(figsize= [6,4] )
    ax1 = plt.axes( [.15,.2,.7,.7] )

    # Plot temperature data
    ax1.plot(months, temperature_max, 'o--', color='darkred', label=lab1)
    ax1.plot(months, temperature_min, 'o--', color='lightcoral', label=lab2)
    ax1.set_xlabel(xlab)
    ax1.set_ylabel(ylab1, color='red')
    ax1.tick_params(axis='y', labelcolor='red')

    # Create a second y-axis to plot precipitation
    ax2 = ax1.twinx()
    ax2.bar(months, precipitation, alpha=0.3, color='green', label=lab3)
    ax2.set_ylabel(ylab2, color='green')
    ax2.tick_params(axis='y', labelcolor='green')

    # Add title and show plot

    plt.title(title)

    fig.legend(loc='lower left', 
               fontsize=8,
               ncols = 3, bbox_to_anchor=(0.1, -0.0))


    fig.tight_layout()
    plt.savefig(ofilep, dpi = 100)        
    #plt.close()

# %%
print(ff[:2])

# %%
lalo = []
for f in ff[:1]:
    cindex = float(f.split('/')[1].split('_')[0])
    
    b = a.loc[cindex]
    city, country = b['City'], b['Country']
    print(city, country)
    
    try:
        
        with open(f) as json_file:
            d = json.load(json_file)
        print(d)
        
        df = pd.DataFrame(  d['city']['climate']['climateMonth']).set_index('month')
        print(df)
        lat, lon = float(d['city'][ 'cityLatitude' ]), float(d['city'][ 'cityLongitude' ])
        lalo.append( [cindex, lat, lon, b['City'], b['Country'] ] )
        
        do = pd.DataFrame( [ pd.to_numeric(df[c], errors='coerce' ) for c in [ 'maxTemp', 'minTemp', 'meanTemp', 'rainfall'] ]).T
        
        odir1 = 'data/'+country+'/'
        odir2 = 'fig/'+country+'/'
        for odir in [odir1, odir2]: 
            if not os.path.exists(odir): os.makedirs(odir)
        

        ofile = odir1 + '/%.0f'% cindex+ '_'+city+  '.csv'
        ofilep = odir2 + '/%.0f'% cindex+ '_'+city+  '.png'
        
        do.to_csv(ofile)
        
    
        if 1:
            temperature_max = do.maxTemp.values
            temperature_min = do.minTemp.values
            precipitation = do.rainfall.values
            title = tit1+b['City'] + ' ('+b['Country']+')'
            plot_hythergraph(temperature_max, temperature_min, precipitation, title)

    except:
        print('have problem')

# %%
dll = pd.DataFrame(lalo, columns=['cityindex', 'latitude', 'longitude', 'city', 'country']).set_index('cityindex')
dll.to_csv('latlon.csv')
