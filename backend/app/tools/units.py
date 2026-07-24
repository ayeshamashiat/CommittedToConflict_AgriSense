"""Farm size unit conversion. All calculations run on acres internally;
farmers can enter size in whatever local unit they think in."""

FARM_SIZE_TO_ACRE: dict[str, float] = {
    "acre": 1.0,
    "bigha": 1 / 3,       # 3 bigha = 1 acre (Bangladesh standard)
    "katha": 1 / 60,      # 60 katha = 1 acre (20 katha = 1 bigha)
    "decimal": 1 / 100,   # 100 decimal = 1 acre
    "shotangsho": 1 / 100,  # shotangsho is the Bangla name for decimal
}


def to_acres(value: float, unit: str) -> float:
    key = unit.strip().lower()
    factor = FARM_SIZE_TO_ACRE.get(key)
    if factor is None:
        raise ValueError(
            f"Unknown farm size unit: {unit!r}. Supported: {list(FARM_SIZE_TO_ACRE)}"
        )
    return value * factor
