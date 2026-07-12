import os
import pandas as pd

from src.extractors.base_extractor import BaseExtractor


class CSVExtractor(BaseExtractor):
    """
    Reads a CSV file and returns it as a pandas DataFrame.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract(self) -> pd.DataFrame:

        if not os.path.exists(self.file_path):
            raise FileNotFoundError(
                f"CSV file not found: {self.file_path}"
            )

        df = pd.read_csv(self.file_path)

        print(f"Loaded {len(df)} rows")
        print(f"Columns: {list(df.columns)}")

        return df