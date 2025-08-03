import os
import sys
import pytest
import pandas as pd
from pathlib import Path
from shutil import rmtree

from src.common.sources.csv_source import CSVSource
from src.common.sources.json_source import JSONSource
from src.common.sources.pickle_source import PickleSource
from src.common.sources.joblib_source import JoblibSource

from src.components.ingestion.ingestion import IngestionManager
from src.common.type_defs import SourceClassMap
from src.common.exception import CustomException

@pytest.fixture(scope="function")
def sample_dataframe():
    return pd.DataFrame({
        "feature1": [1, 2, 3, 4],
        "feature2": ["A", "B", "C", "D"],
        "label": [0, 1, 0, 1]
    })

@pytest.mark.parametrize("source_enum, extension, config_overrides", [
    (SourceClassMap.CSV, ".csv", {"options": {}, "write_options": {"header": True}}),
    (SourceClassMap.JSON, ".json", {"options": {}, "write_options": {"orient": "records", "indent": 2}}),
    (SourceClassMap.PICKLE, ".pkl", {"options": {}, "write_options": {}}),
    (SourceClassMap.JOBLIB, ".joblib", {"options": {}, "write_options": {}}),
])
def test_ingestion_manager_end_to_end(tmp_path, sample_dataframe, source_enum, extension, config_overrides):
    try:
        df = sample_dataframe
        test_path = tmp_path / f"sample{extension}"

        # Write file in correct format
        if extension == ".csv":
            df.to_csv(test_path, index=False)
        elif extension == ".json":
            df.to_json(test_path, orient="records", indent=2)
        elif extension == ".pkl":
            df.to_pickle(test_path)
        elif extension == ".joblib":
            import joblib
            joblib.dump(df, test_path)

        # Run the ingestion manager using new method
        manager = IngestionManager()
        manager.set_ingest_path(str(test_path))
        # manager.set_source_from_config(source_enum, config_overrides)
        df_raw, df_train, df_test = manager.run()

        # Check all files are created
        assert Path(manager.ingestion_config.raw_data_path).exists()
        assert Path(manager.ingestion_config.train_data_path).exists()
        assert Path(manager.ingestion_config.test_data_path).exists()

        # Validate DataFrame output
        assert isinstance(df_raw, pd.DataFrame)
        assert isinstance(df_train, pd.DataFrame)
        assert isinstance(df_test, pd.DataFrame)
        assert len(df_train) + len(df_test) == len(df_raw)

    except Exception as e:
        raise CustomException(e, sys)
