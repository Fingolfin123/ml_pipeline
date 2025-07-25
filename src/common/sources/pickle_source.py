import pandas as pd
import pickle
from common.sources.datasource_base import DataSource

class PickleSource(DataSource):
    def load(self):
        path = self.config["path"]
        with open(path, "rb") as f:
            data = pickle.load(f)

        # If data is already a DataFrame, return it directly
        if isinstance(data, pd.DataFrame):
            return data
        # If it's something convertible to DataFrame (e.g., dict, list of dicts), convert
        try:
            df = pd.DataFrame(data)
            return df
        except Exception as e:
            raise ValueError(f"Loaded pickle data cannot be converted to DataFrame: {e}")

    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        # Save sample df as pickle for demonstration
        sample_path = self.config.get("sample_path", "sample.pkl")
        sample_df.to_pickle(sample_path)
        print(f"Sample pickle file saved to {sample_path}")
        return sample_df
