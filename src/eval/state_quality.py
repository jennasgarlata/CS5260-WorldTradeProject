from __future__ import annotations

import math
from typing import Dict

RESOURCE_WEIGHTS: Dict[str, float] = {}

HEGEMONY_WEIGHT = 500.0

# Extra bonus to encourage holding military-transform ingredients (even if CSV weight is 0)
MIL_READINESS_WEIGHT = 40.0  # tune: 40–200

EPS = 1e-9


def set_resource_weights(weights: dict):
    global RESOURCE_WEIGHTS
    RESOURCE_WEIGHTS = {str(k).strip(): float(v) for k, v in dict(weights).items()}


def _base_weighted_sum(country) -> float:
    # UNION of (weights keys) and (country resource keys)
    keys = set(RESOURCE_WEIGHTS.keys()) | set(country.resources.keys())
    total = 0.0
    for res in keys:
        w = float(RESOURCE_WEIGHTS.get(res, 0.0))
        total += w * float(country.get(res))
    return total


def _military_strength(country) -> float:
    """Uses explicit Military/MilitaryWaste if present. Otherwise returns 0."""
    mil = float(country.get("Military")) if "Military" in country.resources else 0.0
    waste = float(country.get("MilitaryWaste")) if "MilitaryWaste" in country.resources else 0.0
    return max(0.0, mil - waste)


def _hegemony_bonus(country_name: str, world_state) -> float:
    """
    In [-1, +1].
    Positive => this country has more Military than everyone else combined.
    """
    mil_self = _military_strength(world_state.get_country(country_name))

    mil_others = 0.0
    for other_name in world_state.countries.keys():
        if other_name == country_name:
            continue
        mil_others += _military_strength(world_state.get_country(other_name))

    return (mil_self - mil_others) / (mil_self + mil_others + EPS)


def _log_amt(country, key: str) -> float:
    """Diminishing returns; missing resource counts as 0."""
    if key not in country.resources:
        return 0.0
    return math.log1p(max(0.0, float(country.get(key))))


def _military_readiness(country) -> float:
    """
    Readiness should push you toward the *production chain* for Military:
    MetallicElements/Timber -> Alloys/Electronics -> Military

    We intentionally DO NOT reward Water/Energy here because they're abundant
    and easily 'gamed' via transfers in your current action space.
    """
    pops = _log_amt(country, "Population")
    alloys = _log_amt(country, "MetallicAlloys")
    elec = _log_amt(country, "Electronics")

    elements = _log_amt(country, "MetallicElements")
    timber = _log_amt(country, "Timber")

    # Wastes
    alloys_w = _log_amt(country, "MetallicAlloysWaste")
    elec_w = _log_amt(country, "ElectronicsWaste")
    mil_w = _log_amt(country, "MilitaryWaste")

    readiness = (
        3.0 * alloys +
        3.5 * elec +
        1 * elements +
        0.5 * timber +
        0.3 * pops +
        - 1.2 * alloys_w
        - 1.2 * elec_w
        - 2.0 * mil_w
    )
    return readiness


def Q(country_name: str, world_state) -> float:
    if not RESOURCE_WEIGHTS:
        raise ValueError("RESOURCE_WEIGHTS not set. Call set_resource_weights(weights) first.")

    c = world_state.get_country(country_name)

    base = _base_weighted_sum(c)
    readiness = _military_readiness(c)
    hegemony = _hegemony_bonus(country_name, world_state)

    return base + (MIL_READINESS_WEIGHT * readiness) + (HEGEMONY_WEIGHT * hegemony)