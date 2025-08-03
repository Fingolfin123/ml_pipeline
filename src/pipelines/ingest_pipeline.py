import sys
import pandas as pd

from src.exception import CustomException
from src.utils import load_object
from src.common.type_defs import SourceClassMap


def get_available_source_types():
    return [member.name for member in SourceClassMap]


class PredictPipeline:
    def __init__(self, trainer_model_file_path: str, pre_proc_obj_path: str):
        self.trainer_model_file_path = trainer_model_file_path
        self.pre_proc_obj_path = pre_proc_obj_path

    def predict(self, features, target_feature_name):
        try:
            model = load_object(
                file_path=self.trainer_model_file_path, unique_name=target_feature_name
            )
            preprocessor = load_object(
                file_path=self.pre_proc_obj_path, unique_name=target_feature_name
            )
            data_scaled = preprocessor.transform(features)
            prediction = model.predict(data_scaled)

            return prediction

        except Exception as e:
            CustomException(e, sys)


class PredictionSelectionData:
    def __init__(
        self,
        gender: str,
        race_ethnicity: str,
        parental_level_of_education: str,
        lunch: str,
        test_preparation_course: str,
        reading_score: int,
        writing_score: int,
    ):
        self.gender = gender
        self.race_ethnicity = race_ethnicity
        self.parental_level_of_education = parental_level_of_education
        self.lunch = lunch
        self.test_preparation_course = test_preparation_course
        self.reading_score = reading_score
        self.writing_score = writing_score

    def get_data_as_data_frame(self):
        try:
            custom_data_input_dict = {
                "gender": [self.gender],
                "race_ethnicity": [self.race_ethnicity],
                "parental_level_of_education": [self.parental_level_of_education],
                "lunch": [self.lunch],
                "test_preparation_course": [self.test_preparation_course],
                "reading_score": [self.reading_score],
                "writing_score": [self.writing_score],
            }

            return pd.DataFrame(custom_data_input_dict)

        except Exception as e:
            CustomException(e, sys)
