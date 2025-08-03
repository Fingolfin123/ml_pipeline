import os
import sys
import pandas as pd
from pandas import DataFrame

from src.common.monitoring.logger import logging
from src.common.exception import CustomException

class DataSource:
    def __init__(self, config: dict={}):
        """
        Initialize the data source with a configuration dictionary.
        """
        self.config = config

    def set_io_config(self, config: dict = None):
        """
        Set self.config with an config dict.
        """
        self.config = config
        if config:
            self.config.update(config)
        return self.config

    def read_flat_file(self, path:str):
        # path = self.config["path"] if path is None else path
        logging.info(f"Reading data from: {path}")
        try:
            return self._read(path)
        except Exception as e:
            raise CustomException(e, sys)

    def write_flat_file(self, df, path:str = None):
        # path = self.config["path"] if path is None else path
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)  # Create dirs if missing
            logging.info(f"Created directory: {directory}")
        
        logging.info(f"Writing data to: {path}")
        try:
            return self._write(df, path)
        except Exception as e:
            raise CustomException(e, sys)

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
    
