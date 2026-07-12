import pandas as pd

from src.transformers.base_transformer import BaseTransformer


class SalesTransformer(BaseTransformer):

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:

        # Convert date
        df["datum"] = pd.to_datetime(df["datum"])

        # Wide → Long
        df = df.melt(
            id_vars=["datum"],
            var_name="category",
            value_name="sales_units"
        )

        # Rename columns
        df = df.rename(
            columns={
                "datum": "date"
            }
        )

        # Sort
        df = df.sort_values(
            ["category", "date"]
        ).reset_index(drop=True)

        return df