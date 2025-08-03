import pandas as pd
from src.common.sources.base_source import DataSource


class PickleSource(DataSource):
    def _read(self, path: str):
        options = self.config.get("options", {})
        return pd.read_pickle(path, **options)

    def _write(self, df, path: str):
        options = self.config.get("write_options", {})
        df.to_pickle(path, **options)

    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        self.write(sample_df)
        return sample_df
