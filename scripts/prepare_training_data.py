import pandas as pd

from src.features.feature_engineering import FeatureEngineering

print("=" * 60)
print("PREPARING TRAINING DATA")
print("=" * 60)

# ----------------------------------------------------
# Load Raw Dataset
# ----------------------------------------------------

df = pd.read_csv(
    "data/processed/pharma_sales_processed.csv"
)

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