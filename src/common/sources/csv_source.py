import pandas as pd
from src.common.sources.base_source import DataSource

class CSVSource(DataSource):
    def _read(self, path:str):
        options = self.config.get("options", {})
        return pd.read_csv(path, **options)
    
    def _write(self, df, path:str):  
        options = self.config.get("write_options", {})
        df.to_csv(path, index=False, **options)
        
    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        self.write(sample_df)
        return sample_df
