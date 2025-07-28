import os
import sys
import pandas as pd
from src.common.type_defs import SourceClassMap
from src.common.exception import CustomException
from src.common.monitoring.logger import logging
from src.components.type_defs import TraingingParams

from sklearn.model_selection import train_test_split
from dataclasses import dataclass


@dataclass
class DataIngestConfig:
    train_data_path: str=os.path.join('artifacts',"train.csv")
    test_data_path: str=os.path.join('artifacts',"test.csv")
    raw_data_path: str=os.path.join('artifacts',"raw.csv")

class IngestionManager:
    def __init__(self, source_enum: SourceClassMap, source_config: dict):
        self.ingestion_config=DataIngestConfig()
        self.source_enum = source_enum
        self.source_config = source_config

        # Initialize the source class object
        self.source_class = self.source_enum.value
        self.source = self.source_class(self.source_config)        

    def initiate_data_ingestion(self):
        logging.info("Running Data Ingestion")
        try:
            # Read the raw data          
            df=self.source.read()

            # Save the input data to specified training folder
            self.source.write(df, path=self.ingestion_config.raw_data_path)

            # Split the dataset in to training and test sets
            logging.info("Splitting input data into training and testing sets")
            train_set,test_set=train_test_split(
                df,
                test_size=TraingingParams.TEST_SIZE.value,
                random_state=TraingingParams.RANDOM_STATE.value
            )

            # Save the split data
            self.source.write(train_set, path=self.ingestion_config.train_data_path)
            self.source.write(test_set, path=self.ingestion_config.test_data_path)

            logging.info("Data Ingestion has completed.")

            return (
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path,
            )
        except Exception as e:
            raise CustomException(e,sys)
        
    def run(self):
        # Run the data ingestion process and return the raw, 
        # trainging and testing dataframes
        self.initiate_data_ingestion()        
        df_raw = self.source.read(self.ingestion_config.raw_data_path)
        df_train = self.source.read(self.ingestion_config.train_data_path)
        df_test = self.source.read(self.ingestion_config.test_data_path)

        return df_raw,df_train,df_test
    
if __name__=="__main__":
    obj=IngestionManager(
        source_enum=SourceClassMap.CSV,
        source_config = {"path": "data/sample.csv"}
    )
    df_raw,df_train,df_test = obj.run()
    print(df_raw)
    print(df_train)
    print(df_test)