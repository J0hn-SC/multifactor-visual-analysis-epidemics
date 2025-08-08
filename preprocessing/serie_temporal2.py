import pandas as pd
from datetime import datetime
import numpy as np

folder = '../dashboard_data/serie_temporal'

# Load the CSV file
df = pd.read_csv('cases_NSW.csv')  # Replace with your file path

# Convert notification_date to datetime
df['notification_date'] = pd.to_datetime(df['notification_date'], format='%Y-%m-%d')

# Ensure lga_name19 is clean
df['lga_name19'] = df['lga_name19'].str.strip()

# Create quarter and week columns
df['quarter'] = df['notification_date'].dt.to_period('Q')
df['week'] = df['notification_date'].dt.strftime('%Y-W%U')

# Get all LGAs and create "All NSW"
lgas = df['lga_name19'].unique().tolist()
lgas.append('All NSW')

# Define all quarters from 2020Q1 to 2022Q1
date_range = pd.date_range(start='2020-01-01', end='2022-03-31', freq='Q')
quarters = [x.to_period('Q') for x in pd.to_datetime(date_range)]

# Create a complete list of LGA-quarter combinations
lga_quarter_combinations = pd.MultiIndex.from_product([lgas, quarters], names=['lga_name19', 'quarter']).to_frame(index=False)

# 1. Aggregate cases quarterly by LGA
quarterly_lga = df.groupby(['lga_name19', 'quarter']).size().reset_index(name='cases')

# Merge with all LGA-quarter combinations to include zeros
quarterly_lga = lga_quarter_combinations.merge(quarterly_lga, on=['lga_name19', 'quarter'], how='left').fillna({'cases': 0})
quarterly_lga['cases'] = quarterly_lga['cases'].astype(int)

# 2. Aggregate cases quarterly for all NSW
quarterly_nsw = df.groupby('quarter').size().reset_index(name='cases')
quarterly_nsw['lga_name19'] = 'All NSW'
quarterly_nsw = lga_quarter_combinations[lga_quarter_combinations['lga_name19'] == 'All NSW'].merge(
    quarterly_nsw, on=['lga_name19', 'quarter'], how='left').fillna({'cases': 0})
quarterly_nsw['cases'] = quarterly_nsw['cases'].astype(int)

# Combine LGA and NSW quarterly data
quarterly_data = pd.concat([quarterly_lga, quarterly_nsw], ignore_index=True)

# Calculate quarterly stats (min, max, mean, median)
# Since each quarter has one case count, min=max=mean=median=cases
# quarterly_data['min_cases'] = quarterly_data['cases']
# quarterly_data['max_cases'] = quarterly_data['cases']
# quarterly_data['mean_cases'] = quarterly_data['cases']
# quarterly_data['median_cases'] = quarterly_data['cases']

# Create a complete list of weeks for each quarter and LGA
weeks = pd.date_range(start='2020-01-01', end='2022-03-31', freq='W-MON')
week_quarter_map = pd.DataFrame({
    'week': [x.strftime('%Y-W%U') for x in weeks],
    'quarter': [pd.to_datetime(x).to_period('Q') for x in weeks]
})
lga_week_quarter_combinations = pd.MultiIndex.from_product(
    [lgas, quarters, week_quarter_map['week'].unique()],
    names=['lga_name19', 'quarter', 'week']
).to_frame(index=False)
lga_week_quarter_combinations = lga_week_quarter_combinations.merge(
    week_quarter_map, on=['week', 'quarter'], how='inner')

# 3. Aggregate cases weekly by LGA and quarter
weekly_lga = df.groupby(['lga_name19', 'quarter', 'week']).size().reset_index(name='cases')
#stats semanales-------------- yo lo añadi
summary = weekly_lga.groupby(['lga_name19', 'quarter'])['cases'].agg(
    min_cases='min',
    max_cases='max',
    mean_cases='mean',
    median_cases='median'
).reset_index()
quarterly_data = quarterly_data.merge(
    summary,
    on=['lga_name19', 'quarter'],
    how='left'
)
#--------------------------

# Merge with all LGA-week-quarter combinations to include zeros
weekly_lga = lga_week_quarter_combinations.merge(weekly_lga, on=['lga_name19', 'quarter', 'week'], how='left').fillna({'cases': 0})
weekly_lga['cases'] = weekly_lga['cases'].astype(int)

# 4. Aggregate cases weekly for all NSW
weekly_nsw = df.groupby(['quarter', 'week']).size().reset_index(name='cases')
weekly_nsw['lga_name19'] = 'All NSW'
weekly_nsw = lga_week_quarter_combinations[lga_week_quarter_combinations['lga_name19'] == 'All NSW'].merge(
    weekly_nsw, on=['lga_name19', 'quarter', 'week'], how='left').fillna({'cases': 0})
weekly_nsw['cases'] = weekly_nsw['cases'].astype(int)

# Combine weekly LGA and NSW data
weekly_data = pd.concat([weekly_lga, weekly_nsw], ignore_index=True)

# Save to CSV files
quarterly_data.to_csv(f'{folder}/quarterly_cases.csv', index=False)
weekly_data.to_csv(f'{folder}/weekly_cases.csv', index=False)

# Calculate global summary statistics for each LGA and NSW (unchanged)
summary_stats = quarterly_data.groupby('lga_name19').agg({
    'cases': ['min', 'max', 'mean', 'median']
}).reset_index()

# Flatten column names
summary_stats.columns = ['lga_name19', 'min_cases', 'max_cases', 'mean_cases', 'median_cases']
summary_stats.to_csv(f'{folder}/summary_stats.csv', index=False)