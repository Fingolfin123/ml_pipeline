import sys
import numpy as np
import pandas as pd

from src.common.exception import CustomException
# from src.utils import load_object
from src.components.training.model_trainer import ModelTrainer


class TrainingPipeline:
    def __init__(self):
        pass

    def training(self,feature):
        try:
            obj=ModelTrainer()
            training_report = obj.evaluate_features(feature)
            
            return training_report
        
        except Exception as e:
            CustomException(e,sys)

class TrainingSelectionData:
    def __init__(
        self,
        features: str,
        ):
        self.features=features

    def get_data_as_data_frame(self):
        try:
            custom_data_input_dict = {
                "features": [self.features],            
            }

            return pd.DataFrame(custom_data_input_dict)
        
        except Exception as e:
            CustomException(e,sys)

