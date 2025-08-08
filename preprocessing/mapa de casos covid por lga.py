import pandas as pd

folder = '../dashboard_data/mapa_casos_por_lga'
# Cargar archivo original
cases_df_dirty = pd.read_csv('cases_NSW.csv')
covid_df = cases_df_dirty.dropna().convert_dtypes()

# Convertir fechas
covid_df["date"] = pd.to_datetime(covid_df["notification_date"])
covid_df["year_month"] = covid_df["date"].dt.to_period("M").astype(str)

# Calcular casos por LGA y mes
monthly_cases = covid_df.groupby(["lga_code19", "year_month"]).size().reset_index(name="MonthlyCases")

# --- Rellenar todos los meses posibles por LGA ---
# Crear lista de meses desde ene 2020 hasta feb 2022
all_months = pd.date_range("2020-01", "2022-02", freq="MS").to_period("M").astype(str)
all_lgas = covid_df["lga_code19"].unique()

# Crear cartesian product entre LGA y meses
full_index = pd.MultiIndex.from_product([all_lgas, all_months], names=["lga_code19", "year_month"])
df_full = pd.DataFrame(index=full_index).reset_index()

# Merge para incluir todos los meses por LGA, rellenando con 0 si no hay datos
monthly_complete = df_full.merge(monthly_cases, on=["lga_code19", "year_month"], how="left")
monthly_complete["MonthlyCases"] = monthly_complete["MonthlyCases"].fillna(0).astype(int)

# Calcular casos acumulados por LGA
monthly_complete["CumulativeCases"] = (
    monthly_complete.sort_values(["lga_code19", "year_month"])
    .groupby("lga_code19")["MonthlyCases"]
    .cumsum()
)

# Guardar CSV limpio
monthly_complete.to_csv(f"{folder}covid_monthly_summary_filled.csv", index=False)