import os
import pandas as pd
from pathlib import Path

from src.common.utils import get_project_path
from src.common.sources.json_source import JSONSource  # Create if not already
from src.common.sources.base_source import DataSource


# Configuration for JSONSource
config = {
    "path": str(get_project_path("data", "sample.json")),
    "options": {},  # read options for pd.read_json
    "write_options": {"orient": "records", "indent": 2}  # write options for df.to_json
}

# Instantiate and generate/write sample
source = JSONSource(config)
df = source.generate_sample_table()
df = source.read(config['path'])

print(df)
