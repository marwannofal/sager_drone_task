import json
import re
import socket
import time
from typing import Any, Optional

import paho.mqtt.client as mqtt
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from drones.models import Drone, DroneTelemetryPoint
from drones.services.danger import DangerClassifier, DroneState, HeightRule, SpeedRule
from drones.services.geofence import check_geofence

TOPIC_RE = re.compile(r"^thing/product/(?P<serial>[^/]+)/osd$")


def safe_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


class Command(BaseCommand):
    help = "Run MQTT consumer to ingest drone telemetry"

    def handle(self, *args, **options):
        classifier = DangerClassifier(
            rules=[
                HeightRule(settings.DANGEROUS_HEIGHT_M),
                SpeedRule(settings.DANGEROUS_SPEED_MS),
            ]
        )

        # Paho 2.x: safer callback API usage
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        def on_connect(c, userdata, flags, rc, properties=None):
            if rc == 0:
                self.stdout.write(self.style.SUCCESS("Connected to MQTT broker"))
                c.subscribe(settings.MQTT_TOPIC)
                self.stdout.write(self.style.SUCCESS(f"Subscribed to {settings.MQTT_TOPIC}"))
            else:
                self.stdout.write(self.style.ERROR(f"MQTT connect failed with rc={rc}"))

        def on_message(c, userdata, msg):
            m = TOPIC_RE.match(msg.topic)
            if not m:
                return

            serial = m.group("serial")

            try:
                payload = json.loads(msg.payload.decode("utf-8"))
            except Exception:
                return  # ignore invalid JSON

            lat = safe_float(payload.get("latitude"))
            lon = safe_float(payload.get("longitude"))
            height = safe_float(payload.get("height"))
            hspeed = safe_float(payload.get("horizontal_speed"))

            now = timezone.now()

            reasons = classifier.classify(DroneState(height=height, horizontal_speed=hspeed))

            if lat is not None and lon is not None:
                geofence_reason = check_geofence(lat, lon)
                if geofence_reason:
                    reasons.append(geofence_reason)

            reasons = list(dict.fromkeys(reasons))
            is_dangerous = bool(reasons)

            with transaction.atomic():
                drone, _ = Drone.objects.get_or_create(
                    serial=serial,
                    defaults={"last_seen_at": now},
                )

                drone.latitude = lat
                drone.longitude = lon
                drone.height = height
                drone.horizontal_speed = hspeed
                drone.last_seen_at = now
                drone.is_dangerous = is_dangerous
                drone.danger_reasons = reasons
                drone.last_payload = payload

                drone.save(update_fields=[
                    "latitude", "longitude", "height", "horizontal_speed",
                    "last_seen_at", "is_dangerous", "danger_reasons",
                    "last_payload",
                    "updated_at",
                ])

                if lat is not None and lon is not None:
                    DroneTelemetryPoint.objects.create(
                        drone=drone,
                        timestamp=now,
                        latitude=lat,
                        longitude=lon,
                        height=height,
                        horizontal_speed=hspeed,
                    )

        def connect_with_retry(host: str, port: int, attempts: int = 30, sleep_s: float = 1.0):
            last_err: Exception | None = None
            for _ in range(attempts):
                try:
                    client.connect(host, port, keepalive=60)
                    return
                except (ConnectionRefusedError, OSError, socket.error) as e:
                    last_err = e
                    time.sleep(sleep_s)
            raise last_err or RuntimeError("MQTT connect failed")

        client.on_connect = on_connect
        client.on_message = on_message

        connect_with_retry(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT)
        client.loop_forever()
