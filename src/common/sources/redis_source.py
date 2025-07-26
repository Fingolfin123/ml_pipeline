import json
import pandas as pd
import redis
from src.common.sources.base_source import DataSource

class RedisSource(DataSource):
    def load(self):
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 6379)
        db = self.config.get("db", 0)
        password = self.config.get("password", None)
        pattern = self.config.get("pattern", "*")  # Key pattern to fetch
        decode_responses = self.config.get("decode_responses", True)  # decode bytes to str

        client = redis.Redis(host=host, port=port, db=db, password=password, decode_responses=decode_responses)

        keys = client.keys(pattern)
        records = []

        for key in keys:
            val = client.get(key)
            try:
                # Attempt to parse JSON string to dict
                data = json.loads(val)
                records.append(data)
            except (json.JSONDecodeError, TypeError):
                # Fallback: treat as raw string value
                records.append({"key": key, "value": val})

        df = pd.DataFrame(records)
        return df

    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        print("Redis source does not support writing sample data.")
        return sample_df
