import sys
import pytest
import pandas as pd
from pathlib import Path

from src.common.monitoring.logger import logging
from src.common.exception import CustomException

from src.common.sources.csv_source import CSVSource
# from common.sources.parquet_source import ParquetSource  # Uncomment if implemented
# from common.sources.json_source import JSONSource        # Uncomment if implemented

@pytest.mark.parametrize("source_class, extension, config_overrides", [
    (CSVSource, ".csv", {
        "options": {},
        "write_options": {"header": True}
    }),
    # Uncomment and configure if you implement these:
    # (ParquetSource, ".parquet", {
    #     "options": {},
    #     "write_options": {}
    # }),
    # (JSONSource, ".json", {
    #     "options": {},
    #     "write_options": {}
    # }),
])
def test_datasource_io_roundtrip(tmp_path, source_class, extension, config_overrides):
    logging.info("Running DataSource Rountrip Test")    
    try:
        # Create a simple DataFrame for testing
        df = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": ["a", "b", "c"],
            "col3": [True, False, True]
        })

        # Set file path
        file_path = tmp_path / f"test{extension}"

        # Build config
        config = {
            "path": str(file_path),
            **config_overrides
        }

        # Initialize and run roundtrip
        source = source_class(config=config)
        source.write(df)
        result_df = source.read()

        # Assert roundtrip data matches original
        pd.testing.assert_frame_equal(
            df.reset_index(drop=True),
            result_df.reset_index(drop=True),
            check_dtype=False
        )
    
    except Exception as e:
        raise CustomException(e,sys)