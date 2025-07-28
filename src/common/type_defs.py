from enum import Enum

from src.common.sources.csv_source import CSVSource
from src.common.sources.json_source import JSONSource
from src.common.sources.joblib_source import JoblibSource
from src.common.sources.pickle_source import PickleSource
# from common.sources.sql_source import SQLSource
# from common.sources.api_source import APISource
# from common.sources.s3_source import S3Source

class SourceClassMap(Enum):
    CSV = CSVSource
    JSON = JSONSource
    JOBLIB = JoblibSource
    PICKLE = PickleSource
    # SQL = SQLSource
    # API = APISource
    # S3 = S3Source
    
class SourceClassExt(Enum):
    CSV = "csv"
    JSON = "json"
    JOBLIB = "joblib"
    PICKLE = "pkl"
    # SQL = SQLSource
    # API = APISource
    # S3 = S3Source
