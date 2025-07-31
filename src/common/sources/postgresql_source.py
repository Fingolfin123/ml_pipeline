import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from src.common.sources.base_source import DataSource

class PostgreSQLSource(DataSource):
    def __init__(self, config):
        super().__init__(config)
        self.set_path_string()

    def set_path_string(self):
        self.config["path"] = self.config["database"] + "." + self.config["table"]

    def _get_engine(self):
        user = self.config["user"]
        password = self.config["password"]
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 5432)
        database = self.config["database"]
        conn_str = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
        return create_engine(conn_str)

    def _read(self):
        engine = self._get_engine()
        query = self.config["query"]
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        return df

    def _write(self, df):
        engine = self._get_engine()
        table = self.config["table"]
        if not table:
            raise ValueError("Missing required config key: 'table'")
        write_options = self.config.get("write_options", {})
        df.to_sql(table, engine, index=False, if_exists=write_options.get("if_exists", "replace"))

    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        self.write(sample_df)
        print(f"Sample table written to PostgreSQL: {self.config['table']}")
        return sample_df
