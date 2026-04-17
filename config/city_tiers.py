"""
City Tiers Configuration - JARVIS EnviroSense Assurance
Defines economic risk scaling for different Indian metropolitan/urban centers.
"""

CITY_TIERS = {
    "Chennai": {"tier": "Tier1", "base_risk_modifier": 1.20, "base_premium_modifier": 1.25, "payout_pressure": 1.35, "delivery_density": "EXTREME"},
    "Bangalore": {"tier": "Tier1", "base_risk_modifier": 1.15, "base_premium_modifier": 1.20, "payout_pressure": 1.30, "delivery_density": "EXTREME"},
    "Mumbai": {"tier": "Tier1", "base_risk_modifier": 1.25, "base_premium_modifier": 1.30, "payout_pressure": 1.40, "delivery_density": "EXTREME"},
    "Delhi": {"tier": "Tier1", "base_risk_modifier": 1.15, "base_premium_modifier": 1.20, "payout_pressure": 1.35, "delivery_density": "HIGH"},
    "Hyderabad": {"tier": "Tier2", "base_risk_modifier": 1.05, "base_premium_modifier": 1.10, "payout_pressure": 1.15, "delivery_density": "MODERATE"},
    "Coimbatore": {"tier": "Tier2", "base_risk_modifier": 0.95, "base_premium_modifier": 1.00, "payout_pressure": 1.05, "delivery_density": "MODERATE"},
    "Pune": {"tier": "Tier2", "base_risk_modifier": 1.00, "base_premium_modifier": 1.05, "payout_pressure": 1.10, "delivery_density": "MODERATE"},
    "Madurai": {"tier": "Tier3", "base_risk_modifier": 0.90, "base_premium_modifier": 0.90, "payout_pressure": 0.90, "delivery_density": "LOW"},
    "Trichy": {"tier": "Tier3", "base_risk_modifier": 0.85, "base_premium_modifier": 0.85, "payout_pressure": 0.85, "delivery_density": "LOW"},
    "Salem": {"tier": "Tier3", "base_risk_modifier": 0.85, "base_premium_modifier": 0.85, "payout_pressure": 0.85, "delivery_density": "LOW"}
}

def get_city_tier_context(city: str) -> dict:
    return CITY_TIERS.get(city, {"tier": "Tier2", "base_risk_modifier": 1.0, "base_premium_modifier": 1.0, "payout_pressure": 1.0, "delivery_density": "MODERATE"})
