from django.db import models
from django.utils import timezone

# Create your models here.

class Drone(models.Model):
    serial = models.CharField(max_length=128, unique=True, db_index=True)

    # current state
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    horizontal_speed = models.FloatField(null=True, blank=True)

    # tracking
    last_seen_at = models.DateTimeField(null=True, blank=True)

    last_payload = models.JSONField(default=dict, blank=True)

    # dangerous classification
    is_dangerous = models.BooleanField(default=False)
    danger_reasons = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.serial

    class Meta:
        permissions = [
            ("mark_safe", "Can mark drone as safe"),
        ]



class DroneTelemetryPoint(models.Model):
    drone = models.ForeignKey(Drone, on_delete=models.CASCADE, related_name="telemetry_points")

    timestamp = models.DateTimeField(db_index=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    height = models.FloatField(null=True, blank=True)
    horizontal_speed = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["drone", "timestamp"]),
        ]
        ordering = ["timestamp"]

    def __str__(self) -> str:
        return f"{self.drone.serial} @ {self.timestamp.isoformat()}"


# Geofencing as circular no-fly zones
class NoFlyZone(models.Model):
    SHAPE_CIRCLE = "circle"
    SHAPE_POLYGON = "polygon"
    SHAPE_CHOICES = [
        (SHAPE_CIRCLE, "Circle"),
        (SHAPE_POLYGON, "Polygon"),
    ]

    name = models.CharField(max_length=128)
    shape = models.CharField(max_length=16, choices=SHAPE_CHOICES, default=SHAPE_CIRCLE)

    # Circle fields (used when shape == "circle")
    center_lat = models.FloatField(null=True, blank=True)
    center_lon = models.FloatField(null=True, blank=True)
    radius_km = models.FloatField(null=True, blank=True)

    # Polygon fields (used when shape == "polygon")
    # Stored as list of [lon, lat] pairs (GeoJSON style)
    polygon = models.JSONField(default=list, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        permissions = [
            ("modify_settings", "Can modify geofence settings"),
        ]

    def __str__(self) -> str:
        if self.shape == self.SHAPE_CIRCLE:
            return f"{self.name} (circle)"
        return f"{self.name} (polygon)"