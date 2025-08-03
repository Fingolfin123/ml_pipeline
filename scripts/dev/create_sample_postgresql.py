from src.common.sources.dev.postgresql_source import PostgreSQLSource

# Configuration for PostgreSQLSource
config = {
    "user": "your_user",
    "password": "your_password",
    "host": "localhost",
    "port": 5432,
    "database": "your_database",
    "table": "sample_table",
    "write_options": {
        "if_exists": "replace",
        "index": False,
    },
}

# Instantiate and generate/write sample
source = PostgreSQLSource(config)
df = source.generate_sample_table()

print(df)
