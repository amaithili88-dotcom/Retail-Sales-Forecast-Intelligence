import numpy as np
import pandas as pd


class FeatureEngineering:
    """
    Feature engineering for pharmaceutical sales forecasting.

    All features are created using ONLY historical information.
    No future information is leaked into the model.
    """

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # Calendar Features
    # ---------------------------------------------------------

    def add_calendar_features(self, df):

        df = df.copy()

        df["date"] = pd.to_datetime(df["date"])

        df["month"] = df["date"].dt.month
        df["quarter"] = df["date"].dt.quarter
        df["year"] = df["date"].dt.year
        df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)

        # Cyclical encoding
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
        df["week_sin"] = np.sin(2 * np.pi * df["week_of_year"] / 52)
        df["week_cos"] = np.cos(2 * np.pi * df["week_of_year"] / 52)

        return df

    # ---------------------------------------------------------
    # Lag Features
    # ---------------------------------------------------------

    def add_lag_features(self, df):

        df = df.copy()

        grouped = df.groupby("category")["sales_units"]

        df["lag_1"] = grouped.shift(1)
        df["lag_2"] = grouped.shift(2)
        df["lag_3"] = grouped.shift(3)
        df["lag_4"] = grouped.shift(4)
        df["lag_6"] = grouped.shift(6)
        df["lag_8"] = grouped.shift(8)
        df["lag_12"] = grouped.shift(12)
        df["lag_13"] = grouped.shift(13)
        df["lag_26"] = grouped.shift(26)

        return df

    # ---------------------------------------------------------
    # Rolling Features
    # ---------------------------------------------------------

    def add_rolling_features(self, df):

        df = df.copy()

        grouped = df.groupby("category")["sales_units"]

        # 3 Month
        df["rolling_mean_3"] = grouped.transform(
            lambda x: x.shift(1).rolling(3).mean()
        )

        df["rolling_std_3"] = grouped.transform(
            lambda x: x.shift(1).rolling(3).std()
        )

        # 6 Month
        df["rolling_mean_6"] = grouped.transform(
            lambda x: x.shift(1).rolling(6).mean()
        )

        df["rolling_std_6"] = grouped.transform(
            lambda x: x.shift(1).rolling(6).std()
        )

        # 12 Month
        df["rolling_mean_12"] = grouped.transform(
            lambda x: x.shift(1).rolling(12).mean()
        )

        df["rolling_std_12"] = grouped.transform(
            lambda x: x.shift(1).rolling(12).std()
        )

        # Weekly-style windows for retail sales
        df["rolling_mean_4"] = grouped.transform(
            lambda x: x.shift(1).rolling(4).mean()
        )

        df["rolling_std_4"] = grouped.transform(
            lambda x: x.shift(1).rolling(4).std()
        )

        df["rolling_mean_8"] = grouped.transform(
            lambda x: x.shift(1).rolling(8).mean()
        )

        df["rolling_std_8"] = grouped.transform(
            lambda x: x.shift(1).rolling(8).std()
        )

        df["rolling_mean_13"] = grouped.transform(
            lambda x: x.shift(1).rolling(13).mean()
        )

        df["rolling_std_13"] = grouped.transform(
            lambda x: x.shift(1).rolling(13).std()
        )

        df["rolling_mean_26"] = grouped.transform(
            lambda x: x.shift(1).rolling(26).mean()
        )

        df["rolling_std_26"] = grouped.transform(
            lambda x: x.shift(1).rolling(26).std()
        )

        return df

    # ---------------------------------------------------------
    # Expanding Features
    # ---------------------------------------------------------

    def add_expanding_features(self, df):

        df = df.copy()

        grouped = df.groupby("category")["sales_units"]

        df["expanding_mean"] = grouped.transform(
            lambda x: x.shift(1).expanding().mean()
        )

        df["expanding_std"] = grouped.transform(
            lambda x: x.shift(1).expanding().std()
        )

        return df

    # ---------------------------------------------------------
    # Master Function
    # ---------------------------------------------------------

    def create_features(self, df):

        df = df.copy()

        df["date"] = pd.to_datetime(df["date"])

        df = df.sort_values(
            ["category", "date"]
        ).reset_index(drop=True)

        df = self.add_calendar_features(df)

        df = self.add_lag_features(df)

        df = self.add_rolling_features(df)

        df = self.add_expanding_features(df)

        # Remove infinities
        df.replace(
            [np.inf, -np.inf],
            np.nan,
            inplace=True
        )

        return df