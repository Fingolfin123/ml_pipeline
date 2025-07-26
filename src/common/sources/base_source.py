from abc import ABC, abstractmethod
import pandas as pd
from pandas import DataFrame

class DataSource(ABC):
    def __init__(self, config: dict):
        """
        Initialize the data source with a configuration dictionary.
        """
        self.config = config

    @abstractmethod
    def read(self) -> DataFrame:
        """
        Read data and return as a pandas DataFrame.
        """
        pass

    @abstractmethod
    def write(self, df: DataFrame):
        """
        Write a pandas DataFrame to the data source.
        """
        pass

    def generate_sample_table(self) -> DataFrame:
        """
        Default sample table creation using pandas.
        Override in subclasses for source-specific implementations.
        """
        return pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "score": [85.5, 92.0, 78.3]
        })
