from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from drones.models import NoFlyZone
from drones.serializers import NoFlyZoneSerializer
from drones.permissions import CanModifySettings


@extend_schema(
    tags=["Geofencing"],
    summary="List no-fly zones",
    responses={200: NoFlyZoneSerializer(many=True), 401: OpenApiResponse(description="Auth required"), 403: OpenApiResponse(description="Missing permission")},
)
class NoFlyZoneListCreateView(APIView):
    permission_classes = [IsAuthenticated, CanModifySettings]

    def get(self, request):
        qs = NoFlyZone.objects.all().order_by("name")
        return Response(NoFlyZoneSerializer(qs, many=True).data)

    @extend_schema(
        summary="Create a no-fly zone",
        request=NoFlyZoneSerializer,
        responses={201: NoFlyZoneSerializer, 400: OpenApiResponse(description="Validation error")},
    )
    def post(self, request):
        s = NoFlyZoneSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        zone = s.save()
        return Response(NoFlyZoneSerializer(zone).data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Geofencing"],
    summary="Update or delete a no-fly zone",
    request=NoFlyZoneSerializer,
    parameters=[
        OpenApiParameter(
            name="zone_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
            description="No-fly zone id.",
        )
    ],
    responses={
        200: NoFlyZoneSerializer,
        204: OpenApiResponse(description="Deleted"),
        401: OpenApiResponse(description="Auth required"),
        403: OpenApiResponse(description="Missing permission"),
        404: OpenApiResponse(description="Zone not found"),
    },
)
class NoFlyZoneDetailView(APIView):
    permission_classes = [IsAuthenticated, CanModifySettings]

    def patch(self, request, zone_id: int):
        zone = get_object_or_404(NoFlyZone, id=zone_id)
        s = NoFlyZoneSerializer(zone, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        zone = s.save()
        return Response(NoFlyZoneSerializer(zone).data)

    def delete(self, request, zone_id: int):
        zone = get_object_or_404(NoFlyZone, id=zone_id)
        zone.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
