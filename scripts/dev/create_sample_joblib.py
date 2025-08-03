from src.common.utils import get_project_path
from src.common.sources.joblib_source import JoblibSource  # assuming you saved it here

# Configuration for JoblibSource
config = {
    "path": str(get_project_path("data", "sample.joblib")),
    "compress": 3,  # Optional: use zlib compression level 3
    "protocol": None,  # Use default highest protocol
}

# Instantiate and generate/write sample
source = JoblibSource(config)
df = source.generate_sample_table()

print(df)
