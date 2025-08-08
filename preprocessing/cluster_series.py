import pandas as pd
import numpy as np
from datetime import timedelta
from tslearn.preprocessing import TimeSeriesScalerMinMax
from tslearn.metrics import cdist_dtw
from scipy.cluster.hierarchy import linkage, fcluster
import csv

def process_covid_data(file_path='./covid_clean.csv'):
    df = pd.read_csv(file_path)
    df['notification_date'] = pd.to_datetime(df['notification_date'])
    df = df.sort_values(by='notification_date')

    # Dos años
    min_date = df['notification_date'].min()
    # max_date = min_date + timedelta(days=730 - 1)
    # max_date = min_date + timedelta(days=700 - 1)
    max_date = min_date + timedelta(days=365 - 1)
    df_two_years = df[df['notification_date'] <= max_date].copy()
    df_two_years['notification_date'] = df_two_years['notification_date'].dt.date

    daily_cases = df_two_years.groupby(['notification_date', 'lga_code19']).size().reset_index(name='case_count')

    unique_lgas = sorted(daily_cases['lga_code19'].unique())
    unique_dates = sorted(daily_cases['notification_date'].unique())

    lga_to_index = {lga: i for i, lga in enumerate(unique_lgas)}
    date_to_index = {date: i for i, date in enumerate(unique_dates)}

    cases_matrix = np.zeros((len(unique_lgas), len(unique_dates)), dtype=int)

    for _, row in daily_cases.iterrows():
        lga_idx = lga_to_index[row['lga_code19']]
        date_idx = date_to_index[row['notification_date']]
        cases_matrix[lga_idx, date_idx] = row['case_count']

    return cases_matrix, unique_dates

def cluster_and_export(matrix, dates, output_csv='./cluster_timeseries_1year.csv'):
    scaler = TimeSeriesScalerMinMax()
    X_scaled = scaler.fit_transform(matrix)
    distance_matrix = cdist_dtw(X_scaled)
    Z = linkage(distance_matrix, method='average')
    n_clusters = 4
    labels = fcluster(Z, n_clusters, criterion='maxclust')

    with open(output_csv, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'cluster', 'type', 'value', 'series_id'])

        for cluster_id in range(1, n_clusters + 1):
            cluster_series = matrix[labels == cluster_id]
            avg_series = cluster_series.mean(axis=0)

            for day_idx, date in enumerate(dates):
                writer.writerow([date, cluster_id, 'mean', avg_series[day_idx], 'avg'])

            for i, series in enumerate(cluster_series):
                for day_idx, date in enumerate(dates):
                    writer.writerow([date, cluster_id, 'individual', series[day_idx], f'LGA_{cluster_id}_{i}'])

cases_matrix, dates = process_covid_data()
cluster_and_export(cases_matrix, dates)
print("Termine")