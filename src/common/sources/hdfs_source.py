import pandas as pd
import pyarrow as pa
import pyarrow.fs as fs
from common.sources.datasource_base import DataSource

class HDFSSource(DataSource):
    def load(self):
        hdfs_host = self.config["host"]
        hdfs_port = self.config.get("port", 8020)
        hdfs_path = self.config["path"]
        file_format = self.config.get("file_format", "csv")  # or "parquet"

        hdfs = fs.HadoopFileSystem(host=hdfs_host, port=hdfs_port)
        file = hdfs.open_input_file(hdfs_path)

        if file_format == "csv":
            return pd.read_csv(file)
        elif file_format == "parquet":
            return pd.read_parquet(file)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    def generate_sample_table(self):
        sample_df = super().generate_sample_table()

        hdfs_host = self.config["host"]
        hdfs_port = self.config.get("port", 8020)
        output_path = self.config["output_path"]
        file_format = self.config.get("file_format", "csv")

        hdfs = fs.HadoopFileSystem(host=hdfs_host, port=hdfs_port)
        with hdfs.open_output_stream(output_path) as out_stream:
            if file_format == "csv":
                sample_df.to_csv(out_stream, index=False)
            elif file_format == "parquet":
                sample_df.to_parquet(out_stream, index=False)
            else:
                raise ValueError(f"Unsupported file format: {file_format}")

        print(f"Sample file written to HDFS: {output_path}")
