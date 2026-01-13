# drones/urls.py
from django.urls import path
from drones.api.views import (
    DroneListView,
    OnlineDronesView,
    NearbyDronesView,
    DangerousDronesView,
    DroneOSDView,
    DronePathGeoJSONView,
    MarkDroneSafeView,
    NoFlyZoneListCreateView,
    NoFlyZoneDetailView,
)

urlpatterns = [
    path("drones", DroneListView.as_view()),
    path("drones/online", OnlineDronesView.as_view()),
    path("drones/nearby", NearbyDronesView.as_view()),
    path("drones/dangerous", DangerousDronesView.as_view()),
    path("drones/<str:serial>/osd", DroneOSDView.as_view()),
    path("drones/<str:serial>/path", DronePathGeoJSONView.as_view()),
    path("drones/<str:serial>/mark-safe", MarkDroneSafeView.as_view()),

    path("zones", NoFlyZoneListCreateView.as_view()),
    path("zones/<int:zone_id>", NoFlyZoneDetailView.as_view()),
]
