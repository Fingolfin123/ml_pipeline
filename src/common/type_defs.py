from enum import Enum

from src.common.sources.csv_source import CSVSource
from src.common.sources.json_source import JSONSource
from src.common.sources.joblib_source import JoblibSource
from src.common.sources.pickle_source import PickleSource
# from common.sources.sql_source import SQLSource
# from common.sources.api_source import APISource
# from common.sources.s3_source import S3Source


class SourceClassMap(Enum):
    CSV = ("csv", CSVSource)
    JSON = ("json", JSONSource)
    JOBLIB = ("joblib", JoblibSource)
    PICKLE = ("pkl", PickleSource)

    def __init__(self, ext, cls):
        self.ext = ext
        self.cls = cls

    @classmethod
    def from_extension(cls, ext: str):
        """Return enum member based on file extension."""
        ext = ext.lower()
        for member in cls:
            if member.ext == ext:
                return member
        raise ValueError(f"Unsupported file extension: {ext}")

