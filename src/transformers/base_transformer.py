from abc import ABC, abstractmethod
import pandas as pd


class BaseTransformer(ABC):

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the extracted data.
        """
        pass