import sys, glob
import numpy as np
import xarray as xr
sys.path.insert(0, "climindices/src")
from climate_indices import compute, indices, utils
from climate_indices.compute import scale_values, Periodicity


ifiles = sorted(glob.glob('download/era/data/*.nc') )

tp = xr.open_mfdataset(ifiles)['tp']
# not that latitude should have ascending order, otherwise, it does not work.
tp = tp[:, ::-1]



# ERA5 data
dg = tp.stack(point=('latitude', 'longitude')).groupby('point')

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
    dask="allowed",
    kwargs=spi_args,
)

da_spi = da_spi.unstack('point')































