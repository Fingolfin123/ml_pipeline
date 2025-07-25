import pandas as pd
from common.sources.datasource_base import DataSource

class JSONSource(DataSource):
    def load(self):
        path = self.config["path"]
        lines = self.config.get("lines", False)  # True if JSON is line-delimited
        options = self.config.get("options", {})

        return pd.read_json(path, lines=lines, **options)

    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        output_path = self.config.get("output_path")

        if not output_path:
            raise ValueError("Missing required config key: 'output_path'")

        lines = self.config.get("lines", False)
        sample_df.to_json(output_path, orient='records', lines=lines, index=False)

        print(f"Sample JSON file saved to: {output_path}")
