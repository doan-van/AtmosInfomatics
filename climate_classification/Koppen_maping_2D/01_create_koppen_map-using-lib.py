# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Create Koppen map
#
# ### Using koppen_classification library
#
# https://github.com/doan-van/Koppen-Geiger-climate-classification
#
# ### Install:
#
# pip install git+https://github.com/doan-van/Koppen-Geiger-climate-classification.git
#
#
# ### Data
# 1. Original High-Resolution 1-km Köppen-Geiger Maps
# https://figshare.com/articles/dataset/High-resolution_1_km_K_ppen-Geiger_maps_for_1901_2099_based_on_constrained_CMIP6_projections/21789074/1
#
# https://www.gloh2o.org/koppen/
#
# 2. Beck et al. 2018 Paper (Nature)
# https://www.nature.com/articles/sdata2018214
#
# 3. Data have been downloaded and saved in Google Drive
# https://drive.google.com/drive/folders/1e2tRj7WXnycS_EXVbo9pGR6I-o2-V0NL?usp=sharing
#
#

# %%
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr

# %%
from koppen_classification import KoppenClassification

precip = np.array([30, 40, 20, 60, 80, 100, 150, 140, 90, 70, 50, 40])
temp = np.array([10, 12, 15, 18, 20, 25, 30, 28, 22, 15, 12, 8])

koppen = KoppenClassification(precip, temp, south=False)
print("Classification:", koppen.get_classification(writeout=True))

koppen_south = KoppenClassification(precip, temp, south=True)
print("Classification (Southern Hemisphere):", koppen_south.get_classification(writeout=True))

koppen.plot_hythergraph(title="Monthly Temperature and Precipitation")
plt.show()

# %%
koppen.get_classification()

# %%
idir = '/Users/doan/MyDrive/share/2024/clim_class_data/' # google drive data (shared)

# %%
# !ls /Users/doan/MyDrive/share/2024/clim_class_data/21789074/

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
# # Method 2: Climate classification using predefined library
#

# %%
def koppen_classification_along_latlon(a, b, c): # a is precipitation; b is temperature
    if np.isnan(a).any(): return 'unknown' 
    else: return KoppenClassification(a,b,c).get_classification()

### Use apply ufunc to parallelly calculating
# https://docs.xarray.dev/en/stable/generated/xarray.apply_ufunc.html
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
kp = pd.read_excel('../Koppen_class_list.xlsx', index_col=1)
kp

x = np.zeros(kpc.shape)
for i, r in kp.iterrows():
    x = np.where(kpc == i, r['No'], x)
    
plt.imshow(x)

do = kp.set_index('No').to_xarray()
do['koppen_ind'] = ( ['lat', 'lon'], x) 
do.coords['lat'] = (('lat'),dc['lat'].values )
do.coords['lon'] = (('lon'),dc['lon'].values )
do.to_netcdf('koppen_vd_0p1_lib.nc')


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

