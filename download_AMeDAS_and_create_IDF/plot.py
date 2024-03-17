#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 16:09:26 2024

@author: doan
"""
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import time, sys, glob
import pandas as pd
#from download_extract_table import download
import numpy as np
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import os
import pandas as pd
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import pandas as pd

import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.plots import add_metpy_logo, Hodograph, SkewT
from metpy.units import units


# plot map
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LinearSegmentedColormap, PowerNorm
import sys
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy
import numpy as np
from sklearn.linear_model import LinearRegression
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker    
import cartopy.feature as cfeature



from matplotlib.image import imread
def grid(ax,st):
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                      linewidth=2, color='gray', alpha=0.5, linestyle='--')
    gl.xlabels_top = False
    gl.ylabels_right = False
    gl.xlines = False
    gl.ylines = False
    gl.xlocator = mticker.FixedLocator(np.arange(0,360,st))
    gl.ylocator = mticker.FixedLocator(np.arange(-90.,90,st))
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size':10, 'color':'gray'}
    gl.ylabel_style = {'size':10, 'rotation':90, 'va':'center', 'color':'gray'}
    return ax






def plot_basemap():
    
    #land_50m = cfeature.NaturalEarthFeature('physical', 'land', '50m',
    #                                        edgecolor='face',
    #                                        facecolor=cfeature.COLORS['land'])

    bodr = cfeature.NaturalEarthFeature(category='cultural', 
        name='admin_0_boundary_lines_land', scale='10m', facecolor='none', alpha=0.7)
    
    
    proj =  ccrs.PlateCarree() #ccrs.Robinson(central_longitude=145)

    fig = plt.figure(figsize=(5, 5))
    ax = plt.axes(projection= proj )
    ax.set_extent([123,150,25, 49])
    ax.coastlines(resolution='10m',lw=.5)
    #ax.gridlines()
    ax.stock_img()
    
    #fname = os.path.join('/Users/doan/working/00_OBS_studies/Global/NE1_50M_SR_W', 'NE1_50M_SR_W.tif')
    
    fname = 'NE2_50M_SR_W/NE2_50M_SR_W.tif'
    if os.path.exists(fname):
        ax.imshow(imread(fname), origin='upper', transform=proj, 
              extent=[-180, 180, -90, 90])
    
    #ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.5,lw=.5)
    ax.add_feature(bodr, linestyle='-', edgecolor='k', alpha=.5, lw=.5)
    #ax.outline_patch.set_linewidth(.5)
    
    return fig, ax
#==============================================================================






def plot_hourly_temp_hum_wind(dat, odir='fig/'):
    
    date = dat.index[0]
    
    fig = plt.figure(figsize=(7, 3))
    
    ax = plt.axes([.1,.6,.7,.37])
    x = dat.index.hour.values #range(24) #dat.index
    x[-1] = 24
    c1 = 'tomato'
    ax.plot(x,dat['temp_C'], color=c1,lw=1.5, clip_on=False) 
    ax.tick_params(axis='y', labelcolor=c1)
    ax.set_ylabel('Temperature ($^oC$)', color=c1,fontsize=9) 
    #ax.set_xlim(0,23.5)
    ax.set_ylim(int(dat['temp_C'].min() / 2)*2, int(dat['temp_C'].max() / 2+1)*2)
    plt.xticks([1,6,12,18,24],[1,6,12,18,24],fontsize=8)
    plt.yticks(fontsize=5)
    ax.grid(ls='--')
    ax.set_xlim(1,24)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_position(('axes', -.01))
    ax.spines['bottom'].set_position(('axes', -.05))
    plt.xticks(fontsize= 10)
    plt.yticks(fontsize= 10)
    
    #dat['temp_C'].plot(ax=ax,lw=1,c='r')
    ax2 = ax.twinx()
    ax2.spines['right'].set_position(('axes', 1.01))
    c1 = 'g'
    ax2.plot(x,dat['rh_percent'], c = c1,lw=1.5, clip_on=False)
    ax2.tick_params(axis='y', labelcolor=c1)
    ax2.set_ylabel('RH (%)', color=c1) 
    if dat['rh_percent'].min() < 40: ylim = (0,100)
    else: ax2.set_ylim(40,100)
    #dat['rh_percent'].plot(ax=ax2,lw=1,c='g')
    #df2.plot(ax=ax2)
    ax2.spines['left'].set_visible(False)
    
    
    ax3 = ax.twinx()
    ax3.spines['right'].set_position(('axes', 1.15))
    ax3.bar(x,dat['precip_mm'].values, color='royalblue', alpha=0.8)
    ax3.set_ylim(0,10)
    ax3.tick_params(axis='y', labelcolor='royalblue')
    ax3.set_ylabel('Precipitation (mm/hr)', color='royalblue') 
    for a in [ax,ax2,ax3]:
        a.spines['top'].set_visible(False)
    for a in [ax2, ax3]: a.spines['bottom'].set_visible(False)
    ax3.spines['left'].set_visible(False)
    #ax.set_xlim(0,24.5)
    
    #dat['precip_mm'].plot(ax=ax3 )
    #df3.plot(ax=ax3)
    
    
    
    #============================
    ax4 = plt.axes([.1,.17,.7,.22])
    c1 = 'y'
    ax4.plot(x,dat['wspd_ms'], color=c1,lw=1.5, clip_on=False)
    ax4.tick_params(axis='y', labelcolor=c1)
    ax4.set_ylabel('Wind speed (mm/s)', color=c1)     
    
    
    ax4.set_xlabel(date.strftime('%d %b %Y'), fontsize=14, fontweight='bold')
    
    
    #ax2 = ax.twinx()
    #ax2.plot(x,dat['wdir_deg'], color='orange')
    #ax2.set_ylim(-100,370)
    #ax2.set_yticks([0, 90, 180, 270, 360])
    #ax2.set_yticklabels(['N','E', 'S', 'W', 'N'], color='orange')
    ws, wd = dat['wspd_ms'].values, dat['wdir_deg'].values
    u, v = mpcalc.wind_components(ws * units('m/s'), wd * units.deg)
    
    qui = ax4.quiver(x, [0]*len(x) , u, v, width = .003,scale=50)
    plt.quiverkey(qui, 0.9, 1.05, 2, label='2 m/s', 
                  labelpos='E')
    
    ax4.set_ylim( - (int(ws.max()/2)+1)*2 , (int(ws.max()/2)+1) * 2)
    ax4.hlines(0,xmin=1,xmax=24,lw=0.2)
    plt.xticks([1,6,12,18,24],[1,6,12,18,24])
    ax4.set_xlim(1,24)
    ax4.grid(ls='--')
    for f in ['right', 'top']: ax4.spines[f].set_visible(False)
    
    ax4.spines['left'].set_position(('axes', -.01))
    ax4.spines['bottom'].set_position(('axes', -.05))
    
    
    #odir = 'fig/'+stn+'/'+dd.strftime('%Y-%m-%d')+'/' 
    if not os.path.exists(odir): os.makedirs(odir)
    plt.savefig(odir+'/temp-hum-wind.png', dpi=150)   
    
    
    
    
    
    


def plot_sounding(df,date,odir='fig/'):
    # plot sounding
    p = df.index.astype(float).values * units.hPa
    T = df['Temp(C)'].values.astype(float) * units.degC
    rh = df['RH(%)'].values.astype(float) * units('percent')  #/100  #* units.%
    
    Td = mpcalc.dewpoint_from_relative_humidity(T, rh)
    
    # Create a new figure. The dimensions here give a good aspect ratio
    fig = plt.figure(figsize=(7, 7))
    #add_metpy_logo(fig, 630, 80, size='large')
    
    # Grid for plots
    gs = gridspec.GridSpec(3, 3)
    #ax = plt.axes([.1,.1,.8,.8])
    skew = SkewT(fig, rotation=45, subplot=gs[:, :2])
    
    skew.plot(p, T, 'r', lw=2)
    skew.plot(p, Td, 'g', lw=2)
    
    # Good bounds for aspect ratio
    skew.ax.set_xlim(-30, 40)
    
    wd = df['WindDir(deg)'].values.astype(float) 
    ws = df['WindSpd(m/s)'].values.astype(float) / 1.9438444924406
    u, v = mpcalc.wind_components(ws * units('knots'), wd * units.deg)
    skew.plot_barbs(p, u, v)
    skew.ax.set_ylim(1000, 100)
    

    # Calculate LCL height and plot as black dot. Because `p`'s first value is
    # ~1000 mb and its last value is ~250 mb, the `0` index is selected for
    # `p`, `T`, and `Td` to lift the parcel from the surface. If `p` was inverted,
    # i.e. start from low value, 250 mb, to a high value, 1000 mb, the `-1` index
    # should be selected.
    lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
    skew.plot(lcl_pressure, lcl_temperature, 'ko', markerfacecolor='black')
    
    # Calculate full parcel profile and add to plot as black line
    prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
    skew.plot(p, prof, 'k', linewidth=2)
    
    # Shade areas of CAPE and CIN
    #skew.shade_cin(p, T, prof) #, dewpoint= Td)
    skew.shade_cape(p, T, prof)
    
    # these are matplotlib.patch.Patch properties
    #props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    #props = dict( facecolor='wheat', alpha=0.5)
    # place a text box in upper left in axes coords
    cape, cin = mpcalc.cape_cin(p, T, Td, prof, which_lfc='bottom', which_el='top')
    text = 'LCL: '+'%.0f' % lcl_pressure.magnitude + ' (hPa)\n'+ \
           'CAPE: '+'%.0f' % cape.magnitude + ' (J/kg)\n'+ \
           'CIN: ' + '%.0f' % cin.magnitude + ' (J/kg)\n'
           
          
    skew.ax.text(1.2, 0.3, date.strftime('%Y %b %d %H:00'), 
                 transform=skew.ax.transAxes,
                 fontsize=12, verticalalignment='bottom', 
                 fontweight = 'bold'
                 #bbox=props
                 )
           
    skew.ax.text(1.25, 0.26, text, 
                 transform=skew.ax.transAxes,
                 fontsize=11, verticalalignment='top', 
                 #bbox=props
                 )
    
    
    
    # An example of a slanted line at constant T -- in this case the 0
    # isotherm
    skew.ax.axvline(0, color='c', linestyle='--', linewidth=2)
    
    
    # Add the relevant special lines
    skew.plot_dry_adiabats()
    skew.plot_moist_adiabats()
    skew.plot_mixing_lines()
    
    
    # Create a hodograph
    ax = plt.axes([.74,.53,.25,.25]) #fig.add_subplot(gs[0, -1])
    h = Hodograph(ax, component_range=60.)
    h.add_grid(increment=20)
    h.plot(u, v)    
    
    if not os.path.exists(odir): os.makedirs(odir)
    #plt.savefig(odir+'/' + date.strftime('%Y-%b-%d_%H00.png'), dpi=150)
    plt.savefig(odir+'/skewp.png', dpi=150)
#==============================================================================
#==============================================================================


    
    
    
    
    
    
if __name__ == "__main__":
    
    
    point = '47646'
    point = '47662'
    point = '5' 
    
    
    amedas_file = 'Amedas_list.csv'
    alist = pd.read_csv(amedas_file, index_col=0)
    
    #=== SHimonita
    opath = 'data_download/' 
    
    
    # download each point for a given day
    if True:
        
        point = '47646' # Tsukuba station
        date = pd.Timestamp('2022-02-01')
    
        #dat, link = download_amedas(point, date, opath, 'hourly' )
        #time.sleep(0.2)
        
        #from plot import plot_hourly_temp_hum_wind
        #plot_hourly_temp_hum_wind(dat)
    
    
    
    
    
    
    
