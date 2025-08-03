from src.common.type_defs import SourceClassMap


class DataSourceIO:
    # def __init__(self, source_enum: SourceClassMap, source_config: dict):

    #     self.source_enum = source_enum
    #     self.source_config = source_config

    #     # Initialize the source class object
    #     self.source_class = self.source_enum.cls
    #     self.source = self.source_class(self.source_config)

    def set_source_from_config(self, source_enum: SourceClassMap, source_config: dict):
        """
        Initializes the ingestion source.

        Args:
            source_enum: Enum value from SourceClassMap
            source_config: Dictionary of configuration for the source
        """
        source_enum = source_enum
        source_config = source_config

        # Initialize the source class object
        source_class = source_enum.cls
        source = source_class(source_config)
        return source

    def set_source_from_path(self, path: str):
        """
        Initializes the ingestion source.

        Args:
            path
        """
        # Initialize the source class object
        source_enum = SourceClassMap.from_path(path)
        source_class = source_enum.cls
        source = source_class()
        return source

    def read_flat_file(self, path: str):
        """
        Initializes the ingestion source.

        Args:
            path: path of flat file
        """
        source = self.set_source_from_path(path)
        df = source.read_flat_file(path)
        return df

    def write_flat_file(self, df, path: str):
        """
        Initializes the ingestion source.

        Args:
            df: pandas dataframe
            source_enum: Enum value from SourceClassMap
        """
        source = self.set_source_from_path(path)
        source.write_flat_file(df, path)
