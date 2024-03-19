##
# single level: https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=form
# https://cds.climate.copernicus.eu/toolbox/doc/how-to/1_how_to_retrieve_data/1_how_to_retrieve_data.html



# https://confluence.ecmwf.int/display/CKB/Climate+Data+Store+%28CDS%29+API+Keywords




import xarray as xr 
import cdsapi
 
c = cdsapi.Client()
 
years = [ str(i) for i in range(1940,2023)]
month = [ '%.2d' % i for i in range(1,13)]
for y in years[:0]:
    c.retrieve(
        'reanalysis-era5-single-levels-monthly-means',
        {
            'product_type': 'monthly_averaged_reanalysis',
            'variable': ['2m_temperature', 'total_precipitation'],
            'year': y,
            'month': month,
            'time': '00:00',
            'format': 'netcdf',
            'grid': [2.0,2.],
            #'area': [45, 0, 43,11,],
        },
        'data_2deg/'+y+'.nc')

# land mask
c.retrieve(
    'reanalysis-era5-single-levels-monthly-means',
    {
        'product_type': 'monthly_averaged_reanalysis',
        'variable':'land_sea_mask' ,
        'year': "2022",
        'month': "01",
        'time': '00:00',
        'format': 'netcdf',
        'grid': [2.0,2.],
        #'area': [45, 0, 43,11,],
    },
    'landmask_2deg.nc')






