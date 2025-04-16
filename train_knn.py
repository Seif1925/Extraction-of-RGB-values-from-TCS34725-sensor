import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
import joblib

# Load LUT
lut = pd.read_csv('data/color_lut.csv')
X = lut[['R_norm', 'G_norm', 'B_norm']].values
y = lut[['True_R', 'True_G', 'True_B']].values

# Train model
knn = KNeighborsRegressor(n_neighbors=3, weights='distance', algorithm='kd_tree')
knn.fit(X, y)

# Save model
joblib.dump(knn, 'models/color_knn_model.joblib')
print("Model trained and saved")