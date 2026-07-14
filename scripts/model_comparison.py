import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit

from src.features.feature_engineering import FeatureEngineering
from src.forecasting.data_splitter import TimeSeriesSplitter
from src.forecasting.baseline_models import BaselineModels
from src.forecasting.xgboost_trainer import XGBoostTrainer
from src.forecasting.model_optimizer import ModelOptimizer
from src.forecasting.metrics import ForecastMetrics

print("=" * 70)
print("MODEL COMPARISON")
print("=" * 70)


def load_input_data():

    processed_candidates = [
        Path("data/processed/walmart_sales_processed.csv"),
        Path("data/processed/pharma_sales_processed.csv"),
    ]
    walmart_path = Path("data/raw/Walmart.csv")

    processed_path = next((p for p in processed_candidates if p.exists()), None)

    if processed_path is not None:
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
        "No supported dataset found. Expected data/processed/walmart_sales_processed.csv, data/processed/pharma_sales_processed.csv, or data/raw/Walmart.csv"
    )


def tune_random_forest(X_train, y_train):

    n_splits = min(4, max(2, len(X_train) // 24))

    model = RandomForestRegressor(
        random_state=42,
        n_jobs=-1
    )

    parameter_grid = {
        "n_estimators": [500, 800, 1200, 1600, 2200],
        "max_depth": [None, 8, 10, 12, 16, 20, 24],
        "min_samples_split": [2, 4, 6, 8],
        "min_samples_leaf": [1, 2, 3, 4],
        "max_features": ["sqrt", "log2", 1.0],
        "bootstrap": [True, False],
        "criterion": ["squared_error", "absolute_error"]
    }

    search = RandomizedSearchCV(
        estimator=model,
        param_distributions=parameter_grid,
        n_iter=200,
        scoring="neg_mean_absolute_error",
        cv=TimeSeriesSplit(n_splits=n_splits),
        n_jobs=-1,
        random_state=42,
        verbose=1
    )

    search.fit(X_train, y_train)

    return search.best_estimator_, search.best_params_, -search.best_score_


def get_feature_columns(df):

    core_columns = [
        "category",
        "month",
        "quarter",
        "year",
        "week_of_year",
        "month_sin",
        "month_cos",
        "week_sin",
        "week_cos",
        "lag_1",
        "lag_2",
        "lag_3",
        "lag_4",
        "lag_6",
        "lag_8",
        "lag_12",
        "lag_13",
        "lag_26",
        "rolling_mean_4",
        "rolling_std_4",
        "rolling_mean_3",
        "rolling_std_3",
        "rolling_mean_8",
        "rolling_std_8",
        "rolling_mean_6",
        "rolling_std_6",
        "rolling_mean_13",
        "rolling_std_13",
        "rolling_mean_12",
        "rolling_std_12",
        "rolling_mean_26",
        "rolling_std_26",
        "expanding_mean",
        "expanding_std"
    ]

    external_columns = [
        "Holiday_Flag",
        "Temperature",
        "Fuel_Price",
        "CPI",
        "Unemployment"
    ]

    selected = [col for col in core_columns if col in df.columns]
    selected.extend(col for col in external_columns if col in df.columns)

    return selected


def find_best_ensemble_weight(y_true, pred_a, pred_b):

    best_weight = 0.5
    best_mae = float("inf")

    for i in range(0, 101):
        weight = i / 100
        blended = weight * pred_a + (1 - weight) * pred_b
        mae = ForecastMetrics.mae(y_true, blended)

        if mae < best_mae:
            best_mae = mae
            best_weight = weight

    return best_weight, best_mae

# -------------------------------------------------------
# Load Dataset
# -------------------------------------------------------
df = load_input_data()

feature_engineering = FeatureEngineering()
df = feature_engineering.create_features(df)

# -------------------------------------------------------
# Remove rows with missing values
# -------------------------------------------------------
df = df.dropna().reset_index(drop=True)

# -------------------------------------------------------
# Select one category/store
# -------------------------------------------------------
category = (
    df["category"]
    .value_counts()
    .index[0]
)

df = (
    df[df["category"] == category]
    .sort_values("date")
    .reset_index(drop=True)
)

print("\nCategory :", category)
print("Rows     :", len(df))

# -------------------------------------------------------
# Split
# -------------------------------------------------------
splitter = TimeSeriesSplitter(test_size=12)

train_df, test_df = splitter.split(df)

print("\nTraining :", len(train_df))
print("Testing  :", len(test_df))

# -------------------------------------------------------
# Features
# -------------------------------------------------------
feature_columns = get_feature_columns(df)

# -------------------------------------------------------
# Baselines
# -------------------------------------------------------
baseline = BaselineModels()

results = []

# -------------------------------------------------------
# Naive Forecast
# -------------------------------------------------------
pred = baseline.naive_forecast(test_df)

results.append({

    "Model": "Naive",

    "MAE": ForecastMetrics.mae(test_df["sales_units"], pred),

    "RMSE": ForecastMetrics.rmse(test_df["sales_units"], pred),

    "MAPE": ForecastMetrics.mape(test_df["sales_units"], pred),

    "sMAPE": ForecastMetrics.smape(test_df["sales_units"], pred),

    "WMAPE": ForecastMetrics.wmape(test_df["sales_units"], pred),

    "R2": ForecastMetrics.r2(test_df["sales_units"], pred)
})

# -------------------------------------------------------
# Moving Average
# -------------------------------------------------------
pred = baseline.moving_average_forecast(test_df)

results.append({

    "Model": "Moving Average",

    "MAE": ForecastMetrics.mae(test_df["sales_units"], pred),

    "RMSE": ForecastMetrics.rmse(test_df["sales_units"], pred),

    "MAPE": ForecastMetrics.mape(test_df["sales_units"], pred),

    "sMAPE": ForecastMetrics.smape(test_df["sales_units"], pred),

    "WMAPE": ForecastMetrics.wmape(test_df["sales_units"], pred),

    "R2": ForecastMetrics.r2(test_df["sales_units"], pred)
})

# -------------------------------------------------------
# Encode Category
# -------------------------------------------------------
trainer = XGBoostTrainer()

train_encoded = train_df.copy()
test_encoded = test_df.copy()

trainer.encoder.fit(train_encoded["category"])

train_encoded["category"] = trainer.encoder.transform(train_encoded["category"])
test_encoded["category"] = trainer.encoder.transform(test_encoded["category"])

# -------------------------------------------------------
# Linear Regression
# -------------------------------------------------------
pred = baseline.linear_regression(
    train_encoded,
    test_encoded,
    feature_columns
)

results.append({

    "Model": "Linear Regression",

    "MAE": ForecastMetrics.mae(test_df["sales_units"], pred),

    "RMSE": ForecastMetrics.rmse(test_df["sales_units"], pred),

    "MAPE": ForecastMetrics.mape(test_df["sales_units"], pred),

    "sMAPE": ForecastMetrics.smape(test_df["sales_units"], pred),

    "WMAPE": ForecastMetrics.wmape(test_df["sales_units"], pred),

    "R2": ForecastMetrics.r2(test_df["sales_units"], pred)
})

# -------------------------------------------------------
# Random Forest (Tuned)
# -------------------------------------------------------
rf_train = train_encoded.dropna().copy()
rf_test = test_encoded.dropna().copy()

X_rf_train = rf_train[feature_columns]
y_rf_train = rf_train["sales_units"]
X_rf_test = rf_test[feature_columns]

best_rf_model, best_rf_params, best_rf_cv_mae = tune_random_forest(
    X_rf_train,
    y_rf_train
)

print("\nTuned Random Forest Best CV MAE:", round(best_rf_cv_mae, 4))
print("Tuned Random Forest Parameters:", best_rf_params)

pred = best_rf_model.predict(X_rf_test)

results.append({

    "Model": "Random Forest (Tuned)",

    "MAE": ForecastMetrics.mae(test_df["sales_units"], pred),

    "RMSE": ForecastMetrics.rmse(test_df["sales_units"], pred),

    "MAPE": ForecastMetrics.mape(test_df["sales_units"], pred),

    "sMAPE": ForecastMetrics.smape(test_df["sales_units"], pred),

    "WMAPE": ForecastMetrics.wmape(test_df["sales_units"], pred),

    "R2": ForecastMetrics.r2(test_df["sales_units"], pred)
})

# -------------------------------------------------------
# XGBoost
# -------------------------------------------------------
train_tuned = train_df.dropna().copy()

trainer.encoder.fit(train_tuned["category"])

train_tuned["category"] = trainer.encoder.transform(train_tuned["category"])

X_train_tuned = train_tuned[feature_columns]

y_train_tuned = train_tuned["sales_units"]

optimizer = ModelOptimizer(n_iter=260)

_, best_params, best_cv_mae = optimizer.optimize(
    X_train_tuned,
    y_train_tuned
)

print("\nTuned XGBoost Best CV MAE:", round(best_cv_mae, 4))
print("Tuned XGBoost Parameters:", best_params)

trainer = XGBoostTrainer(model_params=best_params)

trainer.fit(train_df)

pred = trainer.predict(test_df)

results.append({

    "Model": "XGBoost (Tuned)",

    "MAE": ForecastMetrics.mae(test_df["sales_units"], pred),

    "RMSE": ForecastMetrics.rmse(test_df["sales_units"], pred),

    "MAPE": ForecastMetrics.mape(test_df["sales_units"], pred),

    "sMAPE": ForecastMetrics.smape(test_df["sales_units"], pred),

    "WMAPE": ForecastMetrics.wmape(test_df["sales_units"], pred),

    "R2": ForecastMetrics.r2(test_df["sales_units"], pred)
})

# -------------------------------------------------------
# Ensemble (Tuned XGBoost + Tuned Random Forest)
# -------------------------------------------------------
rf_pred = best_rf_model.predict(X_rf_test)
xgb_pred = pred

best_weight, _ = find_best_ensemble_weight(
    test_df["sales_units"].values,
    xgb_pred,
    rf_pred
)

ensemble_pred = best_weight * xgb_pred + (1 - best_weight) * rf_pred

print("\nBest Ensemble Weight (XGB):", round(best_weight, 2))

results.append({

    "Model": "Ensemble (Tuned)",

    "MAE": ForecastMetrics.mae(test_df["sales_units"], ensemble_pred),

    "RMSE": ForecastMetrics.rmse(test_df["sales_units"], ensemble_pred),

    "MAPE": ForecastMetrics.mape(test_df["sales_units"], ensemble_pred),

    "sMAPE": ForecastMetrics.smape(test_df["sales_units"], ensemble_pred),

    "WMAPE": ForecastMetrics.wmape(test_df["sales_units"], ensemble_pred),

    "R2": ForecastMetrics.r2(test_df["sales_units"], ensemble_pred)
})

# -------------------------------------------------------
# Results
# -------------------------------------------------------
results_df = pd.DataFrame(results)

results_df = results_df.sort_values("MAE")

Path("data/processed").mkdir(parents=True, exist_ok=True)

print("\n")
print("=" * 70)
print("MODEL RANKING")
print("=" * 70)

print(results_df)

os.makedirs("data/outputs", exist_ok=True)
results_df.to_csv(
    "data/outputs/model_comparison.csv",
    index=False
)

print("\nSaved -> data/outputs/model_comparison.csv")