import pytest
import pandas as pd
import os
from common.sources.csv_source import CSVSource

def test_csv_source_load(tmp_path):
    # Create a sample CSV file in the pytest temp directory
    csv_file = tmp_path / "sample.csv"
    sample_data = """col1,col2,col3
1,a,True
2,b,False
3,c,True
"""
    csv_file.write_text(sample_data)

    # Config for CSVSource
    csv_config = {
        "path": str(csv_file),
        "options": {
            "header": True,
            "delimiter": ",",
            "encoding": "utf-8"
        }
    }

    # Instantiate and load
    source = CSVSource(config=csv_config)
    df = source.load()

    # Assertions: check shape and content
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (3, 3)
    assert list(df.columns) == ["col1", "col2", "col3"]
    assert df["col1"].iloc[0] == 1 or df["col1"].iloc[0] == "1"  # could be int or str depending on read_csv
    assert df["col2"].iloc[1] == "b"
    assert df["col3"].iloc[2].lower() == "true" or df["col3"].iloc[2] is True  # depending on dtype inference

