#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 21:03:16 2024

@author: doan
"""

from mpi4py import MPI
import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
import itertools
import xarray as xr
import sys

# MPI setup
comm = MPI.COMM_WORLD
rank = comm.Get_rank()  # Get process rank
size = comm.Get_size()  # Get number of processes

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

# Load and categorize SPI data
ds = xr.open_dataset('spi_12mon.nc')
spi = ds.tp
spi_categorical = categorize_spi(spi)[:,::2,::2]

# Prepare data for calculations
spicat = spi_categorical[11:]
spicat = spicat.where(~spicat.isin([-1, 0, 1]), np.nan).astype(np.float16)
spicat_flat = spicat.stack(flat_spatial=("latitude", "longitude"))

# Generate all coordinate pairs
num_locations = spicat_flat.shape[1]
coord_pairs = list(itertools.combinations(range(num_locations), 2))

# Split the coordinate pairs among processes
pairs_per_proc = len(coord_pairs) // size
start_idx = rank * pairs_per_proc
end_idx = (rank + 1) * pairs_per_proc if rank != size - 1 else len(coord_pairs)
local_pairs = coord_pairs[start_idx:end_idx]

# Local results for each process
local_results = []

# Calculate Cohen's Kappa Score for each assigned pair
for idx1, idx2 in local_pairs:
    print(rank, idx1)
    series1 = spicat_flat[:, idx1].values
    series2 = spicat_flat[:, idx2].values

    mask = ~np.isnan(series1) & ~np.isnan(series2)
    filtered_series1 = series1[mask]
    filtered_series2 = series2[mask]

    kappa_score = cohen_kappa_score(filtered_series1, filtered_series2) if len(filtered_series1) > 0 else np.nan
    local_results.append(kappa_score)

# Gather results from all processes to the root process
all_results = comm.gather(local_results, root=0)

# Only the root process will combine results and save to NetCDF
if rank == 0:
    # Flatten list of lists
    all_results_flat = [item for sublist in all_results for item in sublist]
    # Convert coordinate pairs to numpy array
    coord_pairs_array = np.array(coord_pairs)
    # Create xarray Dataset
    results_ds = xr.Dataset({
        'coord_pairs': (['pair', 'coords'], coord_pairs_array),
        'kappa_scores': (['pair'], all_results_flat)
    })
    # Save to NetCDF file
    results_ds.to_netcdf('kappa_scores.nc')

