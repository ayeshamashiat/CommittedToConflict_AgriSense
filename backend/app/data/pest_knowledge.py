"""Pest & disease knowledge base (Tier 1): common, well-documented pests and
diseases per crop, with the weather conditions that raise their risk.

These are standard, widely-taught IPM (Integrated Pest Management) facts —
e.g. potato late blight favoring cool+humid conditions is textbook plant
pathology, not something requiring a specific citation the way a price or
yield figure does. Treated as "general agronomy" confidence, same as the
generic soil passages in knowledge_base.py. Estimated treatment costs are
rough smallholder-practice figures, not sourced from a specific price survey.

Trigger conditions are declarative thresholds evaluated against the weather
tool's actual returned values — this is what keeps risk assessment grounded
in real data rather than a static "rice always gets blast" list.
"""

# Threshold keys evaluated against WeatherOutput fields: temperature (C),
# humidity (%), rainfall (mm, current/recent). All present thresholds must
# hold for the risk to be flagged.
PEST_KNOWLEDGE: dict[str, list[dict]] = {
    "rice": [
        {
            "name": "Rice blast",
            "kind": "disease",
            "min_humidity": 85,
            "temp_min": 20,
            "temp_max": 30,
            "prevention": "Use a resistant variety (e.g. BRRI dhan-series blast-resistant lines), avoid excess nitrogen, ensure good field drainage.",
            "treatment": "Apply a tricyclazole or isoprothiolane-based fungicide at first symptoms; remove and destroy infected tillers.",
            "estimated_cost_bdt_per_acre": 1500,
        },
        {
            "name": "Brown planthopper",
            "kind": "pest",
            "min_humidity": 80,
            "prevention": "Avoid excess nitrogen and overly dense planting; maintain alternate wetting-and-drying rather than continuous flooding.",
            "treatment": "Spray a recommended insecticide (e.g. imidacloprid) if hopper burn patches appear; drain the field briefly to disrupt the pest.",
            "estimated_cost_bdt_per_acre": 1200,
        },
        {
            "name": "Bacterial leaf blight",
            "kind": "disease",
            "min_rainfall": 10,
            "min_humidity": 80,
            "prevention": "Use disease-free seed, avoid excess nitrogen, avoid field injury during heavy-rain periods.",
            "treatment": "Apply copper-based bactericide; remove severely infected plants to slow spread.",
            "estimated_cost_bdt_per_acre": 1000,
        },
    ],
    "wheat": [
        {
            "name": "Wheat rust (yellow/brown)",
            "kind": "disease",
            "min_humidity": 75,
            "temp_min": 15,
            "temp_max": 22,
            "prevention": "Plant rust-resistant varieties; avoid late sowing, which extends exposure to cool humid conditions.",
            "treatment": "Apply a propiconazole-based fungicide at first pustules.",
            "estimated_cost_bdt_per_acre": 1300,
        },
        {
            "name": "Aphids",
            "kind": "pest",
            "temp_min": 15,
            "temp_max": 25,
            "max_rainfall": 5,
            "prevention": "Encourage natural predators (ladybird beetles); avoid excess nitrogen which favors aphid colonies.",
            "treatment": "Spray a recommended aphicide if colonies exceed threshold on flag leaves.",
            "estimated_cost_bdt_per_acre": 900,
        },
    ],
    "maize": [
        {
            "name": "Fall armyworm",
            "kind": "pest",
            "temp_min": 25,
            "temp_max": 32,
            "prevention": "Scout whorls weekly from emergence; intercrop with legumes to reduce moth landing.",
            "treatment": "Apply a recommended larvicide directly into the whorl at first sign of feeding damage.",
            "estimated_cost_bdt_per_acre": 1400,
        },
    ],
    "potato": [
        {
            "name": "Late blight",
            "kind": "disease",
            "min_humidity": 90,
            "temp_min": 10,
            "temp_max": 20,
            "prevention": "Use certified disease-free seed tubers, ensure good drainage, avoid overhead irrigation in cool humid weather.",
            "treatment": "Apply a protectant fungicide (e.g. mancozeb) preventively when cool+humid conditions persist; switch to a systemic fungicide if lesions appear.",
            "estimated_cost_bdt_per_acre": 2000,
        },
    ],
    "tomato": [
        {
            "name": "Tomato fruit borer",
            "kind": "pest",
            "temp_min": 25,
            "prevention": "Use pheromone traps to monitor moth activity; remove and destroy damaged fruit.",
            "treatment": "Apply a recommended insecticide targeted at egg-hatch stage.",
            "estimated_cost_bdt_per_acre": 1800,
        },
        {
            "name": "Early/late blight",
            "kind": "disease",
            "min_humidity": 85,
            "prevention": "Stake plants for airflow, avoid overhead watering, rotate away from solanaceous crops.",
            "treatment": "Apply a protectant fungicide at first leaf spotting.",
            "estimated_cost_bdt_per_acre": 1600,
        },
    ],
    "jute": [
        {
            "name": "Jute hairy caterpillar",
            "kind": "pest",
            "temp_min": 25,
            "min_humidity": 75,
            "prevention": "Hand-collect egg masses early in infestation; keep field bunds clean of alternate host weeds.",
            "treatment": "Apply a recommended insecticide if caterpillar density crosses threshold.",
            "estimated_cost_bdt_per_acre": 1000,
        },
    ],
    "sugarcane": [
        {
            "name": "Sugarcane stem borer",
            "kind": "pest",
            "temp_min": 25,
            "prevention": "Remove and destroy dead hearts early; avoid water stress which increases susceptibility.",
            "treatment": "Apply a recommended granular insecticide at the base of affected stalks.",
            "estimated_cost_bdt_per_acre": 1500,
        },
        {
            "name": "Red rot",
            "kind": "disease",
            "min_rainfall": 10,
            "min_humidity": 80,
            "prevention": "Use disease-free setts, avoid waterlogging, rotate out of sugarcane for a season if red rot was previously severe.",
            "treatment": "No effective in-season chemical treatment — rogue and destroy infected stools to limit spread.",
            "estimated_cost_bdt_per_acre": 800,
        },
    ],
    # Brassicas
    "cabbage": [
        {
            "name": "Diamondback moth",
            "kind": "pest",
            "temp_min": 20,
            "max_rainfall": 5,
            "prevention": "Rotate insecticide classes to avoid resistance; intercrop with tomato or non-brassica trap crops.",
            "treatment": "Apply a Bt-based (Bacillus thuringiensis) biopesticide, effective and low-risk for this pest.",
            "estimated_cost_bdt_per_acre": 1100,
        },
    ],
    "cauliflower": [
        {
            "name": "Diamondback moth",
            "kind": "pest",
            "temp_min": 20,
            "max_rainfall": 5,
            "prevention": "Rotate insecticide classes to avoid resistance; intercrop with non-brassica trap crops.",
            "treatment": "Apply a Bt-based biopesticide at first larval damage.",
            "estimated_cost_bdt_per_acre": 1100,
        },
    ],
    # Cucurbits
    "cucumber": [
        {
            "name": "Fruit fly",
            "kind": "pest",
            "temp_min": 25,
            "min_humidity": 70,
            "prevention": "Use pheromone/bait traps; bag young fruit or harvest promptly to reduce exposure.",
            "treatment": "Apply a recommended bait spray targeted at adult flies.",
            "estimated_cost_bdt_per_acre": 1000,
        },
    ],
    "pumpkin": [
        {
            "name": "Fruit fly",
            "kind": "pest",
            "temp_min": 25,
            "min_humidity": 70,
            "prevention": "Use pheromone/bait traps; remove and destroy fallen infested fruit.",
            "treatment": "Apply a recommended bait spray targeted at adult flies.",
            "estimated_cost_bdt_per_acre": 1000,
        },
    ],
    "bitter_gourd": [
        {
            "name": "Fruit fly",
            "kind": "pest",
            "temp_min": 25,
            "min_humidity": 70,
            "prevention": "Use pheromone/bait traps; bag young fruit.",
            "treatment": "Apply a recommended bait spray targeted at adult flies.",
            "estimated_cost_bdt_per_acre": 1000,
        },
    ],
    # Alliums
    "onion": [
        {
            "name": "Purple blotch",
            "kind": "disease",
            "min_humidity": 80,
            "temp_min": 20,
            "temp_max": 30,
            "prevention": "Avoid overhead irrigation, ensure good drainage, use disease-free sets.",
            "treatment": "Apply a mancozeb-based fungicide at first lesions.",
            "estimated_cost_bdt_per_acre": 1300,
        },
        {
            "name": "Thrips",
            "kind": "pest",
            "temp_min": 25,
            "max_rainfall": 5,
            "prevention": "Avoid water stress, which increases thrips susceptibility; use reflective mulch.",
            "treatment": "Apply a recommended insecticide if silvering damage exceeds a few leaves per plant.",
            "estimated_cost_bdt_per_acre": 900,
        },
    ],
    "garlic": [
        {
            "name": "Purple blotch",
            "kind": "disease",
            "min_humidity": 80,
            "temp_min": 20,
            "temp_max": 30,
            "prevention": "Avoid overhead irrigation, ensure good drainage.",
            "treatment": "Apply a mancozeb-based fungicide at first lesions.",
            "estimated_cost_bdt_per_acre": 1300,
        },
    ],
    # Rhizome spices
    "ginger": [
        {
            "name": "Rhizome rot",
            "kind": "disease",
            "min_rainfall": 15,
            "min_humidity": 85,
            "prevention": "Ensure raised beds and good drainage — this disease is driven almost entirely by waterlogging.",
            "treatment": "Drench soil with a copper-oxychloride or metalaxyl-based fungicide; remove and destroy affected clumps.",
            "estimated_cost_bdt_per_acre": 1800,
        },
    ],
    "turmeric": [
        {
            "name": "Rhizome rot",
            "kind": "disease",
            "min_rainfall": 15,
            "min_humidity": 85,
            "prevention": "Ensure raised beds and good drainage.",
            "treatment": "Drench soil with a copper-oxychloride or metalaxyl-based fungicide.",
            "estimated_cost_bdt_per_acre": 1800,
        },
    ],
    "brinjal": [
        {
            "name": "Brinjal fruit and shoot borer",
            "kind": "pest",
            "temp_min": 25,
            "min_humidity": 70,
            "prevention": "Prune and destroy wilted shoots promptly; use pheromone traps to monitor moths.",
            "treatment": "Apply a recommended insecticide targeted at egg-hatch stage before larvae bore in.",
            "estimated_cost_bdt_per_acre": 1500,
        },
    ],
    "okra": [
        {
            "name": "Yellow vein mosaic virus (whitefly-borne)",
            "kind": "disease",
            "temp_min": 28,
            "max_rainfall": 5,
            "prevention": "Control whitefly vectors, use yellow sticky traps, remove infected plants early.",
            "treatment": "No cure once infected — focus on vector control (insecticide or neem-based spray) to protect remaining plants.",
            "estimated_cost_bdt_per_acre": 1000,
        },
    ],
    "lentil": [
        {
            "name": "Pod borer",
            "kind": "pest",
            "temp_min": 22,
            "prevention": "Monitor with pheromone traps; encourage natural predators by avoiding broad-spectrum sprays early season.",
            "treatment": "Apply a recommended insecticide if pod damage exceeds threshold.",
            "estimated_cost_bdt_per_acre": 900,
        },
    ],
    "mustard": [
        {
            "name": "Mustard aphid",
            "kind": "pest",
            "temp_min": 15,
            "temp_max": 25,
            "max_rainfall": 5,
            "prevention": "Early sowing helps plants outgrow peak aphid pressure; encourage ladybird beetle predators.",
            "treatment": "Apply a recommended aphicide if colonies cover a significant share of the inflorescence.",
            "estimated_cost_bdt_per_acre": 900,
        },
    ],
}

# Fallback for crops without a specific entry above (e.g. minor pulses,
# oilseeds, root vegetables) — general soil/fungal risk under wet conditions,
# which is broadly true across most crops rather than crop-specific.
DEFAULT_PEST_RISKS: list[dict] = [
    {
        "name": "Root/collar rot (general)",
        "kind": "disease",
        "min_rainfall": 15,
        "min_humidity": 85,
        "prevention": "Ensure good field drainage; avoid waterlogging around the root zone.",
        "treatment": "Improve drainage immediately; apply a general-purpose fungicide drench if wilting appears.",
        "estimated_cost_bdt_per_acre": 1000,
    },
    {
        "name": "Sap-sucking insects (aphids/whitefly/jassids, general)",
        "kind": "pest",
        "temp_min": 25,
        "max_rainfall": 5,
        "prevention": "Monitor undersides of leaves weekly; encourage natural predators by minimizing broad-spectrum spraying.",
        "treatment": "Apply a recommended insecticide or neem-based spray if populations build up.",
        "estimated_cost_bdt_per_acre": 800,
    },
]
