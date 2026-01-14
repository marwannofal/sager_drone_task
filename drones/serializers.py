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
            "shape",
            "center_lat", "center_lon", "radius_km",
            "polygon",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        shape = attrs.get("shape", getattr(instance, "shape", NoFlyZone.SHAPE_CIRCLE))

        center_lat = attrs.get("center_lat", getattr(instance, "center_lat", None))
        center_lon = attrs.get("center_lon", getattr(instance, "center_lon", None))
        radius_km = attrs.get("radius_km", getattr(instance, "radius_km", None))
        polygon = attrs.get("polygon", getattr(instance, "polygon", []))

        if shape == NoFlyZone.SHAPE_CIRCLE:
            if center_lat is None or center_lon is None or radius_km is None:
                raise serializers.ValidationError(
                    "Circle zones require center_lat, center_lon, and radius_km."
                )
            if radius_km <= 0:
                raise serializers.ValidationError("radius_km must be > 0.")
            if polygon:
                raise serializers.ValidationError("Circle zones must not include polygon points.")

        elif shape == NoFlyZone.SHAPE_POLYGON:
            if not isinstance(polygon, list) or len(polygon) < 3:
                raise serializers.ValidationError(
                    "Polygon zones require polygon with at least 3 points."
                )
            for i, pt in enumerate(polygon):
                if (
                    not isinstance(pt, (list, tuple))
                    or len(pt) != 2
                    or not isinstance(pt[0], (int, float))
                    or not isinstance(pt[1], (int, float))
                ):
                    raise serializers.ValidationError(
                        f"polygon[{i}] must be [lon, lat] numbers."
                    )
                lon, lat = float(pt[0]), float(pt[1])
                if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
                    raise serializers.ValidationError(
                        f"polygon[{i}] lon/lat out of range."
                    )

            if center_lat is not None or center_lon is not None or radius_km is not None:
                raise serializers.ValidationError(
                    "Polygon zones must not include center_lat/center_lon/radius_km."
                )
        else:
            raise serializers.ValidationError("Invalid shape. Use 'circle' or 'polygon'.")

        return attrs