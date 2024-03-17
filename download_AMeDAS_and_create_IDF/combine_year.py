#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 20:59:56 2024

@author: doan
"""


import sys, glob, os
import pandas as pd
import numpy as np


    
point = '47646'

files = sorted(glob.glob('data_download/hourly/'+point+'/*'))
dd = []
for f in files[:][:]:
    print(f)
    year = int(f.split('/')[-1].split('.')[0])
    df = pd.read_csv(f, index_col=0, parse_dates=True)
    t = df[['temp_C', 'precip_mm' ] ]
    dd.append(t)

do = pd.concat(dd).replace(-999,np.NaN) #pd.DataFrame(dd).T 
odir = 'combined_hourly/'+point+'/'
if not os.path.isdir(odir): os.makedirs(odir)
ofile = odir + 'all.csv'
do.to_csv(ofile)








sys.exit()
ff = pd.DataFrame( { 'file':files, 'date': pd.to_datetime( [ f.split('/')[-1].split('.')[0] for f in files ], format = '%Y_%m_%d') }).set_index('date')
print(ff)

ff_years = list(ff.groupby(ff.index.year))


for yy, fils in ff_years[:]:
    
    print(yy)

    dd = []
    for f in fils[:][:]:
        year = int(f.split('/')[-1].split('.')[0])
        df = pd.read_csv(f, index_col=0, parse_dates=True)
        
        t = df[['temp_C', 'precip_mm' ] ]
        
        #if t.isnull().all().all(): continue
        #if ((t.isnull().sum() / day_of_year(year) ) > 0.1).any(): continue
        #if len(t) / day_of_year(year) < 0.9: continue
        dd.append(t)
        
            
    #if len(dd) < 1: print()
    do = pd.concat(dd).replace(-999,np.NaN) #pd.DataFrame(dd).T 
    #dg = do.groupby( [do.index.year, do.index.month  ])
    #da = do.groupby( [do.index.year, do.index.month  ]).mean()
    #da.loc[:,'precip_mm'] = dg.sum().loc[:, 'precip_mm']
    
    
    #stat[s.split('/')[-1]] = da
    #if False: # count year null
    #    d1 = do.isnull().groupby(do.index.year).sum() 
    #    doy = [day_of_year(y) for y in d1.index]
    #    for c in d1.columns: d1.loc[:, c] = 1 - d1.loc[:, c].values / np.array(doy)
    
    
    #dout = pd.concat(stat) #.to_csv('ketqua.csv')
    odir = 'combined_hourly/'+point+'/'
    if not os.path.isdir(odir): os.makedirs(odir)
    ofile = odir + str(yy)+'.csv'
        
    do.to_csv(ofile)
        
        
        
        
        
        
        
        
        