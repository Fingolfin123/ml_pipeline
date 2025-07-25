import pandas as pd
from common.sources.datasource_base import DataSource

class CSVSource(DataSource):
    def read(self):
        path = self.config["path"]
        options = self.config.get("options", {})
        return pd.read_csv(path, **options)
    
    def write(self, df):
        path = self.config["path"]
        options = self.config.get("write_options", {"header": "true"})
        df.write.options(**options).csv(path)
        
    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        path = self.config.get("path", "sample.csv")
        options = self.config.get("options", {})
        sample_df.to_csv(path, index=False, **options)
        print(f"Sample CSV written to: {path}")
