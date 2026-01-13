import math

def haversine_km(lat1: float, lon12: float, lat2: float, lon2: float) -> float:
    """
    Great-circle distance between two points (lat/lon in degrees).
    Returns kilometers.
    """
    # Earth radius in kilometers
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon12)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c