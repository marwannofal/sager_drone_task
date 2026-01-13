# Sager Drone Task — Backend (Django + MQTT)

Backend service for tracking drones, ingesting live telemetry over **MQTT**, detecting **dangerous** drones (rules + geofence),
and exposing a **REST API** documented with **Swagger UI**.

---

## Stack

- **Django 6** + **Django REST Framework**
- **OpenAPI / Swagger UI**: `drf-spectacular`
- **JWT auth**: `djangorestframework-simplejwt`
- **PostgreSQL** (Docker)
- **MQTT broker**: Eclipse Mosquitto (Docker)
- **MQTT consumer**: Paho MQTT (Django management command)
- **Fixtures**: preload zones + drones + telemetry

---

## Project layout (high level)

- `sager_drone_task/` — Django project
- `drones/` — core app
  - `models.py` — `Drone`, `DroneTelemetryPoint`, `NoFlyZone`
  - `api/` — API endpoints (views/serializers/urls)
  - `management/commands/` — `mqtt_consumer`, `bootstrap_demo`, …

---

## Run with Docker Compose (recommended)

### 1) Requirements

- Docker + Docker Compose

### 2) Start everything

```bash
docker compose up --build
```

Services:

- `db` (Postgres): `localhost:5432`
- `mqtt` (Mosquitto): `localhost:1884` → container `1883`
- `web` (Django): `localhost:8001`
- `consumer` (MQTT ingestion worker)

### 3) Open the API docs

Swagger UI is hosted at the root:

- **Swagger UI:** `http://127.0.0.1:8001/`
- **OpenAPI schema (JSON):** `http://127.0.0.1:8001/api/schema/`

---

## Authentication (JWT)

JWT endpoints:

- `POST /api/token/` — get access/refresh tokens
- `POST /api/token/refresh/` — refresh access token

Example:

```bash
curl -s -X POST http://127.0.0.1:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin1","password":"Aa@123456"}'
```

> Demo users/groups are created by the `bootstrap_demo` command (see “Fixtures & demo data”).

---

## Fixtures & demo data

The project includes fixtures under `drones/fixtures/`.

Typical load order:

```bash
python manage.py migrate
python manage.py loaddata drones/fixtures/002_zones.json
python manage.py loaddata drones/fixtures/003_drones.json
python manage.py loaddata drones/fixtures/004_telemetry.json
python manage.py bootstrap_demo
```

If you run via Docker Compose, you can run these inside the `web` container:

```bash
docker compose exec web python manage.py loaddata drones/fixtures/002_zones.json
docker compose exec web python manage.py loaddata drones/fixtures/003_drones.json
docker compose exec web python manage.py loaddata drones/fixtures/004_telemetry.json
docker compose exec web python manage.py bootstrap_demo
```

---

## Sending telemetry via MQTT (publish to the topic)

The consumer listens for telemetry messages on topics shaped like:

```
thing/product/<SERIAL>/osd
```

Example topic for a drone with serial `DRONE-OK-001`:

```
thing/product/DRONE-OK-001/osd
```

### Option A — publish from your host (uses the mapped port `1884`)

If you have `mosquitto_pub` installed locally:

```bash
mosquitto_pub -h 127.0.0.1 -p 1884 \
  -t "thing/product/DRONE-OK-001/osd" \
  -m '{"latitude":31.97836,"longitude":35.83092,"height":120,"horizontal_speed":4.2}'
```

### Option B — publish from inside the MQTT container (no local install needed)

```bash
docker compose exec mqtt sh -lc '
  mosquitto_pub -h localhost -p 1883     -t "thing/product/DRONE-OK-001/osd"     -m "{"latitude":31.97836,"longitude":35.83092,"height":120,"horizontal_speed":4.2}"
'
```

### What happens after publishing?

- The `consumer` parses the message, updates the `Drone` current state, and appends a `DroneTelemetryPoint` (when lat/lon exists).
- Danger reasons are calculated from:
  - rule-based thresholds (height/speed), and
  - geofence check (entering an active no-fly zone).

Then you can verify:

- `GET /api/drones`
- `GET /api/drones/online`
- `GET /api/drones/dangerous`
- `GET /api/drones/{serial}/path` (GeoJSON line string)

---

## Troubleshooting

### “connection refused” to Postgres (web/consumer starts too early)
Sometimes Django starts before Postgres finishes booting.

Quick fix:

```bash
docker compose down
docker compose up --build
```

More robust fix: add a healthcheck to Postgres + use `depends_on: condition: service_healthy` (Compose v2).

### Port already in use (8000/8001)
If you see something like “failed to bind host port … address already in use”:

- change the host port mapping in `docker-compose.yml`:
  - e.g. `"8002:8000"`

### Consumer is not ingesting messages
- Make sure `consumer` container is running:
  ```bash
  docker compose ps
  ```
- Verify the publish topic matches:
  - `thing/product/<SERIAL>/osd`

---

## Architecture

This project follows a **layered (n-tier) Django REST architecture** with a small **service layer** and a separate **MQTT consumer worker**:

- **API layer (Views/Controllers):** `drones/api/views/*`
- **Serialization & validation:** `drones/serializers.py`
- **Domain/Data layer:** `drones/models.py`
- **Business logic (Service layer):** `drones/services/*` (danger rules, geofence checks, geo utils, online window)
- **Infrastructure / Worker:** `drones/management/commands/mqtt_consumer.py` (MQTT ingestion and persistence)

This separation keeps endpoints thin, moves reusable business rules into services, and isolates MQTT ingestion from the HTTP API.


## Notes

- This repository is built as a technical task for SAGER DRONE COMPANY.

