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
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LinearSegmentedColormap, PowerNorm
import sys, os, glob

# %% [markdown]
# # This is sourse code for Koppen

# %%
koppenDict = {
    "Af": 1,"Am": 2,"Aw": 3,
    "BWh": 4, "BWk": 5, "BSh": 6, "BSk": 7,
    "Csa": 8, "Csb": 9, "Csc": 10, "Cwa": 11, "Cwb": 12, "Cwc": 13, "Cfa": 14, "Cfb": 15, "Cfc": 16,
    "Dsa": 17, "Dsb": 18, "Dsc": 19, "Dsd": 20, "Dwa": 21, "Dwb": 22, "Dwc": 23, "Dwd": 24, "Dfa": 25, "Dfb": 26,
    "Dfc": 27, "Dfd": 28,
    "ET": 29, "EF": 30
}

# %%
ifiles = sorted(glob.glob('data_temp_prcp/*/*/*.csv'))

# %%
ds = pd.read_csv('list_of_stations_2.csv', index_col=[0,1,2]).sort_index()
ds['koppen'] = ''

# %%

# %%
from koppen_class import koppen_vd

ts, pr = [], []
ds
for iff, f in enumerate(ifiles[:]):
    if np.mod(iff, 1) == 0:
        df = pd.read_csv(f, index_col=0)

        c0, c1, c2 = f.split('/')[1], f.split('/')[2], f.split('/')[-1][:-10]
        temp, precip = df['Temperature'].values, df['Precipitation'].values
        
        south = ds.loc[(c0, c1, c2), 'latitude'].values[0] < 0
        kop = koppen_vd(precip, temp, south=south) 

        ds.loc[ (c0, c1, c2), 'koppen' ] = kop
        ts.append(temp)
        pr.append(precip)
        
ts, pr = np.array(ts), np.array(pr)
ds.to_csv('koppen.csv')

# %%

# %% [markdown]
# # Plot hythergraph
# ![image.png](attachment:1b8b4230-d64f-4953-884e-09906abd1942.png)

# %%
for iff, f in enumerate(ifiles[:0]):
    if np.mod(iff, 1) == 0:
        df = pd.read_csv(f, index_col=0)
        c0, c1, c2 = f.split('/')[1], f.split('/')[2], f.split('/')[-1][:-10]
        temp, precip = df['Temperature'].values, df['Precipitation'].values
        fig = plot_hythergraph( temp, precip, c2+' (' +c1+')')
        odir = 'fig/'+c0+'/'+c1+'/'
        
        if not os.path.exists(odir): os.makedirs(odir)
        ofile = odir + c2+'.png'
        plt.savefig(ofile, dpi = 100)        
        plt.close()
        

# %% [markdown]
# # Calculate Koppen and plot
#

# %%
koppenDict = {
    "Af": 1,
    "Am": 2,
    "Aw": 3,
    "BWh": 4, 
    "BWk": 5, "BSh": 6, "BSk": 7,
    "Csa": 8, "Csb": 9, "Csc": 10, "Cwa": 11, "Cwb": 12, "Cwc": 13, "Cfa": 14, "Cfb": 15, "Cfc": 16,
    "Dsa": 17, "Dsb": 18, "Dsc": 19, "Dsd": 20, "Dwa": 21, "Dwb": 22, "Dwc": 23, "Dwd": 24, "Dfa": 25, "Dfb": 26,
    "Dfc": 27, "Dfd": 28,
    "ET": 29, "EF": 30
}

diction = {"Af": (150, 0, 0, 255),
           "Am": (255, 0, 0, 255),
           "Aw": (255, 204, 204, 255),
           "BWh":(255, 204, 0, 255),
           "BWk":(255, 255, 100, 255),
           "BSh":(204, 141, 20, 255),
           "BSk":(204, 170, 84, 255),
           "Csa":(0, 255, 0, 255),
           "Csb":(150, 255, 0, 255),
           "Csc":(200, 255, 0, 255),
           "Cwa":(180, 100, 0, 255),
           "Cwb":(150, 100, 0, 255),
           "Cwc":(90, 60, 0, 255),
           "Cfa":(0, 50, 0, 255),
           "Cfb":(0, 80, 0, 255),
           "Cfc":(0, 120, 0, 255),
           "Dsa":(255, 110, 255, 255),
           "Dsb":(255, 180, 255, 255),
           "Dsc":(230, 200, 255, 255),
           "Dsd":(200, 200, 200, 255),
           "Dwa":(200, 180, 255, 255),
           "Dwb":(154, 127, 179, 255),
           "Dwc":(135, 89, 179, 255),
           "Dwd":(111, 36, 179, 255),
           "Dfa":(50, 0, 50, 255),
           "Dfb":(100, 0, 100, 255),
           "Dfc":(200, 0, 200, 255),
           "Dfd":(200, 20, 133, 255),
           "ET": (100, 255, 255, 255),
           "EF": (100, 150, 255, 255)
           }

# %%

# %%
kp = pd.read_excel('Koppen_class_list.xlsx', index_col=1)
if 1:
    import matplotlib.patches as patches
    ds = pd.read_csv('koppen.csv', index_col=[0,1,2])
    

    proj = ccrs.PlateCarree(central_longitude=150)

    plt.figure(figsize=(12, 8))
    ax = plt.axes(projection= proj )
    
    ax.set_extent([-90, 300, -65, 75], crs=ccrs.PlateCarree())
    
    ax.stock_img()
    koppl = list(ds.groupby('koppen'))
    
    legend_handles = []
    for ig, g in enumerate( koppl[:] ):
        dl = g[1] 
        lat, lon = dl['latitude'].values, dl['longitude'].values
        lon = np.where(lon<0, lon+360, lon)
        #col = np.array(diction[g[0]])/255.
        col = kp.loc[g[0], 'Color']
        ax.scatter(lon, lat, s = 3, 
                   color = col,
                   edgecolor = 'k',
                   lw = .1,
                   transform=ccrs.Geodetic())
        legend_handles.append(patches.Patch(color=col, label=g[0]) )
    
    plt.axis('off')
    
    plt.legend(handles=legend_handles, loc='lower left', fontsize=7, ncols=10)
    plt.savefig('fig/koppen_world.png', dpi = 150)


# %%

# %% [markdown]
# # Climograph
# ![image.png](attachment:41bfe678-9015-4f88-801c-38395b24aa4b.png)
# (https://public.wsu.edu/~rlee/biol103/ecologybiosphere/index.htm)
#

# %%
def scatter_base():
    fig = plt.figure(figsize=[5,5])
    ax = plt.axes([.1,.1,.8,.8])
    ax.set_ylim(-20,40)
    ax.set_xlim(0,600)
    plt.xlabel('Precipitation (mm)')
    plt.ylabel('Tempetature (degC)')
    ax.grid()
    return fig, ax


# %%

colors = np.arange(12)
fig, ax = scatter_base()

ist = 1000
precip, temp = pr[ist], ts[ist]
x, y = precip, temp

if (x < 0).any(): sys.exit()
if (y < -60).any(): sys.exit()

x = np.append(x,x[:1])
y = np.append(y,y[:1])
#ax.scatter(x, y, c=colors, cmap='hsv', alpha=0.7)
ax.plot(x, y, color='gray', linestyle='-', alpha=0.7, lw =1)
#labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
labels = list(range(1,13))+[1]
for i in range(len(x)):
    plt.text(x[i], y[i] + 0.03, labels[i], ha='center')
    

# %%

colors = np.arange(13)
fig, ax = scatter_base()

ist = 1000
precip, temp = pr[ist], ts[ist]
x, y = precip, temp

if (x < 0).any(): sys.exit()
if (y < -60).any(): sys.exit()

x = np.append(x,x[:1])
y = np.append(y,y[:1])
ax.scatter(x, y, c=colors, cmap='hsv', alpha=0.7)
ax.plot(x, y, color='gray', linestyle='-', alpha=0.7, lw =1)
#labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
labels = list(range(1,13))+[1]
for i in range(len(x)):
    plt.text(x[i], y[i] + 1, labels[i], ha='center')

