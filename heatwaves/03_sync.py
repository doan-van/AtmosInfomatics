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

# %%
import os
import pandas as pd
import logging
# Define input parameters
input_directory = 'combine_selected'
variable_name = 'temp-max_C'
#quantile,min_duration = 0.9,3
quantile,min_duration = 0.75, 2
float_precision = "%.2f"  # Specify the precision for float values
max_lag = 3  # Example lag window of ±3 days
max_lag = 2

# %%
# Define output file path with more detailed directory structure
output_directory = f'detected_heatwaves/{variable_name}_q{quantile}_d{min_duration}'
output_file = os.path.join(output_directory, 'combined_heatwaves.csv')

# Read the combined heatwave events and pair stations for synchronization analysis
combined_heatwave_events = pd.read_csv(output_file, index_col=['station_number', 'start_date'], parse_dates=['start_date'])

# Get unique station numbers
station_numbers = combined_heatwave_events.index.get_level_values('station_number').unique()

# Initialize DataFrame to store synchronization results
synchronization_results = pd.DataFrame(index=combined_heatwave_events.index, columns=station_numbers)

# %%


for station_a in station_numbers[:]:
    print(station_a)
    for station_b in station_numbers[:]:
        if station_a == station_b: continue
        events_a = combined_heatwave_events.loc[station_a].index
        events_b = combined_heatwave_events.loc[station_b].index

        for sta in events_a:
            lag = (sta - events_b).days
            issyn = (lag >= 0) & (lag <=max_lag)
            if issyn.any(): 
                synchronization_results.loc[(station_a, sta), station_b] = events_b[issyn][0]




# %%
synchronization_results

# %%

# %%
# Save synchronization results to CSV
synchronization_output_file = os.path.join(output_directory, 'synchronization_results.csv')
synchronization_results.to_csv(synchronization_output_file, float_format=float_precision)
#logging.info(f"Saving synchronization results to {synchronization_output_file}.")

#print(f"Synchronization results saved to {synchronization_output_file}.")


# %%


