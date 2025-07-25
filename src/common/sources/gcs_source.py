import pandas as pd
import gcsfs
from common.sources.datasource_base import DataSource

class GCSSource(DataSource):
    def load(self):
        path = self.config["path"]  # e.g., gs://bucket_name/path/to/file.csv
        options = self.config.get("options", {})
        project = self.config.get("project")
        token = self.config.get("token", "default")  # Or a path to a JSON file or dict

        fs = gcsfs.GCSFileSystem(project=project, token=token)

        with fs.open(path, 'rb') as f:
            return pd.read_csv(f, **options)

    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        output_path = self.config.get("output_path")  # e.g., gs://bucket_name/sample_table.csv
        project = self.config.get("project")
        token = self.config.get("token", "default")

        if not output_path:
            raise ValueError("Missing required config key: 'output_path'")

        fs = gcsfs.GCSFileSystem(project=project, token=token)

        with fs.open(output_path, 'w') as f:
            sample_df.to_csv(f, index=False)

        print(f"Sample CSV saved to GCS at: {output_path}")
