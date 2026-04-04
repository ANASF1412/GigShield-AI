"""
MODULE 6: PREDICTIVE ALERTS
Forecast future disruption risks.

Fix vs original:
  - Removed random.uniform() from tomorrow_probability calculation.
    Random noise made forecasts non-deterministic and untestable.
  - Instead, apply a principled "weather trend factor":
      * If multiple triggers fire → +10% (conditions likely to persist)
      * If single trigger → +5%
      * Otherwise → -5% (regression to mean; isolated event unlikely to repeat)
  - No ML logic duplicated here — all predictions go through ModelLoader.
"""
from typing import Dict, Any
from services.model_loader import ModelLoader
from config.settings import RAINFALL_THRESHOLD_MM, TEMPERATURE_THRESHOLD_C, AQI_THRESHOLD
import numpy as np


class PredictiveAlertsService:
    """Generate predictive disruption alerts."""

    def __init__(self):
        self.model_loader = ModelLoader()

    def get_disruption_forecast(self, rainfall_mm: float, temperature: float,
                                aqi: float) -> Dict[str, Any]:
        """
        Forecast tomorrow's disruption probability.

        Uses today's risk score from the ML model as a baseline, then adjusts
        based on how many parametric thresholds are currently breached
        (multi-trigger events persist; single-trigger events tend to resolve).
        """
        try:
            risk_score = self.model_loader.predict_risk({
                "rainfall_mm": rainfall_mm,
                "temperature": temperature,
                "aqi": aqi,
            })

            # Count how many thresholds are currently breached
            active_triggers = sum([
                rainfall_mm > RAINFALL_THRESHOLD_MM,
                temperature > TEMPERATURE_THRESHOLD_C,
                aqi > AQI_THRESHOLD,
            ])

            # Principled persistence adjustment (no randomness)
            if active_triggers >= 2:
                trend_factor = +0.10   # multi-trigger events persist
            elif active_triggers == 1:
                trend_factor = +0.05   # single trigger may persist
            else:
                trend_factor = -0.05   # clear conditions likely to continue

            tomorrow_probability = float(
                np.clip((risk_score + trend_factor) * 100, 0, 100)
            )

            if tomorrow_probability > 70:
                trend      = "increasing"
                alert_text = "⚠️ HIGH RISK — Disruption likely tomorrow"
                color      = "red"
            elif tomorrow_probability > 40:
                trend      = "stable"
                alert_text = "⚡ MODERATE RISK — Possible disruption tomorrow"
                color      = "orange"
            else:
                trend      = "decreasing"
                alert_text = "✅ LOW RISK — Conditions expected to remain stable"
                color      = "green"

            return {
                "success": True,
                "current_risk_score":           round(risk_score, 3),
                "tomorrow_disruption_probability": round(tomorrow_probability, 1),
                "active_triggers":              active_triggers,
                "trend":                        trend,
                "alert_text":                   alert_text,
                "color":                        color,
            }

        except Exception as e:
            return {
                "success":                         False,
                "error":                           str(e),
                "tomorrow_disruption_probability": 50.0,
                "trend":                           "unknown",
                "alert_text":                      "⚠️ Forecast unavailable",
            }
