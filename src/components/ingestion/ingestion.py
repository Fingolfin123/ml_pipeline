import os
import sys
from src.common.exception import CustomException
from src.common.monitoring.logger import logging
from src.common.datasource import DataSourceIO
from src.components.type_defs import TraingingParams

from sklearn.model_selection import train_test_split
from dataclasses import dataclass


@dataclass
class DataIngestConfig:
    train_data_path: str = os.path.join("model_run", "train.csv")
    test_data_path: str = os.path.join("model_run", "test.csv")
    raw_data_path: str = os.path.join("model_run", "raw.csv")


class IngestionManager:
    def __init__(self):
        # Initialize the generic source class object
        self.source = DataSourceIO()
        self.ingestion_config = DataIngestConfig()
        self.ingest_path = None

    def set_ingest_path(self, path: str):
        self.ingest_path = path

    def initiate_data_ingestion(self):
        logging.info("Running Data Ingestion")
        try:
            # Read the raw data
            df = self.source.read_flat_file(path=self.ingest_path)

            # Save the input data to specified training folder
            self.source.write_flat_file(df, path=self.ingestion_config.raw_data_path)

            # Split the dataset in to training and test sets
            logging.info("Splitting input data into training and testing sets")
            train_set, test_set = train_test_split(
                df,
                test_size=TraingingParams.TEST_SIZE.value,
                random_state=TraingingParams.RANDOM_STATE.value,
            )

            # Save the split data
            self.source.write_flat_file(
                train_set, path=self.ingestion_config.train_data_path
            )
            self.source.write_flat_file(
                test_set, path=self.ingestion_config.test_data_path
            )

            logging.info("Data Ingestion has completed.")

            return (
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path,
            )
        except Exception as e:
            raise CustomException(e, sys)

    def get_model_data(self):
        """
        Loads a saved dataset from model_run/ using self.source.read
        Returns: DataFrame
        """
        logging.info("Loading ingested model run data")
        try:
            df_raw = self.source.read_flat_file(self.ingestion_config.raw_data_path)
            df_train = self.source.read_flat_file(self.ingestion_config.train_data_path)
            df_test = self.source.read_flat_file(self.ingestion_config.test_data_path)
        except Exception as e:
            raise CustomException(e, sys)

        return df_raw, df_train, df_test

    def run(self):
        # Run the data ingestion process and return the raw,
        # trainging and testing dataframes
        self.initiate_data_ingestion()
        df_raw, df_train, df_test = self.get_model_data()

        return df_raw, df_train, df_test


if __name__ == "__main__":
    obj = IngestionManager()
    obj.set_ingest_path("data/air_quality_health_dataset.csv")
    df_raw, df_train, df_test = obj.run()
    print(df_raw)
    print(df_train)
    print(df_test)
