from abc import ABC, abstractmethod
from pyspark.sql import DataFrame

class DataSource(ABC):
    @abstractmethod
    def read(self) -> DataFrame:
        """Read data and return as a Spark DataFrame."""
        pass

    @abstractmethod
    def write(self, df: DataFrame):
        """Write a Spark DataFrame to the data source."""
        pass
    
    def generate_sample_table(self):
        """Default sample table creation using pandas. Override in subclasses for source-specific implementations."""
        sample_df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "score": [85.5, 92.0, 78.3]
        })
        return sample_df
    