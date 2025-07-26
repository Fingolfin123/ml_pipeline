import pandas as pd
from sqlalchemy import create_engine
from src.common.sources.base_source import DataSource

class PostgreSQLSource(DataSource):
    def read(self):
        user = self.config["user"]
        password = self.config["password"]
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 5432)
        database = self.config["database"]
        query = self.config["query"]  # SQL query string to fetch data

        conn_str = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
        engine = create_engine(conn_str)

        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        return df

    def write(self, df):
        df.write.format("jdbc").options(**self.config).mode("overwrite").save()

    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        print("PostgreSQL source does not support writing sample data.")
        return sample_df
