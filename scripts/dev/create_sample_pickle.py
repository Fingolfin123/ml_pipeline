import os
import pandas as pd
from pathlib import Path

from src.common.utils import get_project_path
from src.common.sources.pickle_source import PickleSource
from src.common.sources.base_source import DataSource

# Configuration for PickleSource
config = {
    "path": str(get_project_path("data", "sample.pkl")),
    "options": {},       # read options
    "write_options": {}  # write options
}

# Instantiate and generate/write sample
source = PickleSource(config)
df = source.generate_sample_table()

print(df)
