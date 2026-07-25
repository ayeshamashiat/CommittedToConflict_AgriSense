"""Real, live-fetched agri-input shop locations via OpenStreetMap's Overpass
API — free, no API key required.

Searches for nodes tagged shop=agrarian or shop=farm (the standard OSM tags
for agricultural-supply retailers) within a radius of a given point. Returns
real shop names and real coordinates when OSM has them mapped — verified
live for Sylhet, e.g. returns "Kazi Farm", "Tea Distributor" (shop=agrarian)
as real, currently-mapped results.

What this can and can't give us, stated plainly: OSM has no concept of
per-shop pricing, delivery time, or customer ratings for these small
informal retailers — nothing publicly available anywhere does. So this
module only ever returns real identity + real location; marketplace_tool.py
is responsible for clearly labeling the price/delivery/rating fields it
fills in around a real result as estimates, not real data.

OSM's tagging coverage for small rural shops in Bangladesh is often sparse —
a query returning zero results for a given area is an expected, honest
outcome, not a bug. Any failure (timeout, network error, malformed
response) is caught and treated the same as "no results" rather than
raised, so a flaky third-party API never breaks the farmer's marketplace
lookup — see the fallback path in marketplace_tool.py.

Multiple public Overpass mirrors, tried in order: the flagship
overpass-api.de instance is well known to be unreliable/rate-limited under
real-world use (confirmed live while building this — the same request got a
406 from Apache one moment and a 504 timeout the next, from curl directly,
nothing to do with this code). overpass.kumi.systems responded reliably in
testing and is tried first; overpass-api.de is kept as a second attempt
rather than removed outright, since which mirror is having a bad day varies.
"""

import logging

import httpx

logger = logging.getLogger(__name__)

_OVERPASS_URLS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]
_TIMEOUT_SECONDS = 12.0
_SEARCH_RADIUS_M = 50_000  # 50km — wide enough to have a real chance of a hit given sparse rural tagging


def search_agrarian_shops(lat: float, lon: float, limit: int = 6) -> list[dict]:
    """Returns up to `limit` real shops as
    [{"name": str, "lat": float, "lon": float}, ...], nearest first is NOT
    guaranteed (caller re-sorts by real distance) — empty list on no results
    or if every mirror fails, never raises."""
    query = f"""
    [out:json][timeout:10];
    (
      node["shop"="agrarian"](around:{_SEARCH_RADIUS_M},{lat},{lon});
      node["shop"="farm"](around:{_SEARCH_RADIUS_M},{lat},{lon});
    );
    out body {limit * 3};
    """
    data = None
    for url in _OVERPASS_URLS:
        try:
            with httpx.Client(timeout=_TIMEOUT_SECONDS) as client:
                resp = client.post(url, data={"data": query})
                resp.raise_for_status()
                data = resp.json()
            break
        except Exception:
            logger.warning("OpenStreetMap Overpass mirror %s failed, trying next", url, exc_info=True)
            continue

    if data is None:
        logger.warning("All OpenStreetMap Overpass mirrors failed; caller will fall back to the mock catalog")
        return []

    shops = []
    for element in data.get("elements", []):
        name = (element.get("tags") or {}).get("name")
        el_lat, el_lon = element.get("lat"), element.get("lon")
        if not name or el_lat is None or el_lon is None:
            continue
        shops.append({"name": name, "lat": el_lat, "lon": el_lon})
        if len(shops) >= limit:
            break
    return shops
