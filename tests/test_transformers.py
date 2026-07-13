import pytest

from src.transformers.sales_transformer import SalesTransformer


def test_transform_drops_duplicates(sample_raw_df):
    transformer = SalesTransformer()
    result = transformer.transform(sample_raw_df)
    assert len(result) == len(sample_raw_df) - 1


def test_transform_clips_negative_sales(sample_raw_df):
    transformer = SalesTransformer()
    result = transformer.transform(sample_raw_df)
    assert (result["sales_units"] >= 0).all()


def test_transform_raises_on_missing_columns():
    import pandas as pd

    bad_df = pd.DataFrame({"date": ["2023-01-01"], "sales_units": [10]})
    transformer = SalesTransformer()
    with pytest.raises(ValueError):
        transformer.transform(bad_df)


def test_transform_sorts_by_date(sample_raw_df):
    transformer = SalesTransformer()
    result = transformer.transform(sample_raw_df)
    assert result["date"].is_monotonic_increasing


def test_transform_keeps_normalized_category_column(sample_raw_df):
    transformer = SalesTransformer()
    result = transformer.transform(sample_raw_df)
    assert "category" in result.columns


def test_transform_renames_walmart_columns(sample_walmart_df):
    transformer = SalesTransformer()
    result = transformer.transform(sample_walmart_df)
    assert {"category", "date", "sales_units"}.issubset(result.columns)
    assert "Store" not in result.columns
    assert "Date" not in result.columns
    assert "Weekly_Sales" not in result.columns