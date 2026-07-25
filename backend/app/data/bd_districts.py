"""District administrative-center coordinates for all 64 districts of
Bangladesh (public geographic fact, not sourced to a specific dataset the way
a price/yield figure is — same "real, static, not live-fetched" category as
the BRRI/BARI variety facts in knowledge_base.py).

Used by marketplace_tool.py to compute a real straight-line (haversine)
distance between a farmer's stated location and a supplier's district,
replacing what was previously a hardcoded per-supplier distance_km that
implicitly assumed every farmer was near Rangpur — correct-looking for a
Rangpur farmer, silently wrong for anyone else (e.g. showing "60km" for a
supplier that's actually ~350km away for a farmer in Sylhet).

Straight-line distance, not road distance — disclosed as such wherever it's
surfaced, consistent with this app's practice of never presenting an
estimate as more precise than it is.
"""

DISTRICT_COORDS: dict[str, tuple[float, float]] = {
    "bagerhat": (22.6602, 89.7895),
    "bandarban": (22.1953, 92.2184),
    "barguna": (22.0953, 90.1121),
    "barishal": (22.7010, 90.3535),
    "bhola": (22.6859, 90.6482),
    "bogura": (24.8465, 89.3773),
    "brahmanbaria": (23.9571, 91.1119),
    "chandpur": (23.2333, 90.6667),
    "chattogram": (22.3569, 91.7832),
    "chuadanga": (23.6402, 88.8410),
    "cox's bazar": (21.4272, 92.0058),
    "coxs bazar": (21.4272, 92.0058),
    "cumilla": (23.4607, 91.1809),
    "comilla": (23.4607, 91.1809),
    "dhaka": (23.8103, 90.4125),
    "dinajpur": (25.6279, 88.6332),
    "faridpur": (23.6070, 89.8429),
    "feni": (23.0159, 91.3976),
    "gaibandha": (25.3288, 89.5285),
    "gazipur": (23.9999, 90.4203),
    "gopalganj": (23.0050, 89.8266),
    "habiganj": (24.3745, 91.4155),
    "jamalpur": (24.9375, 89.9372),
    "jashore": (23.1667, 89.2167),
    "jessore": (23.1667, 89.2167),
    "jhalokati": (22.6406, 90.1987),
    "jhenaidah": (23.5450, 89.1539),
    "joypurhat": (25.0968, 89.0227),
    "khagrachari": (23.1193, 91.9847),
    "khulna": (22.8456, 89.5403),
    "kishoreganj": (24.4449, 90.7766),
    "kurigram": (25.8054, 89.6362),
    "kushtia": (23.9013, 89.1206),
    "lakshmipur": (22.9447, 90.8282),
    "lalmonirhat": (25.9923, 89.2847),
    "madaripur": (23.1642, 90.1897),
    "magura": (23.4873, 89.4198),
    "manikganj": (23.8644, 89.9954),
    "meherpur": (23.7622, 88.6318),
    "moulvibazar": (24.4829, 91.7774),
    "munshiganj": (23.5422, 90.5305),
    "mymensingh": (24.7471, 90.4203),
    "naogaon": (24.7936, 88.9318),
    "narail": (23.1725, 89.5126),
    "narayanganj": (23.6238, 90.4990),
    "narsingdi": (23.9226, 90.7150),
    "natore": (24.4206, 88.9808),
    "nawabganj": (24.5965, 88.2775),
    "chapainawabganj": (24.5965, 88.2775),
    "netrokona": (24.8710, 90.7276),
    "nilphamari": (25.9317, 88.8560),
    "noakhali": (22.8696, 91.0995),
    "pabna": (24.0064, 89.2372),
    "panchagarh": (26.3411, 88.5541),
    "patuakhali": (22.3596, 90.3298),
    "pirojpur": (22.5841, 89.9720),
    "rajbari": (23.7574, 89.6444),
    "rajshahi": (24.3745, 88.6042),
    "rangamati": (22.6533, 92.1787),
    "rangpur": (25.7439, 89.2752),
    "satkhira": (22.7185, 89.0705),
    "shariatpur": (23.2423, 90.4348),
    "sherpur": (25.0204, 90.0153),
    "sirajganj": (24.4534, 89.7000),
    "sunamganj": (25.0658, 91.3950),
    "sylhet": (24.8949, 91.8687),
    "tangail": (24.2513, 89.9167),
    "thakurgaon": (26.0336, 88.4616),
}


def resolve_district(location_text: str | None) -> tuple[float, float] | None:
    """Best-effort match of free-text location input (e.g. a farmer's typed
    "Sylhet" or "Sylhet Sadar") against a known district's coordinates."""
    if not location_text:
        return None
    low = location_text.strip().lower()
    if low in DISTRICT_COORDS:
        return DISTRICT_COORDS[low]
    for name, coords in DISTRICT_COORDS.items():
        if name in low or low in name:
            return coords
    return None
