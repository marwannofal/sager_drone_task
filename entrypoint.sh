#!/usr/bin/env bash
set -e

echo "Running migrations..."
python manage.py migrate

echo "Loading fixtures..."
python manage.py loaddata drones/fixtures/001_users_groups.json || true
python manage.py loaddata drones/fixtures/002_zones.json || true
python manage.py loaddata drones/fixtures/003_drones.json || true
python manage.py loaddata drones/fixtures/004_telemetry.json || true

echo "Bootstrapping demo users/groups..."
python manage.py bootstrap_demo || true

echo "Starting server..."
exec "$@"
