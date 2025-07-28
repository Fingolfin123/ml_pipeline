import os
import pandas as pd
from pathlib import Path

from src.common.utils import get_project_path
from src.common.sources.postgresql_source import PostgreSQLSource
from src.common.sources.base_source import DataSource

# Configuration for PostgreSQLSource
config = {
    "user": "your_user",
    "password": "your_password",
    "host": "localhost",
    "port": 5432,
    "database": "your_database",
    "table": "sample_table",
    "write_options": {
        "if_exists": "replace",
        "index": False,
    }
}

# Instantiate and generate/write sample
source = PostgreSQLSource(config)
df = source.generate_sample_table()

print(df)
