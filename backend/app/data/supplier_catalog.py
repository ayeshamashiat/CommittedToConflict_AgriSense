"""Tier 2: Marketplace & supplier comparison — seeded/mock supplier catalog.

Per the hackathon brief, "a seeded or mock supplier catalog is completely
acceptable" for this feature — these are NOT real businesses or real prices;
they're representative entries (plausible Bangladeshi district names, prices
in the same ballpark as the real fertilizer prices in crop_data.py) so the
ranking/comparison logic has something realistic to operate on. Unlike the
financial/yield data elsewhere in this app, nothing here is cited to an
official source, and marketplace_tool.py's output says so explicitly.
"""

# Fertilizer suppliers, price in BDT/kg. Real fertilizer prices are
# government-fixed (see crop_data.py) so these cluster near that real price
# with plausible small markups/discounts per supplier — not invented wildly.
FERTILIZER_SUPPLIERS: dict[str, list[dict]] = {
    "urea": [
        {"supplier_name": "Rangpur Krishi Bhandar", "district": "Rangpur", "price_per_unit": 27.5, "delivery_days": 1, "distance_km": 8, "rating": 4.6},
        {"supplier_name": "Bogura Agro Traders", "district": "Bogura", "price_per_unit": 26.8, "delivery_days": 2, "distance_km": 45, "rating": 4.3},
        {"supplier_name": "Dinajpur Farmers Co-op", "district": "Dinajpur", "price_per_unit": 27.0, "delivery_days": 2, "distance_km": 60, "rating": 4.7},
        {"supplier_name": "BADC Dealer - Rajshahi", "district": "Rajshahi", "price_per_unit": 27.0, "delivery_days": 3, "distance_km": 90, "rating": 4.4},
        {"supplier_name": "Sylhet Agro Store", "district": "Sylhet", "price_per_unit": 27.3, "delivery_days": 2, "distance_km": 12, "rating": 4.4},
        {"supplier_name": "Khulna Krishi Depot", "district": "Khulna", "price_per_unit": 27.1, "delivery_days": 2, "distance_km": 12, "rating": 4.5},
        {"supplier_name": "Chattogram Farmers Supply", "district": "Chattogram", "price_per_unit": 27.4, "delivery_days": 2, "distance_km": 12, "rating": 4.3},
    ],
    "tsp": [
        {"supplier_name": "Rangpur Krishi Bhandar", "district": "Rangpur", "price_per_unit": 28.0, "delivery_days": 1, "distance_km": 8, "rating": 4.6},
        {"supplier_name": "Bogura Agro Traders", "district": "Bogura", "price_per_unit": 27.2, "delivery_days": 2, "distance_km": 45, "rating": 4.3},
        {"supplier_name": "Dinajpur Farmers Co-op", "district": "Dinajpur", "price_per_unit": 27.5, "delivery_days": 2, "distance_km": 60, "rating": 4.7},
        {"supplier_name": "Sylhet Agro Store", "district": "Sylhet", "price_per_unit": 28.2, "delivery_days": 2, "distance_km": 12, "rating": 4.4},
        {"supplier_name": "Khulna Krishi Depot", "district": "Khulna", "price_per_unit": 27.8, "delivery_days": 2, "distance_km": 12, "rating": 4.5},
    ],
    "mop": [
        {"supplier_name": "Rangpur Krishi Bhandar", "district": "Rangpur", "price_per_unit": 22.0, "delivery_days": 1, "distance_km": 8, "rating": 4.6},
        {"supplier_name": "Bogura Agro Traders", "district": "Bogura", "price_per_unit": 21.0, "delivery_days": 2, "distance_km": 45, "rating": 4.3},
        {"supplier_name": "BADC Dealer - Rajshahi", "district": "Rajshahi", "price_per_unit": 21.5, "delivery_days": 3, "distance_km": 90, "rating": 4.4},
        {"supplier_name": "Sylhet Agro Store", "district": "Sylhet", "price_per_unit": 22.3, "delivery_days": 2, "distance_km": 12, "rating": 4.4},
        {"supplier_name": "Chattogram Farmers Supply", "district": "Chattogram", "price_per_unit": 21.9, "delivery_days": 2, "distance_km": 12, "rating": 4.3},
    ],
    "pesticide": [
        {"supplier_name": "Rangpur Krishi Bhandar", "district": "Rangpur", "price_per_unit": 350.0, "delivery_days": 1, "distance_km": 8, "rating": 4.5},
        {"supplier_name": "Green Shield Agro-Chem", "district": "Dhaka", "price_per_unit": 320.0, "delivery_days": 3, "distance_km": 300, "rating": 4.2},
        {"supplier_name": "Bogura Agro Traders", "district": "Bogura", "price_per_unit": 340.0, "delivery_days": 2, "distance_km": 45, "rating": 4.3},
        {"supplier_name": "Sylhet Agro Store", "district": "Sylhet", "price_per_unit": 345.0, "delivery_days": 2, "distance_km": 12, "rating": 4.4},
        {"supplier_name": "Khulna Krishi Depot", "district": "Khulna", "price_per_unit": 335.0, "delivery_days": 2, "distance_km": 12, "rating": 4.5},
    ],
}

# Seed suppliers, price in BDT/kg (or BDT per unit noted). Covers common
# crops; anything not listed falls back to a generic estimate in
# marketplace_tool.py, clearly flagged as such.
SEED_SUPPLIERS: dict[str, list[dict]] = {
    "rice": [
        {"supplier_name": "BADC Seed Dealer - Rangpur", "district": "Rangpur", "price_per_unit": 65.0, "delivery_days": 2, "distance_km": 10, "rating": 4.6},
        {"supplier_name": "Lal Teer Seed Ltd.", "district": "Dhaka", "price_per_unit": 72.0, "delivery_days": 4, "distance_km": 300, "rating": 4.7},
        {"supplier_name": "Dinajpur Farmers Co-op", "district": "Dinajpur", "price_per_unit": 60.0, "delivery_days": 2, "distance_km": 60, "rating": 4.5},
        {"supplier_name": "Sylhet Seed Store", "district": "Sylhet", "price_per_unit": 68.0, "delivery_days": 2, "distance_km": 12, "rating": 4.4},
        {"supplier_name": "Khulna BADC Seed Dealer", "district": "Khulna", "price_per_unit": 63.0, "delivery_days": 2, "distance_km": 12, "rating": 4.5},
    ],
    "wheat": [
        {"supplier_name": "BADC Seed Dealer - Rangpur", "district": "Rangpur", "price_per_unit": 55.0, "delivery_days": 2, "distance_km": 10, "rating": 4.6},
        {"supplier_name": "Bogura Agro Traders", "district": "Bogura", "price_per_unit": 52.0, "delivery_days": 2, "distance_km": 45, "rating": 4.3},
    ],
    "maize": [
        {"supplier_name": "Lal Teer Seed Ltd.", "district": "Dhaka", "price_per_unit": 320.0, "delivery_days": 4, "distance_km": 300, "rating": 4.7},
        {"supplier_name": "ACI Seed", "district": "Bogura", "price_per_unit": 300.0, "delivery_days": 3, "distance_km": 45, "rating": 4.5},
    ],
    "potato": [
        {"supplier_name": "BADC Seed Dealer - Rangpur", "district": "Rangpur", "price_per_unit": 45.0, "delivery_days": 1, "distance_km": 10, "rating": 4.6},
        {"supplier_name": "Munshiganj Potato Traders", "district": "Munshiganj", "price_per_unit": 42.0, "delivery_days": 4, "distance_km": 320, "rating": 4.4},
    ],
    "tomato": [
        {"supplier_name": "Lal Teer Seed Ltd.", "district": "Dhaka", "price_per_unit": 8500.0, "delivery_days": 4, "distance_km": 300, "rating": 4.7},
        {"supplier_name": "ACI Seed", "district": "Bogura", "price_per_unit": 7800.0, "delivery_days": 3, "distance_km": 45, "rating": 4.5},
    ],
    "cabbage": [
        {"supplier_name": "Lal Teer Seed Ltd.", "district": "Dhaka", "price_per_unit": 9000.0, "delivery_days": 4, "distance_km": 300, "rating": 4.7},
        {"supplier_name": "Bogura Agro Traders", "district": "Bogura", "price_per_unit": 8200.0, "delivery_days": 2, "distance_km": 45, "rating": 4.3},
    ],
    "onion": [
        {"supplier_name": "Faridpur Onion Seed Co-op", "district": "Faridpur", "price_per_unit": 380.0, "delivery_days": 3, "distance_km": 280, "rating": 4.5},
        {"supplier_name": "BADC Seed Dealer - Rangpur", "district": "Rangpur", "price_per_unit": 400.0, "delivery_days": 2, "distance_km": 10, "rating": 4.6},
    ],
    "lentil": [
        {"supplier_name": "BADC Seed Dealer - Rangpur", "district": "Rangpur", "price_per_unit": 110.0, "delivery_days": 2, "distance_km": 10, "rating": 4.6},
    ],
    "mustard": [
        {"supplier_name": "BADC Seed Dealer - Rangpur", "district": "Rangpur", "price_per_unit": 130.0, "delivery_days": 2, "distance_km": 10, "rating": 4.6},
    ],
    "jute": [
        {"supplier_name": "BJRI Seed Center", "district": "Faridpur", "price_per_unit": 220.0, "delivery_days": 3, "distance_km": 280, "rating": 4.6},
    ],
}
