import pandas as pd


class TimeSeriesSplitter:
    """
    Splits time-series data without shuffling.
    """

    def __init__(self, test_size=12):
        """
        Parameters
        ----------
        test_size : int
            Number of last observations used for testing.
        """
        self.test_size = test_size

    def split(self, df: pd.DataFrame):

        df = df.sort_values("date").reset_index(drop=True)

        train = df.iloc[:-self.test_size]

        test = df.iloc[-self.test_size:]

        return train, test