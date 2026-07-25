"""Shared geo math — haversine (straight-line) distance between two
lat/lon points, used by marketplace_tool.py for both real OSM-sourced
supplier locations and the mock catalog's district-to-district distances."""

import math

_EARTH_RADIUS_KM = 6371.0


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return round(_EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(h)), 1)
