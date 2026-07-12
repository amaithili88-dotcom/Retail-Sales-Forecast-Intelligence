from abc import ABC, abstractmethod
import pandas as pd


class BaseExtractor(ABC):
    """
    Abstract base class for all data extractors.
    Every extractor must implement the extract() method.
    """

    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """
        Extract data from a source and return a pandas DataFrame.
        """
        pass