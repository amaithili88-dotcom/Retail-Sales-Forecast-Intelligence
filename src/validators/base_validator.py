from abc import ABC, abstractmethod
import pandas as pd


class BaseValidator(ABC):
    """
    Base class for all validators.
    """

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> dict:
        """
        Validate a DataFrame.

        Returns:
            dict containing validation results.
        """
        pass