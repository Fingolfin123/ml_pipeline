sample_config = {
    "csv_source": {
        "path": "/path/to/sample.csv",
        "options": {
            "header": True,
            "delimiter": ",",
            "encoding": "utf-8"
        }
    },
    "sql_source": {
        "connection_string": "postgresql+psycopg2://user:password@host:5432/database",
        "query": "SELECT * FROM table_name LIMIT 100"
    },
    "postgresql_source": {
        "user": "user",
        "password": "password",
        "host": "localhost",
        "port": 5432,
        "database": "database",
        "query": "SELECT * FROM table_name LIMIT 100"
    },
    "mysql_source": {
        "user": "user",
        "password": "password",
        "host": "localhost",
        "port": 3306,
        "database": "database",
        "query": "SELECT * FROM table_name LIMIT 100"
    },
    "bigquery_source": {
        "project_id": "your-gcp-project",
        "dataset": "your_dataset",
        "table": "your_table",
        "credentials_path": "/path/to/credentials.json",
        "query": "SELECT * FROM your_dataset.your_table LIMIT 100"
    },
    "gcs_source": {
        "bucket": "your-bucket-name",
        "key": "path/to/file.csv",
        "credentials_path": "/path/to/credentials.json",
        "file_type": "csv",
        "read_options": {
            "delimiter": ",",
            "header": 0
        }
    },
    "hdf5_source": {
        "file_path": "/path/to/file.h5",
        "key": "dataset_key"
    },
    "hdfs_source": {
        "namenode": "hdfs://namenode:9000",
        "file_path": "/path/in/hdfs/file.csv",
        "user": "hdfs-user",
        "file_type": "csv",
        "read_options": {
            "delimiter": ",",
            "header": 0
        }
    },
    "json_source": {
        "path": "/path/to/file.json",
        "lines": True  # or False depending on JSON format
    },
    "kafka_source": {
        "bootstrap_servers": "localhost:9092",
        "topic": "your-topic",
        "group_id": "your-group",
        "auto_offset_reset": "earliest",
        "max_messages": 1000
    },
    "kinesis_source": {
        "stream_name": "your-stream-name",
        "region_name": "us-east-1",
        "max_records": 1000,
        "shard_iterator_type": "TRIM_HORIZON"
    },
    "mongodb_source": {
        "uri": "mongodb://user:password@host:27017",
        "database": "your_db",
        "collection": "your_collection",
        "query": {}
    },
    "pickle_source": {
        "file_path": "/path/to/file.pkl"
    },
    "redis_source": {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": None,
        "pattern": "*",
        "decode_responses": True
    },
    "s3_source": {
        "bucket": "your-bucket",
        "key": "path/to/file.csv",
        "aws_access_key_id": "YOUR_ACCESS_KEY",
        "aws_secret_access_key": "YOUR_SECRET_KEY",
        "region_name": "us-west-2",
        "file_type": "csv",
        "read_options": {
            "delimiter": ",",
            "header": 0
        }
    },
    "snowflake_source": {
        "user": "YOUR_USER",
        "password": "YOUR_PASSWORD",
        "account": "YOUR_ACCOUNT",
        "warehouse": "YOUR_WAREHOUSE",
        "database": "YOUR_DATABASE",
        "schema": "PUBLIC",
        "query": "SELECT * FROM MY_TABLE LIMIT 100"
    }
}
