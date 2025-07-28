import joblib
from src.common.sources.base_source import DataSource

class JoblibSource(DataSource):
    def _read(self, path:str):
        return joblib.load(path)

    def _write(self, obj, path:str):
        compress = self.config.get("compress", 3)  # default: moderate compression
        protocol = self.config.get("protocol", None)  # default: latest
        print(f"Saving joblib object to: {path} (compress={compress}, protocol={protocol})")
        joblib.dump(obj, path, compress=compress, protocol=protocol)

    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        self.write(sample_df)
        return sample_df
