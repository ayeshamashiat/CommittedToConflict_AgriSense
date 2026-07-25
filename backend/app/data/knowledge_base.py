"""Seed passages for the RAG tool: short agronomy facts the agent can cite when
explaining why a crop is (or isn't) a good fit for a farmer's conditions.

Every entry's `source` field names the real institution/report the fact was
pulled from (see app/data/sources.py for full citations) instead of an
invented "agri-notes/*.md" path. A few entries (general soil-drainage facts)
are standard agronomy fundamentals rather than Bangladesh-specific figures;
those are labeled "general agronomy" rather than attributed to a BD source.
"""

KNOWLEDGE_BASE: list[dict] = [
    {
        "id": "rice-boro-variety",
        "source": "BRRI (Bangladesh Rice Research Institute) variety releases",
        "text": (
            "BRRI's high-yielding Boro (irrigated, winter-season) rice varieties "
            "such as BRRI dhan89 and BRRI dhan96 mature in 140-158 days and yield "
            "roughly 7 t/ha under good management. Boro needs clay or clay-loam "
            "soil that holds standing water and consistent irrigation, since it is "
            "grown outside the monsoon (planted Nov-Dec, harvested Mar-Apr)."
        ),
    },
    {
        "id": "rice-salt-tolerant-variety",
        "source": "BRRI variety releases (BRRI dhan97/dhan99/dhan112/dhan73)",
        "text": (
            "BRRI has released salinity-tolerant rice varieties (e.g. BRRI dhan97, "
            "dhan99 for Boro; dhan112, dhan73 for Aman) that tolerate 8-14 dS/m "
            "salinity and still yield 3.5-6.1 t/ha, making them a better fit than "
            "standard varieties for coastal or saline-affected farms."
        ),
    },
    {
        "id": "rice-drought-tolerant-variety",
        "source": "Bangladesh Rice Journal / BRRI (BRRI dhan66 variety development study)",
        "text": (
            "BRRI dhan66, approved in 2014 for T. Aman (wet season) cultivation, is "
            "a drought-tolerant rice variety bred for rainfed lowland areas without "
            "irrigation. It matures in 110-115 days and yields 4.5-5.0 t/ha even "
            "when soil moisture drops below 20% during the reproductive stage, "
            "making it a strong fit for drought-prone or unirrigated farms rather "
            "than the standard irrigated Boro varieties."
        ),
    },
    {
        "id": "rice-aus-variety",
        "source": "BRRI variety releases (BRRI dhan98/dhan106)",
        "text": (
            "For the Aus season (sown Mar-Apr, harvested Jul-Aug), short-duration "
            "BRRI varieties like dhan98 (112 days, ~5.1 t/ha) and dhan106 (117 "
            "days, ~4.8-5.5 t/ha, suited to non-saline tidal areas) fit farms with "
            "a shorter window between Boro harvest and Aman sowing."
        ),
    },
    {
        "id": "wheat-rabi-loam",
        "source": "BBS Yearbook of Agricultural Statistics-2024, crop calendar",
        "text": (
            "Wheat is a Rabi (dry winter) crop in Bangladesh, sown roughly "
            "mid-October to mid-March, and prefers well-drained loam or "
            "sandy-loam soil with moderate water. It performs poorly in "
            "waterlogged or high-rainfall conditions, making it risky where "
            "irrigation is unreliable."
        ),
    },
    {
        "id": "maize-drainage",
        "source": "BBS Yearbook of Agricultural Statistics-2024",
        "text": (
            "Maize is grown in both Rabi and Kharif seasons in Bangladesh and has "
            "become one of the highest-yielding cereals nationally (BBS reports "
            "roughly 6.9 t/ha for FY2023-24). It grows well in loam and "
            "sandy-loam soils with moderate water needs and good drainage."
        ),
    },
    {
        "id": "potato-bari-variety",
        "source": "BARI (Bangladesh Agricultural Research Institute) potato program",
        "text": (
            "BARI has released roughly 100 potato varieties (e.g. BARI Alu-7 / "
            "Diamant), some yielding 30-40 t/ha under good management. Potato "
            "needs sandy-loam soil, moderate water, and cool temperatures, and is "
            "a high-value Rabi crop but requires significant upfront capital for "
            "seed tubers."
        ),
    },
    {
        "id": "jute-kharif-water",
        "source": "BBS Yearbook of Agricultural Statistics-2024, crop calendar",
        "text": (
            "Jute is grown in the Kharif-I season (mid-March to end-June) and "
            "requires high water availability and warm, humid conditions. It "
            "grows well in clay-loam soil and remains a traditional cash fiber "
            "crop in Bangladesh's low-lying floodplains."
        ),
    },
    {
        "id": "mustard-bari-variety",
        "source": "BARI mustard program (BARI Sarisha-14)",
        "text": (
            "BARI Sarisha-14, released in 2006, raised mustard seed yields by up "
            "to 50% over local checks in intercropping systems. Mustard is a "
            "low-water, short-duration Rabi oilseed that grows well in loam and "
            "clay-loam soils, making it a good option for farmers with limited "
            "irrigation access and smaller budgets."
        ),
    },
    {
        "id": "lentil-rabi-nitrogen-fixing",
        "source": "BARI pulse research program",
        "text": (
            "Lentil (Masur) is a Rabi pulse that BARI varieties now cover on "
            "roughly 85% of national lentil area. It is drought-tolerant, needs "
            "minimal irrigation, suits loam or sandy-loam soils, and fixes "
            "nitrogen in the soil, benefiting the crop planted after it."
        ),
    },
    {
        "id": "tomato-intensive",
        "source": "general agronomy",
        "text": (
            "Tomato is a high-value vegetable needing loam soil, moderate and "
            "consistent watering, and intensive labor for staking and pest "
            "control. It gives strong returns but carries higher price-volatility "
            "risk than staple grain crops."
        ),
    },
    {
        "id": "onion-rabi-water",
        "source": "BBS Yearbook of Agricultural Statistics-2024",
        "text": (
            "Onion is typically planted in the Rabi season and prefers "
            "well-drained loam or clay-loam soil with moderate, evenly "
            "distributed watering; it is sensitive to both drought stress and "
            "waterlogging. Bangladesh's national average onion yield was about "
            "5.7 t/ha in FY2023-24."
        ),
    },
    {
        "id": "sugarcane-long-duration",
        "source": "BSFIC (Bangladesh Sugar and Food Industries Corporation)",
        "text": (
            "Sugarcane is a long-duration (10-12 month), high-water crop suited "
            "to clay-loam soils. It requires significant upfront investment but "
            "has a guaranteed mill-gate buyer: BSFIC set the 2024-25/2025-26 "
            "purchase price at roughly BDT 240-250 per maund, giving farmers "
            "price certainty that most other crops lack."
        ),
    },
    {
        "id": "soil-clay-general",
        "source": "general agronomy",
        "text": (
            "Clay soil retains water and nutrients well but drains slowly, making "
            "it best for water-loving crops like rice and jute, and risky for "
            "crops prone to root rot in waterlogged conditions."
        ),
    },
    {
        "id": "soil-sandy-loam-general",
        "source": "general agronomy",
        "text": (
            "Sandy-loam soil drains quickly and warms up fast in spring, suiting "
            "root vegetables like potato and onion, but it requires more frequent "
            "irrigation since it holds less water than clay or loam."
        ),
    },
    {
        "id": "season-rabi",
        "source": "BBS Yearbook of Agricultural Statistics-2024, Sec 1.7-1.8",
        "text": (
            "The Rabi season in Bangladesh runs roughly mid-October to "
            "mid-March: cool and dry, suiting wheat, mustard, lentil, potato, "
            "and onion, which need less water and cooler temperatures than "
            "monsoon crops."
        ),
    },
    {
        "id": "season-kharif-aus-aman",
        "source": "BBS Yearbook of Agricultural Statistics-2024, Sec 1.7-1.8",
        "text": (
            "The Kharif season runs roughly mid-March to mid-October and splits "
            "into Kharif-I (mid-March to June, Aus rice, jute) and Kharif-II "
            "(July to mid-October, Aman rice). It is warm and wet, driven by "
            "monsoon rainfall, and suits water-intensive crops."
        ),
    },
    {
        "id": "fertilizer-subsidy-prices",
        "source": "USDA GAIN Report BG2025-0017, citing Bangladesh Ministry of Agriculture",
        "text": (
            "The Government of Bangladesh fixes and subsidizes retail fertilizer "
            "prices: for FY2025-26, Urea and TSP are BDT 27/kg, MOP is BDT 21/kg, "
            "and DAP is BDT 20/kg. Urea is the dominant nitrogen source (split "
            "doses, especially in rice); TSP and DAP supply phosphorus as a basal "
            "dose; MOP supplies potassium and boosts stress tolerance."
        ),
    },
    {
        "id": "fertilizer-rice-dose",
        "source": "Peer-reviewed fertilizer-use study (Eastern Gangetic Plain)",
        "text": (
            "Average actual fertilizer application for rice cultivation in "
            "Bangladesh is about 180-43-42 kg/ha of Urea-TSP-MoP respectively, "
            "though farmers often apply more urea than the DAE-recommended rate, "
            "which increases production cost without proportionally raising yield."
        ),
    },
    {
        "id": "labor-wage-rate",
        "source": "BBS Yearbook of Agricultural Statistics-2024, Table 7.5",
        "text": (
            "The BBS reports a national daily agricultural wage (without food) "
            "of roughly BDT 480-680 depending on division, averaging around "
            "BDT 580/day. Labor-intensive crops like potato, onion, and tomato "
            "therefore carry a meaningfully higher labor cost per acre than "
            "lower-maintenance crops like lentil or mustard."
        ),
    },
    {
        "id": "budget-risk-tradeoff",
        "source": "general agronomy / market observation",
        "text": (
            "High-value crops like tomato, onion, and sugarcane require larger "
            "upfront budgets and carry higher price-volatility risk (BBS "
            "wholesale price series show onion prices swinging from ~27 to ~106 "
            "BDT/kg within a year), while staple and pulse crops like lentil and "
            "mustard need less capital and offer steadier, if lower, returns."
        ),
    },
]
