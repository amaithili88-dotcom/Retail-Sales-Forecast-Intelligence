import os
import pandas as pd
from pathlib import Path

from src.features.feature_engineering import FeatureEngineering
from src.forecasting.xgboost_trainer import XGBoostTrainer
from src.forecasting.metrics import ForecastMetrics
from src.forecasting.future_forecaster import FutureForecaster

print("=" * 70)
print("GLOBAL TUNED XGBOOST TRAINING")
print("=" * 70)

BEST_XGBOOST_PARAMS = {
    "subsample": 0.65,
    "reg_lambda": 1.0,
    "reg_alpha": 0.0,
    "n_estimators": 1200,
    "min_child_weight": 1,
    "max_depth": 5,
    "max_bin": 256,
    "learning_rate": 0.02,
    "gamma": 0.0,
    "colsample_bytree": 1.0
}


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

        return walmart_df

    raise FileNotFoundError(
        "No supported dataset found. Expected data/processed/pharma_sales_processed.csv or data/Walmart.csv"
    )

# --------------------------------------------------
# Load Dataset
# --------------------------------------------------
df = load_input_data()

print("\nOriginal Dataset Shape")
print(df.shape)

# --------------------------------------------------
# Feature Engineering
# --------------------------------------------------
feature_engineering = FeatureEngineering()
df = feature_engineering.create_features(df)

print("\nDataset After Feature Engineering")
print(df.shape)

# --------------------------------------------------
# Sort Data
# --------------------------------------------------
df["date"] = pd.to_datetime(df["date"])

df = df.sort_values(
    ["date", "category"]
).reset_index(drop=True)

# --------------------------------------------------
# Remove rows containing missing values
# --------------------------------------------------
df = df.dropna().reset_index(drop=True)

print("\nDataset After Removing Missing Values")
print(df.shape)

# --------------------------------------------------
# Global Train/Test Split
# Last 12 months become the test set
# --------------------------------------------------
last_date = df["date"].max()

test_start = last_date - pd.DateOffset(months=11)

train_df = df[df["date"] < test_start].copy()

test_df = df[df["date"] >= test_start].copy()

print("\nTraining Shape")
print(train_df.shape)

print("\nTesting Shape")
print(test_df.shape)

print("\nTraining Date Range")
print(train_df["date"].min())
print(train_df["date"].max())

print("\nTesting Date Range")
print(test_df["date"].min())
print(test_df["date"].max())

# --------------------------------------------------
# Train Model
# --------------------------------------------------
trainer = XGBoostTrainer(model_params=BEST_XGBOOST_PARAMS)

trainer.fit(train_df)

print("\nModel Training Completed")

# --------------------------------------------------
# Predict
# --------------------------------------------------
predictions = trainer.predict(test_df)

results = test_df.copy()

results["prediction"] = predictions

# --------------------------------------------------
# Metrics
# --------------------------------------------------
mae = ForecastMetrics.mae(
    results["sales_units"],
    results["prediction"]
)

rmse = ForecastMetrics.rmse(
    results["sales_units"],
    results["prediction"]
)

mape = ForecastMetrics.mape(
    results["sales_units"],
    results["prediction"]
)

smape = ForecastMetrics.smape(
    results["sales_units"],
    results["prediction"]
)

wmape = ForecastMetrics.wmape(
    results["sales_units"],
    results["prediction"]
)

r2 = ForecastMetrics.r2(
    results["sales_units"],
    results["prediction"]
)

print("\n")
print("=" * 70)
print("GLOBAL MODEL PERFORMANCE")
print("=" * 70)

print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"MAPE : {mape:.2f}%")
print(f"sMAPE: {smape:.2f}%")
print(f"WMAPE: {wmape:.2f}%")
print(f"R2   : {r2:.4f}")

# --------------------------------------------------
# Save Model
# --------------------------------------------------
os.makedirs("models", exist_ok=True)

trainer.save_model(
    "models/global_xgboost.pkl"
)

print("\nModel Saved")
print("models/global_xgboost.pkl")

# --------------------------------------------------
# Save Predictions
# --------------------------------------------------
os.makedirs("data/processed", exist_ok=True)

results.to_csv(
    "data/processed/global_predictions.csv",
    index=False
)

print("\nPredictions Saved")
print("data/processed/global_predictions.csv")

# --------------------------------------------------
# Save Next-Month Forecasts
# --------------------------------------------------
future_forecaster = FutureForecaster(
    feature_engineering=feature_engineering,
    trainer=trainer
)

weekly_future, monthly_future = future_forecaster.forecast_next_month(
    history_df=df,
    weeks_ahead=20,
    months_ahead=3
)

if not weekly_future.empty:
    weekly_future.to_csv(
        "data/processed/future_weekly_predictions.csv",
        index=False
    )
    print("\nFuture Weekly Forecast Saved")
    print("data/processed/future_weekly_predictions.csv")

if not monthly_future.empty:
    monthly_future.to_csv(
        "data/processed/future_month_forecast.csv",
        index=False
    )
    print("\nFuture Month Forecast Saved")
    print("data/processed/future_month_forecast.csv")
    print("\nFuture Month Forecast Preview")
    print(monthly_future.head(10))

print("\nSample Predictions")
print(
    results[
        [
            "date",
            "category",
            "sales_units",
            "prediction"
        ]
    ].head(20)
)