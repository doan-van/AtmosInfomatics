#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  9 14:07:47 2024

@author: doan
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import metpy.calc as mpcalc
from metpy.units import units
from metpy.plots import Hodograph, SkewT
from cartopy import crs as ccrs
from cartopy.feature import NaturalEarthFeature
from matplotlib.image import imread
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker

class JMADataPlotter:
    def __init__(self, output_dir="fig"):
        self.output_dir = output_dir

    def grid(self, ax, st):
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                          linewidth=2, color='gray', alpha=0.5, linestyle='--')
        gl.xlabels_top = False
        gl.ylabels_right = False
        gl.xlines = False
        gl.ylines = False
        gl.xlocator = mticker.FixedLocator(np.arange(0, 360, st))
        gl.ylocator = mticker.FixedLocator(np.arange(-90., 90, st))
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': 10, 'color': 'gray'}
        gl.ylabel_style = {'size': 10, 'rotation': 90, 'va': 'center', 'color': 'gray'}
        return ax

    def plot_basemap(self):
        bodr = NaturalEarthFeature(category='cultural',
                                   name='admin_0_boundary_lines_land', scale='10m', facecolor='none', alpha=0.7)
        proj = ccrs.PlateCarree()
        fig = plt.figure(figsize=(5, 5))
        ax = plt.axes(projection=proj)
        ax.set_extent([123, 150, 25, 49])
        ax.coastlines(resolution='10m', lw=.5)
        ax.stock_img()
        
        fname = 'NE2_50M_SR_W/NE2_50M_SR_W.tif'
        if os.path.exists(fname):
            ax.imshow(imread(fname), origin='upper', transform=proj,
                      extent=[-180, 180, -90, 90])
        ax.add_feature(bodr, linestyle='-', edgecolor='k', alpha=.5, lw=.5)
        return fig, ax

    def plot_hourly_temp_hum_wind(self, dat):
        date = dat.index[0]
        fig = plt.figure(figsize=(7, 3))
        
        ax = plt.axes([.1, .6, .7, .37])
        x = dat.index.hour.values
        x[-1] = 24
        ax.plot(x, dat['temp_C'], color='tomato', lw=1.5, clip_on=False)
        ax.tick_params(axis='y', labelcolor='tomato')
        ax.set_ylabel('Temperature (°C)', color='tomato', fontsize=9)
        ax.set_ylim(int(dat['temp_C'].min() / 2) * 2, int(dat['temp_C'].max() / 2 + 1) * 2)
        plt.xticks([1, 6, 12, 18, 24], [1, 6, 12, 18, 24], fontsize=8)
        plt.yticks(fontsize=5)
        ax.grid(ls='--')
        ax.set_xlim(1, 24)
        
        ax2 = ax.twinx()
        ax2.plot(x, dat['rh_percent'], color='g', lw=1.5, clip_on=False)
        ax2.tick_params(axis='y', labelcolor='g')
        ax2.set_ylabel('RH (%)', color='g')
        
        ax3 = ax.twinx()
        ax3.bar(x, dat['precip_mm'].values, color='royalblue', alpha=0.8)
        ax3.set_ylim(0, 10)
        ax3.set_ylabel('Precipitation (mm/hr)', color='royalblue')
        
        ax4 = plt.axes([.1, .17, .7, .22])
        ax4.plot(x, dat['wspd_ms'], color='y', lw=1.5, clip_on=False)
        ax4.set_ylabel('Wind speed (mm/s)', color='y')
        
        ws, wd = dat['wspd_ms'].values, dat['wdir_deg'].values
        u, v = mpcalc.wind_components(ws * units('m/s'), wd * units.deg)
        ax4.quiver(x, [0] * len(x), u, v, width=.003, scale=50)
        plt.xticks([1, 6, 12, 18, 24], [1, 6, 12, 18, 24])
        ax4.set_xlim(1, 24)
        ax4.grid(ls='--')
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        plt.savefig(os.path.join(self.output_dir, 'temp-hum-wind.png'), dpi=150)
        
    def plot_sounding(self, df, date):
        
        p = df.index.astype(float).values * units.hPa
        T = df['Temp(C)'].values.astype(float) * units.degC
        rh = df['RH(%)'].values.astype(float) * units.percent
        Td = mpcalc.dewpoint_from_relative_humidity(T, rh)

        fig = plt.figure(figsize=(7, 7))
        gs = gridspec.GridSpec(3, 3)
        skew = SkewT(fig, rotation=45, subplot=gs[:, :2])
        
        skew.plot(p, T, 'r', lw=2)
        skew.plot(p, Td, 'g', lw=2)
        skew.ax.set_xlim(-30, 40)
        wd = df['WindDir(deg)'].values.astype(float)
        ws = df['WindSpd(m/s)'].values.astype(float) / 1.9438444924406
        u, v = mpcalc.wind_components(ws * units.knots, wd * units.deg)
        skew.plot_barbs(p, u, v)
        skew.ax.set_ylim(1000, 100)
        
        lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
        skew.plot(lcl_pressure, lcl_temperature, 'ko', markerfacecolor='black')
        prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
        skew.plot(p, prof, 'k', linewidth=2)
        skew.shade_cape(p, T, prof)
        
        cape, cin = mpcalc.cape_cin(p, T, Td, prof, which_lfc='bottom', which_el='top')
        text = f'LCL: {lcl_pressure.m:.0f} hPa\nCAPE: {cape.m:.0f} J/kg\nCIN: {cin.m:.0f} J/kg\n'
        skew.ax.text(1.2, 0.3, date.strftime('%Y %b %d %H:00'), transform=skew.ax.transAxes, fontsize=12, fontweight='bold')
        skew.ax.text(1.25, 0.26, text, transform=skew.ax.transAxes, fontsize=11)
        skew.ax.axvline(0, color='c', linestyle='--', linewidth=2)
        skew.plot_dry_adiabats()
        skew.plot_moist_adiabats()
        skew.plot_mixing_lines()
        
        ax = plt.axes([.74, .53, .25, .25])
        h = Hodograph(ax, component_range=60)
        h.add_grid(increment=20)
        h.plot(u, v)
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        plt.savefig(os.path.join(self.output_dir, 'skewt.png'), dpi=150)



