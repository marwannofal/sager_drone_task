from typing import List, Optional, Sequence

from drones.models import NoFlyZone
from drones.services.geo import haversine_km


def _point_in_polygon(lon: float, lat: float, polygon: Sequence[Sequence[float]]) -> bool:
    """
    Ray-casting algorithm.
    polygon: list of [lon, lat] points (GeoJSON style). It may be open or closed.
    """
    if len(polygon) < 3:
        return False

    # Normalize to list of tuples
    pts = [(float(p[0]), float(p[1])) for p in polygon]

    if pts[0] != pts[-1]:
        pts.append(pts[0])

    inside = False
    x, y = lon, lat

    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]

        # Check if point is between y1 and y2 in vertical sense
        intersects = ((y1 > y) != (y2 > y))
        if intersects:
            # Compute intersection x coordinate of edge with horizontal ray at y
            # Avoid division by zero: y2 != y1 guaranteed by intersects condition
            x_intersect = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
            if x_intersect > x:
                inside = not inside

    return inside


def check_geofence(lat: float, lon: float) -> Optional[str]:
    """
    Returns a string reason if drone is inside any active zone, else None.

    Keeps the original reason string used in your fixtures:
    - "entered_no_fly_zone"
    """
    zones = NoFlyZone.objects.filter(is_active=True)

    for z in zones:
        if z.shape == NoFlyZone.SHAPE_CIRCLE:
            if z.center_lat is None or z.center_lon is None or z.radius_km is None:
                continue
            dist = haversine_km(lat, lon, float(z.center_lat), float(z.center_lon))
            if dist <= float(z.radius_km):
                return "entered_no_fly_zone"

        elif z.shape == NoFlyZone.SHAPE_POLYGON:
            poly = z.polygon or []
            if _point_in_polygon(lon, lat, poly):
                return "entered_no_fly_zone"

    return None
