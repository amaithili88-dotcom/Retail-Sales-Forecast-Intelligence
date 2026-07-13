import pandas as pd

from src.validators.base_validator import BaseValidator


class SalesValidator(BaseValidator):

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

    OPTIONAL_NUMERIC_COLUMNS = [
        "Holiday_Flag",
        "Temperature",
        "Fuel_Price",
        "CPI",
        "Unemployment"
    ]

    def _detect_schema(self, df: pd.DataFrame) -> str:

        raw_present = all(
            col in df.columns for col in self.RAW_REQUIRED_COLUMNS
        )

        normalized_present = all(
            col in df.columns for col in self.NORMALIZED_REQUIRED_COLUMNS
        )

        if raw_present:
            return "raw"

        if normalized_present:
            return "normalized"

        return "unknown"

    def validate(self, df: pd.DataFrame) -> dict:

        report = {}

        schema = self._detect_schema(df)

        report["detected_schema"] = schema

        if schema == "raw":
            required_columns = self.RAW_REQUIRED_COLUMNS
            date_col = "Date"
            sales_col = "Weekly_Sales"
        elif schema == "normalized":
            required_columns = self.NORMALIZED_REQUIRED_COLUMNS
            date_col = "date"
            sales_col = "sales_units"
        else:
            required_columns = self.RAW_REQUIRED_COLUMNS
            date_col = None
            sales_col = None

        missing_columns = [col for col in required_columns if col not in df.columns]

        report["missing_columns"] = missing_columns

        report["missing_values"] = df.isnull().sum().to_dict()

        report["duplicate_rows"] = int(df.duplicated().sum())

        numeric_cols = []
        if sales_col and sales_col in df.columns:
            numeric_cols.append(sales_col)

        numeric_cols.extend(
            col for col in self.OPTIONAL_NUMERIC_COLUMNS
            if col in df.columns
        )

        report["negative_values"] = {
            col: int((df[col] < 0).sum())
            for col in numeric_cols
        }

        if date_col and date_col in df.columns:
            parsed_dates = pd.to_datetime(
                df[date_col],
                dayfirst=True,
                errors="coerce"
            )
            report["date_valid"] = bool(parsed_dates.notna().all())
            report["invalid_date_rows"] = int(parsed_dates.isna().sum())
        else:
            report["date_valid"] = False
            report["invalid_date_rows"] = None

        return report