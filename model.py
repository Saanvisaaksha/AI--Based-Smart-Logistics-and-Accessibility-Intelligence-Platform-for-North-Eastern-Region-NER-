import os
import sys

# --- ENVIRONMENT FIX FOR GDAL PATH ---
conda_prefix = sys.prefix
gdal_data_path = os.path.join(conda_prefix, "Library", "share", "gdal")
if os.path.exists(gdal_data_path):
  os.environ["GDAL_DATA"] = gdal_data_path
# -----------------------------------

import joblib
import numpy as np
import pandas as pd
import rasterio
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# --- EXACT FILE PATHS ---
raster_path = r"C:\Krish\SIH\Database\class.tif"
csv_paths = [
    r"C:\Krish\SIH\Database\1st dataset.csv",
    r"C:\Krish\SIH\Database\2nd dataset.csv",
    r"C:\Krish\SIH\Database\3rd dataset.csv",
]
model_output_path = r"C:\Krish\SIH\Database\landslide_safety_model.pkl"

print("1. Opening 6.21 GB raster dataset for topography baseline...")
with rasterio.open(raster_path) as src:
  print(f"   Raster dimensions: Width={src.width}, Height={src.height}")

  # Downsample factor to safely handle the 6.21 GB file without crashing RAM
  scale_factor = 20
  data = src.read(
      1,
      out_shape=(
          int(src.height // scale_factor),
          int(src.width // scale_factor),
      ),
      resampling=rasterio.enums.Resampling.nearest,
  )

  # Extract spatial coordinates
  height, width = data.shape
  cols, rows = np.meshgrid(
      np.arange(width) * scale_factor, np.arange(height) * scale_factor
  )
  xs, ys = rasterio.transform.xy(src.transform, rows, cols)

  raster_lons = np.array(xs).flatten()
  raster_lats = np.array(ys).flatten()
  raster_classes = data.flatten().astype(float)

# Clean and filter raster data (remove NaN / NoData values)
valid_raster = ~np.isnan(raster_classes)
if src.nodata is not None:
  valid_raster = valid_raster & (raster_classes != src.nodata)

raster_lons = raster_lons[valid_raster]
raster_lats = raster_lats[valid_raster]
raster_classes = raster_classes[valid_raster]

# Subsample raster points for balancing
if len(raster_lons) > 50000:
  idx = np.random.choice(len(raster_lons), 50000, replace=False)
  raster_lons, raster_lats, raster_classes = (
      raster_lons[idx],
      raster_lats[idx],
      raster_classes[idx],
  )

print(f"   Extracted {len(raster_lons)} valid terrain grid pixels.")

print("2. Loading and merging CSV meteorological datasets...")
dfs = []
for path in csv_paths:
  if os.path.exists(path):
    print(f"   Loading: {os.path.basename(path)}")
    dfs.append(pd.read_csv(path))
  else:
    print(f"   Warning: Path not found -> {path}")

if dfs:
  combined_df = pd.concat(dfs, ignore_index=True)
  # Drop rows with missing location or rainfall data
  combined_df = combined_df.dropna(
      subset=["Latitude", "Longitude", "Telemetry Hourly Rainfall (mm)"]
  )

  csv_lons = combined_df["Longitude"].values
  csv_lats = combined_df["Latitude"].values
  rainfall = combined_df["Telemetry Hourly Rainfall (mm)"].values

  print(
      f"   Processed {len(combined_df)} telemetry records from CSV"
      " datasets."
  )

  # Prepare feature matrix X: [Longitude, Latitude, Rainfall Intensity]
  X_csv = np.column_stack((csv_lons, csv_lats, rainfall))

  # Synthesize target risk label from rainfall trigger intensity (Risk scale 1 to 5)
  y_csv = np.clip((rainfall / 30.0) + 1, 1, 5).astype(int)

  # Terrain baseline array with nominal baseline rainfall (2.0 mm/hr)
  X_raster = np.column_stack(
      (
          raster_lons,
          raster_lats,
          np.full(len(raster_lons), 2.0),
      )
  )
  y_raster = raster_classes.astype(int)

  # Combine both data sources into a unified training set
  X = np.vstack((X_raster, X_csv))
  y = np.concatenate((y_raster, y_csv))
else:
  print("   No CSV datasets found. Training on raster baseline only.")
  X = np.column_stack(
      (raster_lons, raster_lats, np.full(len(raster_lons), 2.0))
  )
  y = raster_classes.astype(int)

print(f"Total unified training dataset size: {len(X)} samples.")

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("3. Training multi-parameter Random Forest Route Safety Model...")
model = RandomForestClassifier(
    n_estimators=100, max_depth=15, random_state=42, n_jobs=-1
)
model.fit(X_train, y_train)

# Evaluate model performance
accuracy = model.score(X_test, y_test)
print(f"Model Training Complete! Test Accuracy: {accuracy * 100:.2f}%")

# Save model directly to the specified folder path
joblib.dump(model, model_output_path)
print(f"Model successfully saved to: {model_output_path}")