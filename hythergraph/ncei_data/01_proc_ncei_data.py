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
import numpy as np


# %% [markdown]
# ## Data downloaded from NCEI
#
# https://www.ncei.noaa.gov/data/oceans/archive/arc0216/0253808/4.4/data/0-data/
#
#
# Data have been downloaded and saved in Google Drive https://drive.google.com/drive/folders/1e2tRj7WXnycS_EXVbo9pGR6I-o2-V0NL?usp=sharing

# %%
idir = '/Users/doan/MyDrive/share/2024/clim_class_data/' # google drive data (shared)
files = sorted(glob.glob(idir + '0253808/4.4/data/0-data/Region-*-WMO-Normals-9120/*/CSV/*.csv'))
print(len(files))
odir0 = idir

# %%
# !open 0253808/4.4/data/0-data/Region-2-WMO-Normals-9120/Japan/CSV/Fukuoka_47807.csv

# %%
ss = []
for iff, f in enumerate(files[:]):
    co, _, afile = f.split('/')[-3:]
    reg = f.split('/')[-4][:8]
    try:
        ll = open(f, encoding='latin-1').readlines()
    except:
        print('wrong in reading file', iff, f)
        continue
    

    i1 = [i for i, l in enumerate(ll) if l.split(',')[0].strip() == 'Parameter_Code']
    i2 = i1[1:] + [len(ll)]

    dd = {}
    
    try:
        ila = [i for i, l in enumerate(ll) if l.split(',')[0].strip() == 'WMO_Number' and l.split(',')[1].strip() == 'Latitude' ][0]
        snu, la, lo, alt = ll[ila+1].split(',')[:4]
        ss.append( [ co, afile[:-10], snu, la, lo, alt ])
        
        for j1, j2  in zip(i1, i2):

            var = ll[j1+1].split(',')[1].strip()


            kk = [k for k, l2 in enumerate(ll[j1:j2]) if l2.split(',')[0].strip() == 'WMO_Number']
            ll2 = ll[kk[0] + j1 : j2 ] 
            ll3 = [l3.split(',') for l3 in ll2 if l3.split(',')[0].strip() != '']

            d1 = pd.DataFrame(ll3)

            d2 = d1.T
            d3 = d2.set_index(0).T
            #d3.loc[:,'Calculation_Name'] = d3.loc[:,'Calculation_Name'].str.strip().values
            
            d4 = d3.set_index(  [c  for c in d3.columns[0:4] ] ) .T
            d5 = d4[:12]
            dd[var] =  d5# exclude annual

        if 1:
            do = pd.concat(dd, axis=1)
            do.index.name = ''
            #do = do.loc[:, (slice(None), snu)].droplevel(level=[1,2,4], axis=1)
            for ic in range(do.shape[1]):
                do.iloc[:,ic] = pd.to_numeric(do.iloc[:,ic],errors = 'coerce')
            odir = odir0+'/data/'+reg+'/'+co+'/'
            if not os.path.exists(odir): os.makedirs(odir)
            ofile = odir + afile
            do.to_csv(ofile)
            

    except:
        print('wrong in processing', iff, f)
    
    
ds = pd.DataFrame(ss, columns=['country', 'place', 'station_id', 'latitude', 'longitude', 'altitude'])
ds.to_csv('list_of_stations.csv', index=None)

# %%
ds

# %% [markdown]
# # Extract only temperature and precipitation from available stations

# %% [markdown]
# ## step 2: extract to data_temp_prcp

# %%
ifiles = sorted(glob.glob(idir+'/data/*/*/*.csv'))
print(len(ifiles))

# %%
for i, f in enumerate(ifiles[:]):

    try:
        
        df = pd.read_csv(f, index_col=0, header=[0,1,2]) #
        df.columns = df.columns.set_levels(df.columns.levels[0].str.lower(), level=0)
        
        
        df.index = df.index.str.strip()
        df.loc['Calculation_Name'] = df.loc['Calculation_Name'].str.lower().str.strip().values
        
        d3 = []
        vv1 = ['Precipitation_Total',  'Daily_Mean_Temperature'][:]
        vv2 = ['Sum', 'Mean'][:]
        b1 =np.array(vv1)[ ~np.array([ v.lower() in df.columns.get_level_values(0) for v in vv1])]
        
        for v1, v2 in zip( vv1,vv2 ):
            if v1 == 'Precipitation_Total':
                try:
                    d1 = df.loc[:,v1.lower()]
                except:
                    d1 = df.loc[:,v1.lower()+'1']
            else:
                d1 = df.loc[:,v1.lower()]
            d2 = d1.loc[:, d1.iloc[0].values == v2.lower()]
            d3.append(d2)
            

        do = pd.concat( d3, axis=1).droplevel(level=[1],axis=1)[2:]
        do.columns = ['Precipitation', 'Temperature']

        ofile = f.replace('data', 'data_temp_prcp')
        if not do.isnull().any().any():
            odir = os.path.dirname(f).replace('data', 'data_temp_prcp')
            if not os.path.exists(odir): os.makedirs(odir)
            do.to_csv(ofile)
        else:
            null=1
        
    except:
        wrong=1


# %% [markdown]
# ## step 3: extract latitude and longitude information for available stations

# %%
files_2 = sorted(glob.glob('data_temp_prcp/*/*/*.csv'))
print('number of stations: ', len(files_2))
ds = pd.read_csv('list_of_stations.csv', index_col=[0,1,2])

# %%
dss = []
for i, f in enumerate(files_2[:]):
    
    c0, c1,c2, c3 = f.split('/')[1], f.split('/')[2], f.split('/')[3][:-10], f.split('/')[3][-9:-4] 
    
    d = ds.loc[ (c1, c2) ]

    
    xx = []
    for cla in [ 'latitude', 'longitude'][:]:
        try:
            a0 = d[cla].values[0].replace('"', '')
            if '|' in a0: 
                la = a0.split('|')
                a1 = float(la[0])
                for ia, a2 in enumerate(la[1:-1]): 
                    if a2.strip() == '': a2 = '0'
                    a22 =  float(a2) / 60 / 10**ia
                    a1 = a1 + a22
                a3 = la[-1].strip()[-1]

            else: 
                # Egypt
                la = a0.split(' ')
                a1 = float(la[0])
                for ia, a2 in enumerate(la[1:]): 
                    if a2.strip() == '': a2 = '0'
                    a22 =  float(a2) / 60 / 10**ia
                    a1 = a1 + a22
                
                if cla == 'longitude': a3 = 'E'
                if cla == 'latitude': a3 = 'N'
                
                
            if a3 not in ['E', 'W', 'S', 'N']:
                print('    ', cla, c1, c2, la, a1, a3)
                continue
                
            xx.append(c0); xx.append(c1); xx.append(c2)
            xx.append(a1); xx.append(a3); xx.append(d['altitude'].values[0])
            
        except:
            
            print('wrong ', cla, c1, c2, la)
    
    dss.append(xx)
    
do = pd.DataFrame(dss)
do = do[~(do.iloc[:,4].astype(str) == 'None')]
do = do[~(do.iloc[:,9].astype(str) == 'None')]
do.loc[do.iloc[:,4].astype(str) == 'S', 3] = - do.loc[do.iloc[:,4].astype(str) == 'S', 3].values
do.loc[do.iloc[:,10].astype(str) == 'W', 9] = - do.loc[do.iloc[:,10].astype(str) == 'W', 9].values
do = do.loc[:,[0,1,2,3,9, 11]]
do.columns = [ 'region', 'country', 'place', 'latitude', 'longitude', 'altitude']
do = do.set_index(['region', 'country', 'place'])
do.to_csv('list_of_stations_2.csv')

# %% [markdown]
# ## Plot map with stations

# %%
len(dl)

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy
df = do
proj = ccrs.PlateCarree(central_longitude=150)
plt.figure(figsize=(12, 8))
ax = plt.axes(projection= proj )
ax.set_extent([-90, 300, -65, 75], crs=ccrs.PlateCarree())
ax.stock_img()
for ig, g in enumerate(list(do.groupby(level=0))):
    dl = g[1] 
    lat, lon = dl['latitude'].values, dl['longitude'].values
    lon = np.where(lon<0, lon+360, lon)
    ax.scatter(lon, lat, s = 4, 
               color = ['r', 'b', 'yellow', 'g', 'k', 'violet'][ig], 
               edgecolor = 'k',
               lw = .1,
               label = dl.index[0][0] + ' ('+str(len(dl))+' sites)',
               transform=ccrs.Geodetic())
plt.legend(ncols = 3, fontsize=10)
plt.axis('off')
plt.savefig('fig/world_stations.png', dpi = 150)

# %%
