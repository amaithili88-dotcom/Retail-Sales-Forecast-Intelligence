import numpy as np
from sklearn.metrics import r2_score


class ForecastMetrics:
    """
    Calculates forecasting evaluation metrics.
    """

    @staticmethod
    def mae(actual, predicted):
        actual = np.array(actual)
        predicted = np.array(predicted)

        return np.mean(np.abs(actual - predicted))

    @staticmethod
    def rmse(actual, predicted):
        actual = np.array(actual)
        predicted = np.array(predicted)

        return np.sqrt(np.mean((actual - predicted) ** 2))

    @staticmethod
    def mape(actual, predicted):
        actual = np.array(actual)
        predicted = np.array(predicted)

        mask = actual != 0

        actual = actual[mask]
        predicted = predicted[mask]

        if len(actual) == 0:
            return np.nan

        return np.mean(np.abs((actual - predicted) / actual)) * 100

    @staticmethod
    def smape(actual, predicted):
        actual = np.array(actual)
        predicted = np.array(predicted)

        denominator = np.abs(actual) + np.abs(predicted)
        mask = denominator != 0

        if np.sum(mask) == 0:
            return np.nan

        return np.mean(
            2 * np.abs(actual[mask] - predicted[mask]) / denominator[mask]
        ) * 100

    @staticmethod
    def wmape(actual, predicted):
        actual = np.array(actual)
        predicted = np.array(predicted)

        denominator = np.sum(np.abs(actual))

        if denominator == 0:
            return np.nan

        return np.sum(np.abs(actual - predicted)) / denominator * 100

    @staticmethod
    def r2(actual, predicted):
        actual = np.array(actual)
        predicted = np.array(predicted)

        return r2_score(actual, predicted)