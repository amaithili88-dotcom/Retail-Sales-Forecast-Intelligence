from abc import ABC, abstractmethod
import pandas as pd


class BaseLoader(ABC):

    @abstractmethod
    def load(self, df: pd.DataFrame):
        """
        Load a DataFrame into a destination.
        """
        pass