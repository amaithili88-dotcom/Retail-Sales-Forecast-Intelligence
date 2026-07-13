import pandas as pd
from pathlib import Path

from src.features.feature_engineering import FeatureEngineering

print("=" * 60)
print("PREPARING TRAINING DATA")
print("=" * 60)

# ----------------------------------------------------
# Load Raw Dataset
# ----------------------------------------------------

processed_candidates = [
    Path("data/processed/walmart_sales_processed.csv"),
    Path("data/processed/pharma_sales_processed.csv"),
]

processed_path = next((p for p in processed_candidates if p.exists()), None)

if processed_path is None:
    raise FileNotFoundError(
        "No processed dataset found. Expected data/processed/walmart_sales_processed.csv or data/processed/pharma_sales_processed.csv"
    )

df = pd.read_csv(processed_path)

print("\nRaw Dataset Shape")
print(df.shape)

# ----------------------------------------------------
# Create Features
# ----------------------------------------------------

feature_engineering = FeatureEngineering()

df = feature_engineering.create_features(df)

print("\nShape After Feature Engineering")
print(df.shape)

# ----------------------------------------------------
# Remove Missing Values
# ----------------------------------------------------

df = df.dropna().reset_index(drop=True)

print("\nShape After Removing Missing Values")
print(df.shape)

# ----------------------------------------------------
# Save Training Dataset
# ----------------------------------------------------

df.to_csv(
    "data/processed/training_dataset.csv",
    index=False
)

print("\nTraining dataset created successfully.")

print("\nColumns")

print(df.columns.tolist())

print("\nFirst Five Rows")

print(df.head())