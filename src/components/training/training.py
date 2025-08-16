import os
import sys
from dataclasses import dataclass
import numpy as np
np.int = int  # For older libraries compatibility

import shap
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
)
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import AdaBoostRegressor
from xgboost import XGBRegressor
from catboost import CatBoostRegressor

from skopt import BayesSearchCV
from skopt.space import Real, Integer

from src.common.exception import CustomException
from src.common.monitoring.logger import logging
from src.common.datasource import DataSourceIO
from src.components.transformation.transformation import DataTransformation


@dataclass
class ModelTrainerConfig:
    models = {
        "Random Forest": RandomForestRegressor(),
        "Decision Tree": DecisionTreeRegressor(),
        "Gradient Boosting": GradientBoostingRegressor(),
        "Linear Regression": LinearRegression(),
        "K-Neighbors Regressor": KNeighborsRegressor(),
        "XGB Regressor": XGBRegressor(),
        # "CatBoost Regressor": CatBoostRegressor(verbose=False),
        "AdaBoost Regressor": AdaBoostRegressor(),
    }

    hyperparameter_tuning_specs = {
        "Random Forest": {
            "n_estimators": Integer(100, 500),
            "max_depth": Integer(3, 30),
            "min_samples_split": Integer(2, 20),
        },
        "Decision Tree": {
            "criterion": ["friedman_mse", "absolute_error", "squared_error", "poisson"],
        },
        "Gradient Boosting": {
            "n_estimators": Integer(100, 500),
            "learning_rate": Real(0.005, 0.3, prior="log-uniform"),
            "max_depth": Integer(3, 15),
        },
        "AdaBoost Regressor": {
            "learning_rate": Real(0.01, 0.3, prior="log-uniform"),
            "n_estimators": Integer(50, 300),
        },
    }

    shap_threshold = 0.005  # Absolute mean SHAP value threshold
    


class ModelTrainer:
    def __init__(self):
        self.source = DataSourceIO()
        self.model_trainer_config = ModelTrainerConfig()
        self.data_transformer = DataTransformation()

    def set_model_obj_path(self, best_model_name, target_feature_name):
        model_name = best_model_name + "_" + target_feature_name
        self.trainer_model_file_path = os.path.join(
            "model_run", f"model_{model_name}.joblib"
        )

    # def split_input_arrays(self, X_array):
    #     X = X_array[:, :-1]
    #     y = X_array[:, -1]
    #     if hasattr(y, "toarray"):
    #         y = y.toarray()
    #     return X, y.ravel()  

    def get_preprocessed_feature_names(self):
        """
        Retrieve feature names after preprocessing.
        Falls back to generic names if unavailable.
        """
        try:
            preprocessor_obj = self.source.read_flat_file(
                path=self.data_transformer.transformation_config.pre_proc_obj_path
            )
            # Works if using sklearn >= 1.0
            feature_names = preprocessor_obj.get_feature_names_out()
            print(list(feature_names))
            return list(feature_names)
        except AttributeError:
            # If get_feature_names_out is unavailable, fall back to generic names
            # if hasattr(preprocessor_obj, 'transform'):
            #     # Temporarily transform dummy data to get correct number of features
            #     import numpy as np
            #     import pandas as pd
            #     dummy = np.zeros((1, len(preprocessor_obj.feature_names_in_)))
            #     transformed = preprocessor_obj.transform(dummy)
            #     n_features = transformed.shape[1]
            #     return [f"feature_{i}" for i in range(n_features)]
            # else:
                # Worst case: just return empty list
                return []

    def split_input_arrays(self, X_array):
        """
        Splits transformed array into X and y, ensuring dense NumPy format.
        """
        # Convert sparse matrix to dense if necessary
        if hasattr(X_array, "toarray"):
            X_array = X_array.toarray()

        # X is all but last column, y is last column
        X = X_array[:, :-1]
        y = X_array[:, -1]

        # If y is sparse, make dense
        if hasattr(y, "toarray"):
            y = y.toarray()

        # Flatten y to 1D
        y = y.ravel()

        return X, y

    def shap_feature_selection(self, X_train, y_train, feature_names):
        """
        Fit a baseline model and use SHAP to remove low-importance features.
        """
        logging.info("Running SHAP feature selection...")

        # Use a fast baseline model for SHAP
        baseline_model = RandomForestRegressor(n_estimators=100, random_state=42)
        baseline_model.fit(X_train, y_train)

        # Tree SHAP
        explainer = shap.TreeExplainer(baseline_model)
        shap_values = explainer.shap_values(X_train)

        # Mean absolute SHAP importance
        mean_shap_importance = np.abs(shap_values).mean(axis=0)

        # Keep features above threshold
        keep_mask = mean_shap_importance >= self.model_trainer_config.shap_threshold
        kept_features = np.array(feature_names)[keep_mask]
        removed_features = np.array(feature_names)[~keep_mask]

        logging.info(f"Removed low-importance features: {removed_features.tolist()}")
        logging.info(f"Kept features: {kept_features.tolist()}")

        return X_train[:, keep_mask], kept_features, keep_mask

    def evaluate_models(self, X_train, y_train, X_test, y_test, models):
        try:
            report = {}
            hyper_specs = self.model_trainer_config.hyperparameter_tuning_specs

            for name, model in models.items():
                logging.info(f"Training model: {name}")

                if name in hyper_specs:
                    search = BayesSearchCV(
                        estimator=model,
                        search_spaces=hyper_specs[name],
                        n_iter=20,
                        cv=3,
                        scoring="r2",
                        n_jobs=-1,
                        random_state=42,
                    )
                    search.fit(X_train, y_train)
                    best_model = search.best_estimator_
                else:
                    best_model = model
                    best_model.fit(X_train, y_train)

                y_pred = best_model.predict(X_test)
                r2 = r2_score(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))

                report[name] = {"r2": r2, "rmse": rmse}

                logging.info(f"{name} → R²: {r2:.4f}, RMSE: {rmse:.4f}")

            # Sort by best R²
            sorted_report = dict(
                sorted(report.items(), key=lambda x: x[1]["r2"], reverse=True)
            )
            return sorted_report

        except Exception as e:
            raise CustomException(e, sys)

    def initiate_model_trainer(self, train_array, test_array, target_feature_name):
        logging.info(f"Initiating Model Training for {target_feature_name}")

        try:
            X_train, y_train = self.split_input_arrays(train_array)
            X_test, y_test = self.split_input_arrays(test_array)

            feature_options, categorical_features, numeric_features, datetime_cols = self.data_transformer.get_raw_features()
            # feature_names = list(categorical_features) + list(numerical_features)
            feature_names = self.get_preprocessed_feature_names()
            # feature_names = [feature for feature in feature_names if feature != target_feature_name]

            print(feature_names)

            # SHAP feature elimination
            include_shap = True
            if include_shap:
                X_train_sel, kept_features, keep_mask = self.shap_feature_selection(
                    X_train, y_train, feature_names
                )
                X_test_sel = X_test[:, keep_mask]
            else:
                X_train_sel = X_train
                kept_features = feature_names
                X_test_sel = X_test

            # Train & Evaluate
            model_report = self.evaluate_models(
                X_train_sel, y_train, X_test_sel, y_test, self.model_trainer_config.models
            )

            best_model_name = next(iter(model_report))
            best_model_score = model_report[best_model_name]["r2"]
            best_model = self.model_trainer_config.models[best_model_name]

            if best_model_score < 0.6:
                raise CustomException("No models passing R² > 0.6 threshold.")

            logging.info(
                f"Best Model: {best_model_name} | R²: {best_model_score:.4f} | RMSE: {model_report[best_model_name]['rmse']:.4f}"
            )

            self.set_model_obj_path(best_model_name, target_feature_name)
            self.source.write_flat_file(best_model, path=self.trainer_model_file_path)

            return model_report

        except Exception as e:
            raise CustomException(e, sys)

    def evaluate_features(self, target_feature_name="EvaluateAllNumericFeatures"):
        dt = self.data_transformer
        if target_feature_name == "EvaluateAllNumericFeatures":
            df_raw, df_train, df_test = dt.get_ingest_data()
            _, numeric_features = dt.split_features(df_raw)
            for target in numeric_features:
                train_arr, test_arr, _ = dt.run(target)
                self.initiate_model_trainer(train_arr, test_arr, target)
        else:
            train_arr, test_arr, _ = dt.run(target_feature_name)
            return self.initiate_model_trainer(train_arr, test_arr, target_feature_name)


if __name__ == "__main__":
    obj = ModelTrainer()
    # obj.evaluate_features("math_score")
    obj.evaluate_features("respiratory_admissions")
