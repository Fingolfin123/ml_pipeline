import boto3
import json
import pandas as pd
from src.common.sources.base_source import DataSource

class KinesisSource(DataSource):
    def load(self):
        stream_name = self.config["stream_name"]
        region_name = self.config.get("region_name", "us-east-1")
        shard_id = self.config.get("shard_id", "shardId-000000000000")
        limit = self.config.get("limit", 1000)  # max records to fetch

        client = boto3.client('kinesis', region_name=region_name)

        # Get shard iterator
        shard_iterator_response = client.get_shard_iterator(
            StreamName=stream_name,
            ShardId=shard_id,
            ShardIteratorType='TRIM_HORIZON'  # or 'LATEST', 'AT_SEQUENCE_NUMBER', etc.
        )
        shard_iterator = shard_iterator_response['ShardIterator']

        records = []
        while len(records) < limit and shard_iterator:
            response = client.get_records(ShardIterator=shard_iterator, Limit=limit - len(records))
            shard_iterator = response.get('NextShardIterator')
            for record in response['Records']:
                # Assuming JSON data encoded in base64
                data_str = record['Data'].decode('utf-8') if isinstance(record['Data'], bytes) else record['Data']
                try:
                    data_json = json.loads(data_str)
                    records.append(data_json)
                except json.JSONDecodeError:
                    # Skip or handle malformed record
                    continue
            if not response['Records']:
                break  # No more records

        df = pd.DataFrame(records)
        return df

    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        print("Kinesis source does not support writing sample data.")
        return sample_df
