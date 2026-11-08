#!/bin/sh
set -e

echo "Applying database migrations..."
alembic upgrade head

echo "Starting application..."
exec uvicorn exchange.main:app --host "$APP_HOST" --port "$APP_PORT"
