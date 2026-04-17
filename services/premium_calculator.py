"""
MODULE 3: DYNAMIC PREMIUM CALCULATION
Calculate weekly premium based on AI risk scoring and Economic City Tier scaling.
"""
from typing import Dict, Any, Optional
from services.model_loader import ModelLoader
from services.ncb_service import NCBService
from services.repositories.worker_repository import WorkerRepository
from config.settings import PREMIUM_LOW_RISK, PREMIUM_MID_RISK, PREMIUM_HIGH_RISK
from config.city_tiers import get_city_tier_context

class PremiumCalculator:
    """Calculate insurance premiums based on ML risk assessment and Advanced City Tiers."""

    def __init__(self):
        self.model_loader = ModelLoader()
        self.worker_repo = WorkerRepository()

    def calculate_premium(self, rainfall_mm: float, temperature: float,
                          aqi: float, city: str = "Chennai", worker_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate premium based on environmental conditions and City Tier multiplier.
        """
        try:
            weather_data = {
                "rainfall_mm": rainfall_mm,
                "temperature": temperature,
                "aqi": aqi,
            }

            base_risk_score = self.model_loader.predict_risk(weather_data)
            
            # --- CITY TIER ECONOMIC SCALING (Step 3 Integration) ---
            city_ctx = get_city_tier_context(city)
            city_tier = city_ctx["tier"]
            risk_modifier = city_ctx["base_risk_modifier"]
            premium_modifier = city_ctx["base_premium_modifier"]
            
            # Adjust final risk perception based on city tier risk modifier
            risk_score = min(1.0, base_risk_score * risk_modifier)

            if risk_score < 0.3:
                base_premium, risk_level = PREMIUM_LOW_RISK, "Low"
            elif risk_score < 0.7:
                base_premium, risk_level = PREMIUM_MID_RISK, "Medium"
            else:
                base_premium, risk_level = PREMIUM_HIGH_RISK, "High"

            # Scale premium by explicit tier premium modifier
            base_tier_premium = round(base_premium * premium_modifier, 2)
            
            # --- NCB INTEGRATION ---
            streak = 0
            if worker_id:
                worker = self.worker_repo.get_worker(worker_id)
                if worker: streak = worker.get("ncb_streak", 0)
                
            ncb_data = NCBService.calculate_final_premium(base_tier_premium, streak)
            final_premium = ncb_data["final_premium"]

            return {
                "success": True,
                "risk_score": round(risk_score, 3),
                "risk_level": risk_level,
                "city_tier": city_tier,
                "tier_multiplier": premium_modifier,
                "base_premium": base_tier_premium,
                "weekly_premium": final_premium,
                "ncb_discount_rate": ncb_data["ncb_discount_rate"],
                "ncb_streak": ncb_data["ncb_streak"],
                "savings_amount": ncb_data["savings_amount"],
                "final_premium": final_premium,
                "ncb_tier_label": ncb_data["ncb_tier_label"],
                "ai_recommendation": self._get_recommendation(risk_score, final_premium, city_tier, city),
                "breakdown": {
                    "rainfall_factor":    rainfall_mm,
                    "temperature_factor": temperature,
                    "aqi_factor":         aqi,
                    "tier_adj_risk":      risk_modifier,
                    "tier_adj_premium":   premium_modifier
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Premium calculation failed: {str(e)}",
                "risk_score": 0.5,
                "risk_level": "Medium",
                "weekly_premium": PREMIUM_MID_RISK,
            }

    def _get_recommendation(self, risk_score: float, premium: float, tier: str, city: str) -> str:
        tier_msg = f"Premium adjusted because {city} is a {tier} city with elevated payout pressure."
        if risk_score < 0.3:
            return f"✅ Low Risk — Recommended: ₹{premium}/week. {tier_msg}"
        elif risk_score < 0.7:
            return f"⚠️ Medium Risk — Recommended: ₹{premium}/week. {tier_msg}"
        else:
            return f"🚨 High Risk — Recommended: ₹{premium}/week. {tier_msg}"
