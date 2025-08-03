import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from src.common.sources.base_source import DataSource


class BigQuerySource(DataSource):
    def load(self):
        project_id = self.config["project_id"]
        query = self.config["query"]
        credentials_path = self.config.get("credentials_path")

        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            return pd.read_gbq(query, project_id=project_id, credentials=credentials)
        else:
            return pd.read_gbq(query, project_id=project_id)

    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        project_id = self.config["project_id"]
        dataset_id = self.config["dataset_id"]
        table_id = self.config.get("table_id", "sample_table")
        credentials_path = self.config.get("credentials_path")

        client = (
            bigquery.Client.from_service_account_json(
                credentials_path, project=project_id
            )
            if credentials_path
            else bigquery.Client(project=project_id)
        )

        table_ref = f"{project_id}.{dataset_id}.{table_id}"
        job = client.load_table_from_dataframe(sample_df, table_ref)
        job.result()  # Wait for the job to complete

        print(f"Sample table '{table_ref}' written to BigQuery.")
