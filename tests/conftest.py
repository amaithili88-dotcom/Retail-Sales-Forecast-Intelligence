import pandas as pd
import pytest


@pytest.fixture
def sample_raw_df():
    return pd.DataFrame(
        {
            "date": ["2023-01-01", "2023-02-01", "2023-02-01", "2023-03-01"],
            "category": ["M01AB", "M01AB", "M01AB", "N02BA"],
            "sales_units": [100.0, 150.0, 150.0, -5.0],
        }
    )


@pytest.fixture
def sample_walmart_df():
    return pd.DataFrame(
        {
            "Store": [1, 1, 1, 2],
            "Date": ["05-02-2010", "12-02-2010", "12-02-2010", "19-02-2010"],
            "Weekly_Sales": [1643690.9, 1641957.44, 1641957.44, -10.0],
            "Holiday_Flag": [0, 1, 1, 0],
            "Temperature": [42.31, 38.51, 38.51, 39.93],
            "Fuel_Price": [2.572, 2.548, 2.548, 2.514],
            "CPI": [211.0963, 211.2421, 211.2421, 211.2891],
            "Unemployment": [8.106, 8.106, 8.106, 8.106],
        }
    )