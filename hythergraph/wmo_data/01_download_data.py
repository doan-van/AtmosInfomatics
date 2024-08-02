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
# # This is script to download json data from WMO homepage
# Created on Fri Jul 19 2024
#
# @author: Quang-Van Doan
#
# Homepage WMO
# https://worldweather.wmo.int/en/dataguide.html
#

# %%
import wget
import sys, os, glob
import pandas as pd
import json


# %%
path = 'download/'

# %%
if 0:
    a = wget.download('https://worldweather.wmo.int/en/json/full_city_list.txt')
    df = pd.read_csv(a, delimiter=';').set_index('Country')[:-1]
    df.to_csv('list_id.csv')

# %%
df = pd.read_csv('list_id.csv', index_col=0)

# %%
link0 = 'https://worldweather.wmo.int/en/json/'
for i, r in df[:].iterrows():
    link = link0+ '%.0f'%r['CityId']+'_en.json'
    a = wget.download(link, out=path)
    print(a)

