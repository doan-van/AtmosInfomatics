##
import sys

import numpy as np
import xarray as xr

# prepend the parent directory so it'll find the local climate_indices in the path
#if "/home/james/git/climate_indices" not in sys.path:
#    sys.path.insert(0, "/home/james/git/climate_indices")
    
sys.path.insert(0, "../src")
from climate_indices import compute, indices, utils
from climate_indices.compute import scale_values, Periodicity


if False:
    ds_lo = xr.open_dataset('example/input/nclimgrid_lowres_prcp.nc')
    
    # get the precipitation arrays, over which we'll compute the SPI
    da_precip_lo = ds_lo['prcp']
    # make sure we have the arrays with time as the inner-most dimension
    preferred_dims = ('lat', 'lon', 'time')
    da_precip_lo = da_precip_lo.transpose(*preferred_dims)
    


    da_precip_lo_groupby = da_precip_lo.stack(point=('lat', 'lon')).groupby('point')



        
        
    data_array = da_precip_lo
    months = 3
    data_start_year = 1940
    calibration_year_initial = 1940
    calibration_year_final = 2100
    # stack the lat and lon dimensions into a new dimension named point, so at each lat/lon
    # we'll have a time series for the geospatial point, and group by these points
    da_precip_groupby = data_array.stack(point=('lat', 'lon')).groupby('point')
    
    print(da_precip_groupby)
    spi_args = {
            'scale': months,
            'distribution': indices.Distribution.gamma,
            'data_start_year': data_start_year,
            'calibration_year_initial': calibration_year_initial,
            'calibration_year_final': calibration_year_final,
            'periodicity': compute.Periodicity.monthly
    }
    
    # apply the SPI function to the data array
    da_spi = xr.apply_ufunc(
        indices.spi,
        da_precip_groupby,
        kwargs=spi_args,
    )
    
    # unstack the array back into original dimensions
    da_spi = da_spi.unstack('point')
        
    
    
    x = list(da_precip_groupby)[1000][1]
    y = indices.spi(x, **spi_args)





# ERA5 data
ds = xr.open_dataset('prcp.nc').tp[:,:][::-1]  # not that latitude should have ascending order, otherwise, it does not work.
dg = ds.stack(point=('lat', 'lon')).groupby('point')

spi_args = {
        'scale': 12,
        'distribution': indices.Distribution.gamma,
        'data_start_year': 1,
        'calibration_year_initial': 20,
        'calibration_year_final': 50,
        'periodicity': compute.Periodicity.monthly
}


da_spi = xr.apply_ufunc(
    indices.spi,
    dg,
    kwargs=spi_args,
)

da_spi = da_spi.unstack('point')































