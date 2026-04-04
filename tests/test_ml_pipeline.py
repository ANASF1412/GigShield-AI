"""
pytest unit tests for GigShield AI ML pipeline.

Run from project root:
    cd project && python -m pytest tests/ -v

Tests cover:
  - ModelLoader.predict_risk(): continuous output, direction, edge cases
  - ModelLoader.predict_income_loss(): positive output, sanity range
  - ModelLoader.run_model_validation_suite(): suite passes
  - PremiumCalculator: tier mapping correctness
  - PredictiveAlertsService: deterministic output, no random noise
  - LossEstimator: output matches expectations
  - Feature validation: raises on bad input
"""

import sys
import os
import warnings
import pytest
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings("ignore")


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def model_loader():
    """Import ModelLoader once per test module."""
    from services.model_loader import ModelLoader
    return ModelLoader


@pytest.fixture(scope="module")
def premium_calc():
    from services.premium_calculator import PremiumCalculator
    return PremiumCalculator()


@pytest.fixture(scope="module")
def alerts_svc():
    from services.predictive_alerts import PredictiveAlertsService
    return PredictiveAlertsService()


@pytest.fixture(scope="module")
def loss_estimator():
    from services.claims.estimate_loss import LossEstimator
    return LossEstimator()


# ─── ModelLoader: predict_risk ─────────────────────────────────────────────────

class TestPredictRisk:

    def test_output_is_float(self, model_loader):
        score = model_loader.predict_risk({"rainfall_mm": 10, "temperature": 30, "aqi": 100})
        assert isinstance(score, float)

    def test_output_in_unit_range(self, model_loader):
        for rain, temp, aqi in [(0, 20, 50), (60, 42, 300), (150, 50, 500)]:
            score = model_loader.predict_risk({"rainfall_mm": rain, "temperature": temp, "aqi": aqi})
            assert 0.0 <= score <= 1.0, f"Score {score} out of [0,1] for R={rain} T={temp} AQI={aqi}"

    def test_high_severity_higher_than_low(self, model_loader):
        low_score  = model_loader.predict_risk({"rainfall_mm": 0,   "temperature": 22, "aqi": 80})
        high_score = model_loader.predict_risk({"rainfall_mm": 100, "temperature": 45, "aqi": 350})
        assert high_score > low_score, (
            f"High-severity score ({high_score:.3f}) must exceed low-severity ({low_score:.3f})"
        )

    def test_scores_vary_across_scenarios(self, model_loader):
        """Model must not return a constant value."""
        scores = [
            model_loader.predict_risk({"rainfall_mm": r, "temperature": t, "aqi": a})
            for r, t, a in [(0, 22, 80), (30, 35, 200), (100, 45, 350), (150, 50, 450)]
        ]
        std = float(np.std(scores))
        assert std > 0.05, f"Risk scores have very low variance (std={std:.4f}) — model may be constant"

    def test_deterministic_same_input(self, model_loader):
        """Same input must produce same output every time."""
        weather = {"rainfall_mm": 45, "temperature": 38, "aqi": 200}
        score_a = model_loader.predict_risk(weather)
        score_b = model_loader.predict_risk(weather)
        assert abs(score_a - score_b) < 1e-9, "predict_risk is not deterministic"

    def test_fallback_on_empty_input(self, model_loader):
        """Empty dict should trigger fallback, not crash."""
        score = model_loader.predict_risk({})
        assert 0.0 <= score <= 1.0

    def test_severity_derived_correctly(self, model_loader):
        """Heavy rain scenario should push risk score into medium-high range."""
        score = model_loader.predict_risk({"rainfall_mm": 80, "temperature": 30, "aqi": 100})
        assert score >= 0.3, f"Heavy rain should produce at least medium risk, got {score:.3f}"

    def test_heatwave_increases_risk(self, model_loader):
        """Temperature above threshold should increase risk vs mild temp."""
        mild_score = model_loader.predict_risk({"rainfall_mm": 5, "temperature": 25, "aqi": 100})
        heat_score = model_loader.predict_risk({"rainfall_mm": 5, "temperature": 45, "aqi": 100})
        assert heat_score > mild_score, "Heatwave must increase risk score"

    def test_pollution_increases_risk(self, model_loader):
        """AQI above 300 should increase risk vs clean air."""
        clean = model_loader.predict_risk({"rainfall_mm": 5, "temperature": 28, "aqi": 80})
        toxic = model_loader.predict_risk({"rainfall_mm": 5, "temperature": 28, "aqi": 400})
        assert toxic > clean, "Severe pollution must increase risk score"


# ─── ModelLoader: predict_income_loss ─────────────────────────────────────────

class TestPredictIncomeLoss:

    def test_output_is_positive(self, model_loader):
        loss = model_loader.predict_income_loss(4, 100)
        assert loss >= 0.0

    def test_zero_hours_returns_zero(self, model_loader):
        loss = model_loader.predict_income_loss(0, 100)
        assert loss == 0.0

    def test_zero_income_returns_zero(self, model_loader):
        loss = model_loader.predict_income_loss(4, 0)
        assert loss == 0.0

    def test_returns_float_not_none(self, model_loader):
        """Critical regression test: original code could return None on exception."""
        loss = model_loader.predict_income_loss(4, 100)
        assert loss is not None, "predict_income_loss must never return None"
        assert isinstance(loss, float)

    def test_higher_hours_higher_loss(self, model_loader):
        loss_2h = model_loader.predict_income_loss(2, 100)
        loss_8h = model_loader.predict_income_loss(8, 100)
        assert loss_8h > loss_2h, "More hours lost should produce higher estimated loss"

    def test_higher_income_higher_loss(self, model_loader):
        loss_low  = model_loader.predict_income_loss(4, 50)
        loss_high = model_loader.predict_income_loss(4, 200)
        assert loss_high > loss_low, "Higher income should produce higher estimated loss"

    def test_severe_weather_context_accepted(self, model_loader):
        """Model should accept and process severe weather context without error."""
        loss = model_loader.predict_income_loss(
            hours_lost=6, hourly_income=150,
            rainfall_mm=100, temperature=44, aqi=350
        )
        assert loss > 0.0

    def test_sanity_range_vs_naive(self, model_loader):
        """Loss should be within 40%-300% of naive hours*rate calculation."""
        hours, rate = 5, 120
        loss = model_loader.predict_income_loss(hours, rate)
        naive = hours * rate
        assert naive * 0.4 <= loss <= naive * 3.0, (
            f"Loss {loss:.2f} outside sanity range [{naive*0.4:.2f}, {naive*3.0:.2f}]"
        )


# ─── ModelLoader: validation suite ────────────────────────────────────────────

class TestValidationSuite:

    def test_suite_passes(self, model_loader):
        results = model_loader.run_model_validation_suite()
        assert results["passed"], f"Validation suite failed: {results['issues']}"

    def test_suite_has_risk_stats(self, model_loader):
        results = model_loader.run_model_validation_suite()
        stats = results.get("risk_stats", {})
        assert "min" in stats and "max" in stats and "std" in stats

    def test_risk_variance_in_suite(self, model_loader):
        results = model_loader.run_model_validation_suite()
        assert results["risk_stats"]["std"] >= 0.05, "Risk scores must vary across scenarios"

    def test_income_stats_positive(self, model_loader):
        results = model_loader.run_model_validation_suite()
        assert results["income_stats"]["mean"] > 0


# ─── PremiumCalculator ─────────────────────────────────────────────────────────

class TestPremiumCalculator:

    def test_low_conditions_produce_low_tier(self, premium_calc):
        result = premium_calc.calculate_premium(rainfall_mm=5, temperature=28, aqi=100)
        assert result["success"]
        assert result["risk_level"] == "Low"
        assert result["weekly_premium"] == 20.0

    def test_severe_conditions_produce_high_tier(self, premium_calc):
        result = premium_calc.calculate_premium(rainfall_mm=120, temperature=46, aqi=400)
        assert result["success"]
        assert result["risk_level"] == "High"
        assert result["weekly_premium"] == 45.0

    def test_risk_score_in_range(self, premium_calc):
        result = premium_calc.calculate_premium(rainfall_mm=30, temperature=35, aqi=200)
        assert 0.0 <= result["risk_score"] <= 1.0

    def test_breakdown_has_three_factors(self, premium_calc):
        result = premium_calc.calculate_premium(rainfall_mm=20, temperature=33, aqi=150)
        breakdown = result.get("breakdown", {})
        assert "rainfall_factor" in breakdown
        assert "temperature_factor" in breakdown
        assert "aqi_factor" in breakdown

    def test_returns_dict_on_failure(self, premium_calc):
        """Should return a fallback dict, not raise an exception."""
        # Force unusual inputs
        result = premium_calc.calculate_premium(rainfall_mm=-1, temperature=999, aqi=0)
        assert isinstance(result, dict)


# ─── PredictiveAlertsService ──────────────────────────────────────────────────

class TestPredictiveAlerts:

    def test_output_structure(self, alerts_svc):
        result = alerts_svc.get_disruption_forecast(10, 30, 120)
        assert "tomorrow_disruption_probability" in result
        assert "trend" in result
        assert "alert_text" in result

    def test_probability_in_range(self, alerts_svc):
        result = alerts_svc.get_disruption_forecast(80, 42, 310)
        prob = result["tomorrow_disruption_probability"]
        assert 0 <= prob <= 100

    def test_deterministic_no_randomness(self, alerts_svc):
        """Fix check: output must be deterministic (no random.uniform)."""
        r1 = alerts_svc.get_disruption_forecast(60, 40, 280)
        r2 = alerts_svc.get_disruption_forecast(60, 40, 280)
        assert r1["tomorrow_disruption_probability"] == r2["tomorrow_disruption_probability"], (
            "Forecast must be deterministic — remove any random.uniform() calls"
        )

    def test_severe_conditions_produce_high_prob(self, alerts_svc):
        result = alerts_svc.get_disruption_forecast(120, 46, 400)
        assert result["tomorrow_disruption_probability"] > 60, (
            "Severe weather should produce >60% disruption probability"
        )

    def test_calm_conditions_produce_low_prob(self, alerts_svc):
        result = alerts_svc.get_disruption_forecast(2, 24, 80)
        assert result["tomorrow_disruption_probability"] < 50


# ─── LossEstimator ────────────────────────────────────────────────────────────

class TestLossEstimator:

    def test_basic_estimate(self, loss_estimator):
        result = loss_estimator.estimate_loss(4, 100)
        assert result["success"]
        assert result["estimated_loss"] > 0

    def test_zero_hours_invalid(self, loss_estimator):
        result = loss_estimator.estimate_loss(0, 100)
        assert not result["success"]

    def test_negative_income_invalid(self, loss_estimator):
        result = loss_estimator.estimate_loss(4, -50)
        assert not result["success"]

    def test_weather_context_passed(self, loss_estimator):
        """Loss with severe weather should not error."""
        result = loss_estimator.estimate_loss(6, 150, rainfall_mm=90, temperature=43, aqi=330)
        assert isinstance(result, dict)
        assert "estimated_loss" in result

    def test_breakdown_fields(self, loss_estimator):
        result = loss_estimator.estimate_loss(4, 100)
        bd = result.get("breakdown", {})
        assert "base_calculation" in bd
        assert "model_adjusted" in bd
        assert "adjustment_factor" in bd

    def test_higher_hours_higher_loss(self, loss_estimator):
        r2 = loss_estimator.estimate_loss(2, 100)
        r8 = loss_estimator.estimate_loss(8, 100)
        assert r8["estimated_loss"] > r2["estimated_loss"]


# ─── Feature validation ────────────────────────────────────────────────────────

class TestFeatureValidation:

    def test_validate_features_raises_on_missing(self, model_loader):
        import pandas as pd
        df = pd.DataFrame([{"Temperature": 30, "Rainfall_mm": 10}])  # missing Humidity etc.
        with pytest.raises(ValueError, match="Missing features"):
            model_loader._validate_features(
                df,
                ["Temperature", "Rainfall_mm", "Humidity", "Wind_Speed", "Severity"],
                "TestModel"
            )

    def test_validate_features_raises_on_null(self, model_loader):
        import pandas as pd
        import numpy as np
        df = pd.DataFrame([{
            "Temperature": np.nan, "Rainfall_mm": 10,
            "Humidity": 60, "Wind_Speed": 10, "Severity": 1
        }])
        with pytest.raises(ValueError, match="Null values"):
            model_loader._validate_features(
                df,
                ["Temperature", "Rainfall_mm", "Humidity", "Wind_Speed", "Severity"],
                "TestModel"
            )

    def test_validate_features_passes_on_valid(self, model_loader):
        import pandas as pd
        df = pd.DataFrame([{
            "Temperature": 30, "Rainfall_mm": 10,
            "Humidity": 60, "Wind_Speed": 10, "Severity": 1
        }])
        # Should not raise
        model_loader._validate_features(
            df,
            ["Temperature", "Rainfall_mm", "Humidity", "Wind_Speed", "Severity"],
            "TestModel"
        )
