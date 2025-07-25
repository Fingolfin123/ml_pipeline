import pandas as pd
from sqlalchemy import create_engine
from common.sources.datasource_base import DataSource

class SQLSource(DataSource):
    def load(self):
        connection_uri = self.config["connection_uri"]
        query = self.config["query"]
        engine = create_engine(connection_uri)
        return pd.read_sql(query, engine)

    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        connection_uri = self.config["connection_uri"]
        table_name = self.config.get("table_name", "sample_table")
        engine = create_engine(connection_uri)

        # Write the sample DataFrame to the SQL database
        sample_df.to_sql(table_name, engine, if_exists="replace", index=False)
        print(f"Sample table '{table_name}' written to {connection_uri}")
