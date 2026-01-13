from django.utils import timezone
from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from drones.models import Drone
from drones.serializers import DroneSerializer, QueryNearbySerializer, DroneOSDResponseSerializer
from drones.services.geo import haversine_km
from drones.services.online import is_online
from drones.permissions import CanMarkDroneSafe


@extend_schema(
    tags=["Drones"],
    summary="List drones (optionally filter by serial substring)",
    parameters=[
        OpenApiParameter(
            name="serial",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter drones where serial contains this substring (case-insensitive).",
            examples=[
                OpenApiExample("", value=""),
                OpenApiExample("DRONE", value="DRONE"),
                OpenApiExample("DR1234", value="DR1234"),
                OpenApiExample("DD123", value="DD123"),
                OpenApiExample("DRR11", value="DRR11"),
                OpenApiExample("DDR22", value="DDR22")
            ],
        )
    ],
    responses={200: DroneSerializer(many=True)},
)
class DroneListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        serial_q = (request.query_params.get("serial") or "").strip()
        qs = Drone.objects.all().order_by("serial")
        if serial_q:
            qs = qs.filter(serial__icontains=serial_q)
        return Response(DroneSerializer(qs, many=True).data)


@extend_schema(
    tags=["Drones"],
    summary="List online drones with their current location",
    description="A drone is considered online if last_seen_at is within ONLINE_WINDOW_SECONDS.",
    responses={200: DroneSerializer(many=True)},
)
class OnlineDronesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        window = settings.ONLINE_WINDOW_SECONDS
        cutoff = timezone.now() - timezone.timedelta(seconds=window)

        qs = (
            Drone.objects
            .filter(last_seen_at__gte=cutoff)
            .exclude(latitude__isnull=True)
            .exclude(longitude__isnull=True)
            .order_by("serial")
        )
        return Response(DroneSerializer(qs, many=True).data)


@extend_schema(
    tags=["Drones"],
    summary="List drones within 5km of a point (lat, lon)",
    parameters=[
        OpenApiParameter(
            name="lat",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Latitude of the reference point.",
            examples=[OpenApiExample("Example", value=31.97836)],
        ),
        OpenApiParameter(
            name="lon",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Longitude of the reference point.",
            examples=[OpenApiExample("Example", value=35.83092)],
        ),
    ],
    responses={
        200: DroneSerializer(many=True),
        400: OpenApiResponse(description="Validation error (lat/lon missing or invalid)."),
    },
)
class NearbyDronesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        s = QueryNearbySerializer(data=request.query_params)
        s.is_valid(raise_exception=True)

        lat = s.validated_data["lat"]
        lon = s.validated_data["lon"]
        radius_km = float(settings.NEARBY_RADIUS_KM)

        candidates = Drone.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)

        result = []
        for d in candidates:
            dist = haversine_km(lat, lon, float(d.latitude), float(d.longitude))
            if dist <= radius_km:
                result.append(d)

        return Response(DroneSerializer(result, many=True).data)


@extend_schema(
    tags=["Drones"],
    summary="List dangerous drones with reasons",
    description="A drone is dangerous if any dangerous rule matched (height/speed/geofence...).",
    responses={200: DroneSerializer(many=True)},
)
class DangerousDronesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Drone.objects.filter(is_dangerous=True).order_by("serial")
        return Response(DroneSerializer(qs, many=True).data)


@extend_schema(
    tags=["Drones"],
    summary="Get drone OSD payload by serial",
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
        200: DroneOSDResponseSerializer,
        404: OpenApiResponse(description="Drone not found"),
    },
)
class DroneOSDView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, serial: str):
        drone = get_object_or_404(Drone, serial=serial)
        return Response(
            {
                "serial": drone.serial,
                "last_seen_at": drone.last_seen_at,
                "osd": drone.last_payload,
            }
        )


@extend_schema(
    tags=["Drones"],
    summary="Mark a drone as safe (RBAC protected)",
    request=None,
    responses={
        200: OpenApiResponse(description="Drone marked safe"),
        401: OpenApiResponse(description="Authentication required"),
        403: OpenApiResponse(description="Missing permission (mark_safe)"),
        404: OpenApiResponse(description="Drone not found"),
    },
)
class MarkDroneSafeView(APIView):
    permission_classes = [IsAuthenticated, CanMarkDroneSafe]

    def post(self, request, serial: str):
        drone = get_object_or_404(Drone, serial=serial)
        drone.is_dangerous = False
        drone.danger_reasons = []
        drone.save(update_fields=["is_dangerous", "danger_reasons", "updated_at"])
        return Response({"status": "ok", "serial": drone.serial})
