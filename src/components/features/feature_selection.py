import sys
import numpy as np
import pandas as pd
from src.common.monitoring.logger import logging
from sklearn.feature_selection import mutual_info_regression
from src.common.exception import CustomException

class FeatureSelector:
    """
    A reusable feature selection pipeline:
      - Removes datetime/object datetime fields
      - Removes near-constant features
      - Removes highly correlated features
      - Applies supervised filter (Mutual Information)
    """

    def __init__(self, transform_config:dict):
        """
        Args:
            correlation_factor: Threshold above which correlated features are dropped.
            mutual_info_filter_count: Number of top features to keep based on MI.
        """
        # correlation_factor: float = 0.9, mutual_info_filter_count: int = 15
        self.timeseries_toggle = transform_config.timeseries_toggle
        self.correlation_factor = transform_config.correlation_factor
        self.mutual_info_filter_count = transform_config.mutual_info_filter_count

    # def _get_features(self, df, target_feature_name):
    #     return [col for col in df.columns if col != target_feature_name]
    def _get_features(self, df: pd.DataFrame, target_feature_name: str):
        # Drop target + known non-features
        excluded = {target_feature_name, "date"}  
        
        features = []
        for col, dtype in df.dtypes.items():
            if col in excluded:
                continue
            
            if np.issubdtype(dtype, np.number):
                # keep numeric features
                features.append(col)
            
        return features   

    def preprocess_object_fields(self, df: pd.DataFrame, exclude: list[str] = None) -> pd.DataFrame:
        """
        Converts object/string fields into categorical codes, except excluded columns.
        Also skips datetime-like fields.
        """

        for col in df.columns:
            if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
                # check if it's actually datetime-like
                try:
                    pd.to_datetime(df[col], errors="raise")
                    # if conversion works without error, treat as datetime → skip
                    continue
                except Exception:
                    pass

                # otherwise, categorical encoding
                df[col] = df[col].astype("category").cat.codes

        return df

    def preprocess_datetime(self, df):
        """
        Expands or preserves datetime columns consistently across multiple DataFrames.
        - Detects native datetime columns.
        - Detects object columns that can be parsed as dates.
        - Converts objects to datetime if parseable.
        - Expands into components if timeseries_toggle is False.
        Prevents column mismatch between train/test/raw.
        """
        try:        
            datetime_cols = set()

            # Pass 1: Detect datetime and parseable object date columns across all datasets
            # Native datetime64 columns
            datetime_cols = []

            for col in df.columns:
                # If it's already datetime dtype
                if np.issubdtype(df[col].dtype, np.datetime64):
                    datetime_cols.append(col)
                # If it's object but parses as datetime
                elif df[col].dtype == 'object':
                    try:
                        pd.to_datetime(df[col], errors='raise')
                        datetime_cols.append(col)
                    except Exception:
                        pass

            # Pass 2: Standardize datetime handling in each dataset
            # Convert all detected datetime columns to datetime dtype
            for col in datetime_cols:
                if col in df.columns and not np.issubdtype(df[col].dtype, np.datetime64):
                    try:
                        df[col] = pd.to_datetime(df[col], errors="coerce")
                    except Exception:
                        pass

            # If not time series mode, expand datetime columns into components
            if not self.timeseries_toggle and datetime_cols:
                """Expands datetime columns into separate numeric features."""
                for col in list(datetime_cols):
                    df[f"{col}_year"] = df[col].dt.year
                    df[f"{col}_month"] = df[col].dt.month
                    df[f"{col}_day"] = df[col].dt.day
                    df[f"{col}_dayofweek"] = df[col].dt.dayofweek
                    df.drop(columns=[col], inplace=True)   
                logging.info(f"Converted datatime columns to features")

            return df

        except Exception as e:
            raise CustomException(e, sys)        
    
    def preprocess_low_variance(self, df, target_feature_name):
        """
        Remove near-constant features.
        """
        try:
            features = self._get_features(df, target_feature_name)
            constant_cols = [col for col in features if df[col].nunique() <= 1]

            df = df.drop(columns=constant_cols)
            logging.info(f"Dropping near-constant features: {constant_cols}")
            return df
        except Exception as e:
            raise CustomException(e, sys)       

    def preprocess_correlated_features(self, df, target_feature_name):
        """
        Remove highly correlated features (> threshold).
        Keeps the target column intact.
        """
        try:        
            features = self._get_features(df, target_feature_name)
            corr_matrix = df[features].corr().abs()

            # Select upper triangle of correlation matrix
            upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))

            # Identify columns with correlation above threshold
            high_corr = [col for col in upper.columns if any(upper[col] > self.correlation_factor)]

            df = df.drop(columns=high_corr)
            logging.info(f"Dropping highly correlated features: {high_corr}")
            return df
        except Exception as e:
            raise CustomException(e, sys)      

    def preprocess_mutual_info(self, df, target_feature_name):
        """
        Select top-N features by mutual information with target.
        """
        try:
            features = self._get_features(df, target_feature_name)

            # Drop non-numeric columns before MI
            X = df[features].select_dtypes(include=[np.number])
            y = df[target_feature_name]

            if X.empty:
                logging.warning("No numeric features available for MI filter. Skipping.")
                return df

            mi_scores = mutual_info_regression(X, y, random_state=42)
            mi_df = pd.DataFrame({'feature': X.columns, 'mi_score': mi_scores})
            mi_df = mi_df.sort_values(by='mi_score', ascending=False)

            top_features = mi_df['feature'].head(
                self.mutual_info_filter_count
            ).tolist()

            # Always keep target + selected features
            keep_cols = [target_feature_name] + top_features
            df = df[keep_cols]
            logging.info(f"Keeping top mutual info features: {top_features}")
            return df
        
        except Exception as e:
            raise CustomException(e, sys)      

    def run(self, df: pd.DataFrame, target_feature_name: str) -> pd.DataFrame:
        """
        Apply full feature selection pipeline.
        Returns:
            DataFrame with reduced features.
        """
        # Step 1: Drop datetime-like columns
        
        features = self._get_features(df, target_feature_name)
        # print(df[features].dtypes)       
        df = self.preprocess_datetime(df)
        features = self._get_features(df, target_feature_name)
        # print(df[features].dtypes)       
        df = self.preprocess_object_fields(df, [target_feature_name])
        features = self._get_features(df, target_feature_name)
        # print(df[features].dtypes)               

        # Step 2: Remove low variance
        df = self.preprocess_low_variance(df, target_feature_name)

        # Step 3: Remove correlated features
        df = self.preprocess_correlated_features(df, target_feature_name)

        # Step 4: Apply mutual information filter (supervised)
        # df = self.preprocess_mutual_info(df, target_feature_name)
        features = self._get_features(df, target_feature_name)
        print(df[features].dtypes) 
        return df
