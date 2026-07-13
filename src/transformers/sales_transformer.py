import pandas as pd

from src.transformers.base_transformer import BaseTransformer


class SalesTransformer(BaseTransformer):

    RAW_REQUIRED_COLUMNS = [
        "Store",
        "Date",
        "Weekly_Sales"
    ]

    NORMALIZED_REQUIRED_COLUMNS = [
        "category",
        "date",
        "sales_units"
    ]

    OPTIONAL_COLUMNS = [
        "Holiday_Flag",
        "Temperature",
        "Fuel_Price",
        "CPI",
        "Unemployment"
    ]

    @staticmethod
    def _has_columns(df: pd.DataFrame, columns: list[str]) -> bool:
        return all(col in df.columns for col in columns)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:

        transformed = df.copy()

        if self._has_columns(transformed, self.RAW_REQUIRED_COLUMNS):
            transformed = transformed.rename(
                columns={
                    "Store": "category",
                    "Date": "date",
                    "Weekly_Sales": "sales_units"
                }
            )
        elif not self._has_columns(transformed, self.NORMALIZED_REQUIRED_COLUMNS):
            raise ValueError(
                "Input data must contain either raw Walmart columns "
                "(Store, Date, Weekly_Sales) or normalized columns "
                "(category, date, sales_units)."
            )

        transformed["category"] = transformed["category"].astype(str)

        transformed["date"] = pd.to_datetime(
            transformed["date"],
            dayfirst=True,
            errors="coerce"
        )

        transformed["sales_units"] = pd.to_numeric(
            transformed["sales_units"],
            errors="coerce"
        )

        transformed = transformed.dropna(
            subset=["category", "date", "sales_units"]
        )

        transformed["sales_units"] = transformed["sales_units"].clip(lower=0)

        keep_columns = [
            "category",
            "date",
            "sales_units"
        ]

        keep_columns.extend(
            col for col in self.OPTIONAL_COLUMNS
            if col in transformed.columns
        )

        transformed = transformed[keep_columns]

        transformed = transformed.drop_duplicates(
            subset=["category", "date"],
            keep="last"
        )

        transformed = transformed.sort_values(
            ["date", "category"]
        ).reset_index(drop=True)

        return transformed