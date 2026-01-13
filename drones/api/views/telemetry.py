from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from drones.models import Drone, DroneTelemetryPoint


@extend_schema(
    tags=["Telemetry"],
    summary="Get drone flight path as GeoJSON by serial",
    parameters=[
        OpenApiParameter(
            name="serial",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
            description="Drone serial number.",
        )
    ],
    responses={
        200: OpenApiResponse(description="GeoJSON Feature(LineString)"),
        404: OpenApiResponse(description="Drone not found"),
    },
)
class DronePathGeoJSONView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, serial: str):
        drone = get_object_or_404(Drone, serial=serial)
        points = DroneTelemetryPoint.objects.filter(drone=drone).order_by("timestamp")

        coordinates = [[p.longitude, p.latitude] for p in points]

        geojson = {
            "type": "Feature",
            "properties": {"serial": drone.serial, "points": len(coordinates)},
            "geometry": {"type": "LineString", "coordinates": coordinates},
        }
        return Response(geojson)
