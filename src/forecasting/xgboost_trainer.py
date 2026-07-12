import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor


class XGBoostTrainer:

    def __init__(self, model_params=None):

        self.encoder = LabelEncoder()

        # Must exactly match feature_engineering.py
        self.feature_columns = [

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

        self.optional_feature_columns = [
            "Holiday_Flag",
            "Temperature",
            "Fuel_Price",
            "CPI",
            "Unemployment"
        ]

        self.active_feature_columns = []

        default_params = {

            "objective": "reg:squarederror",

            "n_estimators": 1200,

            "learning_rate": 0.02,

            "max_depth": 4,

            "min_child_weight": 4,

            "subsample": 0.85,

            "colsample_bytree": 0.85,

            "gamma": 0.1,

            "reg_alpha": 0.5,

            "reg_lambda": 2,

            "eval_metric": "mae",

            "n_jobs": -1,

            "random_state": 42
        }

        if model_params is not None:
            default_params.update(model_params)

        self.model = XGBRegressor(**default_params)

    def _prepare_features(self, df, fit_encoder=False, require_target=False):

        prepared_df = df.copy()

        if fit_encoder:
            prepared_df["category"] = self.encoder.fit_transform(
                prepared_df["category"]
            )
        else:
            prepared_df["category"] = self.encoder.transform(
                prepared_df["category"]
            )

        selected_columns = [
            col for col in self.feature_columns
            if col in prepared_df.columns
        ]

        selected_columns.extend(
            col for col in self.optional_feature_columns
            if col in prepared_df.columns
        )

        self.active_feature_columns = selected_columns

        required_columns = ["category"] + self.active_feature_columns
        if require_target:
            required_columns.append("sales_units")

        prepared_df = prepared_df.dropna(subset=required_columns)

        X = prepared_df[self.active_feature_columns]

        return prepared_df, X

    def fit(self, train_df, validation_ratio=0.2, early_stopping_rounds=75):

        prepared_df, X_train_full = self._prepare_features(
            train_df,
            fit_encoder=True,
            require_target=True
        )

        y_train_full = prepared_df["sales_units"]

        val_size = int(len(prepared_df) * validation_ratio)

        if len(prepared_df) > 50 and val_size > 0:

            X_train = X_train_full.iloc[:-val_size]
            y_train = y_train_full.iloc[:-val_size]

            X_val = X_train_full.iloc[-val_size:]
            y_val = y_train_full.iloc[-val_size:]

            self.model.set_params(
                early_stopping_rounds=early_stopping_rounds
            )

            self.model.fit(
                X_train,
                y_train,
                eval_set=[(X_val, y_val)],
                verbose=False
            )
        else:
            self.model.fit(X_train_full, y_train_full)

    def predict(self, test_df):

        _, X_test = self._prepare_features(
            test_df,
            fit_encoder=False,
            require_target=False
        )

        return self.model.predict(X_test)

    def save_model(self, path):

        joblib.dump(
            {
                "model": self.model,
                "encoder": self.encoder
            },
            path
        )

    def load_model(self, path):

        saved = joblib.load(path)

        self.model = saved["model"]

        self.encoder = saved["encoder"]