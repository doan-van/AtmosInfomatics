# ---
# jupyter:
#   jupytext:
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
# # Create Koppen map
#
# Data downloaded from 
# https://figshare.com/articles/dataset/High-resolution_1_km_K_ppen-Geiger_maps_for_1901_2099_based_on_constrained_CMIP6_projections/21789074/1
#
# https://www.gloh2o.org/koppen/
#
# Paper from Beck
# https://www.nature.com/articles/sdata2018214
#
# Data have been downloaded and saved in Google Drive
# https://drive.google.com/drive/folders/1e2tRj7WXnycS_EXVbo9pGR6I-o2-V0NL?usp=sharing
#
# Github for reference:
# https://github.com/salvah22/koppenclassification
#
# Koppen wiki: https://en.wikipedia.org/wiki/K%C3%B6ppen_climate_classification
#
#

# %%
import xarray as xr
import numpy as np

# %% [markdown]
#

# %%
idir = '/Users/doan/MyDrive/share/2024/clim_class_data/' # google drive data (shared)

# %%
# !ls /Users/doan/MyDrive/share/2024/clim_class_data/21789074/
# !ls /Users/doan/MyDrive/share/2024/clim_class_data/21789074/climate_data_0p1/ 

# %%
#ifile = idir + '21789074/climate_data_1p0/1991_2020/ensemble_mean_1p0.nc'
ifile = idir + '21789074/climate_data_0p1/1991_2020/ensemble_mean_0p1.nc'
dc = xr.open_dataset(ifile)

# %%
dc.air_temperature[0].plot()

# %%
t = dc.air_temperature    # temperature
p = dc.precipitation      # precipitation
lon, lat = np.meshgrid(dc.lon, dc.lat)
s = xr.DataArray(lat < 0, dims = ['lat', 'lon'], coords = {'lat':dc.lat, 'lon':dc.lon})

# %%
s # s is boolearn if south True, else False
# s have same frame with p, except having no time dimension


# %%
t[0].plot()
plt.show()
p[0].plot()
plt.show()
s.plot()

# %% [markdown]
# ## Use apply ufunc
#
# https://docs.xarray.dev/en/stable/generated/xarray.apply_ufunc.html
#
#
#

# %%
from koppen_class import koppen_vd

def koppen_classification_along_latlon(a, b, c):
    if np.isnan(a).any():
        return 'unknown'
    else:
        return koppen_vd(a,b,c) 


# %% [markdown]
# ### Use apply ufunc to parallelly calculating
#
# https://docs.xarray.dev/en/stable/generated/xarray.apply_ufunc.html
#
#

# %%
kpc = xr.apply_ufunc(koppen_classification_along_latlon, # this is the function defined above
                        p, t, s, # arguments of function (three arguments: precip, temp, and boolean south )
                        input_core_dims=[["time"], ["time"], []], # use array via dim "time" in precip, temp, and one value in south
                        output_core_dims=[[]], # output have one value
                        vectorize=True,  # seach line for more information
                        dask='allowed' # seach line for more information
                       )

# %%
# output have two dimensions 'lat', 'lon'
kpc

# %% [markdown]
# ### Convert symbol to number using Koppen_class_list excel file

# %%
import pandas as pd
kp = pd.read_excel('Koppen_class_list.xlsx', index_col=1)
kp

x = np.zeros(kpc.shape)
for i, r in kp.iterrows():
    x = np.where(kpc == i, r['No'], x)
    
plt.imshow(x)

# %% [markdown]
# ### Save to file

# %%
do = kp.set_index('No').to_xarray()
do['koppen_ind'] = ( ['lat', 'lon'], x) 
do.coords['lat'] = (('lat'),dc['lat'].values )
do.coords['lon'] = (('lon'),dc['lon'].values )
do.to_netcdf('koppen_vd_0p1.nc')

# %%



# %% [markdown]
# ## Plot

# %%
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import matplotlib.colors as mcolors
from matplotlib.colors import from_levels_and_colors

# %%
dx = do
kp = pd.read_excel('Koppen_class_list.xlsx', index_col=1)
lev = [.5]  + [ r['No'] + 0.5 for i, r in kp.iterrows()]
cols =    [ r['Color'] for i, r in kp.iterrows() ]
legend_handles = [ patches.Patch(color = r['Color'], label=i )  for i, r in kp.iterrows() ]

lon, lat = np.meshgrid(dx.lon, dx.lat)
data = dx.koppen_ind
cmap, norm = from_levels_and_colors(lev, cols)
fig, ax = plt.subplots(figsize=(10, 5), subplot_kw={'projection': ccrs.PlateCarree()})
# Add geographic features
#ax.add_feature(cfeature.LAND)
#ax.add_feature(cfeature.OCEAN)
#ax.add_feature(cfeature.COASTLINE)
#ax.add_feature(cfeature.BORDERS, linestyle=':')
mesh = ax.pcolormesh(lon, lat, data, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())
#ax.set_extent([70, 155, 0, 60], crs=ccrs.PlateCarree())

# Add gridlines
ax.gridlines(draw_labels=True)
plt.legend(handles=legend_handles, loc='lower left', fontsize=7, ncols=10,
           bbox_to_anchor=(0, -.3))
# Show the plot
plt.title('')
plt.show()


# %%

# %%

# %%

# %% [markdown]
# ### Plot orginal data downloaded
#
#
#
#
#

# %%
dk = xr.open_dataset(idir+'21789074/koppen_geiger_nc/1991_2020/koppen_geiger_0p1.nc')
kDict = {
    "Af": 1,"Am": 2,"Aw": 3, 
    "BWh": 4, "BWk": 5, "BSh": 6, "BSk": 7,
    "Csa": 8, "Csb": 9, "Csc": 10, "Cwa": 11, "Cwb": 12, "Cwc": 13, "Cfa": 14, "Cfb": 15, "Cfc": 16,
    "Dsa": 17, "Dsb": 18, "Dsc": 19, "Dsd": 20, "Dwa": 21, "Dwb": 22, "Dwc": 23, "Dwd": 24, "Dfa": 25, "Dfb": 26, "Dfc": 27, "Dfd": 28,
    "ET": 29, "EF": 30
}

# %%
data = dk.kg_class.values
lon, lat = np.meshgrid(dk.lon, dk.lat)
kp = pd.read_excel('Koppen_class_list.xlsx', index_col=1)
lev = [.5]  + [ r['No'] + 0.5 for i, r in kp.iterrows()]
cols =    [ r['Color'] for i, r in kp.iterrows() ]
legend_handles = [ patches.Patch(color = r['Color'], label=i )  for i, r in kp.iterrows() ]

# %%
kp

# %%
x = np.zeros(data.shape)
for k in list(kDict.keys()): x = np.where(data==kDict[k], kp.loc[k,'No'], x)

# %%
dat = x
# Define a colormap with specific colors for each category
cmap, norm = from_levels_and_colors(lev, cols)
# Create a plot with a specific projection
fig, ax = plt.subplots(figsize=(10, 5), subplot_kw={'projection': ccrs.PlateCarree()})
mesh = ax.pcolormesh(lon, lat, dat, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())
ax.set_extent([70, 155, 0, 60], crs=ccrs.PlateCarree())
ax.gridlines(draw_labels=True)
plt.legend(handles=legend_handles, loc='lower left', fontsize=7, ncols=10,
           bbox_to_anchor=(0, -.3))
plt.title('Koppen map')
plt.show()
