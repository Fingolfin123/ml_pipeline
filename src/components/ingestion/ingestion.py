from common.sources.csv_source import CSVSource
from common.sources.json_source import JSONSource
from common.sources.sql_source import SQLSource
from common.sources.api_source import APISource
from common.sources.s3_source import S3Source

SOURCE_CLASS_MAP = {
    "csv": CSVSource,
    "json": JSONSource,
    "sql": SQLSource,
    "api": APISource,
    "s3": S3Source,
}

class IngestionManager:
    def __init__(self, source_type: str, source_config: dict, spark):
        self.source_type = source_type
        self.source_config = source_config
        self.spark = spark

    def run(self):
        if self.source_type not in SOURCE_CLASS_MAP:
            raise ValueError(f"Unsupported source type: {self.source_type}")
        source_class = SOURCE_CLASS_MAP[self.source_type]
        source = source_class(self.source_config, self.spark)
        return source.load()
