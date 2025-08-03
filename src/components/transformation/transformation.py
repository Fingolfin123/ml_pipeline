import os
import sys
import numpy as np
from scipy.sparse import issparse, hstack, csr_matrix

from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from dataclasses import dataclass

from src.common.exception import CustomException
from src.common.monitoring.logger import logging

# from src.common.utils import save_object
from src.common.datasource import DataSourceIO
from src.components.ingestion.ingestion import IngestionManager


@dataclass
class DataTransformConfig:
    pre_proc_obj_path: str = os.path.join("model_run", "pre_proc.joblib")


class DataTransformation:
    def __init__(self):
        # Initialize the generic source class object
        self.source = DataSourceIO()
        self.transformation_config = DataTransformConfig()
        self.data_ingestion = IngestionManager()

    def get_raw_features(self):
        df_raw, df_train, df_test = self.data_ingestion.get_model_data()
        categorical_features, numerical_features = self.split_features(df_raw)

        # Add suffixes for dropdown display
        feature_options = [f"{f} (categorical)" for f in categorical_features] + [
            f"{f} (numerical)" for f in numerical_features
        ]

        return feature_options

    def combine_input_target_arrays(self, input_array, target_array):
        """
        Combines input features and target values into a single array/matrix.

        Handles both dense NumPy arrays and sparse CSR matrices.
        Ensures target_array is reshaped to a column vector.
        """

        # Ensure target is a column vector
        target_array = np.array(target_array).reshape(-1, 1)

        if issparse(input_array):
            # If sparse, keep sparse to avoid huge memory use
            combined_array = hstack([input_array, csr_matrix(target_array)])
        else:
            # If dense, ensure NumPy array and concatenate
            input_array = np.array(input_array)
            combined_array = np.hstack((input_array, target_array))

        print(
            "input_array shape:",
            input_array.shape if not issparse(input_array) else input_array.shape,
        )
        print("target_array shape:", target_array.shape)
        print("combined_array shape:", combined_array.shape)

        return combined_array

    def split_features(self, df):
        categorical_features = df.select_dtypes(include="object").columns
        numeric_features = df.select_dtypes(exclude="object").columns

        return categorical_features, numeric_features

    def split_input_X_and_target_y(self, df, target_feature_name):

        # Seperate Model Input (X) and predicted values (y)
        X = df.drop(columns=[target_feature_name], axis=1)
        y = df[target_feature_name]

        return X, y

    def get_transformer_obj(self, df, target_feature_name):
        """
        Performs data cleaning, feature engineering, and creates preprocessing object.

        Steps:
        🧹 Data Cleaning:
        - Handle missing values (median for numeric, mode for categorical)
        - Detect and treat outliers (IQR-based clipping)
        - Remove duplicates
        - Validate schema & data types
        - Correct inconsistent formatting for categorical features (lowercase, strip spaces)

        ⚙️ Normalization & Scaling:
        - Standard scaling for numeric features
        - One-hot encoding for categorical features
        - Domain-specific transformations (log scaling for skewed numeric features)
        - Track transformations applied for consistent inference
        """
        logging.info("Obtaining Processing Object")

        try:
            # Remove duplicates early
            before = len(df)
            df = df.drop_duplicates()
            logging.info(f"Removed {before - len(df)} duplicate rows")

            # Validate schema (basic: ensure target exists)
            if target_feature_name not in df.columns:
                raise ValueError(
                    f"Target feature '{target_feature_name}' not found in dataframe"
                )

            # Correct inconsistent formatting for string columns
            for col in df.select_dtypes(include="object").columns:
                df[col] = df[col].astype(str).str.strip().str.lower()

            # Split features and target
            X, y = self.split_input_X_and_target_y(df, target_feature_name)
            categorical_features, numeric_features = self.split_features(X)
            print(categorical_features)
            print(numeric_features)

            # Outlier treatment: IQR clipping for numeric features
            logging.info(
                "Applying IQR clipping for outlier values in numerical features"
            )
            for col in numeric_features:
                Q1 = X[col].quantile(0.25)
                Q3 = X[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                X[col] = X[col].clip(lower=lower_bound, upper=upper_bound)

            # Domain-specific: log transform skewed numeric features
            skewness = X[numeric_features].skew().abs()
            skewed_cols = skewness[skewness > 1].index.tolist()
            logging.info(f"Applying log1p to skewed columns: {skewed_cols}")
            for col in skewed_cols:
                X[col] = np.log1p(X[col])

            # Numerical pipeline
            logging.info(
                f"Creating pipeline to adjust numerical features: {numeric_features}"
            )
            num_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="median")),  # missing → median
                    ("scaler", StandardScaler()),
                ]
            )

            # Categorical pipeline
            logging.info(
                f"Creating pipeline to adjust categorical features: {categorical_features}"
            )
            cat_pipeline = Pipeline(
                steps=[
                    (
                        "imputer",
                        SimpleImputer(strategy="most_frequent"),
                    ),  # missing → mode
                    ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ("scaler", StandardScaler(with_mean=False)),
                ]
            )

            # Column transformer
            logging.info("Creating preprocessor object")
            preprocessor = ColumnTransformer(
                [
                    ("num_pipeline", num_pipeline, numeric_features),
                    ("cat_pipeline", cat_pipeline, categorical_features),
                ]
            )

            # Save metadata for inference consistency
            self.feature_metadata = {
                "categorical_features": categorical_features,
                "numeric_features": numeric_features,
                "skewed_cols": skewed_cols,
            }

            return preprocessor

        except Exception as e:
            raise CustomException(e, sys)

    def run(self, target_feature_name=None):
        logging.info("Transforming Model Input")
        try:
            # Get ingestion data
            df_raw, df_train, df_test = self.data_ingestion.get_model_data()

            # Separate input matrix and predicted output vector
            X_train, y_train = self.split_input_X_and_target_y(
                df_train, target_feature_name
            )
            X_test, y_test = self.split_input_X_and_target_y(
                df_test, target_feature_name
            )

            # Get preprocessir object to fit model for numerical and categorical features
            preprocessor_obj = self.get_transformer_obj(df_raw, target_feature_name)
            X_train_feature = preprocessor_obj.fit_transform(X_train)
            X_test_feature = preprocessor_obj.transform(X_test)

            # Separate input matrix and mredicted output vector into train and test sets
            train_arr = self.combine_input_target_arrays(X_train_feature, y_train)
            test_arr = self.combine_input_target_arrays(X_test_feature, y_test)

            self.source.write_flat_file(
                preprocessor_obj, path=self.transformation_config.pre_proc_obj_path
            )
            logging.info("Input Transformations Completed")

            return (
                train_arr,
                test_arr,
                self.transformation_config.pre_proc_obj_path,
            )

        except Exception as e:
            raise CustomException(e, sys)


if __name__ == "__main__":
    obj = DataTransformation()
    obj.run("respiratory_admissions")
