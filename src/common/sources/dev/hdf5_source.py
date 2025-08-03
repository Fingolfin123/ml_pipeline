import pandas as pd
from src.common.sources.base_source import DataSource


class HDF5Source(DataSource):
    def load(self):
        path = self.config["path"]  # Local path to .h5/.hdf5 file
        key = self.config.get("key")
        options = self.config.get("options", {})

        if not key:
            raise ValueError("Missing required config key: 'key'")

        return pd.read_hdf(path, key=key, **options)

    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        output_path = self.config.get("output_path")  # e.g., data/sample.h5
        key = self.config.get("key", "data")

        if not output_path:
            raise ValueError("Missing required config key: 'output_path'")

        sample_df.to_hdf(output_path, key=key, index=False, mode="w", format="table")
        print(f"Sample HDF5 file saved to: {output_path}")
