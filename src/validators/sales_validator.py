import pandas as pd

from src.validators.base_validator import BaseValidator


class SalesValidator(BaseValidator):

    REQUIRED_COLUMNS = [
        "datum",
        "M01AB",
        "M01AE",
        "N02BA",
        "N02BE",
        "N05B",
        "N05C",
        "R03",
        "R06"
    ]

    def validate(self, df: pd.DataFrame) -> dict:

        report = {}

        # Check required columns
        missing_columns = [
            col for col in self.REQUIRED_COLUMNS
            if col not in df.columns
        ]

        report["missing_columns"] = missing_columns

        # Missing values
        report["missing_values"] = df.isnull().sum().to_dict()

        # Duplicate rows
        report["duplicate_rows"] = int(df.duplicated().sum())

        # Negative values
        numeric_cols = df.columns.drop("datum")

        report["negative_values"] = {
            col: int((df[col] < 0).sum())
            for col in numeric_cols
        }

        # Date conversion
        try:
            pd.to_datetime(df["datum"])
            report["date_valid"] = True
        except Exception:
            report["date_valid"] = False

        return report