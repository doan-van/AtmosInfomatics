# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
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
# # this script is to calculate drought index from climate data
# ##
#
# https://climate-indices.readthedocs.io/en/latest/
#
#

# %%
import sys, glob
import numpy as np
import xarray as xr
import pandas as pd

# %%
if 0:
    ifiles = sorted(glob.glob('download/era/data/*.nc') )
    ds = xr.open_mfdataset(ifiles) #['tp']
    do = ds.isel(longitude = np.arange(0,360,2), latitude = np.arange(0,181,2) )
    do.to_netcdf('era5_2deg.nc')

# %%
dg = tp.stack(point=('latitude', 'longitude')).groupby('point')
tp[0].plot()

# %%
tp = xr.open_dataset('era5_2deg.nc')['tp']


# %%
import xarray as xr
import pandas as pd
from scipy.stats import gamma, norm
import numpy as np

def spi_1d(precip_series, scale):
    # Rolling sum to compute SPI for the desired scale
    precip_roll = pd.Series(precip_series).rolling(window=scale, min_periods=scale).sum().values

    # Replace zero values with NaN and count them to compute zero probabilities
    zero_count = (precip_roll == 0).sum()
    prob_zero = zero_count / len(precip_roll)

    # Remove NaNs and values <= 0 for fitting
    valid_precip_roll = precip_roll[~np.isnan(precip_roll) & (precip_roll > 0)]

    # Check if there's enough data to fit the gamma distribution
    if len(valid_precip_roll) < scale:
        return np.full(len(precip_series), np.nan, dtype=np.float64)

    # Fit gamma distribution to non-zero precipitation data
    shape, loc, scale_param = gamma.fit(valid_precip_roll, floc=0)

    # Calculate cumulative probability of the gamma distribution for the entire series
    gamma_cdf = gamma.cdf(precip_roll, shape, loc=loc, scale=scale_param)

    # Normalize the CDF to account for the probability of zero precipitation
    adjusted_probabilities = prob_zero + ((1 - prob_zero) * gamma_cdf)

    # Convert adjusted probabilities to SPI (Z-score) using the normal distribution
    spi = norm.ppf(adjusted_probabilities)

    return spi

def calculate_spi_xarray(tp, scale=3):
    """
    Calculate Standardized Precipitation Index (SPI) from an xarray DataArray of precipitation.

    Parameters:
        tp (xarray.DataArray): Precipitation data with dimensions ('time', 'latitude', 'longitude').
        scale (int): The timescale over which SPI is computed (e.g., 3 for 3-month SPI).

    Returns:
        spi (xarray.DataArray): DataArray of SPI values with the same shape as the input.
    """
    # Apply SPI calculation along the 'time' dimension for each grid point
    spi = xr.apply_ufunc(
        spi_1d,
        tp,
        scale,
        input_core_dims=[['time'], []],
        output_core_dims=[['time'] ],
        vectorize=True,
        dask='allowed',
        output_dtypes=[np.float64]
    )

    return spi

# Example usage
# Assuming 'tp' is defined elsewhere as an xarray.DataArray
for scale in [3,6,12]:
    spi = calculate_spi_xarray(tp, scale=scale)
    spi = spi.transpose('time', 'latitude', 'longitude')
    spi.to_netcdf('spi_'+str(scale)+'mon.nc')


# %%
spi.dims

# %%
spi[30:50,:20,-100].plot()

# %%
(spi > 2.)[200].plot()

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gamma, norm

# Extract the precipitation time series for the specified grid point (latitude=50, longitude=50)
precip_series = tp[:, 50, 50].values
scale = 3  # Define the scale for SPI (e.g., 3 months)

# Step 1: Calculate the rolling sum for the desired scale
precip_roll = pd.Series(precip_series).rolling(window=scale, min_periods=scale).sum().values

# Plot the rolling sum
plt.figure(figsize=(10, 4))
plt.plot(tp.time.values, precip_roll, label=f"{scale}-Month Rolling Precipitation Sum", color="orange")
plt.title(f"{scale}-Month Rolling Sum of Precipitation at tp[:,50,50]")
plt.xlabel("Date")
plt.ylabel("3-Month Sum (mm)")
plt.legend()
plt.show()

# Step 2: Replace zero values with NaN and calculate the probability of zero precipitation
zero_count = (precip_roll == 0).sum()
prob_zero = zero_count / len(precip_roll)

# Display the probability of zero precipitation
print(f"Probability of zero precipitation: {prob_zero:.4f}")

# Step 3: Remove NaNs and values <= 0 for fitting the gamma distribution
valid_precip_roll = precip_roll[~np.isnan(precip_roll) & (precip_roll > 0)]

# Plot the cleaned rolling sum data
plt.figure(figsize=(10, 4))
plt.plot(tp.time.values[:len(valid_precip_roll)], valid_precip_roll, label="Cleaned 3-Month Rolling Sum", color="green")
plt.title("Cleaned 3-Month Rolling Sum of Precipitation (Valid Values Only)")
plt.xlabel("Date")
plt.ylabel("3-Month Sum (mm)")
plt.legend()
plt.show()

# Step 4: Fit a gamma distribution to the valid precipitation data
shape, loc, scale_param = gamma.fit(valid_precip_roll, floc=0)
print(f"Gamma Parameters - Shape: {shape:.4f}, Location: {loc:.4f}, Scale: {scale_param:.4f}")

# Step 5: Calculate cumulative probability of the gamma distribution for the entire series
gamma_cdf = gamma.cdf(precip_roll, shape, loc=loc, scale=scale_param)

# Plot the CDF values over time
plt.figure(figsize=(10, 4))
plt.plot(tp.time.values, gamma_cdf, label="Gamma CDF of 3-Month Precipitation Sum", color="purple")
plt.title("CDF of 3-Month Precipitation Sum at tp[:,50,50]")
plt.xlabel("Date")
plt.ylabel("CDF")
plt.legend()
plt.show()


# Plot the actual CDF values of rolling precipitation sums and the fitted gamma CDF
plt.figure(figsize=(10, 6))

# Plot histogram of valid precipitation data to approximate the empirical CDF
plt.hist(valid_precip_roll, bins=20, density=True, cumulative=True, alpha=0.5, color='skyblue', edgecolor='black', label="Empirical CDF")
# Generate x values for the gamma CDF plot based on valid precipitation values
x_vals = np.linspace(0, valid_precip_roll.max(), 100)
gamma_cdf_vals = gamma.cdf(x_vals, shape, loc=loc, scale=scale_param)
# Plot the fitted gamma CDF
plt.plot(x_vals, gamma_cdf_vals, "r-", label="Fitted Gamma CDF")

# Set plot titles and labels
plt.title("Empirical CDF and Fitted Gamma CDF of 3-Month Rolling Precipitation Sum")
plt.xlabel("Precipitation (3-Month Sum, mm)")
plt.ylabel("Cumulative Probability")
plt.legend()

plt.show()


# Step 6: Normalize the CDF to account for the probability of zero precipitation
adjusted_probabilities = prob_zero + ((1 - prob_zero) * gamma_cdf)

# Plot the adjusted probabilities over time
plt.figure(figsize=(10, 6))
plt.plot(tp.time.values, adjusted_probabilities, label="Adjusted Gamma CDF (with Zero Probability)", color="purple")
plt.show()

# Step 7: Convert adjusted probabilities to SPI using the normal distribution
spi_values = norm.ppf(adjusted_probabilities)

# Plot the SPI values
plt.figure(figsize=(10, 4))
plt.plot(tp.time.values, spi_values, label="Standardized Precipitation Index (SPI)", color="blue")
plt.title("Standardized Precipitation Index (SPI) Time Series at tp[:,50,50]")
plt.xlabel("Date")
plt.ylabel("SPI")
plt.legend()
plt.show()


# Plotting the Probability Density Function (PDF) and Cumulative Distribution Function (CDF) of the SPI values
plt.figure(figsize=(12, 6))

# PDF of SPI values
plt.subplot(1, 2, 1)
plt.hist(spi_values, bins=20, density=True, alpha=0.6, color="skyblue", edgecolor="black")
plt.title("Probability Density Function (PDF) of SPI Values")
plt.xlabel("SPI")
plt.ylabel("Density")

# CDF of SPI values
sorted_spi_values = np.sort(spi_values)
cdf_values = np.arange(1, len(sorted_spi_values) + 1) / len(sorted_spi_values)

plt.subplot(1, 2, 2)
plt.plot(sorted_spi_values, cdf_values, marker=".", linestyle="none", color="purple")
plt.title("Cumulative Distribution Function (CDF) of SPI Values")
plt.xlabel("SPI")
plt.ylabel("Cumulative Probability")

plt.tight_layout()
plt.show()

# %%

# %%

# %%

# %%

# %%

# %%
