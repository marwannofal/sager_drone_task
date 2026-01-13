from rest_framework import serializers
from drones.models import Drone, NoFlyZone


class DroneSerializer(serializers.ModelSerializer):
    """
    Represents a drone basic state snapshot.
    Used by list/online/nearby/dangerous endpoints.
    """

    class Meta:
        model = Drone
        fields = [
            "serial",
            "latitude",
            "longitude",
            "height",
            "horizontal_speed",
            "last_seen_at",
            "is_dangerous",
            "danger_reasons",
        ]


class QueryNearbySerializer(serializers.Serializer):
    """
    Query params for nearby endpoint:
    /api/drones/nearby?lat=..&lon=..
    """
    lat = serializers.FloatField(help_text="Latitude (-90..90)")
    lon = serializers.FloatField(help_text="Longitude (-180..180)")

    def validate_lat(self, value: float) -> float:
        if value < -90 or value > 90:
            raise serializers.ValidationError("lat must be between -90 and 90")
        return value

    def validate_lon(self, value: float) -> float:
        if value < -180 or value > 180:
            raise serializers.ValidationError("lon must be between -180 and 180")
        return value


class DroneOSDResponseSerializer(serializers.Serializer):
    """
    Response schema for:
    GET /api/drones/{serial}/osd
    """
    serial = serializers.CharField()
    last_seen_at = serializers.DateTimeField(allow_null=True)
    osd = serializers.JSONField(help_text="Raw OSD payload published by the drone.")


class NoFlyZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoFlyZone
        fields = [
            "id",
            "name",
            "center_lat",
            "center_lon",
            "radius_km",
            "is_active",
            "created_at",
        ]
