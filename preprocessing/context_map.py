import numpy as np
from scipy.spatial.distance import pdist, squareform
import pandas as pd
import seaborn as sns
from sklearn.preprocessing import StandardScaler
def compute_data_context_distance_matrix(X: np.ndarray) -> np.ndarray:
    """
    Construye la matriz de distancia compuesta (m+n) x (m+n)
    a partir de una matriz de datos de tamaño m x n.

    Args:
        X: np.ndarray de forma (m, n)

    Returns:
        D: np.ndarray de forma (m+n, m+n), matriz de distancias compuesta
    """
    m, n = X.shape

    # 1. Data-to-Data (DD)
    dd = squareform(pdist(X, metric='euclidean'))  # (m x m)

    # 2. Variable-to-Variable (VV)
    corr_matrix = np.corrcoef(X.T)                # (n x n)
    vv = 1 - np.abs(corr_matrix)                  # distancia = 1 - |correlación|

    # 3. Data-to-Variable (DV)
    unit_vectors = np.eye(n)                      # Vectores unitarios para variables
    dv = np.zeros((m, n))
    for i in range(m):
        for j in range(n):
            dv[i, j] = np.linalg.norm(X[i] - unit_vectors[j])  # distancia euclidiana

    # 4. Variable-to-Data (VD)
    vd = dv.T  # simétrico en este modelo

    # 5. Matriz final
    top = np.hstack((dd, dv))     # (m x m+n)
    bottom = np.hstack((vd, vv))  # (n x m+n)
    D = np.vstack((top, bottom))  # (m+n x m+n)

    return D


import matplotlib.pyplot as plt
from sklearn.manifold import MDS

def plot_mds_from_distance_matrix(D, m, n):
    """
    Aplica MDS a una matriz de distancias (m+n x m+n) y grafica los puntos resultantes.

    Args:
        D: np.ndarray de forma (m+n, m+n), matriz de distancias
        m: int, número de registros (datos)
        n: int, número de variables (atributos)
        return_coords: bool, si True devuelve las coordenadas 2D resultantes

    Returns:
        coords: np.ndarray de forma (m+n, 2), coordenadas 2D de todos los puntos
    """
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
    coords = mds.fit_transform(D)

    # Graficar resultados
    plt.figure(figsize=(8, 6))

    # Datos
    plt.scatter(coords[:m, 0], coords[:m, 1], c='blue', label='Datos')
    for i in range(m):
        plt.text(coords[i, 0], coords[i, 1], f'D{i+1}', fontsize=9, color='blue')

    # Variables
    plt.scatter(coords[m:, 0], coords[m:, 1], c='red', marker='^', label='Variables')
    for j in range(n):
        plt.text(coords[m+j, 0], coords[m+j, 1], f'V{j+1}', fontsize=9, color='red')

    plt.title('Proyección 2D usando MDS')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

    return coords



from scipy.stats import gaussian_kde
import numpy as np

def compute_akde_density(points_2d, grid_size=100, bandwidth='scott', margin=1.0):
    """
    Calcula el mapa de densidad adaptativo sobre puntos 2D con KDE.
    
    Args:
        points_2d: np.ndarray de forma (m, 2), coordenadas 2D
        grid_size: resolución del grid
        bandwidth: ancho del kernel ('scott', 'silverman' o float)
        margin: margen alrededor del área a cubrir

    Returns:
        xgrid, ygrid: mallas de coordenadas
        density: matriz de densidad evaluada sobre el grid
    """
    kde = gaussian_kde(points_2d.T, bw_method=bandwidth)

    x_min, x_max = points_2d[:, 0].min() - margin, points_2d[:, 0].max() + margin
    y_min, y_max = points_2d[:, 1].min() - margin, points_2d[:, 1].max() + margin
    xgrid, ygrid = np.mgrid[x_min:x_max:grid_size*1j, y_min:y_max:grid_size*1j]
    grid_coords = np.vstack([xgrid.ravel(), ygrid.ravel()])
    density = kde(grid_coords).reshape(xgrid.shape)

    return xgrid, ygrid, density



def nadaraya_watson_regression(points_2d, values, grid_size=100, bandwidth=0.5):
    """
    Aproxima una regresión de Nadaraya-Watson sobre puntos 2D con valores asociados.
    
    Args:
        points_2d: np.ndarray (m, 2), coordenadas 2D
        values: np.ndarray (m,), valores asociados a cada punto
        grid_size: resolución de la grilla
        bandwidth: ancho del kernel Gaussiano

    Returns:
        xgrid, ygrid: mallas
        reg_values: valores suavizados interpolados
    """
    from sklearn.metrics.pairwise import euclidean_distances

    x_min, x_max = points_2d[:, 0].min(), points_2d[:, 0].max()
    y_min, y_max = points_2d[:, 1].min(), points_2d[:, 1].max()
    xgrid, ygrid = np.meshgrid(
        np.linspace(x_min, x_max, grid_size),
        np.linspace(y_min, y_max, grid_size)
    )
    grid_points = np.column_stack([xgrid.ravel(), ygrid.ravel()])
    
    # Distancias punto a punto
    dists = euclidean_distances(grid_points, points_2d)
    weights = np.exp(- (dists**2) / (2 * bandwidth**2))
    
    weighted_values = weights @ values
    sum_weights = weights.sum(axis=1)
    reg_values = np.divide(weighted_values, sum_weights, out=np.zeros_like(weighted_values), where=sum_weights!=0)
    return xgrid, ygrid, reg_values.reshape(xgrid.shape)




import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def plot_contour_boundaries(xgrid, ygrid, surface, ax=None, levels=5, color='k', linewidth=1):
    """
    Traza contornos sobre una superficie (densidad o regresión).

    Args:
        xgrid, ygrid: mallas de coordenadas 2D
        surface: matriz con los valores sobre los que se trazan contornos
        ax: objeto Axes opcional de matplotlib
        levels: número o lista de niveles de contorno
        color: color de los contornos
        linewidth: grosor de línea

    Returns:
        contours: objeto matplotlib.contour.QuadContourSet
    """
    if ax is None:
        ax = plt.gca()

    contours = ax.contour(xgrid, ygrid, surface, levels=levels, colors=color, linewidths=linewidth)
    ax.clabel(contours, inline=True, fontsize=8, fmt=ticker.FuncFormatter(lambda x, _: f"{x:.2f}"))
    return contours






# X = np.array([
#     [1, 2, 3],
#     [3, 1, 4],
#     [2, 4, 1],
#     [0, 2, 2],
#     [4, 3, 0]
# ])
# D = compute_data_context_distance_matrix(X)
# print(np.round(D, 2))  # redondeado para lectura
# m, n = X.shape
# plot_mds_from_distance_matrix(D, m, n)
selected_10 = [
    'Population_Density',
    'MedianAge',
    'PercentofPublicTransportation',
    'MedianHouseholdIncome',
    'Persons_per_Bedroom',
    'LowIncome%',
    'Person>=70',
    'Population',
    'Young',
    'Elderly'
]


df = pd.read_csv('census_clean.csv')
df_reduced = df.dropna()
df_reduced = df_reduced.iloc[:, 3:]
df_reduced_clean = df_reduced.dropna()
# df_selected = df_reduced_clean[selected_10].dropna()
df_selected = df_reduced_clean

scaler = StandardScaler()

sns.heatmap(df_selected.corr(), annot=True, cmap='coolwarm')
plt.title("Correlación entre variables seleccionadas")
plt.show()


df_clean = df_selected.apply(pd.to_numeric, errors='coerce')
X = df_clean.to_numpy()
X_scaled = scaler.fit_transform(X)
D = compute_data_context_distance_matrix(X_scaled)
print(np.round(D, 2))
m, n = X_scaled.shape
coords = plot_mds_from_distance_matrix(D, m, n)
data_coords = coords[:m]


xgrid, ygrid, density = compute_akde_density(data_coords)





# fig, ax = plt.subplots(figsize=(8, 6))
# ax.contourf(xgrid, ygrid, density, levels=100, cmap='Blues', alpha=0.5)
# plot_contour_boundaries(xgrid, ygrid, density, ax=ax, levels=5)

# ax.scatter(data_coords[:, 0], data_coords[:, 1], color='blue', label='Datos')
# ax.scatter(coords[m:, 0], coords[m:, 1], color='red', marker='^', label='Variables')

# ax.set_title("Mapa con AKDE + Contornos")
# ax.legend()
# plt.tight_layout()
# plt.show()


fig, ax = plt.subplots(figsize=(10, 7))

# Fondo KDE + contornos
ax.contourf(xgrid, ygrid, density, levels=100, cmap='Blues', alpha=0.5)
plot_contour_boundaries(xgrid, ygrid, density, ax=ax, levels=5)

# Puntos de datos
ax.scatter(data_coords[:, 0], data_coords[:, 1], color='blue', label='Datos')

# Variables
var_coords = coords[m:]
ax.scatter(var_coords[:, 0], var_coords[:, 1], color='red', marker='^', label='Variables')

# Etiquetar las variables con su nombre real
for j, var_name in enumerate(selected_10):
    ax.text(var_coords[j, 0], var_coords[j, 1], var_name, fontsize=8, color='darkred', ha='center', va='bottom')

# Título y estética
ax.set_title("Mapa de Contexto con Nombres de Variables", fontsize=13)
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.show()



#-----------------------------------------------------------------------------------------

import numpy as np
import json

def export_context_map_json(
    coords,
    m,
    n,
    selected_variable_names,
    dv_matrix,
    contour_paths=None,
    filename='context_map.json'
):
    """
    Exporta los datos de un Data Context Map a un archivo JSON estructurado para D3.js.

    Args:
        coords: np.ndarray de forma (m+n, 2), coordenadas 2D de los puntos proyectados.
        m: int, número de datos (instancias).
        n: int, número de variables.
        selected_variable_names: lista de nombres de las variables (longitud n).
        dv_matrix: np.ndarray de forma (m, n), distancias de cada dato a cada variable.
        contour_paths: lista de listas de puntos de contorno (cada punto como dict con x, y), opcional.
        filename: nombre del archivo de salida .json

    Returns:
        filename: nombre del archivo guardado
    """
    data = {
        "points": [],
        "distances": {},
        "contours": contour_paths if contour_paths is not None else []
    }

    # Agregar puntos de datos (instancias)
    for i in range(m):
        data["points"].append({
            "type": "data",
            "name": f"D{i+1}",
            "x": float(coords[i, 0]),
            "y": float(coords[i, 1])
        })

    # Agregar puntos de variables
    for j in range(n):
        data["points"].append({
            "type": "variable",
            "name": selected_variable_names[j],
            "x": float(coords[m + j, 0]),
            "y": float(coords[m + j, 1])
        })

    # Agregar distancias data → variable (ordenadas por cercanía)
    for i in range(m):
        dists = [
            {
                "variable": selected_variable_names[j],
                "distance": float(dv_matrix[i, j])
            }
            for j in range(n)
        ]
        dists.sort(key=lambda x: x["distance"])
        data["distances"][f"D{i+1}"] = dists

    # Exportar como archivo JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    return filename


filename = export_context_map_json(
    coords=coords,
    m=m,
    n=n,
    selected_variable_names=selected_10,
    dv_matrix=D,  # matriz (m x n) con distancias data ↔ variable
    contour_paths=None,  # puedes pasar coordenadas de contornos si las tienes
    filename = "../dashboard/context_map/context_map_2.json"
)
