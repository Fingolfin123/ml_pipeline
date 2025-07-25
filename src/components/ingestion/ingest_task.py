from prefect import task
from ingestion.ingestion import IngestionManager
from pyspark.sql import SparkSession

@task
def run_ingestion(config: dict):
    spark = SparkSession.builder.appName("IngestionTask").getOrCreate()
    manager = IngestionManager(
        source_type=config["source_type"],
        source_config=config["source_config"],
        spark=spark
    )
    return manager.run()
