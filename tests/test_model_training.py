import sys
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from src.components.training.training import ModelTrainer
from src.common.exception import CustomException


@pytest.fixture
def sample_train_test_arrays():
    """Fixture returning simple numpy arrays for training/testing."""
    # 4 features + 1 target column
    X_train = np.array([
        [1.0, 0.0, 0.5, 2.0, 10.0],
        [2.0, 1.0, 1.5, 3.0, 20.0],
        [3.0, 0.0, 2.5, 4.0, 30.0],
    ])
    X_test = np.array([
        [4.0, 1.0, 3.5, 5.0, 40.0],
    ])
    return X_train, X_test


class MockDataTransformation:
    """Mock replacement for DataTransformation in ModelTrainer."""
    def get_ingest_data(self):
        # Return dummy raw, train, test DataFrames
        df = pd.DataFrame({
            "f1": [1, 2, 3, 4],
            "f2": [0, 1, 0, 1],
            "target": [10, 20, 30, 40]
        })
        return df, df.iloc[:3], df.iloc[3:]

    def split_features(self, df):
        return ["f2"], ["target"]

    def initiate_data_transformation(self, target_feature):
        # Return dummy train/test arrays and fake preprocessor path
        train_arr = np.array([
            [1.0, 0.0, 10.0],
            [2.0, 1.0, 20.0],
            [3.0, 0.0, 30.0],
        ])
        test_arr = np.array([
            [4.0, 1.0, 40.0],
        ])
        return train_arr, test_arr, "fake_preproc_path.joblib"


def test_initiate_model_trainer(tmp_path, sample_train_test_arrays, monkeypatch):
    try:
        trainer = ModelTrainer()

        # Patch DataTransformation in ModelTrainer
        trainer.model_trainer_config.data_transformer = MockDataTransformation()

        # Patch write_flat_file so it doesn't actually write to disk
        def fake_write_flat_file(obj, path):
            Path(path).write_text("fake model object")

        monkeypatch.setattr(trainer.source, "write_flat_file", fake_write_flat_file)

        # Run evaluation on fake data
        train_arr, test_arr = sample_train_test_arrays
        results = trainer.initiate_model_trainer(train_arr, test_arr, "target")

        # === Assertions ===
        assert isinstance(results, dict)
        assert all(isinstance(v, float) for v in results.values())
        assert Path(trainer.trainer_model_file_path).exists()
        assert max(results.values()) <= 1.0  # R² can't exceed 1

    except Exception as e:
        raise CustomException(e, sys)
