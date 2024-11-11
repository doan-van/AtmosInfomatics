#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 11:42:21 2024

@author: doan
"""

import os, glob, sys
import matplotlib.pyplot as plt
import pandas as pd



files = sorted(glob.glob('timeseries/*'))
for f in files:
    print(f)
    df = pd.read_csv(f, index_col=0, parse_dates=True)
    df.plot()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    