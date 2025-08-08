import pandas as pd
import json
from datetime import datetime

def load_lga_cluster_map(json_file='./lga_clusters.json'):
    with open(json_file, 'r') as f:
        return json.load(f)

def generate_monthly_stats(covid_file='./covid_clean.csv', cluster_map_file='./lga_clusters.json',
                            out_cluster='monthly_cluster_stats_fixed.csv',
                            out_global='monthly_global_stats_fixed.csv'):
    # Leer archivos
    df = pd.read_csv(covid_file)
    cluster_map = load_lga_cluster_map(cluster_map_file)

    # Convertir fecha
    df['notification_date'] = pd.to_datetime(df['notification_date'])
    df['month'] = df['notification_date'].dt.to_period('M')

    # Filtrar por LGAs conocidos (evita HotelQ o códigos raros como "X999")
    df = df[df['lga_code19'].astype(str).isin(cluster_map.keys())].copy()

    # Asignar cluster
    df['cluster'] = df['lga_code19'].astype(str).map(cluster_map)

    # Agrupar: contar casos por día y LGA
    daily_cases = df.groupby(['month', 'notification_date', 'lga_code19', 'cluster']).size().reset_index(name='cases')

    # --- Estadísticas por cluster ---
    cluster_stats = daily_cases.groupby(['cluster', 'month'])['cases'].agg(
        total='sum',
        min='min',
        max='max',
        mean='mean',
        median='median'
    ).reset_index()
    cluster_stats['month'] = cluster_stats['month'].astype(str)
    cluster_stats.to_csv(out_cluster, index=False)
    print(f"✅ Estadísticas por cluster guardadas en: {out_cluster}")

    # --- Estadísticas globales ---
    global_stats = daily_cases.groupby(['month'])['cases'].agg(
        total='sum',
        min='min',
        max='max',
        mean='mean',
        median='median'
    ).reset_index()
    global_stats['month'] = global_stats['month'].astype(str)
    global_stats.to_csv(out_global, index=False)
    print(f"✅ Estadísticas globales guardadas en: {out_global}")

if __name__ == "__main__":
    generate_monthly_stats()