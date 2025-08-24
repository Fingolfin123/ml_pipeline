import sys
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from src.components.transformation.transformation import DataTransformation
from src.common.exception import CustomException


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(
        {
            "feature_num": [1.0, 2.0, 3.0, 4.0],
            "feature_cat": ["A", "B", "A", "B"],
            "target": [0, 1, 0, 1],
        }
    )


class MockIngestionManager:
    """Mock version of IngestionManager that returns in-memory data."""

    def get_model_data(self, data_set):
        data_set = None # Not used here
        df = pd.DataFrame(
            {
                "feature_num": [1.0, 2.0, 3.0, 4.0],
                "feature_cat": ["A", "B", "A", "B"],
                "target": [0, 1, 0, 1],
            }
        )
        # Simulate just the raw data here
        return df

    def save_train_test(self, df):
        train_set, test_set = df.iloc[:3], df.iloc[3:]

        return (
            train_set,
            test_set
        )

def test_data_transformation_run(tmp_path, sample_dataframe, monkeypatch):
    try:
        # Patch IngestionManager inside DataTransformation with mock
        transformer = DataTransformation()
        transformer.data_ingestion = MockIngestionManager()
        transformer.transformation_config.pre_proc_obj_path = str(
            tmp_path / "pre_proc.joblib"
        )

        # Run transformation
        train_arr, test_arr, preproc_path = transformer.run(
            target_feature_name="target"
        )

        # === Assertions ===
        # Check preprocessing object file was saved
        assert Path(preproc_path).exists()

        # Check returned arrays are numpy/sparse-compatible
        assert hasattr(train_arr, "shape")
        assert hasattr(test_arr, "shape")

        # Check correct row counts
        assert train_arr.shape[0] == 3
        assert test_arr.shape[0] == 1

        # Ensure exactly 1 extra column for target
        if hasattr(train_arr, "toarray"):  # sparse case
            train_dense = train_arr.toarray()
        else:
            train_dense = np.array(train_arr)
        assert train_dense.shape[1] > 1

    except Exception as e:
        raise CustomException(e, sys)
