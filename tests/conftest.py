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