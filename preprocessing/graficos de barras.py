import pandas as pd

folder = '../dashboard_data/grafico_de_barras'
# Cargar el archivo CSV original
df = pd.read_csv('census_clean.csv')  # Cambia esto al nombre real del archivo

# Filtrar columnas numéricas útiles
df_numeric = df.select_dtypes(include=['number'])

# Agregamos la columna de nombre del LGA
df_numeric.insert(0, 'LGA_Name', df['LGA_Name'])

# Guardar un nuevo CSV para usar en D3
df_numeric.to_csv(f'{folder}/lga_data_clean.csv', index=False)

# Mostrar columnas numéricas disponibles
print("Variables disponibles para el gráfico:")
print(list(df_numeric.columns[1:]))