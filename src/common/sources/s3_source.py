import boto3
import pandas as pd
import io
from common.sources.datasource_base import DataSource

class S3Source(DataSource):
    def load(self):
        bucket = self.config["bucket"]
        key = self.config["key"]  # S3 object key (path to the file)
        aws_access_key_id = self.config.get("aws_access_key_id")
        aws_secret_access_key = self.config.get("aws_secret_access_key")
        aws_session_token = self.config.get("aws_session_token")  # optional
        region_name = self.config.get("region_name")  # optional
        file_type = self.config.get("file_type", "csv")  # default to CSV
        read_options = self.config.get("read_options", {})  # options for pandas read_csv, etc.

        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region_name,
        )

        s3 = session.client("s3")
        obj = s3.get_object(Bucket=bucket, Key=key)
        data = obj['Body'].read()

        if file_type == "csv":
            df = pd.read_csv(io.BytesIO(data), **read_options)
        elif file_type == "json":
            df = pd.read_json(io.BytesIO(data), **read_options)
        else:
            raise ValueError(f"Unsupported file_type: {file_type}")

        return df

    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        print("S3 source does not support writing sample data.")
        return sample_df
