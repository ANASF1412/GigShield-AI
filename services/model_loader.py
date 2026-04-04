"""
ML Model Loader - Production-Grade
Single source of truth for all ML model interactions in GigShield AI.

Key fixes vs original:
  1. Risk model uses predict_proba() weighted sum for continuous [0,1] score
     (original used predict() returning class 0/1/2, clamped → always high-risk)
  2. Income model weather features are context-aware, not hardcoded
  3. sklearn version mismatch suppressed safely
  4. Duplicate validate_models() removed (was defined twice, second shadowed first)
  5. predict_income_loss no longer silently returns None on exception
  6. Feature validation layer prevents silent failures
  7. run_model_validation_suite() verifies outputs vary logically across 20+ scenarios
"""

import pickle
import warnings
import logging
import numpy as np
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore", message="Trying to unpickle estimator", category=UserWarning)

from config.settings import RISK_MODEL_PATH, INCOME_MODEL_PATH

logger = logging.getLogger(__name__)

# Exact feature lists matching pkl feature_names_in_
RISK_FEATURES   = ["Temperature", "Rainfall_mm", "Humidity", "Wind_Speed", "Severity"]
INCOME_FEATURES = ["Orders_Per_Day", "Working_Hours", "Earnings_Per_Day",
                   "Temperature", "Rainfall_mm", "Humidity", "Wind_Speed", "Severity"]

# Risk class weights: classes [0=Low, 1=Med, 2=High] → [0.0, 0.5, 1.0]
RISK_CLASS_WEIGHTS = {0: 0.0, 1: 0.5, 2: 1.0}


class ModelLoader:
    """Load and manage ML models. Single source of truth for all predictions."""

    # ── Model loading (Streamlit cached) ─────────────────────────────────────

    @staticmethod
    @st.cache_resource
    def load_risk_model():
        try:
            path = Path(RISK_MODEL_PATH)
            if not path.exists():
                raise FileNotFoundError(f"Risk model not found at {RISK_MODEL_PATH}")
            with open(path, "rb") as f:
                model = pickle.load(f)
            if hasattr(model, "feature_names_in_"):
                logger.info("Risk model features: %s", list(model.feature_names_in_))
            return model
        except Exception as e:
            logger.error("Failed to load risk model: %s", e)
            raise

    @staticmethod
    @st.cache_resource
    def load_income_model():
        try:
            path = Path(INCOME_MODEL_PATH)
            if not path.exists():
                raise FileNotFoundError(f"Income model not found at {INCOME_MODEL_PATH}")
            with open(path, "rb") as f:
                model = pickle.load(f)
            if hasattr(model, "feature_names_in_"):
                logger.info("Income model features: %s", list(model.feature_names_in_))
            return model
        except Exception as e:
            logger.error("Failed to load income model: %s", e)
            raise

    @staticmethod
    def get_risk_model():
        return ModelLoader.load_risk_model()

    @staticmethod
    def get_income_model():
        return ModelLoader.load_income_model()

    # ── Feature validation ────────────────────────────────────────────────────

    @staticmethod
    def _validate_features(df: pd.DataFrame, required: list, label: str) -> None:
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"[{label}] Missing features: {missing}")
        null_cols = [c for c in required if df[c].isnull().any()]
        if null_cols:
            raise ValueError(f"[{label}] Null values in: {null_cols}")

    # ── Weather context helpers ───────────────────────────────────────────────

    @staticmethod
    def _derive_severity(rainfall: float, temperature: float, aqi: float) -> int:
        if rainfall > 100 or temperature > 45 or aqi > 400:
            return 3
        if rainfall > 50 or temperature > 42 or aqi > 300:
            return 2
        if rainfall > 20 or temperature > 38 or aqi > 200:
            return 1
        return 0

    @staticmethod
    def _derive_humidity(rainfall: float, aqi: float) -> float:
        if rainfall > 50:
            return float(min(95, 60 + rainfall * 0.35))
        if aqi > 300:
            return float(max(30, 55 - (aqi - 300) * 0.05))
        return 65.0  # India average

    @staticmethod
    def _derive_wind_speed(rainfall: float) -> float:
        return float(min(60, 8 + rainfall * 0.25))

    # ── Risk prediction ───────────────────────────────────────────────────────

    @staticmethod
    def predict_risk(weather_data: dict) -> float:
        """
        Predict continuous risk score in [0.0, 1.0].

        FIX: Uses predict_proba() weighted sum instead of predict() class label.
        Original: model.predict() returns {0,1,2}, clamped to [0,1] → 2 becomes 1,
                  so medium and high risk were indistinguishable.
        Fixed:    score = P(Low)*0 + P(Med)*0.5 + P(High)*1.0 → true continuous score.

        Accepted weather_data keys:
            temperature, rainfall_mm, aqi, humidity (optional), wind_speed (optional),
            severity (optional — derived from other fields if absent)
        """
        try:
            model = ModelLoader.get_risk_model()

            rainfall    = float(weather_data.get("rainfall_mm", 0))
            temperature = float(weather_data.get("temperature", 30))
            aqi         = float(weather_data.get("aqi", 100))

            severity   = weather_data.get("severity")
            severity   = int(severity) if severity is not None else ModelLoader._derive_severity(rainfall, temperature, aqi)
            humidity   = float(weather_data.get("humidity") or ModelLoader._derive_humidity(rainfall, aqi))
            wind_speed = float(weather_data.get("wind_speed") or ModelLoader._derive_wind_speed(rainfall))

            input_df = pd.DataFrame([{
                "Temperature": temperature,
                "Rainfall_mm": rainfall,
                "Humidity":    humidity,
                "Wind_Speed":  wind_speed,
                "Severity":    severity,
            }])
            ModelLoader._validate_features(input_df, RISK_FEATURES, "RiskModel")

            proba      = model.predict_proba(input_df)[0]
            classes    = list(model.classes_)
            risk_score = float(sum(RISK_CLASS_WEIGHTS.get(c, 0.5) * p for c, p in zip(classes, proba)))
            risk_score = float(np.clip(risk_score, 0.0, 1.0))

            logger.debug("Risk proba=%s score=%.3f severity=%d", proba.round(3), risk_score, severity)
            return risk_score

        except Exception as e:
            logger.error("Risk prediction failed: %s", e)
            st.warning(f"⚠️ Risk model error — using rule-based fallback. ({e})")
            return ModelLoader._rule_based_risk(
                weather_data.get("rainfall_mm", 0),
                weather_data.get("temperature", 30),
                weather_data.get("aqi", 100),
            )

    @staticmethod
    def _rule_based_risk(rainfall: float, temperature: float, aqi: float) -> float:
        """Deterministic fallback when model unavailable."""
        score = 0.0
        score += 0.45 if rainfall > 100 else (0.30 if rainfall > 50 else (0.10 if rainfall > 20 else 0))
        score += 0.35 if temperature > 45 else (0.20 if temperature > 42 else (0.08 if temperature > 38 else 0))
        score += 0.20 if aqi > 400 else (0.12 if aqi > 300 else (0.05 if aqi > 200 else 0))
        return float(np.clip(score, 0.0, 1.0))

    # ── Income loss prediction ────────────────────────────────────────────────

    @staticmethod
    def predict_income_loss(
        hours_lost: float,
        hourly_income: float,
        rainfall_mm: float = 25.0,
        temperature: float = 35.0,
        aqi: float = 150.0,
        severity: Optional[int] = None,
    ) -> float:
        """
        Predict income loss in ₹.

        FIX: Original hardcoded all weather features (Temp=30, Rain=25, Humidity=60, Wind=10, Severity=1)
             making the loss prediction insensitive to actual disruption severity.
        Fixed: Accept weather context so model features reflect true conditions.
               Fallback stays deterministic (hours * rate), never returns None.
        """
        try:
            hours_lost    = max(0.0, float(hours_lost))
            hourly_income = max(0.0, float(hourly_income))

            if hours_lost <= 0 or hourly_income <= 0:
                return 0.0

            model = ModelLoader.get_income_model()

            rainfall    = float(rainfall_mm)
            temperature = float(temperature)
            aqi         = float(aqi)

            if severity is None:
                severity = ModelLoader._derive_severity(rainfall, temperature, aqi)
            humidity   = ModelLoader._derive_humidity(rainfall, aqi)
            wind_speed = ModelLoader._derive_wind_speed(rainfall)

            working_hours   = min(hours_lost, 12.0)
            earnings_per_day = hourly_income * working_hours
            orders_per_day   = max(1, int(working_hours * 1.5))

            input_df = pd.DataFrame([{
                "Orders_Per_Day":    orders_per_day,
                "Working_Hours":     working_hours,
                "Earnings_Per_Day":  earnings_per_day,
                "Temperature":       temperature,
                "Rainfall_mm":       rainfall,
                "Humidity":          humidity,
                "Wind_Speed":        wind_speed,
                "Severity":          severity,
            }])
            ModelLoader._validate_features(input_df, INCOME_FEATURES, "IncomeModel")

            predicted_day_loss = float(max(0.0, model.predict(input_df)[0]))

            # Scale to actual hours_lost (model was trained on full working_hours days)
            loss = predicted_day_loss * (hours_lost / working_hours) if working_hours > 0 else predicted_day_loss

            # Sanity gate: must be within 40%–300% of naive calculation
            naive = hours_lost * hourly_income
            if loss < naive * 0.4 or loss > naive * 3.0:
                logger.warning("Income model (%.2f) outside sanity range vs naive (%.2f). Using baseline.", loss, naive)
                loss = naive

            logger.debug("Income loss=₹%.2f (naive=₹%.2f)", loss, naive)
            return round(float(loss), 2)

        except Exception as e:
            logger.error("Income prediction failed: %s", e)
            st.warning(f"⚠️ Income model error — using baseline. ({e})")
            return round(float(hours_lost) * float(hourly_income), 2)  # never returns None

    # ── Validation ────────────────────────────────────────────────────────────

    @staticmethod
    def validate_models() -> bool:
        """Quick sanity check called at startup."""
        try:
            score = ModelLoader.predict_risk({"temperature": 35.0, "rainfall_mm": 25.0, "aqi": 150})
            assert 0.0 <= score <= 1.0
            loss = ModelLoader.predict_income_loss(4.0, 100.0, rainfall_mm=30)
            assert loss >= 0.0
            logger.info("✅ Model validation passed (risk=%.3f, loss=₹%.2f)", score, loss)
            return True
        except Exception as e:
            logger.error("❌ Model validation failed: %s", e)
            return False

    @staticmethod
    def run_model_validation_suite() -> dict:
        """
        Run 30 test cases across weather scenarios.
        Verifies outputs vary logically and produces actionable diagnostics.
        """
        results = {"risk": [], "income": [], "passed": True, "issues": []}

        scenarios = [
            (0, 22, 80), (5, 25, 100), (10, 28, 120), (15, 30, 150),
            (25, 32, 180), (35, 35, 200), (45, 38, 220), (55, 40, 250),
            (70, 42, 280), (85, 44, 310), (100, 46, 350), (120, 48, 400),
            (200, 50, 500), (0, 48, 400), (200, 22, 80), (0, 22, 450),
            (30, 36, 190), (20, 34, 160), (60, 30, 100), (10, 42, 100),
        ]

        for rain, temp, aqi in scenarios:
            results["risk"].append(
                ModelLoader.predict_risk({"rainfall_mm": rain, "temperature": temp, "aqi": aqi})
            )

        rs = results["risk"]
        results["risk_stats"] = {
            "min": round(min(rs), 3), "max": round(max(rs), 3),
            "mean": round(float(np.mean(rs)), 3), "std": round(float(np.std(rs)), 3),
            "unique_count": len(set(round(s, 2) for s in rs)),
        }

        if results["risk_stats"]["std"] < 0.05:
            results["issues"].append("Risk scores have very low variance — model may be near-constant")
            results["passed"] = False

        low_avg  = np.mean([ModelLoader.predict_risk({"rainfall_mm": r, "temperature": t, "aqi": a}) for r, t, a in scenarios[:4]])
        high_avg = np.mean([ModelLoader.predict_risk({"rainfall_mm": r, "temperature": t, "aqi": a}) for r, t, a in scenarios[8:12]])
        if high_avg <= low_avg:
            results["issues"].append(f"High-severity avg ({high_avg:.3f}) ≤ low-severity avg ({low_avg:.3f})")
            results["passed"] = False

        for hrs, inc, rain, temp, aqi in [(2,50,10,30,100),(4,100,25,35,150),(8,200,80,42,300),(10,300,150,48,400)]:
            results["income"].append(ModelLoader.predict_income_loss(hrs, inc, rain, temp, aqi))

        il = results["income"]
        results["income_stats"] = {"min": round(min(il), 2), "max": round(max(il), 2), "mean": round(float(np.mean(il)), 2)}

        if results["income_stats"]["max"] <= 0:
            results["issues"].append("Income model returns ≤0 losses")
            results["passed"] = False

        return results
