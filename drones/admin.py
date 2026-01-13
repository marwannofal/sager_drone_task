from django.contrib import admin
from .models import Drone, DroneTelemetryPoint, NoFlyZone

@admin.register(Drone)
class DroneAdmin(admin.ModelAdmin):
    list_display = ("serial", "last_seen_at", "latitude", "longitude", "is_dangerous")
    search_fields = ("serial",)
    list_filter = ("is_dangerous",)

@admin.register(DroneTelemetryPoint)
class DroneTelemetryPointAdmin(admin.ModelAdmin):
    list_display = ("drone", "timestamp", "latitude", "longitude")
    search_fields = ("drone__serial",)
    list_filter = ("timestamp",)


@admin.register(NoFlyZone)
class NoFlyZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "center_lat", "center_lon", "radius_km", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)