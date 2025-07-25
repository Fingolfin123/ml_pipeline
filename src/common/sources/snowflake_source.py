import pandas as pd
import snowflake.connector
from common.sources.datasource_base import DataSource

class SnowflakeSource(DataSource):
    def load(self):
        user = self.config["user"]
        password = self.config["password"]
        account = self.config["account"]
        warehouse = self.config.get("warehouse")
        database = self.config.get("database")
        schema = self.config.get("schema")
        query = self.config["query"]

        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            schema=schema,
        )
        try:
            df = pd.read_sql(query, conn)
        finally:
            conn.close()

        return df

    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        print("Snowflake source does not support writing sample data.")
        return sample_df
