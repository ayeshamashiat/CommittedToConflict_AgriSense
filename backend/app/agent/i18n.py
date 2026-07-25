"""Tier 2: Bengali (Bangla) language support.

Two separate concerns, both needed because Tier 0 requires the agent to keep
working with no LLM key configured:

1. LLM_BN_INSTRUCTION — appended to system prompts so the LLM (when
   available) writes its free text (clarifying questions, reasoning, replies)
   in Bengali instead of English.
2. The dictionaries below — deterministic Bengali strings for the exact same
   fallback paths that already exist in English (planner.FIELD_PROMPTS,
   explainer._default_reply, chat_responder's greeting/field-lookup text),
   so the agent still speaks Bengali even without an LLM key.

These are plain, standard Bengali phrasings a farmer would recognize — not
machine-translated filler — but are not "sourced" the way yield/price figures
are, since they're just language, not data.
"""

LLM_BN_INSTRUCTION = (
    "\n\nIMPORTANT: Respond in Bengali (Bangla script — বাংলা), not English. "
    "Keep any proper nouns (place names, crop names) recognizable but write "
    "all sentences in Bengali."
)

FIELD_PROMPTS_BN = {
    "location": "আপনার খামারটি কোথায় অবস্থিত (জেলা/উপজেলা)?",
    "farm_size": "আপনার জমির পরিমাণ কত? (একর, বিঘা, কাঠা বা শতাংশে বলতে পারেন।)",
    "soil_type": "আপনার মাটির ধরন কী (যেমন: এঁটেল, দোআঁশ, বেলে দোআঁশ)?",
    "water_availability": "আপনার জমিতে পানির প্রাপ্যতা কেমন (কম, মাঝারি, বেশি)?",
    "budget": "এই মৌসুমের জন্য আপনার বাজেট কত (টাকায়)?",
    "target_season": "আপনি কোন মৌসুমের জন্য পরিকল্পনা করছেন (যেমন: রবি, খরিফ)?",
}

FIELD_LOOKUP_LABELS_BN = {
    "farm_size": "জমির পরিমাণ",
    "location": "অবস্থান",
    "soil_type": "মাটির ধরন",
    "water_availability": "পানির প্রাপ্যতা",
    "budget": "বাজেট",
    "target_season": "মৌসুম",
}

GREETING_REPLY_BN_WITH_CROP = (
    "হ্যালো! এখনও আছি — আপনার সর্বশেষ সুপারিশ ছিল {crop}। এ বিষয়ে কিছু জিজ্ঞাসা "
    "করতে পারেন, অথবা খামারে কিছু পরিবর্তন হলে জানান।"
)
GREETING_REPLY_BN_NO_CROP = (
    "হ্যালো! যেকোনো প্রশ্ন করতে পারেন, অথবা আপনার খামার সম্পর্কে বলুন, আমি একটি "
    "পরিকল্পনা তৈরি করে দেব।"
)
CHAT_FALLBACK_BN = "আরেকটু বিস্তারিত বলবেন কি, আপনি কী জানতে চান?"

DEFAULT_REPLY_TEMPLATE_BN = (
    "{location}-এ আপনার {farm_size} একর জমির জন্য, যেখানে মাটি {soil_type} এবং পানির "
    "প্রাপ্যতা {water_availability}, {season} মৌসুমের জন্য শীর্ষ {count}টি ফসলের সুপারিশ, "
    "একটি মৌসুম পরিকল্পনা এবং {top}-এর জন্য আর্থিক সারসংক্ষেপ নিচে দেওয়া হলো।"
)
