from typing import Dict, Any

CITY_TIERS = {
    "Mumbai": {"tier": 1, "base_risk_modifier": 1.25, "base_premium_modifier": 1.30, "payout_pressure": 1.40, "delivery_density": "EXTREME"},
    "Chennai": {"tier": 1, "base_risk_modifier": 1.20, "base_premium_modifier": 1.25, "payout_pressure": 1.35, "delivery_density": "EXTREME"},
    "Bengaluru": {"tier": 1, "base_risk_modifier": 1.15, "base_premium_modifier": 1.25, "payout_pressure": 1.35, "delivery_density": "HIGH"},
    "Delhi": {"tier": 1, "base_risk_modifier": 1.15, "base_premium_modifier": 1.20, "payout_pressure": 1.30, "delivery_density": "HIGH"},
    "Pune": {"tier": 2, "base_risk_modifier": 1.05, "base_premium_modifier": 1.10, "payout_pressure": 1.15, "delivery_density": "MODERATE"},
    "Hyderabad": {"tier": 2, "base_risk_modifier": 1.05, "base_premium_modifier": 1.10, "payout_pressure": 1.15, "delivery_density": "MODERATE"},
    "Kochi": {"tier": 2, "base_risk_modifier": 1.10, "base_premium_modifier": 1.05, "payout_pressure": 1.10, "delivery_density": "MODERATE"},
    "Madurai": {"tier": 3, "base_risk_modifier": 0.95, "base_premium_modifier": 0.90, "payout_pressure": 0.90, "delivery_density": "LOW"},
    "Coimbatore": {"tier": 3, "base_risk_modifier": 0.90, "base_premium_modifier": 0.95, "payout_pressure": 0.90, "delivery_density": "LOW"},
}

def get_city_tier_info(city_name: str) -> Dict[str, Any]:
    return CITY_TIERS.get(city_name, {"tier": 2, "base_risk_modifier": 1.0, "base_premium_modifier": 1.0, "payout_pressure": 1.0, "delivery_density": "MODERATE"})
