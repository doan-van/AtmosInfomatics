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
# ---

# %%
"""
Created on Sun May 24 14:03:15 2020

@author: doan
"""


# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

# %%
import numpy as np
import pandas as pd
#from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LinearSegmentedColormap, PowerNorm
import sys

# %%

# %%
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy


# %%
if 1:
    
    df = pd.read_csv('latlon.csv', index_col=0)
    lat, lon = df['latitude'].values, df['longitude'].values
    lon = np.where(lon<0, lon+360, lon)
    proj = ccrs.PlateCarree(central_longitude=150)
    #proj._threshold /= 10
    #proj = ccrs.Robinson(central_longitude=145)
    #proj = ccrs.Mollweide(central_longitude=145, globe=None)
    

    plt.figure(figsize=(10, 6))
    ax = plt.axes(projection= proj )
    
    ax.set_extent([-90, 300, -65, 75], crs=ccrs.PlateCarree())
    
    #ax.coastlines() #resolution='10m',lw=.1)
    #sys.exit()
    #ax.gridlines()
    ax.stock_img()
    ax.scatter(lon, lat, s = 1, 
               color = 'r',
               transform=ccrs.Geodetic())
    #ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.5,lw=.3)
    #ax.outline_patch.set_linewidth(.5)
    #sys.exit()
    plt.savefig('city_map.png', dpi = 100)


# %%
if 0:
    
    df = pd.read_csv('latlon.csv', index_col=4)
    
    for dx in list(df.groupby(df.index))[:]:
        country, d = dx
        print(d)
        lat, lon = d['latitude'].values, d['longitude'].values
        
        #lon = np.where(lon<0, lon+360, lon)
        proj = ccrs.PlateCarree(central_longitude=150)
    

        plt.figure(figsize=(10, 6))
        ax = plt.axes(projection= proj )
        extent = [ lon.min() - 5, lon.max()+5, lat.min() - 5, lat.max()+5]
    
        ax.set_extent(extent, crs=ccrs.PlateCarree())
    
        ax.stock_img()
        
        for i, r in d.iterrows():
            la, lo = r['latitude'], r['longitude']
            #ax.scatter(lo, la, s = 10, color = 'r',transform=ccrs.Geodetic())

            ax.text(lo, la, r['city'], 
                   color = 'r',
                   ha = 'center',
                   fontsize=12,
                   transform=ccrs.Geodetic())
            
        plt.savefig('fig/'+country+'/'+'city_map.png', dpi = 100)
        
        #ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.5,lw=.3)
        #ax.outline_patch.set_linewidth(.5)
    #sys.exit()
    #plt.savefig('city_map.png', dpi = 100)

# %%

# %%
if False:
    from  geopy.geocoders import Nominatim
    geolocator = Nominatim()
    ll = []
    for cc in [  ['Tsukuba', 'Japan'],
                 ['Hanoi', 'Vietnam'], 
                 ['Ho Chi Minh city', 'Vietnam'], 
                 ['Singapore', 'Singapore'],
                 ['Kolkata','India'],
                 ['Boulder', 'USA'],
                 ['Brisbane', 'Australia'],
                 ['Shanghai', 'China'],
                 ['Cork', 'Ireland'], 
                 ['Austin', 'USA'], 
                 ['Sydney', 'Australia']]:
    
        print(cc)
        city =cc[0]
        country =cc[1]
        loc = geolocator.geocode(city+','+ country)
        ll.append( cc+[loc.latitude,loc.longitude] )
        #print("latitude is :-" ,loc.latitude,"\nlongtitude is:-" ,loc.longitude)
    pd.DataFrame(ll,columns=['City', 'Country', 'lat', 'lon']).to_csv('latlon.csv',index=None)

# %%


# %%
if False:
    df = pd.read_excel('latlon.xlsx', index_col=0)[:-1]
    out_filename='international_cooperation.png'
    
    proj = ccrs.PlateCarree(central_longitude=145)
    #proj._threshold /= 10
    #proj = ccrs.Robinson(central_longitude=145)
    #proj = ccrs.Mollweide(central_longitude=145, globe=None)
    
    
    
    
    plt.figure(figsize=(10, 6))
    ax = plt.axes(projection= proj )
    
    
    ax.set_extent([-25, 340, -60, 75], crs=ccrs.PlateCarree())
    
    ax.coastlines(resolution='10m',lw=.1)
    
    #ax.gridlines()
    ax.stock_img()
    
    ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.5,lw=.3)
    #ax.outline_patch.set_linewidth(.5)
    #sys.exit()
    
    for i, row in df.iterrows():
        ax.scatter(row.lon,row.lat,color='r',transform=ccrs.PlateCarree(),s=20)
        plt.plot([df.loc['Tsukuba'].lon, row.lon], [df.loc['Tsukuba'].lat, row.lat],
                 color='r', linewidth=row['lw']/2, marker=None,
                 ls = 'none',
                 transform=ccrs.Geodetic(),
                 )
        
        if False:
            x, y, fs, al = row.lon + row.x, row.lat + row.y, row.fs, row.al
            text = row['text'].replace(';','\n')
            plt.text( x, y, text, fontsize=fs, ha=al,
                     transform=ccrs.PlateCarree(),fontweight = 'bold', 
                     )
    
    plt.savefig(out_filename, format='png', bbox_inches='tight', dpi = 200)

# %%
    

# %%
    

# %%
    


# %%
sys.exit()
if True:
    df = pd.read_excel('latlon.xlsx', index_col=0)
    out_filename='intter-con_3.png'
    
    #proj = ccrs.PlateCarree(central_longitude=145)
    #proj._threshold /= 10
    proj = ccrs.Robinson(central_longitude=145)
    
    plt.figure(figsize=(10, 6))
    ax = plt.axes(projection= proj )
    ax.coastlines(resolution='10m',lw=.1)
    #ax.gridlines()
    ax.stock_img()
    
    ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.5,lw=.3)
    #ax.outline_patch.set_linewidth(.5)

    
    for i, row in df.iterrows():
        ax.scatter(row.lon,row.lat,color='r' ,transform=ccrs.PlateCarree(),s=4)
        
        x, y, fs, al = row.lon + row.x, row.lat + row.y, row.fs, row.al
        text = row['text'].replace(';','\n')
        plt.text( x, y, text, fontsize=fs, ha=al,
                 transform=ccrs.Geodetic(), 
                 )
    
    plt.savefig(out_filename, format='png', bbox_inches='tight', dpi = 200)

# %%
    


# %%
if True:
    df = pd.read_excel('latlon.xlsx', index_col=0)
    out_filename='intter-con_1.png'
    
    #proj = ccrs.PlateCarree(central_longitude=145)
    #proj._threshold /= 10
    proj = ccrs.Robinson(central_longitude=145)
    
    plt.figure(figsize=(10, 6))
    ax = plt.axes(projection= proj )
    ax.coastlines(resolution='10m',lw=.1)
    #ax.gridlines()
    ax.stock_img()
    
    ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.5,lw=.3)
    #ax.outline_patch.set_linewidth(.5)

    
    for i, row in df.iterrows():
        ax.scatter(row.lon,row.lat,color='r',transform=ccrs.PlateCarree(),s=4)
        
        x, y, fs, al = row.lon + row.x, row.lat + row.y, row.fs, row.al
        text = row['text'].replace(';','\n')
        plt.text( x, y, text, fontsize=fs, ha=al,
                 transform=ccrs.Geodetic(),fontweight = 'bold', 
                 )
    
    plt.savefig(out_filename, format='png', bbox_inches='tight', dpi = 200)

# %%


# %%
if True:
    df = pd.read_excel('latlon.xlsx', index_col=0)
    out_filename='intter-con_2.png'
    
    #proj = ccrs.PlateCarree(central_longitude=145)
    #proj._threshold /= 10
    proj = ccrs.Robinson(central_longitude=145)
    
    plt.figure(figsize=(10, 6))
    ax = plt.axes(projection= proj )
    ax.coastlines(resolution='10m',lw=.1)
    #ax.gridlines()
    ax.stock_img()
    
    ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.5,lw=.3)
    #ax.outline_patch.set_linewidth(.5)

    
    for i, row in df.iterrows():
        ax.scatter(row.lon,row.lat,color='r',transform=ccrs.PlateCarree(),s=4)
        
    
    plt.savefig(out_filename, format='png', bbox_inches='tight', dpi = 200)

# %%
        

# %%
        

# %%
    

# %%
    

# %%
    

# %%
    

# %%
    


# %%
if True:
    grpa = { 'U1': (['Tsukuba', 'Boulder', 'Nanjing','Singapore'], 'r'), 
             'U2': (['Tsukuba', 'Kolkata', 'Austin'], 'y'), 
             'U3': (['Tsukuba', 'Kolkata', 'Sydney'], 'orange'), 
             'H1': (['Tsukuba', 'Ho Chi Minh city', 'Brisbane'], 'b'), 
             'E1': (['Tsukuba', 'Cork', 'Hanoi'], 'g'),
             'E2': (['Tsukuba', 'Ho Chi Minh city', 'Singapore'], 'g'),
                    }
        
    for ik, k in enumerate([['U1'], ['U2','U3'], ['H1'], ['E1', 'E2']][:]):
        
        grps = { k1: grpa[k1] for k1 in k }
        df = pd.read_excel('latlon.xlsx', index_col=0)
        #proj = ccrs.PlateCarree(central_longitude=145)
        #proj._threshold /= 10
        proj = ccrs.Robinson(central_longitude=145)
        
        plt.figure(figsize=(10, 6))
        ax = plt.axes(projection= proj )
        ax.coastlines(resolution='10m',lw=.1)
        #ax.gridlines()
        ax.stock_img()
        
        ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.5,lw=.3)
        ax.outline_patch.set_linewidth(.5)
        
        for i, row in df[:0].iterrows():
            ax.scatter(row.lon,row.lat,color='r',transform=ccrs.PlateCarree(),s=4)
            plt.plot([df.loc['Tsukuba'].lon, row.lon], [df.loc['Tsukuba'].lat, row.lat],
                 color='r', linewidth=row['lw']/2, marker=None,
                 transform=ccrs.PlateCarree(),
                 )
            x, y, fs, al = row.lon + row.x, row.lat + row.y, row.fs, row.al
            text = row['text'].replace(';','\n')
            plt.text( x, y, text, fontsize=fs, ha=al,
                     transform=ccrs.Geodetic(),fontweight = 'bold', 
                     )
            
    
        df.loc[:,'lon'] = np.where( df.lon.values < -10 , 360 + df.lon.values, df.lon.values)
        
        grpk = list(grps.keys())
        for gr in grpk:
            
            d1 = df.loc[grps[gr][0]]
            import matplotlib.patches as mpatches
            
            for i, row in d1[:].iterrows():
                ax.scatter(row.lon,row.lat,color='r',transform=ccrs.PlateCarree(),s=4)
                plt.plot([df.loc['Tsukuba'].lon, row.lon], [df.loc['Tsukuba'].lat, row.lat],
                     color='r', linewidth=row['lw']/2, marker=None,
                     transform=ccrs.Geodetic(),
                     )
                x, y, fs, al = row.lon + row.x, row.lat + row.y, row.fs, row.al
                text = row['text'].replace(';','\n')
                plt.text( x, y, text, fontsize=fs, ha=al,
                         transform=ccrs.PlateCarree(),
                         )
            
            
            
            
            lat_corners = d1.lat
            lon_corners = d1.lon # offset from gridline for clarity
            
            poly_corners = np.zeros((len(lat_corners), 2), np.float64)
            poly_corners[:,0] = lon_corners
            poly_corners[:,1] = lat_corners
        
        
            poly = mpatches.Polygon(poly_corners, 
                                    closed=True, ec='r', 
                                    fill=True, lw=1, 
                                    fc=grps[gr][1],
                                    alpha=0.4,
                                    #transform=ccrs.PlateCarree()
                                    transform=ccrs.Geodetic()
                                    ) # transform=ccrs.Geodetic())
            ax.add_patch(poly)
        
        
            #plt.plot(d1.lon,d1.lat, 
            #             color='r', lw = 1, marker=None,
            #             transform=ccrs.PlateCarree(),
            #             )
            
            plt.savefig('international_cooperation'+str(ik)+'.png', format='png', bbox_inches='tight', dpi = 200)

# %%
            

# %%
    

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%


# %%
sys.exit()

# %%
in_filename = 'data.csv' 
color_mode='screen'
out_filename='flights_map_mpl.png'
absolute=False
"""Plots the given CSV data files use matplotlib basemap and saves it to
a PNG file.
Args:
    in_filename: Filename of the CSV containing the data points.
    out_filename: Output image filename
    color_mode: Use 'screen' if you intend to use the visualisation for
                on screen display. Use 'print' to save the visualisation
                with printer-friendly colors.
    absolute: set to True if you want coloring to depend on your dataset
              parameter value (ie for comparison).
              When set to false, each coordinate pair gets a different
              color.
"""

# %%
if color_mode == 'screen':
    bg_color = (0.0, 0.0, 0, 1.0)
    coast_color = (204/255.0, 0, 153/255.0, 0.7)
    color_list = [(0.0, 0.0, 0.0, 0.0),
                  (204/255.0, 0, 153/255.0, 0.6),
                  (255/255.0, 204/255.0, 230/255.0, 1.0)]
else:
    bg_color = (1.0, 1.0, 1.0, 1.0)
    coast_color = (10.0/255.0, 10.0/255.0, 10/255.0, 0.8)
    color_list = [(1.0, 1.0, 1.0, 0.0),
                  (255/255.0, 204/255.0, 230/255.0, 1.0),
                  (204/255.0, 0, 153/255.0, 0.6)
                  ]

# %%
# define the expected CSV columns
CSV_COLS = ('dep_lat', 'dep_lon', 'arr_lat', 'arr_lon',
            'nb_flights', 'CO2')

# %%
routes = pd.read_csv(in_filename, names=CSV_COLS, na_values=['\\N'],
                     sep=';', skiprows=1)

# %%
num_routes = len(routes.index)

# %%
# normalize the dataset for color scale
norm = PowerNorm(0.3, routes['nb_flights'].min(),
                 routes['nb_flights'].max())
# norm = Normalize(routes['nb_flights'].min(), routes['nb_flights'].max())

# %%
# create a linear color scale with enough colors
if absolute:
    n = routes['nb_flights'].max()
else:
    n = num_routes
cmap = LinearSegmentedColormap.from_list('cmap_flights', color_list,
                                         N=n)
# create the map and draw country boundaries
plt.figure(figsize=(10, 8))
m = Basemap(projection='moll', lon_0=135)
m.drawcoastlines(color=coast_color, linewidth=1.0)
m.fillcontinents(color=bg_color, lake_color=bg_color)
m.drawmapboundary(fill_color=bg_color)

# %%
# plot each route with its color depending on the number of flights
for i, route in enumerate(routes.sort_values(by='nb_flights',
                          ascending=True).iterrows()):
    route = route[1]
    if absolute:
        color = cmap(norm(int(route['nb_flights'])))
    else:
        color = cmap(i * 1.0 / num_routes)

    line, = m.drawgreatcircle(route['dep_lon'], route['dep_lat'],
                              route['arr_lon'], route['arr_lat'],
                              linewidth=0.5, color=color)
    # if the path wraps the image, basemap plots a nasty line connecting
    # the points at the opposite border of the map.
    # we thus detect path that are bigger than 30km and split them
    # by adding a NaN
    path = line.get_path()
    cut_point, = np.where(np.abs(np.diff(path.vertices[:, 0])) > 30000e3)
    if len(cut_point) > 0:
        cut_point = cut_point[0]
        vertices = np.concatenate([path.vertices[:cut_point, :],
                                  [[np.nan, np.nan]],
                                  path.vertices[cut_point+1:, :]])
        path.codes = None  # treat vertices as a serie of line segments
        path.vertices = vertices

# %%
# save the map
plt.savefig(out_filename, format='png', bbox_inches='tight')

