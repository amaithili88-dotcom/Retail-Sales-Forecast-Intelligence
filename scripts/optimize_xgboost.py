import pandas as pd
from pathlib import Path

from src.features.feature_engineering import FeatureEngineering
from src.forecasting.data_splitter import TimeSeriesSplitter
from src.forecasting.model_optimizer import ModelOptimizer
from src.forecasting.xgboost_trainer import XGBoostTrainer

print("=" * 60)
print("XGBOOST HYPERPARAMETER OPTIMIZATION")
print("=" * 60)


def load_input_data():

    processed_path = Path("data/processed/pharma_sales_processed.csv")
    walmart_path = Path("data/Walmart.csv")

    if processed_path.exists():
        return pd.read_csv(processed_path)

    if walmart_path.exists():
        walmart_df = pd.read_csv(walmart_path)

        walmart_df = walmart_df.rename(
            columns={
                "Store": "category",
                "Date": "date",
                "Weekly_Sales": "sales_units"
            }
        )

        walmart_df["category"] = walmart_df["category"].astype(str)
        walmart_df["date"] = pd.to_datetime(
            walmart_df["date"],
            dayfirst=True,
            errors="coerce"
        )

        walmart_df = walmart_df.dropna(
            subset=["date", "sales_units", "category"]
        )

        return walmart_df[["category", "date", "sales_units"]]

    raise FileNotFoundError(
        "No supported dataset found. Expected data/processed/pharma_sales_processed.csv or data/Walmart.csv"
    )

# ----------------------------------------
# Load Data
# ----------------------------------------

df = load_input_data()

# ----------------------------------------
# Feature Engineering
# ----------------------------------------

feature_engineering = FeatureEngineering()

df = feature_engineering.create_features(df)

# ----------------------------------------
# Select Category/Store
# ----------------------------------------

category = (
    df["category"]
    .value_counts()
    .index[0]
)

category_df = (
    df[df["category"] == category]
    .sort_values("date")
    .reset_index(drop=True)
)

# ----------------------------------------
# Split
# ----------------------------------------

splitter = TimeSeriesSplitter(test_size=12)

train_df, test_df = splitter.split(category_df)

# ----------------------------------------
# Remove Missing Values
# ----------------------------------------

train_df = train_df.dropna()

# ----------------------------------------
# Features
# ----------------------------------------

trainer = XGBoostTrainer()

trainer.encoder.fit(train_df["category"])

train_df["category"] = trainer.encoder.transform(train_df["category"])

X_train = train_df[trainer.feature_columns]

y_train = train_df["sales_units"]

# ----------------------------------------
# Optimize
# ----------------------------------------

optimizer = ModelOptimizer(n_iter=60)

best_model, best_params, best_mae = optimizer.optimize(
    X_train,
    y_train
)

print("\nBest Parameters")
print(best_params)

print("\nBest Cross Validation MAE")
print(best_mae)