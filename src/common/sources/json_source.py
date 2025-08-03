import pandas as pd
from src.common.sources.base_source import DataSource


class JSONSource(DataSource):
    def __init__(self, config: dict = None):
        # Default configuration
        default_config = {
            "path": None,
            "options": {"orient": "records"},
            "lines": False,
        }
        # Merge defaults with user config (if provided)
        self.config = {**default_config, **(config or {})}

    def _read(self, path: str):
        # Ensure config is at least an empty dict
        config = self.config or {}

        # If no path passed, use config's path
        path = path or config.get("path")
        if path is None:
            raise ValueError(
                "Path must be provided either in method argument or config."
            )

        # Get options safely
        options = config.get("options", {})
        lines = config.get("lines", False)

        return pd.read_json(path, lines=lines, **options)

    def _write(self, df, path: str):
        # Ensure config is at least an empty dict
        config = self.config or {}
        options = config.get("write_options", {}).copy()
        lines = config.get("lines", False)
        # Use orient from options if present, else default
        orient = options.get("orient", "records")
        # Remove orient from options dict so it isn't duplicated
        options.pop("orient", None)
        # Remove index if invalid for orient
        if orient not in ["split", "table"]:
            options.pop("index", None)

        # Pass orient explicitly once, and unpack other options
        df.to_json(path, orient=orient, lines=lines, **options)

    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        self.write(sample_df)
        return sample_df
