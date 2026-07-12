import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor


class BaselineModels:

    # -------------------------------------------------------
    # Naive Forecast
    # -------------------------------------------------------

    def naive_forecast(self, test_df):

        return test_df["lag_1"].values

    # -------------------------------------------------------
    # Moving Average Forecast
    # -------------------------------------------------------

    def moving_average_forecast(self, test_df):

        return test_df["rolling_mean_3"].values

    # -------------------------------------------------------
    # Linear Regression
    # -------------------------------------------------------

    def linear_regression(self, train_df, test_df, feature_columns):

        train_df = train_df.dropna().copy()
        test_df = test_df.dropna().copy()

        X_train = train_df[feature_columns]
        y_train = train_df["sales_units"]

        X_test = test_df[feature_columns]

        model = LinearRegression()

        model.fit(X_train, y_train)

        return model.predict(X_test)

    # -------------------------------------------------------
    # Random Forest
    # -------------------------------------------------------

    def random_forest(self, train_df, test_df, feature_columns):

        train_df = train_df.dropna().copy()
        test_df = test_df.dropna().copy()

        X_train = train_df[feature_columns]
        y_train = train_df["sales_units"]

        X_test = test_df[feature_columns]

        model = RandomForestRegressor(

            n_estimators=500,

            max_depth=12,

            min_samples_leaf=2,

            random_state=42,

            n_jobs=-1
        )

        model.fit(X_train, y_train)

        return model.predict(X_test)