import sys
import pytest
import pandas as pd

from src.common.monitoring.logger import logging
from src.common.exception import CustomException

from src.common.sources.postgresql_source import PostgreSQLSource


@pytest.mark.parametrize("source_class, config_overrides", [
    (PostgreSQLSource, {
        "host": "localhost",
        "port": 5432,
        "database": "test_db",
        "user": "postgres",
        "password": "postgres",
        "table": "test_table",
        "options": {},
        "write_options": {}
    }),
])
def test_postgresql_datasource_roundtrip(source_class, config_overrides):
    logging.info("Running PostgreSQL DataSource Roundtrip Test")
    try:
        # Create a simple DataFrame for testing
        df = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": ["a", "b", "c"],
            "col3": [True, False, True]
        })

        # Initialize and run roundtrip
        source = source_class(config=config_overrides)
        source.write(df)
        result_df = source.read()

        # Assert roundtrip data matches original
        pd.testing.assert_frame_equal(
            df.reset_index(drop=True),
            result_df.reset_index(drop=True),
            check_dtype=False
        )

    except Exception as e:
        raise CustomException(e, sys)
