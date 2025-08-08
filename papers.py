import numpy as np
from sklearn.preprocessing import normalize
X = np.matrix([[2, 3], [4, 7], [6, 9]])
X_mean = np.mean(X, axis=0)
print(X_mean)
X_std = np.std(X, axis=0)
# print(X_std)
X_scaled = (X - X_mean)
print(X_scaled)
X_scaled_manual = X_scaled / X_std
print(X_scaled_manual)

print("-----------------------------------------")

def min_max_normalize(matrix):
    """Normalizes a matrix using Min-Max scaling to the range [0, 1]."""
    min_val = np.min(matrix)
    max_val = np.max(matrix)
    normalized_matrix = (matrix - min_val) / (max_val - min_val)
    return normalized_matrix

def z_score_normalize(matrix):
    """Normalizes a matrix using Z-score standardization."""
    mean_val = np.mean(matrix)
    std_val = np.std(matrix)
    normalized_matrix = (matrix - mean_val) / std_val
    return normalized_matrix

normalized_matrix = min_max_normalize(X)
print(normalized_matrix)

standardized_matrix = z_score_normalize(X)
print("\nStandardized Matrix (Z-score):\n", standardized_matrix)

# normalized_cols = normalize(X, axis=0, norm='l2')
# print("\nColumn-wise L2 Normalized Matrix:\n", normalized_cols)