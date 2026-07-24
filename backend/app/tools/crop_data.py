"""Per-acre cost/yield reference data used by the financial calculator.

Where possible, figures are pulled from real official sources rather than
invented:

- yield_per_acre_units (kg) and price_per_unit (BDT/kg): Bangladesh Bureau
  of Statistics, Yearbook of Agricultural Statistics-2024 (FY2023-24 area/
  yield/production tables, and wholesale-2023 or retail-2022 price tables,
  whichever the source document publishes for that crop). See
  app/data/sources.py::BBS_YEARBOOK_2024. Covers 34 crops across cereals,
  pulses, oilseeds, spices, vegetables, fiber, and sugar — the crop groups
  BBS itself tracks as Bangladesh's major and minor crops.
- fertilizer_cost_per_acre: real government-fixed fertilizer prices
  (app/data/sources.py::USDA_GAIN_FERTILIZER_2026) applied to a real
  measured application rate for rice (::RICE_FERTILIZER_DOSE_STUDY); other
  crops' fertilizer cost is *estimated* by scaling rice's cost with commonly
  cited relative fertilizer-intensity ratios, because the official FRG-2018
  per-crop dose tables block automated fetching (::FRG_2018_NOTE).
- labor_cost_per_acre: real BBS daily agricultural wage rate
  (app/data/sources.py::BBS_YEARBOOK_2024, Table 7.5) multiplied by an
  *estimated* labor-days-per-acre figure (no official per-crop labor-day
  survey was found).
- seed_cost_per_acre and water_cost_per_acre: still *estimated* — no
  official per-crop seed/irrigation cost survey was located in the time
  available. Flagged via `cost_confidence`.
- duration_days: typical agronomic practice, cross-checked against BRRI/BARI
  variety data where available (see app/data/sources.py).

`cost_confidence` on each entry summarizes this: "official" means yield,
price, and fertilizer cost are all sourced; "mixed" means yield/price are
sourced but cost components include estimates.
"""

from dataclasses import dataclass

from app.data import sources

# BBS Yearbook 2024, Table 7.5: daily wage "without food", male, national
# average across divisions (Jan-2023 data point within the 2023-24 table).
DAILY_WAGE_BDT = 580.0

# USDA GAIN BG2025-0017, government-fixed retail fertilizer prices, FY2025-26.
FERTILIZER_PRICE_BDT_PER_KG = {"urea": 27.0, "tsp": 27.0, "mop": 21.0}

# Real measured average application rate for rice: 180-43-42 kg/ha
# Urea-TSP-MoP (RICE_FERTILIZER_DOSE_STUDY), converted to kg/acre (1 ha = 2.471 acres).
_RICE_UREA_KG_ACRE = 180 / 2.471
_RICE_TSP_KG_ACRE = 43 / 2.471
_RICE_MOP_KG_ACRE = 42 / 2.471
RICE_FERTILIZER_COST_PER_ACRE = round(
    _RICE_UREA_KG_ACRE * FERTILIZER_PRICE_BDT_PER_KG["urea"]
    + _RICE_TSP_KG_ACRE * FERTILIZER_PRICE_BDT_PER_KG["tsp"]
    + _RICE_MOP_KG_ACRE * FERTILIZER_PRICE_BDT_PER_KG["mop"],
    2,
)  # ~2792 BDT/acre


@dataclass(frozen=True)
class CropEconomics:
    seed_cost_per_acre: float
    fertilizer_cost_per_acre: float
    labor_cost_per_acre: float
    water_cost_per_acre: float
    yield_per_acre_units: float
    price_per_unit: float
    duration_days: int
    water_need: str  # low | medium | high
    suitable_soils: list[str]
    cost_confidence: str = "mixed"  # "official" | "mixed" (see module docstring)
    yield_source: str = sources.BBS_YEARBOOK_2024
    price_source: str = sources.BBS_YEARBOOK_2024
    notes: str = ""


def _labor_cost(days_per_acre: float) -> float:
    return round(days_per_acre * DAILY_WAGE_BDT, 2)


def _scaled_fertilizer_cost(intensity_vs_rice: float) -> float:
    """Estimated: scales rice's real fertilizer cost by a commonly cited
    relative fertilizer-intensity ratio. See FRG_2018_NOTE."""
    return round(RICE_FERTILIZER_COST_PER_ACRE * intensity_vs_rice, 2)


CROP_REFERENCE: dict[str, CropEconomics] = {
    "rice": CropEconomics(
        seed_cost_per_acre=3000,  # estimated
        fertilizer_cost_per_acre=RICE_FERTILIZER_COST_PER_ACRE,  # sourced
        labor_cost_per_acre=_labor_cost(35),  # wage sourced, days estimated
        water_cost_per_acre=5000,  # estimated
        yield_per_acre_units=1748.0,  # Boro (irrigated HYV, dominant rice season), FY2023-24
        price_per_unit=30.21,  # Paddy Aman medium, wholesale avg
        duration_days=145,  # typical Boro HYV duration (BRRI dhan89/96 range)
        water_need="high",
        suitable_soils=["clay", "clay loam", "loam"],
        cost_confidence="mixed",
        notes="Yield is for Boro (irrigated HYV), the dominant and highest-yielding rice season.",
    ),
    "wheat": CropEconomics(
        seed_cost_per_acre=2500,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(0.85),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(20),  # wage sourced, days estimated
        water_cost_per_acre=2000,  # estimated
        yield_per_acre_units=1522.0,  # BBS Yearbook 2024, FY2023-24
        price_per_unit=44.33,  # Wheat local red, wholesale avg
        duration_days=115,
        water_need="medium",
        suitable_soils=["loam", "sandy loam", "clay loam"],
        cost_confidence="mixed",
    ),
    "maize": CropEconomics(
        seed_cost_per_acre=3500,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(0.95),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(22),  # wage sourced, days estimated
        water_cost_per_acre=2500,  # estimated
        yield_per_acre_units=6982.0,  # BBS Yearbook 2024, FY2023-24 (maize is high-yielding)
        price_per_unit=31.41,  # Maize wholesale avg, computed from monthly 2023 series
        duration_days=105,
        water_need="medium",
        suitable_soils=["loam", "sandy loam"],
        cost_confidence="mixed",
    ),
    "potato": CropEconomics(
        seed_cost_per_acre=12000,  # estimated (tuber seed is genuinely capital-intensive)
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(1.8),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(45),  # wage sourced, days estimated
        water_cost_per_acre=3000,  # estimated
        yield_per_acre_units=9355.0,  # BBS Yearbook 2024, FY2023-24
        price_per_unit=23.30,  # DAM government-fixed wholesale price, Mar 2024
        duration_days=95,
        water_need="medium",
        suitable_soils=["sandy loam", "loam"],
        cost_confidence="mixed",
        price_source=sources.DAM_PRICE_NOTICE_2024,
        notes="BARI has released ~100 potato varieties (e.g. BARI Alu-7) yielding up to 30-40 t/ha under good management.",
    ),
    "jute": CropEconomics(
        seed_cost_per_acre=1500,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(0.5),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(30),  # wage sourced, days estimated
        water_cost_per_acre=1500,  # estimated
        yield_per_acre_units=851.1,  # BBS Yearbook 2024, FY2022-23 (latest available for jute)
        price_per_unit=57.82,  # Jute (Tosha grade) wholesale avg
        duration_days=120,
        water_need="high",
        suitable_soils=["clay loam", "loam"],
        cost_confidence="mixed",
        notes="Yield converted from 4.69 bale/acre (1 bale = 181.4 kg); FY2023-24 figure was not published for jute in the source table.",
    ),
    "mustard": CropEconomics(
        seed_cost_per_acre=1200,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(0.45),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(12),  # wage sourced, days estimated
        water_cost_per_acre=800,  # estimated
        yield_per_acre_units=557.44,  # BBS Yearbook 2024, "Rape & Mustard", FY2023-24
        price_per_unit=84.02,  # Mustard oilseed wholesale avg
        duration_days=85,
        water_need="low",
        suitable_soils=["loam", "sandy loam", "clay loam"],
        cost_confidence="mixed",
        notes="BARI Sarisha-14 (released 2006) raised mustard yields ~50% over local checks in intercropping systems.",
    ),
    "lentil": CropEconomics(
        seed_cost_per_acre=2000,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(0.25),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(12),  # wage sourced, days estimated
        water_cost_per_acre=500,  # estimated
        yield_per_acre_units=598.88,  # BBS Yearbook 2024, "Masur", FY2023-24
        price_per_unit=88.38,  # Kalai mashur (raw lentil) wholesale avg
        duration_days=100,
        water_need="low",
        suitable_soils=["loam", "sandy loam"],
        cost_confidence="mixed",
    ),
    "tomato": CropEconomics(
        seed_cost_per_acre=6000,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(1.9),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(48),  # wage sourced, days estimated
        water_cost_per_acre=4000,  # estimated
        yield_per_acre_units=6393.23,  # BBS Yearbook 2024, FY2023-24
        price_per_unit=30.20,  # DAM government-fixed wholesale price, Mar 2024
        duration_days=95,
        water_need="medium",
        suitable_soils=["loam", "sandy loam"],
        cost_confidence="mixed",
        price_source=sources.DAM_PRICE_NOTICE_2024,
    ),
    "onion": CropEconomics(
        seed_cost_per_acre=8000,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(1.5),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(40),  # wage sourced, days estimated
        water_cost_per_acre=3000,  # estimated
        yield_per_acre_units=5681.01,  # BBS Yearbook 2024, FY2023-24
        price_per_unit=53.20,  # DAM government-fixed wholesale price, local onion, Mar 2024
        duration_days=115,
        water_need="medium",
        suitable_soils=["loam", "clay loam"],
        cost_confidence="mixed",
        price_source=sources.DAM_PRICE_NOTICE_2024,
        notes="Onion prices are historically volatile in Bangladesh; BBS's 2023 monthly series showed swings from ~27 to ~106 BDT/kg within the year.",
    ),
    "sugarcane": CropEconomics(
        seed_cost_per_acre=15000,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(1.6),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(50),  # wage sourced, days estimated
        water_cost_per_acre=6000,  # estimated
        yield_per_acre_units=17530.78,  # BBS Yearbook 2024, FY2023-24
        price_per_unit=6.5,  # BSFIC mill-gate purchase price, 2024-25/2025-26 season
        duration_days=330,
        water_need="high",
        suitable_soils=["clay loam", "loam"],
        cost_confidence="mixed",
        price_source=sources.SUGARCANE_PRICE_BSFIC,
    ),
    # ---- Pulses (BBS Yearbook 2024, FY2023-24 yield; wholesale price computed
    # manually from Table 10.1 monthly series, since that table's own
    # "Average" column is corrupted for several pulse/oilseed rows) ----
    "gram": CropEconomics(
        seed_cost_per_acre=1800,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(0.25),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(12),  # wage sourced, days estimated
        water_cost_per_acre=500,  # estimated
        yield_per_acre_units=517.68,
        price_per_unit=78.32,  # "Chola" wholesale avg, computed from monthly 2023 series
        duration_days=100,
        water_need="low",
        suitable_soils=["loam", "sandy loam"],
        cost_confidence="mixed",
    ),
    "mung": CropEconomics(
        seed_cost_per_acre=1600,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(0.2),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(10),  # wage sourced, days estimated
        water_cost_per_acre=500,  # estimated
        yield_per_acre_units=368.09,
        price_per_unit=89.59,  # "Kalai mug" wholesale avg, computed from monthly 2023 series
        duration_days=65,
        water_need="low",
        suitable_soils=["loam", "sandy loam"],
        cost_confidence="mixed",
        notes="Mung bean (green gram); short duration, nitrogen-fixing, fits between two main crops.",
    ),
    "mashkalai": CropEconomics(
        seed_cost_per_acre=1600,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(0.2),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(10),  # wage sourced, days estimated
        water_cost_per_acre=500,  # estimated
        yield_per_acre_units=399.65,
        price_per_unit=114.57,  # "Kalai mash" wholesale avg, computed from monthly 2023 series
        duration_days=90,
        water_need="low",
        suitable_soils=["loam", "sandy loam"],
        cost_confidence="mixed",
        notes="Black gram (Mashkalai/urad).",
    ),
    "khesari": CropEconomics(
        seed_cost_per_acre=1200,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(0.15),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(10),  # wage sourced, days estimated
        water_cost_per_acre=400,  # estimated
        yield_per_acre_units=482.33,
        price_per_unit=59.17,  # "Kalai kheshari" wholesale avg
        duration_days=110,
        water_need="low",
        suitable_soils=["loam", "clay loam"],
        cost_confidence="mixed",
        notes="Grass pea (Khesari); very hardy, often relay-cropped into standing Aman rice.",
    ),
    # ---- Oilseeds ----
    "sesame": CropEconomics(
        seed_cost_per_acre=1500,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(0.35),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(14),  # wage sourced, days estimated
        water_cost_per_acre=500,  # estimated
        yield_per_acre_units=809.38,
        price_per_unit=98.57,  # "Till" oilseed wholesale avg (one monthly value looked like an
        # OCR artifact in the source table; average computed with that value included as-is)
        duration_days=90,
        water_need="low",
        suitable_soils=["sandy loam", "loam"],
        cost_confidence="mixed",
        notes="Til/sesame.",
    ),
    "groundnut": CropEconomics(
        seed_cost_per_acre=3500,  # estimated (groundnut seed rate is relatively high)
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(0.4),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(18),  # wage sourced, days estimated
        water_cost_per_acre=600,  # estimated
        yield_per_acre_units=1564.60,
        price_per_unit=133.50,  # "Nut" oilseed wholesale avg, computed from monthly 2023 series
        duration_days=110,
        water_need="low",
        suitable_soils=["sandy loam"],
        cost_confidence="mixed",
        notes="Groundnut/peanut; suited to sandy/sandy-loam char and coastal land.",
    ),
    "soybean": CropEconomics(
        seed_cost_per_acre=2200,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(0.4),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(16),  # wage sourced, days estimated
        water_cost_per_acre=800,  # estimated
        yield_per_acre_units=755.69,
        price_per_unit=100.0,  # no distinct soybean row in the BBS wholesale price table found;
        # estimated as roughly in line with other edible oilseeds (groundnut/mustard)
        duration_days=100,
        water_need="medium",
        suitable_soils=["loam", "sandy loam"],
        cost_confidence="mixed",
        notes="price_per_unit is an estimate — no distinct soybean wholesale price row was found in the source table.",
    ),
    "linseed": CropEconomics(
        seed_cost_per_acre=1300,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(0.3),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(10),  # wage sourced, days estimated
        water_cost_per_acre=400,  # estimated
        yield_per_acre_units=303.13,
        price_per_unit=119.29,  # "Tishi" oilseed wholesale avg, computed from monthly 2023 series
        duration_days=110,
        water_need="low",
        suitable_soils=["loam", "clay loam"],
        cost_confidence="mixed",
    ),
    # ---- Spices ----
    "garlic": CropEconomics(
        seed_cost_per_acre=15000,  # estimated (clove seed is expensive)
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(1.6),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(45),  # wage sourced, days estimated
        water_cost_per_acre=1500,  # estimated
        yield_per_acre_units=3023.60,
        price_per_unit=94.61,  # DAM government-fixed wholesale price, local garlic, Mar 2024
        duration_days=120,
        water_need="low",
        suitable_soils=["loam", "sandy loam"],
        cost_confidence="mixed",
        price_source=sources.DAM_PRICE_NOTICE_2024,
    ),
    "turmeric": CropEconomics(
        seed_cost_per_acre=20000,  # estimated (rhizome seed is expensive)
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(1.7),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(55),  # wage sourced, days estimated
        water_cost_per_acre=2500,  # estimated
        yield_per_acre_units=3706.88,
        price_per_unit=153.85,  # "Turmeric round" wholesale avg
        duration_days=270,
        water_need="medium",
        suitable_soils=["loam", "clay loam"],
        cost_confidence="mixed",
        notes="Long-duration rhizome crop (~9 months); high capital and labor requirement.",
    ),
    "ginger": CropEconomics(
        seed_cost_per_acre=18000,  # estimated (rhizome seed is expensive)
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(1.7),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(50),  # wage sourced, days estimated
        water_cost_per_acre=2500,  # estimated
        yield_per_acre_units=3240.38,
        price_per_unit=120.25,  # DAM government-fixed wholesale price, imported ginger, Mar 2024
        duration_days=240,
        water_need="medium",
        suitable_soils=["loam", "clay loam"],
        cost_confidence="mixed",
        price_source=sources.DAM_PRICE_NOTICE_2024,
        notes="Price is DAM's imported-ginger reference; local ginger typically trades higher.",
    ),
    "chilli": CropEconomics(
        seed_cost_per_acre=2000,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(1.3),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(45),  # wage sourced, days estimated (picking-intensive)
        water_cost_per_acre=1800,  # estimated
        yield_per_acre_units=3065.57,  # blended Kharif+Rabi chilli, FY2023-24
        price_per_unit=45.40,  # DAM government-fixed wholesale price, green chili, Mar 2024
        duration_days=150,
        water_need="medium",
        suitable_soils=["loam", "sandy loam"],
        cost_confidence="mixed",
        price_source=sources.DAM_PRICE_NOTICE_2024,
        notes="Green chilli price; DAM's red/dried chilli reference is much higher (~253 BDT/kg).",
    ),
    "coriander": CropEconomics(
        seed_cost_per_acre=800,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(0.5),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(15),  # wage sourced, days estimated
        water_cost_per_acre=600,  # estimated
        yield_per_acre_units=471.66,  # coriander seed
        price_per_unit=150.73,  # "Coriander old" wholesale avg
        duration_days=100,
        water_need="low",
        suitable_soils=["loam", "sandy loam"],
        cost_confidence="mixed",
        notes="Yield/price are for coriander seed (dhone), not the leafy-herb crop.",
    ),
    # ---- Vegetables (yield: BBS Yearbook 2024 FY2023-24; price: BBS retail
    # price table, Year-2022 — a year older than the wholesale table above,
    # since the vegetable-specific rows appear only in that retail table) ----
    "cauliflower": CropEconomics(
        seed_cost_per_acre=4000,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(1.5),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(35),  # wage sourced, days estimated
        water_cost_per_acre=2500,  # estimated
        yield_per_acre_units=7391.62,
        price_per_unit=24.50,  # DAM government-fixed wholesale price, Mar 2024
        duration_days=90,
        water_need="medium",
        suitable_soils=["loam", "clay loam"],
        cost_confidence="mixed",
        price_source=sources.DAM_PRICE_NOTICE_2024,
    ),
    "cabbage": CropEconomics(
        seed_cost_per_acre=3500,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(1.4),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(32),  # wage sourced, days estimated
        water_cost_per_acre=2500,  # estimated
        yield_per_acre_units=8428.73,
        price_per_unit=23.45,  # DAM government-fixed wholesale price, Mar 2024
        duration_days=90,
        water_need="medium",
        suitable_soils=["loam", "clay loam"],
        cost_confidence="mixed",
        price_source=sources.DAM_PRICE_NOTICE_2024,
    ),
    "brinjal": CropEconomics(
        seed_cost_per_acre=3000,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(1.4),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(40),  # wage sourced, days estimated
        water_cost_per_acre=2500,  # estimated
        yield_per_acre_units=5633.73,  # Rabi Brinjal, FY2023-24
        price_per_unit=38.25,  # DAM government-fixed wholesale price, Mar 2024
        duration_days=130,
        water_need="medium",
        suitable_soils=["loam", "sandy loam"],
        cost_confidence="mixed",
        price_source=sources.DAM_PRICE_NOTICE_2024,
        notes="Eggplant/aubergine.",
    ),
    "okra": CropEconomics(
        seed_cost_per_acre=2000,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(1.0),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(35),  # wage sourced, days estimated (frequent picking)
        water_cost_per_acre=1800,  # estimated
        yield_per_acre_units=3168.64,
        price_per_unit=39.55,  # BBS retail price table, "Lady's Finger", 2022 avg
        duration_days=60,
        water_need="medium",
        suitable_soils=["loam", "sandy loam"],
        cost_confidence="mixed",
        notes="Lady's finger.",
    ),
    "cucumber": CropEconomics(
        seed_cost_per_acre=2500,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(1.1),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(30),  # wage sourced, days estimated
        water_cost_per_acre=2000,  # estimated
        yield_per_acre_units=4235.14,
        price_per_unit=32.16,  # BBS retail price table, "Sosha", 2022 avg
        duration_days=60,
        water_need="medium",
        suitable_soils=["sandy loam", "loam"],
        cost_confidence="mixed",
    ),
    "pumpkin": CropEconomics(
        seed_cost_per_acre=1500,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(0.8),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(20),  # wage sourced, days estimated
        water_cost_per_acre=1200,  # estimated
        yield_per_acre_units=5243.45,  # Kharif pumpkin, FY2023-24
        price_per_unit=16.45,  # DAM government-fixed wholesale price, "sweet pumpkin", Mar 2024
        duration_days=100,
        water_need="low",
        suitable_soils=["loam", "sandy loam"],
        cost_confidence="mixed",
        price_source=sources.DAM_PRICE_NOTICE_2024,
    ),
    "bitter_gourd": CropEconomics(
        seed_cost_per_acre=2200,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(1.1),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(35),  # wage sourced, days estimated
        water_cost_per_acre=2000,  # estimated
        yield_per_acre_units=2929.19,  # "Karalla", FY2023-24
        price_per_unit=53.38,  # BBS retail price table, 2022 avg
        duration_days=100,
        water_need="medium",
        suitable_soils=["loam", "sandy loam"],
        cost_confidence="mixed",
    ),
    "carrot": CropEconomics(
        seed_cost_per_acre=3000,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(1.2),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(30),  # wage sourced, days estimated
        water_cost_per_acre=2000,  # estimated
        yield_per_acre_units=6327.90,
        price_per_unit=61.61,  # BBS retail price table, 2022 avg
        duration_days=90,
        water_need="medium",
        suitable_soils=["sandy loam"],
        cost_confidence="mixed",
    ),
    "radish": CropEconomics(
        seed_cost_per_acre=1500,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(0.9),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(20),  # wage sourced, days estimated
        water_cost_per_acre=1500,  # estimated
        yield_per_acre_units=5668.06,
        price_per_unit=70.0,  # derived: real retail price ~90 BDT/kg (market report, Oct 2024)
        # x ~0.78 average wholesale/retail ratio observed across the DAM Mar-2024 notice's
        # overlapping items (onion/garlic/ginger/chilli/cabbage/cauliflower/brinjal/potato/tomato)
        duration_days=45,
        water_need="medium",
        suitable_soils=["sandy loam"],
        cost_confidence="mixed",
        notes=(
            "price_per_unit is derived, not directly sourced: no wholesale/farmgate radish "
            "figure was found, so a retail figure (~90 BDT/kg, Oct 2024 market report) was "
            "scaled by the average wholesale/retail ratio seen in DAM's Mar-2024 price notice."
        ),
    ),
    "spinach": CropEconomics(
        seed_cost_per_acre=1000,  # estimated
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(0.7),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(18),  # wage sourced, days estimated
        water_cost_per_acre=1200,  # estimated
        yield_per_acre_units=2743.34,  # "Palongsak", FY2023-24
        price_per_unit=20.41,  # BBS retail price table, 2022 avg
        duration_days=45,
        water_need="medium",
        suitable_soils=["loam", "sandy loam"],
        cost_confidence="mixed",
        notes="Palong shak (spinach); short-cycle leafy green, often grown multiple times a season.",
    ),
    "sweet_potato": CropEconomics(
        seed_cost_per_acre=4000,  # estimated (vine cuttings)
        fertilizer_cost_per_acre=_scaled_fertilizer_cost(1.3),  # estimated, scaled from rice
        labor_cost_per_acre=_labor_cost(35),  # wage sourced, days estimated
        water_cost_per_acre=1500,  # estimated
        yield_per_acre_units=4373.37,
        price_per_unit=26.76,  # BBS retail price table, 2022 avg
        duration_days=110,
        water_need="low",
        suitable_soils=["sandy loam"],
        cost_confidence="mixed",
    ),
}

DEFAULT_CROP = CropEconomics(
    seed_cost_per_acre=3000,
    fertilizer_cost_per_acre=_scaled_fertilizer_cost(1.0),
    labor_cost_per_acre=_labor_cost(30),
    water_cost_per_acre=2500,
    yield_per_acre_units=2000,
    price_per_unit=25,
    duration_days=100,
    water_need="medium",
    suitable_soils=["loam"],
    cost_confidence="mixed",
    notes="Fallback average for a crop not in CROP_REFERENCE; not tied to a specific source.",
)


def get_crop_economics(crop_name: str) -> CropEconomics:
    return CROP_REFERENCE.get(crop_name.strip().lower(), DEFAULT_CROP)
