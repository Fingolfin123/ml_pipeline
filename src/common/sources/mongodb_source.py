import pandas as pd
from pymongo import MongoClient
from src.common.sources.base_source import DataSource

class MongoDBSource(DataSource):
    def load(self):
        uri = self.config["uri"]  # e.g. "mongodb://user:pass@host:port/db"
        database = self.config["database"]
        collection = self.config["collection"]
        query = self.config.get("query", {})  # MongoDB find query filter
        projection = self.config.get("projection")  # Optional fields to include/exclude

        client = MongoClient(uri)
        db = client[database]
        coll = db[collection]

        cursor = coll.find(query, projection)
        data = list(cursor)
        if not data:
            return pd.DataFrame()  # empty df if no results
        df = pd.DataFrame(data)
        # Drop MongoDB _id field if present
        if "_id" in df.columns:
            df = df.drop(columns=["_id"])
        return df

    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        print("MongoDB source does not support writing sample data.")
        return sample_df
