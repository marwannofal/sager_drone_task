from typing import Optional
from drones.services.geo import haversine_km
from drones.models import NoFlyZone
from drones.services.danger import DroneState

class GeofenceRule:
    """
    Strategy rule: dangerous if inside any active no-fly zone.
    """
    def check(self, state: DroneState) -> Optional[str]:
        return None


def check_geofence(lat: float, lon: float) -> Optional[str]:
    zones = NoFlyZone.objects.filter(is_active=True)
    for z in zones:
        dist = haversine_km(lat, lon, z.center_lat, z.center_lon)
        if dist <= z.radius_km:
            return f"inside no-fly zone: {z.name}"
    return None
