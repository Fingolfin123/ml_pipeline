import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
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
    eda_folder_path: str = os.path.join("model_run", "eda")

class IngestionManager:
    def __init__(self, ingest_path=None):
        # Initialize the generic source class object
        self.source = DataSourceIO()
        self.ingestion_config = DataIngestConfig()
        self.ingest_path = ingest_path

    def load_raw(self, path):
        logging.info("Running Data Ingestion")
        try:
            # Read the raw data            
            if path is None:
                df_raw = self.source.read_flat_file(path=self.ingest_path)
            else:
                df_raw = self.source.read_flat_file(path=path)

            # Save the input data to specified training folder and read back
            self.source.write_flat_file(df_raw, path=self.ingestion_config.raw_data_path)
            df = self.source.read_flat_file(path=self.ingestion_config.raw_data_path)
            return df

        except Exception as e:
            raise CustomException(e, sys)            

    def run_eda(self, df: pd.DataFrame):
        logging.info("Running Exporatory Data Analysis")
        try:
            eda_folder_path = self.ingestion_config.eda_folder_path
            os.makedirs(eda_folder_path, exist_ok=True)
            eda_images = []

            # Show first few rows
            eda_head = df.head().to_html(classes="table table-striped table-bordered", border=0)

            # Show shape
            eda_shape = f"Rows: {df.shape[0]}, Columns: {df.shape[1]}"

            # Summary statistics
            eda_df = df.describe(include="all")

            # Add a row for null counts
            eda_df.loc["null_count"] = df.isnull().sum()

            # Convert to HTML
            eda_summary = eda_df.to_html(classes="table table-striped table-bordered", border=0)

            # Numeric columns
            numeric_cols = df.select_dtypes(include="number").columns

            for num_col in numeric_cols:
                plt.figure(figsize=(8, 6))
                sns.histplot(df[num_col], kde=True, color="blue")
                plt.title(f"Distribution of {num_col}")
                filename = f"{num_col}_distribution.png"
                save_path = os.path.join(eda_folder_path, filename)
                plt.savefig(save_path)
                plt.close()

                # Store relative path for HTML
                eda_images.append(f"static/eda_results/{filename}")

            if len(numeric_cols) > 1:
                plt.figure(figsize=(10, 8))
                sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm")
                filename = "correlation_heatmap.png"
                save_path = os.path.join(eda_folder_path, filename)
                plt.savefig(save_path)
                plt.close()

                # Store relative path for HTML
                eda_images.append(f"static/eda_results/{filename}")

            return eda_head, eda_shape, eda_images, eda_summary

        except Exception as e:
            raise CustomException(e, sys)       
    
    def save_train_test(self, df: pd.DataFrame):
        logging.info("Splitting input data into training and testing sets")
        try:
            # Split the dataset in to training and test sets
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
                train_set,
                test_set
            )
        except Exception as e:
            raise CustomException(e, sys)

    def get_model_data(self, data_set):
        """
        Loads a saved dataset from model_run/ using self.source.read
        Returns: DataFrame
        """
        logging.info("Loading ingested model run data")
        try:
            if data_set == "raw":
                df = self.source.read_flat_file(self.ingestion_config.raw_data_path)
            elif data_set == "train":          
                df = self.source.read_flat_file(self.ingestion_config.train_data_path)      
            elif data_set == "test":                
                df = self.source.read_flat_file(self.ingestion_config.test_data_path)
            
            return df
                
        except Exception as e:
            raise CustomException(e, sys)

    def run(self):
        # Get the raw data
        df_raw = self.load_raw(self.ingest_path)

        # Run EDA
        eda_head, eda_shape, eda_images, eda_summary = self.run_eda(df_raw)

        return {
            'df_raw':df_raw,
            'eda_head':eda_head,
            'eda_shape':eda_shape,
            'eda_images':eda_images,
            'eda_summary':eda_summary
        }


if __name__ == "__main__":
    obj = IngestionManager("data/air_quality_health_dataset.csv")
    return_dict = obj.run()
    print(f"\nEDA - Data Preview: ")
    print(return_dict['df_raw'])

