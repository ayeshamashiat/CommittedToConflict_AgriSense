"""Citation registry for every real-world figure used in crop_data.py and
knowledge_base.py. Each entry is a short human-readable citation string;
keep these in sync with wherever a number/fact is actually used so the
provenance of "trustable" data is auditable, not just asserted.

Fetched and cross-checked directly from primary/official documents on
2026-07-24 (PDFs downloaded and parsed with pdftotext, not hallucinated).
"""

BBS_YEARBOOK_2024 = (
    "Bangladesh Bureau of Statistics, Yearbook of Agricultural Statistics-2024 "
    "(36th series, published June 2025), Table 2.1.1 (Area, Yield Rate and "
    "Production of Crops, FY2021-22 to 2023-24) and Table 10.1 (Monthly Average "
    "Wholesale Price) / retail price tables, Chapter 10."
)

USDA_GAIN_FERTILIZER_2026 = (
    "USDA Foreign Agricultural Service, GAIN Report BG2025-0017 'Fertilizer "
    "Situation in Bangladesh' (Dhaka Post, dated 2026-03-30), citing Bangladesh "
    "Ministry of Agriculture / DAE / BADC government-fixed retail fertilizer "
    "prices for FY2025-26."
)

RICE_FERTILIZER_DOSE_STUDY = (
    "Average actual Urea-TSP-MoP application rate for rice cultivation in "
    "Bangladesh (180-43-42 kg/ha), reported in peer-reviewed fertilizer-use "
    "research (PMC/ResearchGate: 'Unbalanced fertilizer use in the Eastern "
    "Gangetic Plain')."
)

SUGARCANE_PRICE_BSFIC = (
    "Bangladesh Sugar and Food Industries Corporation (BSFIC) mill-gate "
    "purchase price for sugarcane, 2024-25/2025-26 crushing season "
    "(~BDT 240-250/maund), as reported by The Daily Star and ChiniMandi."
)

CROP_CALENDAR_MULTI_SOURCE = (
    "Bangladesh crop season calendar (Aus: Mar-Apr sowing / Jul-Aug harvest; "
    "Aman: mid-Jul sowing / mid-Nov-Dec harvest; Boro: Nov-Dec sowing / "
    "Mar-Apr harvest; Rabi: mid-Oct to mid-Mar), cross-referenced from BBS "
    "Yearbook 2024 Sec 1.7-1.8 and agriculturistmusa.com / Banglapedia."
)

BRRI_VARIETIES = (
    "Bangladesh Rice Research Institute (BRRI) variety release data "
    "(brri.portal.gov.bd) as reported in BRRI achievement reports, The Daily "
    "Star, and The Business Standard coverage of BRRI dhan90-118 releases."
)

BARI_VARIETIES = (
    "Bangladesh Agricultural Research Institute (BARI, bari.gov.bd) variety "
    "release data for potato and mustard, as reported by Banglapedia and "
    "Lawyers & Jurists institutional summaries."
)

DAM_PRICE_NOTICE_2024 = (
    "Bangladesh Department of Agricultural Marketing (DAM), government-fixed "
    "wholesale/retail price notice for 29 agro products, dated March 2024 "
    "(reported by BSS News). Used in preference to BBS retail-2022 figures "
    "where the two overlap, since DAM is the mandated price-setting body and "
    "its notice is more recent."
)

FRG_2018_NOTE = (
    "The official Fertilizer Recommendation Guide 2018 (FRG-2018, Bangladesh "
    "Agricultural Research Council) publishes per-crop NPK/urea-TSP-MoP dose "
    "tables but blocks automated fetching via robots.txt; only the rice dose "
    "figure above (from a secondary peer-reviewed source) could be obtained "
    "without a manual browser download. Non-rice fertilizer costs below are "
    "estimated from rice's real dose, scaled by commonly cited relative "
    "fertilizer-intensity ratios, and are flagged accordingly."
)
