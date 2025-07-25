import requests
import tempfile
from common.sources.datasource_base import DataSource

class APISource(DataSource):
    def load(self):
        url = self.config["url"]
        headers = self.config.get("headers", {})
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Save API response to temp file
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp:
            tmp.write(response.text)
            tmp_path = tmp.name

        return self.spark.read.json(tmp_path)