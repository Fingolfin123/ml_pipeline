import os
import sys
import dill
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from typing import List, Dict, Any

from src.exception import CustomException
from src.logger import logging

def save_object(file_path, unique_name, obj):
    try:
        logging.info('Saving Processing Object')
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)

        # Split filename and insert unique name before the extension
        base, ext = os.path.splitext(os.path.basename(file_path))
        modified_filename = f"{base}_{unique_name}{ext}"
        modified_path = os.path.join(dir_path, modified_filename)

        # Use joblib if it's a .joblib file, otherwise use dill
        if ext.lower() == ".joblib":
            joblib.dump(obj, modified_path)
        else:
            with open(modified_path, "wb") as file_obj:
                dill.dump(obj, file_obj)

    except Exception as e:
        raise CustomException(e, sys)
    
def load_object(file_path, unique_name):
    try:
        logging.info('Loading Processing Object')
        dir_path = os.path.dirname(file_path)
        
        # Split filename and insert unique name before the extension
        base, ext = os.path.splitext(os.path.basename(file_path))
        modified_filename = f"{base}_{unique_name}{ext}"
        modified_path = os.path.join(dir_path, modified_filename)

        if os.path.isdir(dir_path):
            # Use joblib if it's a .joblib file, otherwise use dill
            if ext.lower() == ".joblib":
                obj = joblib.load(modified_path)
            else:
                with open(modified_path, "rb") as file_obj:
                    obj = dill.load(file_obj)
        return obj

    except Exception as e:
        raise CustomException(e, sys)


class GetProcessorObj:
    def __init__(self, proc_obj_path: str, target_feature_name: str):
        self.processor_obj=load_object(file_path=proc_obj_path, unique_name=target_feature_name)        
        self.numerical_features = self.get_numerical_features()
        self.categorical_feature_options = self.get_categorical_feature_options()

    def get_numerical_features(self) -> List[str]:
        """Returns a list of numerical feature names"""
        for name, transformer, columns in self.processor_obj.transformers_:
            if transformer == 'drop' or transformer == 'passthrough':
                continue
            if isinstance(transformer, Pipeline):
                # Check if it's a pipeline with scaler (assumes numerical)
                last_step = transformer.steps[-1][1]
                if hasattr(last_step, "transform"):  # crude check for scaler
                    return columns
            else:
                # Direct transformer (not wrapped in pipeline)
                if hasattr(transformer, "transform"):  # e.g., StandardScaler
                    return columns
        return []

    def get_categorical_feature_options(self) -> Dict[str, List[Any]]:
        """Returns a dict of categorical column name → learned category values"""
        result = {}
        for name, transformer, columns in self.processor_obj.transformers_:
            if transformer == 'drop' or transformer == 'passthrough':
                continue

            # Handle pipeline-wrapped encoders
            if isinstance(transformer, Pipeline):
                for _, step in transformer.steps:
                    if isinstance(step, OneHotEncoder):
                        ohe = step
                        break
                else:
                    continue  # No OHE found
            elif isinstance(transformer, OneHotEncoder):
                ohe = transformer
            else:
                continue  # Not an OHE

            for col_name, categories in zip(columns, ohe.categories_):
                result[col_name] = categories.tolist()

        return result

    @property
    def feature_options(self):
        '''Returns a dictionary of categorical features [dict] and numerical features [list]'''   
        return  {
            "categorical": self.categorical_feature_options,
            "numerical": self.numerical_features
        }  