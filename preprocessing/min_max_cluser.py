import pandas as pd
import numpy as np
from pathlib import Path

def compute_monthly_statistics(file_path='cluster_timeseries_675days.csv',
                               out_cluster='monthly_cluster_stats.csv',
                               out_global='monthly_global_stats.csv'):
    # Leer el CSV
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')  # Agruparemos por mes

    # Solo trabajamos con registros individuales (no los promedios)
    df_individual = df[df['type'] == 'individual'].copy()

    # Calcular estadísticas por cluster y mes
    stats = df_individual.groupby(['cluster', 'month'])['value'].agg(
        total='sum',
        min='min',
        max='max',
        mean='mean',
        median='median'
    ).reset_index()

    stats['month'] = stats['month'].astype(str)
    stats.to_csv(out_cluster, index=False)
    print(f"Estadísticas mensuales por cluster guardadas en: {out_cluster}")

    # Calcular estadísticas globales (todos los clusters juntos)
    global_stats = df_individual.groupby('month')['value'].agg(
        total='sum',
        min='min',
        max='max',
        mean='mean',
        median='median'
    ).reset_index()

    global_stats['month'] = global_stats['month'].astype(str)
    global_stats.to_csv(out_global, index=False)
    print(f"Estadísticas mensuales globales guardadas en: {out_global}")


if __name__ == "__main__":
    compute_monthly_statistics()