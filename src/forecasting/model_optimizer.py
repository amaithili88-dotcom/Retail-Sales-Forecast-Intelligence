from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from xgboost import XGBRegressor


class ModelOptimizer:
    """
    Finds the best XGBoost hyperparameters using
    RandomizedSearchCV with TimeSeriesSplit.
    """

    def __init__(self, n_iter=40):

        self.n_iter = n_iter

        self.parameter_grid = {

            "n_estimators": [600, 900, 1200, 1800, 2400],

            "max_depth": [3, 4, 5, 6, 8],

            "min_child_weight": [1, 2, 4, 6, 8, 10],

            "learning_rate": [0.005, 0.01, 0.02, 0.03, 0.05],

            "subsample": [0.65, 0.75, 0.85, 1.0],

            "colsample_bytree": [0.6, 0.7, 0.8, 0.9, 1.0],

            "gamma": [0.0, 0.05, 0.1, 0.2, 0.4],

            "reg_alpha": [0.0, 0.1, 0.5, 1.0, 2.0],

            "reg_lambda": [1.0, 2.0, 3.0, 5.0, 8.0],

            "max_bin": [256, 512, 1024]

        }

    def optimize(self, X_train, y_train):

        if len(X_train) < 20:
            raise ValueError(
                "At least 20 samples are required for robust time-series tuning."
            )

        n_splits = min(5, max(2, len(X_train) // 24))

        if n_splits >= len(X_train):
            n_splits = len(X_train) - 1

        model = XGBRegressor(
            objective="reg:squarederror",
            eval_metric="mae",
            tree_method="hist",
            n_jobs=-1,
            random_state=42
        )

        tscv = TimeSeriesSplit(n_splits=n_splits)

        randomized_search = RandomizedSearchCV(

            estimator=model,

            param_distributions=self.parameter_grid,

            n_iter=self.n_iter,

            scoring="neg_mean_absolute_error",

            cv=tscv,

            n_jobs=-1,

            random_state=42,

            verbose=1

        )

        randomized_search.fit(X_train, y_train)

        return (
            randomized_search.best_estimator_,
            randomized_search.best_params_,
            -randomized_search.best_score_
        )