import pandas as pd
from src.common.sources.base_source import DataSource

class JSONSource(DataSource):
    def _read(self, path:str):
        options = self.config.get("options", {})
        lines = self.config.get("lines", False)
        return pd.read_json(path, lines=lines, **options)

    def _write(self, df, path:str):
        options = self.config.get("write_options", {}).copy()
        lines = self.config.get("lines", False)

        # Use orient from options if present, else default
        orient = options.get("orient", "records")
        # Remove orient from options dict so it isn't duplicated
        options.pop("orient", None)

        # Remove index if invalid for orient
        if orient not in ["split", "table"]:
            options.pop("index", None)

        # Pass orient explicitly once, and unpack other options
        df.to_json(path, orient=orient, lines=lines, **options)


    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        self.write(sample_df)
        return sample_df
