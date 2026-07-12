import os
import pandas as pd

from src.loaders.base_loader import BaseLoader


class CSVLoader(BaseLoader):
    """
    Saves a DataFrame to a CSV file.
    """

    def __init__(self, output_path: str):
        self.output_path = output_path

    def load(self, df: pd.DataFrame):

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        df.to_csv(self.output_path, index=False)

        print(f"\nData saved successfully!")
        print(f"Location: {self.output_path}")
        print(f"Rows saved: {len(df)}")