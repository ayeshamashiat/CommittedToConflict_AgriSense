"""Tier 2: Marketplace & supplier comparison — matches an input need (a
fertilizer or seed) to suppliers ranked by price, delivery time, distance,
and rating.

Two supplier sources, tried in order:
1. Real shop locations from OpenStreetMap's Overpass API (see
   app/integrations/osm_places.py) — real names, real coordinates, real
   distance. No public source publishes real per-shop pricing/delivery
   time/ratings for these informal retailers, so those three fields are
   filled in as disclosed estimates even for a real OSM-sourced result.
2. The seeded mock catalog (app/data/supplier_catalog.py — explicitly
   allowed by the hackathon brief) — used only when OSM has no shops mapped
   near the farmer's location, which is common in rural areas.

Whichever source produced the offers, `MarketplaceOutput.source` and each
offer's `is_real_location` flag say so explicitly. The ranking math itself
is always real and disclosed: each factor normalized to 0-1 and combined
with fixed weights, not an LLM judgment call, so the same inputs always
produce the same ranking.
"""

from app.data.bd_districts import resolve_district
from app.data.supplier_catalog import FERTILIZER_SUPPLIERS, SEED_SUPPLIERS
from app.db.database import SessionLocal
from app.db.repositories.crop_reference_repo import get_by_name
from app.integrations import osm_places
from app.schemas.tool_io import MarketplaceInput, MarketplaceOutput, SupplierOffer
from app.tools.base import AgriTool
from app.tools.crop_data import DEFAULT_CROP
from app.tools.geo import haversine_km

# price 40% / delivery 20% / distance 20% / rating 20% — price dominates
# since it's usually the farmer's biggest constraint, but the other three
# still meaningfully move the ranking rather than being decorative.
WEIGHTS = {"price": 0.4, "delivery": 0.2, "distance": 0.2, "rating": 0.2}

UNITS = {"urea": "kg", "tsp": "kg", "mop": "kg", "pesticide": "liter", "seed": "kg"}

# A supplier in (or clearly near) the farmer's stated location is far cheaper
# to reach than its catalog distance_km implies if that figure represents a
# generic "distance from a mid-sized farm in this supplier's usual service
# area" — disclosed heuristic, not a real geocoded distance.
_SAME_AREA_DISTANCE_KM = 12.0

# Used only for OSM-sourced real shops, where we have no real delivery-time
# data either — a real local shop within the search radius is reasonably
# assumed to be same-day/next-day pickup, not a multi-day delivery like the
# mock catalog's more distant entries.
_REAL_SHOP_ESTIMATED_DELIVERY_DAYS = 1


def _catalog_average_price(item: str) -> float | None:
    offers = FERTILIZER_SUPPLIERS.get(item)
    if not offers:
        return None
    return round(sum(o["price_per_unit"] for o in offers) / len(offers), 2)


class MarketplaceTool(AgriTool):
    name = "marketplace"
    description = (
        "Given an input need (urea, tsp, mop, pesticide, or seed for a named crop), "
        "returns nearby/available suppliers ranked by price, delivery time, distance, "
        "and rating. Call this when the farmer asks where to buy something or wants to "
        "compare suppliers/prices for an input."
    )
    input_schema = MarketplaceInput
    output_schema = MarketplaceOutput

    def run(self, input_data: MarketplaceInput) -> MarketplaceOutput:
        item = input_data.item.strip().lower()
        unit = UNITS.get(item, "unit")
        crop_key = (input_data.crop or "").strip().lower()
        farmer_coords = resolve_district(input_data.farmer_location)

        real_offers, real_shops_found = self._try_osm_offers(item, crop_key, farmer_coords, input_data.farmer_location)
        if real_shops_found:
            raw_offers = real_offers
            is_real_source = True
            source = (
                "Real shop locations from OpenStreetMap (name, location, distance are real). Price and "
                "delivery time are estimated — no public source publishes real per-shop pricing for "
                "these informal retailers — and rating data isn't available for them."
            )
        else:
            raw_offers, source = self._catalog_offers(item, crop_key, input_data.farmer_location)
            is_real_source = False

        if not raw_offers:
            return MarketplaceOutput(
                item=item, unit=unit, offers=[], ranking_method=self._ranking_note(), source=source
            )

        # Real haversine distance between the farmer's district and each
        # supplier's district when both resolve to a known district (see
        # bd_districts.py) — this replaces what used to be each supplier's
        # fixed catalog distance_km used unconditionally, which was only ever
        # roughly accurate for a farmer near Rangpur and silently wrong for
        # everyone else. OSM-sourced offers already carry a real point-to-
        # point distance from the search itself, so they're left untouched
        # here rather than re-resolved at district granularity.
        used_real_distance = is_real_source
        adjusted = []
        for offer in raw_offers:
            distance = offer["distance_km"]
            if not is_real_source:
                supplier_coords = resolve_district(offer["district"])
                if farmer_coords and supplier_coords:
                    distance = haversine_km(farmer_coords, supplier_coords)
                    used_real_distance = True
                elif input_data.farmer_location and input_data.farmer_location.strip().lower() in offer["district"].lower():
                    distance = min(distance, _SAME_AREA_DISTANCE_KM)
            adjusted.append({**offer, "distance_km": distance})

        prices = [o["price_per_unit"] for o in adjusted]
        deliveries = [o["delivery_days"] for o in adjusted]
        distances = [o["distance_km"] for o in adjusted]
        known_ratings = [o["rating"] for o in adjusted if o.get("rating") is not None]

        def norm(value, lo, hi, invert=True):
            if hi == lo:
                return 1.0
            n = (value - lo) / (hi - lo)
            return 1 - n if invert else n

        offers: list[SupplierOffer] = []
        for o in adjusted:
            rating = o.get("rating")
            # No real rating data for OSM-sourced shops — score that factor
            # neutrally (neither rewarded nor penalized) instead of either
            # inventing a number or crashing on min()/max() of an empty list.
            rating_score = norm(rating, min(known_ratings), max(known_ratings), invert=False) if (rating is not None and known_ratings) else 0.5
            score = (
                WEIGHTS["price"] * norm(o["price_per_unit"], min(prices), max(prices))
                + WEIGHTS["delivery"] * norm(o["delivery_days"], min(deliveries), max(deliveries))
                + WEIGHTS["distance"] * norm(o["distance_km"], min(distances), max(distances))
                + WEIGHTS["rating"] * rating_score
            )
            estimated_total = (
                round(o["price_per_unit"] * input_data.quantity, 2) if input_data.quantity else None
            )
            offers.append(
                SupplierOffer(
                    supplier_name=o["supplier_name"],
                    district=o["district"],
                    price_per_unit=o["price_per_unit"],
                    unit=unit,
                    delivery_days=o["delivery_days"],
                    distance_km=o["distance_km"],
                    rating=rating,
                    estimated_total_cost=estimated_total,
                    composite_score=round(score, 3),
                    is_real_location=is_real_source,
                )
            )

        offers.sort(key=lambda x: x.composite_score, reverse=True)

        return MarketplaceOutput(
            item=item,
            unit=unit,
            offers=offers,
            ranking_method=self._ranking_note(),
            source=source,
            distance_note=self._distance_note(used_real_distance, is_real_source, input_data.farmer_location),
        )

    @staticmethod
    def _try_osm_offers(
        item: str, crop_key: str, farmer_coords: tuple[float, float] | None, farmer_location: str | None
    ) -> tuple[list[dict], bool]:
        """Attempts a real OpenStreetMap lookup near the farmer's district
        centroid. Returns (offers, found) — found=False whenever OSM has no
        shops mapped nearby (common in rural areas) or the farmer's location
        couldn't be resolved to a district at all, telling the caller to fall
        back to the mock catalog."""
        if not farmer_coords:
            return [], False
        shops = osm_places.search_agrarian_shops(*farmer_coords)
        if not shops:
            return [], False

        baseline_price = _catalog_average_price(item)
        if baseline_price is None:
            db = SessionLocal()
            try:
                econ = get_by_name(db, crop_key) or DEFAULT_CROP
            finally:
                db.close()
            baseline_price = econ.seed_cost_per_acre

        offers = []
        for shop in shops:
            offers.append(
                {
                    "supplier_name": shop["name"],
                    "district": farmer_location or "Nearby",
                    "price_per_unit": baseline_price,
                    "delivery_days": _REAL_SHOP_ESTIMATED_DELIVERY_DAYS,
                    "distance_km": haversine_km(farmer_coords, (shop["lat"], shop["lon"])),
                    "rating": None,
                }
            )
        return offers, True

    @staticmethod
    def _catalog_offers(item: str, crop_key: str, farmer_location: str | None) -> tuple[list[dict], str]:
        if item == "seed":
            raw_offers = SEED_SUPPLIERS.get(crop_key)
            source = (
                "Seeded/mock supplier catalog (illustrative, not real businesses or live prices)."
                if raw_offers
                else "No seed suppliers catalogued for this crop — falling back to an estimated "
                "single-source price derived from this crop's reference seed cost."
            )
            if not raw_offers:
                db = SessionLocal()
                try:
                    econ = get_by_name(db, crop_key) or DEFAULT_CROP
                finally:
                    db.close()
                raw_offers = [
                    {
                        "supplier_name": "Estimated local input dealer",
                        "district": farmer_location or "Unknown",
                        "price_per_unit": econ.seed_cost_per_acre,
                        "delivery_days": 3,
                        "distance_km": _SAME_AREA_DISTANCE_KM,
                        "rating": 4.0,
                    }
                ]
            return raw_offers, source
        return FERTILIZER_SUPPLIERS.get(item, []), (
            "Seeded/mock supplier catalog (illustrative, not real businesses or live prices)."
        )

    @staticmethod
    def _distance_note(used_real_distance: bool, is_real_source: bool, farmer_location: str | None) -> str:
        if is_real_source:
            return (
                "Distance is a real straight-line (not road) distance from your farm's district center "
                "to each real shop's OpenStreetMap location."
            )
        if used_real_distance:
            return (
                f"Distance is a straight-line (not road) distance between {farmer_location}'s district "
                "and each supplier's district, calculated from real district coordinates — not a "
                "generic estimate."
            )
        return (
            "Distance shown is the supplier's generic catalog estimate, not calculated from your "
            f"farm's actual location ({farmer_location or 'not provided'} could not be matched to a "
            "known district) — treat it as approximate."
        )

    @staticmethod
    def _ranking_note() -> str:
        return (
            f"Composite score = {WEIGHTS['price']:.0%} price + {WEIGHTS['delivery']:.0%} delivery time "
            f"+ {WEIGHTS['distance']:.0%} distance + {WEIGHTS['rating']:.0%} rating, each normalized "
            "across the offers shown (not an absolute scale). Higher score = better overall match, "
            "sorted highest first."
        )
