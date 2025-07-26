import os
import pandas as pd
from pathlib import Path

from src.common.monitoring.logger import logging
from src.common.utils import get_project_path
from src.common.sources.csv_source import CSVSource
from src.common.sources.base_source import DataSource


# Configuration for CSVSource
config = {
    "path": str(get_project_path("data","sample.csv")),
    "options": {},  # read options
    "write_options": {"header": True}  # write options
}

# Instantiate and generate/write sample
source = CSVSource(config)
logging.info(f"""Saving project file to: {config["path"]}""")
df = source.generate_sample_table()

# print("Sample DataFrame written to:", sample_path)
print(df)
