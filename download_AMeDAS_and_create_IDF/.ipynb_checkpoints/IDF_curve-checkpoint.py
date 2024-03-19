#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 13:23:47 2024

@author: doan
"""


import sys, glob, os
import pandas as pd
import numpy as np
import math


point = '47646'
idir = 'combined_hourly/'+point+'/'

df = pd.read_csv(idir+'all.csv', index_col=0, parse_dates=True)['precip_mm']
df = df.replace(np.NaN, 0)




dd = {}

duration = [1, 3, 6, 12, 24]
ms = []
for window in duration:
    print(window)  
    d1 = df.rolling(window, center=True).sum()[window-1::window]
    anmax = d1.groupby(d1.index.year).max()[:-1]
    dd[window] = { 'mean': anmax.mean(), 'std': anmax.std(), 'all': anmax}
    ms.append( [anmax.mean(), anmax.std()] )
    
    
    
    
    
    
Kt= {}
return_years = [2,5,10,30, 50,100]
for i in return_years:
    Kt[i] =  - np.sqrt(6)/np.pi*(0.5772+ np.log( np.log(i/(i-1)))) 




results = pd.DataFrame(index = duration, columns = return_years )


for return_y in return_years:
    for dur in duration:
        
        
        mu = dd[dur]['mean']
        sig = dd[dur]['std']
        k = Kt[return_y]
        
        x = ( mu + k * sig ) / dur
        
        print(return_y, dur, x)

        results.loc[dur, return_y] = round(x,4)




import matplotlib.pyplot as plt

fig = plt.figure(figsize=(8, 5))
ax = plt.axes([.1,.1,.8,.8])

for i, return_y in enumerate(results.columns):
    
    ax.plot(results.index,results.loc[:,return_y],linestyle='--', 
            marker='o', 
            color=['b', 'g', 'r', 'c', 'y','k'][i],
            label = 'T = '+str(return_y)+' years')




plt.ylabel('RainFall Intensity (mm/hr)', fontsize=14)
plt.xlabel('RainFall Duration (Hrs)', fontsize=14)
ax.set_xticks(duration)
ax.legend()
plt.grid()
plt.show()






    
    
    
    












    
    
    