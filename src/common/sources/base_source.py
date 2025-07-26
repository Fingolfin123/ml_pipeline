import pandas as pd
from pandas import DataFrame

from src.common.monitoring.logger import logging

class DataSource:
    def __init__(self, config: dict):
        """
        Initialize the data source with a configuration dictionary.
        """
        self.config = config

    def read(self):
        path = self.config["path"]
        logging.info(f"Reading data from: {path}")
        return self._read()

    def write(self, df):
        path = self.config["path"]
        logging.info(f"Writing data to: {path}")
        return self._write(df)

    def _read(self):
        raise NotImplementedError

    def _write(self, df):
        raise NotImplementedError

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
