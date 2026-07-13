import pandas as pd

from src.features.feature_engineering import FeatureEngineering
from src.forecasting.data_splitter import TimeSeriesSplitter
from src.forecasting.xgboost_trainer import XGBoostTrainer
from src.forecasting.metrics import ForecastMetrics
from pathlib import Path

class ForecastingPipeline:

    def __init__(self):

        self.feature_engineering = FeatureEngineering()

        self.splitter = TimeSeriesSplitter(test_size=12)

        self.trainer = XGBoostTrainer()

        # Store pipeline state
        self.df = None

        self.feature_df = None

        self.train_df = None

        self.test_df = None

        self.predictions = None

        self.results = None

        self.metrics = None

    # ----------------------------------------------------
    # Load Dataset
    # ----------------------------------------------------

    def load_data(self):

        project_root = Path(__file__).resolve().parents[2]

        processed_path = (
            project_root
            / "data"
            / "processed"
            / "pharma_sales_processed.csv"
        )

        walmart_path = (
            project_root
            / "data"
            / "Walmart.csv"
        )

        if processed_path.exists():
            self.df = pd.read_csv(processed_path)
            return self.df

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
            walmart_df["sales_units"] = pd.to_numeric(
                walmart_df["sales_units"],
                errors="coerce"
            )

            walmart_df = walmart_df.dropna(
                subset=["category", "date", "sales_units"]
            )

            self.df = walmart_df

            return self.df

        raise FileNotFoundError(
            "No supported dataset found. Expected data/processed/pharma_sales_processed.csv or data/Walmart.csv"
        )

    # ----------------------------------------------------
    # Feature Engineering
    # ----------------------------------------------------

    def create_features(self, df):

        df = self.feature_engineering.create_features(df)

        df = df.dropna().reset_index(drop=True)

        return df

    # ----------------------------------------------------
    # Train/Test Split
    # ----------------------------------------------------

    def split_data(self, df):

        df["date"] = pd.to_datetime(df["date"])

        df = df.sort_values(
            ["date", "category"]
        ).reset_index(drop=True)

        last_date = df["date"].max()

        test_start = last_date - pd.DateOffset(months=11)

        train_df = df[
            df["date"] < test_start
        ].copy()

        test_df = df[
            df["date"] >= test_start
        ].copy()

        return train_df, test_df

    # ----------------------------------------------------
    # Train Model
    # ----------------------------------------------------

    def train_model(self, train_df):

        self.trainer.fit(train_df)

        return self.trainer

    # ----------------------------------------------------
    # Predict
    # ----------------------------------------------------

    def predict(self, test_df):

        predictions = self.trainer.predict(test_df)

        return predictions

    # ----------------------------------------------------
    # Evaluate
    # ----------------------------------------------------

    def evaluate(self, actual, predicted):

        metrics = {

            "MAE": ForecastMetrics.mae(actual, predicted),

            "RMSE": ForecastMetrics.rmse(actual, predicted),

            "MAPE": ForecastMetrics.mape(actual, predicted)

        }

        return metrics

    # ----------------------------------------------------
    # Complete Pipeline
    # ----------------------------------------------------

    def run(self):

        df = self.load_data()

        feature_df = self.create_features(df)

        train_df, test_df = self.split_data(feature_df)

        self.train_model(train_df)

        predictions = self.predict(test_df)

        metrics = self.evaluate(
            test_df["sales_units"],
            predictions
        )

        results = test_df.copy()

        results["prediction"] = predictions

        return {

            "train_df": train_df,

            "test_df": test_df,

            "results": results,

            "metrics": metrics,

            "model": self.trainer.model

        }