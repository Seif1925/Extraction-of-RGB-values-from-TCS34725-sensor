import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('data/color_dataset.csv')

# Normalize using clear channel
df['R_norm'] = df['R'] / df['C']
df['G_norm'] = df['G'] / df['C']
df['B_norm'] = df['B'] / df['C']

# Create LUT
lut = df[['R_norm', 'G_norm', 'B_norm', 'True_R', 'True_G', 'True_B']]
lut.to_csv('data/color_lut.csv', index=False)

print("LUT created with", len(lut), "entries")