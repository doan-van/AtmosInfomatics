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


# %%
#files = sorted(glob.glob('0253808/4.4/data/0-data/Region-2-WMO-Normals-9120/Japan/CSV/*.csv'))

# %%
files = sorted(glob.glob('0253808/4.4/data/0-data/Region-*-WMO-Normals-9120/*/CSV/*.csv'))

# %%
print(len(files))

# %%
# !open 0253808/4.4/data/0-data/Region-2-WMO-Normals-9120/Japan/CSV/Fukuoka_47807.csv

# %%
# !open 0253808/4.4/data/0-data/Region-2-WMO-Normals-9120/Japan/CSV/Abashiri_47409.csv

# %%
# !open 0253808/4.4/data/0-data/Region-1-WMO-Normals-9120/Algeria/CSV/Adrar_60620.csv

# %%



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
            odir = 'data/'+reg+'/'+co+'/'
            if not os.path.exists(odir): os.makedirs(odir)
            ofile = odir + afile
            do.to_csv(ofile)
            

    except:
        print('wrong in processing', iff, f)
    
    
ds = pd.DataFrame(ss, columns=['country', 'place', 'station_id', 'latitude', 'longitude', 'altitude'])
ds.to_csv('list_of_stations.csv', index=None)

# %%
ds

# %%
# !open '0253808/4.4/data/0-data/Region-1-WMO-Normals-9120/Rwanda/CSV/BUGARAMA_RIZ.csv'

# %%
ds

# %%

# %%
ll = open(f).readlines()

# %%
# !open 0253808/4.4/data/0-data/Region-6-WMO-Normals-9120/Sweden/CSV/Vaxjo_Kronoberg_02641.csv

# %%
i2 = i1[1:] + [len(ll)]

# %%
ll = open(f).readlines()


# %%
do

# %%
d4 = d3.set_index(  [c  for c in d3.columns[0:4] ] ) .T

# %%

# %%
dll = pd.DataFrame(lalo, columns=['cityindex', 'latitude', 'longitude', 'city', 'country']).set_index('cityindex')
dll.to_csv('latlon.csv')
