import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
ds = xr.open_dataset('spi_12mon.nc')
spi = ds.tp
(ds.tp[200] <-2).plot()
plt.show()
(ds.tp[200] >2).plot()
plt.show()

import xarray as xr
import numpy as np

def categorize_spi(spi):
    """
    Categorize SPI values into integer categories based on thresholds.

    Parameters:
        spi (xarray.DataArray): SPI values with dimensions ('time', 'latitude', 'longitude').

    Returns:
        xarray.DataArray: Categorical SPI data with the same dimensions as the input, using integers.
    """
    # Initialize an empty DataArray with the same coordinates and dimensions as spi, filled with zeros
    spi_categorical = xr.full_like(spi, 0, dtype="int")

    # Apply conditions for each category using integer codes
    spi_categorical = spi_categorical.where(spi <= 2.0, 3)                     # Extremely wet
    spi_categorical = spi_categorical.where((spi <= 1.5) | (spi > 2.0), 2)     # Severely wet
    spi_categorical = spi_categorical.where((spi <= 1.0) | (spi > 1.5), 1)     # Moderately wet
    spi_categorical = spi_categorical.where((spi < -1.0) | (spi > 1.0), 0)     # Near normal
    spi_categorical = spi_categorical.where((spi < -1.5) | (spi >= -1.0), -1)  # Moderately dry
    spi_categorical = spi_categorical.where((spi < -2.0) | (spi >= -1.5), -2)  # Severely dry
    spi_categorical = spi_categorical.where(spi >= -2.0, -3)                   # Extremely dry

    return spi_categorical

# Example usage
# Assuming 'spi' is an xarray.DataArray with SPI values calculated previously
spi_categorical = categorize_spi(spi)

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
import itertools
import xarray as xr

# Example: Assuming spicat is an xarray.DataArray with dimensions (time, lat, lon)
# spicat = xr.DataArray(...)

# Convert spicat to float32 for memory efficiency
spicat = spicat.astype(np.float16)

# Get latitude and longitude dimensions
lat_dim, lon_dim = spicat.shape[1], spicat.shape[2]

# Generate all unique coordinate pairs
coord_pairs = list(itertools.combinations([(i, j) for i in range(lat_dim) for j in range(lon_dim)], 2))

# Initialize lists to store results
results = []

# Loop through each pair of coordinates
for (i, j), (m, n) in coord_pairs:
    # Extract time series for each coordinate pair as float32
    series1 = spicat[:, i, j].values.astype(np.float32)
    series2 = spicat[:, m, n].values.astype(np.float32)

    # Calculate agreement percentage, casting to float32
    agreement_percentage = np.nanmean((series1 == series2).astype(np.float32)) * 100

    # Filter out NaN values
    mask = ~np.isnan(series1) & ~np.isnan(series2)
    filtered_series1 = series1[mask].astype(np.float32)
    filtered_series2 = series2[mask].astype(np.float32)

    # Calculate Cohen's Kappa Score, handling empty cases
    kappa_score = cohen_kappa_score(filtered_series1, filtered_series2) if len(filtered_series1) > 0 else np.nan

    # Append results to the list
    results.append({
        "Coordinate Pair": ((i, j), (m, n)),
        "Agreement Percentage (%)": agreement_percentage,
        "Cohen's Kappa Score": kappa_score
    })

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Display the DataFrame
print(results_df)



