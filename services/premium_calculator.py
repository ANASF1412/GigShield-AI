"""
MODULE 3: DYNAMIC PREMIUM CALCULATION
Calculate weekly premium based on AI risk scoring.

Fix vs original:
  - Pass actual aqi/derived-severity into weather_data so risk score is context-sensitive
  - AQI is now used by predict_risk (original passed it in dict but model_loader ignored it;
    fixed model_loader now derives severity from aqi which feeds the model)
  - No ML logic here — all predictions go through ModelLoader
"""
from typing import Dict, Any
from services.model_loader import ModelLoader
from config.settings import PREMIUM_LOW_RISK, PREMIUM_MID_RISK, PREMIUM_HIGH_RISK


class PremiumCalculator:
    """Calculate insurance premiums based on ML risk assessment."""

    def __init__(self):
        self.model_loader = ModelLoader()

    def calculate_premium(self, rainfall_mm: float, temperature: float,
                          aqi: float) -> Dict[str, Any]:
        """Calculate recommended premium based on weather/environmental conditions."""
        try:
            weather_data = {
                "rainfall_mm": rainfall_mm,
                "temperature": temperature,
                "aqi": aqi,
                # severity + humidity + wind_speed derived inside ModelLoader
            }

            risk_score = self.model_loader.predict_risk(weather_data)

            if risk_score < 0.3:
                premium, risk_level = PREMIUM_LOW_RISK, "Low"
            elif risk_score < 0.7:
                premium, risk_level = PREMIUM_MID_RISK, "Medium"
            else:
                premium, risk_level = PREMIUM_HIGH_RISK, "High"

            return {
                "success": True,
                "risk_score": round(risk_score, 3),
                "risk_level": risk_level,
                "weekly_premium": premium,
                "ai_recommendation": self._get_recommendation(risk_score, premium),
                "breakdown": {
                    "rainfall_factor":    self._rainfall_impact(rainfall_mm),
                    "temperature_factor": self._temperature_impact(temperature),
                    "aqi_factor":         self._aqi_impact(aqi),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Premium calculation failed: {str(e)}",
                "risk_score": 0.5,
                "risk_level": "Medium",
                "weekly_premium": PREMIUM_MID_RISK,
                "ai_recommendation": "Unable to calculate — using default premium",
            }

    def _get_recommendation(self, risk_score: float, premium: float) -> str:
        if risk_score < 0.3:
            return f"✅ Low Risk — Recommended Premium: ₹{premium}/week. Weather conditions are stable."
        elif risk_score < 0.7:
            return f"⚠️ Medium Risk — Recommended Premium: ₹{premium}/week. Moderate disruption possible."
        else:
            return f"🚨 High Risk — Recommended Premium: ₹{premium}/week. Severe conditions expected."

    def _rainfall_impact(self, mm: float) -> Dict[str, Any]:
        if mm < 10:   return {"level": "Low",    "mm": mm}
        if mm < 50:   return {"level": "Medium",  "mm": mm}
        return {"level": "High", "mm": mm, "warning": "Heavy rainfall triggered"}

    def _temperature_impact(self, temp: float) -> Dict[str, Any]:
        if temp < 35: return {"level": "Low",    "celsius": temp}
        if temp < 42: return {"level": "Medium",  "celsius": temp}
        return {"level": "High", "celsius": temp, "warning": "Extreme heat triggered"}

    def _aqi_impact(self, aqi: float) -> Dict[str, Any]:
        if aqi < 200: return {"level": "Low",    "aqi": aqi}
        if aqi < 300: return {"level": "Medium",  "aqi": aqi}
        return {"level": "High", "aqi": aqi, "warning": "Severe pollution triggered"}

    def get_premium_tier_info(self) -> Dict[str, Any]:
        return {
            "low_risk":    {"risk_range": "< 0.3",     "premium": PREMIUM_LOW_RISK,  "description": "Stable weather conditions"},
            "medium_risk": {"risk_range": "0.3 – 0.7", "premium": PREMIUM_MID_RISK,  "description": "Moderate weather impacts"},
            "high_risk":   {"risk_range": "> 0.7",     "premium": PREMIUM_HIGH_RISK, "description": "Severe disruptions likely"},
        }
