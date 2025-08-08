import pandas as pd
import numpy as np
from datetime import timedelta
from tslearn.preprocessing import TimeSeriesScalerMinMax
from tslearn.metrics import cdist_dtw
from scipy.cluster.hierarchy import linkage, fcluster
import json
import csv

def process_covid_data(file_path='covid_clean.csv'):
    """
    Procesa el archivo CSV de datos COVID para generar la matriz de casos diarios
    por LGA para los primeros 2 años de datos.

    Returns:
        - cases_matrix (np.ndarray): Matriz [n_LGA x días]
        - lga_codes (list): Lista de LGA_code19
        - dates (list): Lista de fechas únicas
    """
    df = pd.read_csv(file_path)
    df['notification_date'] = pd.to_datetime(df['notification_date'])
    df = df.sort_values(by='notification_date')

    # Filtrar primeros 2 años
    min_date = df['notification_date'].min()
    # max_date = min_date + timedelta(days=365 - 1)
    max_date = min_date + timedelta(days=675)
    df = df[df['notification_date'] <= max_date]
    df['notification_date'] = df['notification_date'].dt.date

    # Agrupar casos diarios
    daily_cases = df.groupby(['notification_date', 'lga_code19']).size().reset_index(name='case_count')

    unique_lgas = sorted(daily_cases['lga_code19'].unique())
    unique_dates = sorted(daily_cases['notification_date'].unique())

    lga_to_index = {lga: i for i, lga in enumerate(unique_lgas)}
    date_to_index = {date: i for i, date in enumerate(unique_dates)}

    # Crear matriz
    matrix = np.zeros((len(unique_lgas), len(unique_dates)), dtype=int)
    for _, row in daily_cases.iterrows():
        i = lga_to_index[row['lga_code19']]
        j = date_to_index[row['notification_date']]
        matrix[i, j] = row['case_count']

    return matrix, unique_lgas, unique_dates

def cluster_and_export(matrix, lga_codes, dates, n_clusters=4,
                       csv_out='cluster_timeseries_675days.csv',
                       json_out='lga_clusters.json'):
    """
    Realiza clustering con DTW, exporta series y asignación de clusters.

    Genera:
    - cluster_timeseries.csv: series por día, cluster y tipo (mean o individual)
    - lga_clusters.json: mapeo LGA_code -> cluster
    """
    # Normalizar
    scaler = TimeSeriesScalerMinMax()
    matrix_scaled = scaler.fit_transform(matrix)

    # Calcular distancias DTW y clustering jerárquico
    dist_matrix = cdist_dtw(matrix_scaled)
    Z = linkage(dist_matrix, method='average')
    labels = fcluster(Z, n_clusters, criterion='maxclust')

    # Guardar archivo CSV de series
    with open(csv_out, 'w', newline='') as f:
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

    # Guardar mapeo LGA -> cluster
    lga_cluster_map = {str(lga_codes[i]): int(labels[i]) for i in range(len(lga_codes))}
    with open(json_out, 'w') as jf:
        json.dump(lga_cluster_map, jf, indent=2)

# Ejecutar todo
if __name__ == "__main__":
    matrix, lga_codes, dates = process_covid_data()
    cluster_and_export(matrix, lga_codes, dates)