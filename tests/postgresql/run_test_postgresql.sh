#!/bin/bash

set -e  # stop on first error

echo "🛠️  Starting PostgreSQL via Docker..."
docker compose -f docker/postgres/docker-compose.yml up -d

echo "⏳ Waiting for PostgreSQL to start..."
sleep 5  # adjust if needed

echo "🧪 Running tests..."
poetry run pytest tests/postgresql/test_datasource_io.py

echo "🧹 Shutting down Docker container..."
docker compose -f docker/postgres/docker-compose.yml down

echo "✅ All done!"
