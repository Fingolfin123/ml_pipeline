import os
import sys
from dataclasses import dataclass

from catboost import CatBoostRegressor
from sklearn.ensemble import (
    AdaBoostRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from skopt import BayesSearchCV
from skopt.space import Real, Integer, Categorical

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object

from src.components.data_transformation import DataTransformation


@dataclass
class ModelTrainerConfig:
    # Define the root path name to the model object
    # NOTE: This path is modified with each model/target feature tested
    trainer_model_file_path=os.path.join('artifacts',"model.joblib")
    # Define a dictionary of model options to test
    models = {
        "Random Forest": RandomForestRegressor(),
        "Decision Tree": DecisionTreeRegressor(),
        "Gradient Boosting": GradientBoostingRegressor(),
        "Linear Regression": LinearRegression(),
        "K-Neighbors Classifier": KNeighborsRegressor(),
        "XGBClassifier": XGBRegressor(),
        "CatBoosting Classifier": CatBoostRegressor(verbose=False),
        "AdaBoost Classifier": AdaBoostRegressor(),
    }
    # Define hyperparameter search spaces for specific model types
    # NOTE: Dictionary keys must match above model dicitionary keys
    hyperparameter_tuning_specs = {
        "Random Forest": {
            "n_estimators": Integer(50, 300),
            "max_depth": Integer(3, 20),
            "min_samples_split": Integer(2, 10),
        },
        "Decision Tree": {
            "criterion": ['friedman_mse','absolute_error','squared_error','poisson'],
        },         
        "Gradient Boosting": {
            "n_estimators": Integer(50, 300),
            "learning_rate": Real(0.01, 0.3, prior="log-uniform"),
            "max_depth": Integer(3, 10),
        },
        "CatBoosting Classifier": {
            "depth": [6,8,10],
            "learning_rate": Real(0.01, 0.1, prior="log-uniform"),
            "iterations": [30,50,100],
        },   
        "AdBoosting Classifier": {
            "learning_rate": Real(0.01, 0.1, prior="log-uniform"),
            "n_estimators": [8,16,32,64,128,256],
        },             
        # Add more models and their hyperparameter spaces here
    }

    # Get Transformed Data and Preprocessor
    data_transformer=DataTransformation()
    
    
class ModelTrainer:
    def __init__(self):
        self.model_trainer_config=ModelTrainerConfig()

    def split_input_arrays(self,X_array):
        # Seperate Model Input (X) input array by dropping ending target column
        X = X_array[:,:-1]
        y = X_array[:,-1]

        return X,y

    def evaluate_features(self, target_feature_name="EvaluateAllNumericFeatures"):
        data_transformer_obj = self.model_trainer_config.data_transformer
        if target_feature_name=="EvaluateAllNumericFeatures":
            # Load Raw data and extract all numerical features
            df_raw,df_train,df_test = data_transformer_obj.get_ingest_data()
            categorical_features, numeric_features = data_transformer_obj.split_features(df_raw)
            # Iterate through all numerical features and perform model evalulation for each
            for target_feature in numeric_features:
                train_arr,test_arr,pre_proc_obj_path = data_transformer_obj.initiate_data_transformation(target_feature)
                smodel_report = self.initiate_model_trainer(train_arr,test_arr,target_feature)
        else:
            # Load Raw data and extract all numerical features
            train_arr,test_arr,pre_proc_obj_path = data_transformer_obj.initiate_data_transformation(target_feature_name)
            model_report = self.initiate_model_trainer(train_arr,test_arr,target_feature_name)
        
        return model_report
                 
    def evaluate_models(self,X_train,y_train,X_test,y_test,models):
        try:
            report = {}
            hyperparameter_tuning_specs = self.model_trainer_config.hyperparameter_tuning_specs
            # Iterate through model types
            for name, model in models.items():
                logging.info(f"Testing Model with model type: {name}")
                if name in hyperparameter_tuning_specs:
                    search = BayesSearchCV(
                        estimator=model,
                        search_spaces=hyperparameter_tuning_specs[name],
                        n_iter=20,
                        cv=3,
                        scoring='r2',
                        n_jobs=-1,
                        random_state=42
                    )

                    # Fit with hyperparameter tuning
                    search.fit(X_train, y_train)

                    # Best model after tuning
                    best_model = search.best_estimator_
                else:
                    # No tuning if no param space defined
                    best_model = model
                    best_model.fit(X_train, y_train)

                # Predict
                y_train_pred = best_model.predict(X_train)
                y_test_pred = best_model.predict(X_test)

                # Score
                train_model_score = r2_score(y_train, y_train_pred)
                test_model_score = r2_score(y_test, y_test_pred)

                report[name] = test_model_score
                logging.info(f"Model {name} has a test R2 score of {test_model_score}")
                results = dict(sorted(report.items(), key=lambda item: item[1], reverse=True))
            return results

        except Exception as e:
            raise CustomException(e,sys)

    def initiate_model_trainer(self,train_array,test_array,target_feature_name):
        logging.info(f"Initiating Model Training for {target_feature_name}")
        try:
            logging.info("Split training and test input/target arrays")
            X_train,y_train=self.split_input_arrays(train_array)
            X_test,y_test=self.split_input_arrays(test_array)

            model_report:dict=self.evaluate_models(
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
                models=self.model_trainer_config.models)
            
            # Extract the best scores out of all model runs
            best_model_score = max(sorted(model_report.values()))
            best_model_name = list(model_report.keys())[list(model_report.values()).index(best_model_score)]
            best_model = self.model_trainer_config.models[best_model_name]

            if best_model_score < 0.6:
                raise CustomException("No models passing minimum criteria of R2 score > 0.6.")
            logging.info(f"The best model found was {best_model_name} with a R2 score of {best_model_score}")

            # Save model object
            save_object(
                file_path=self.model_trainer_config.trainer_model_file_path,
                unique_name=best_model_name+"_"+target_feature_name,
                obj=best_model,
            )
            return model_report
        
        except Exception as e:
            raise CustomException(e,sys)
        
if __name__=="__main__":
    obj=ModelTrainer()
    obj.evaluate_features('math_score')