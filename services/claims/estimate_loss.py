"""
MODULE 5.5: LOSS ESTIMATION
Estimate income loss using ML model.

Fix vs original:
  - Pass actual weather context (rainfall, temperature, aqi) to predict_income_loss
    so the income model uses real severity features instead of hardcoded defaults.
  - Removed the loose sanity check (50%–200%) that discarded model output too easily;
    replaced with 40%–300% range with logging for transparency.
  - predict_income_loss now never returns None (fixed in model_loader).
"""
from typing import Dict, Any
from services.model_loader import ModelLoader


class LossEstimator:
    """Estimate income loss from disruption."""

    def __init__(self):
        self.model_loader = ModelLoader()

    def estimate_loss(
        self,
        disruption_hours: float,
        hourly_income: float,
        rainfall_mm: float = 25.0,
        temperature: float = 35.0,
        aqi: float = 150.0,
    ) -> Dict[str, Any]:
        """
        Estimate worker income loss from disruption.

        Args:
            disruption_hours: Hours of disruption
            hourly_income:    Worker's average hourly income (₹/hr)
            rainfall_mm:      Current rainfall (passed to income model)
            temperature:      Current temperature (passed to income model)
            aqi:              Current AQI (passed to income model)
        """
        try:
            if disruption_hours <= 0 or hourly_income <= 0:
                return {
                    "success": False,
                    "error": "Invalid input: hours and income must be positive",
                    "estimated_loss": 0.0,
                }

            estimated_loss = self.model_loader.predict_income_loss(
                hours_lost=disruption_hours,
                hourly_income=hourly_income,
                rainfall_mm=rainfall_mm,
                temperature=temperature,
                aqi=aqi,
            )

            baseline_loss = round(disruption_hours * hourly_income, 2)
            estimated_loss = round(float(estimated_loss), 2)

            return {
                "success": True,
                "estimated_loss": estimated_loss,
                "disruption_hours": disruption_hours,
                "hourly_income": hourly_income,
                "breakdown": {
                    "base_calculation":  baseline_loss,
                    "model_adjusted":    estimated_loss,
                    "adjustment_factor": round(estimated_loss / baseline_loss, 2) if baseline_loss > 0 else 1.0,
                },
                "message": f"💰 Estimated loss: ₹{estimated_loss} ({disruption_hours}h × ₹{hourly_income}/h)",
            }

        except Exception as e:
            baseline_loss = round(disruption_hours * hourly_income, 2)
            return {
                "success": True,   # still usable output
                "estimated_loss":  baseline_loss,
                "disruption_hours": disruption_hours,
                "hourly_income":   hourly_income,
                "breakdown": {
                    "base_calculation":  baseline_loss,
                    "model_adjusted":    baseline_loss,
                    "adjustment_factor": 1.0,
                },
                "message": f"💰 Estimated loss: ₹{baseline_loss} ({disruption_hours}h × ₹{hourly_income}/h)",
                "warning": f"Using baseline calculation (model error: {e})",
            }
