"""
MODULE 4: PARAMETRIC EVENT DETECTION ENGINE
Detect disruption events based on environmental thresholds and alerts
"""
from typing import Dict, Any, List, Tuple
from config.settings import (
    RAINFALL_THRESHOLD_MM,
    TEMPERATURE_THRESHOLD_C,
    AQI_THRESHOLD,
)


class EventDetector:
    """Detect disruption events using parametric triggers."""

    def __init__(self):
        """Initialize event detector."""
        self.triggers_history = []

    def detect_event(self, rainfall_mm: float, temperature: float,
                    aqi: float, alert_texts: List[str] = None) -> Dict[str, Any]:
        """
        Detect disruption event based on thresholds.

        Process:
        1. Check parametric triggers:
           - Rainfall > 50mm → Heavy Rain
           - Temperature > 42°C → Heatwave
           - AQI > 300 → Pollution
        2. Check text-based alerts
        3. Return event_detected status and trigger list

        Args:
            rainfall_mm: Rainfall in mm
            temperature: Temperature in Celsius
            aqi: Air Quality Index
            alert_texts: Optional list of alert text strings

        Returns:
            Event detection result with details
        """
        triggers = []
        event_types = []

        # ===== RAINFALL CHECK =====
        if rainfall_mm > RAINFALL_THRESHOLD_MM:
            triggers.append(f"Rainfall > {RAINFALL_THRESHOLD_MM}mm ({rainfall_mm}mm detected)")
            event_types.append("Heavy Rain")

        # ===== TEMPERATURE CHECK =====
        if temperature > TEMPERATURE_THRESHOLD_C:
            triggers.append(f"Temperature > {TEMPERATURE_THRESHOLD_C}°C ({temperature}°C detected)")
            event_types.append("Heatwave")

        # ===== AQI CHECK =====
        if aqi > AQI_THRESHOLD:
            triggers.append(f"AQI > {AQI_THRESHOLD} ({aqi} detected)")
            event_types.append("Severe Pollution")

        # ===== TEXT-BASED ALERT CHECK =====
        if alert_texts:
            alert_trigger = self._check_text_alerts(alert_texts)
            if alert_trigger:
                triggers.append(alert_trigger["trigger"])
                event_types.append(alert_trigger["event_type"])

        # Determine if event is triggered
        is_triggered = len(triggers) > 0

        # Determine severity
        severity = self._calculate_severity(rainfall_mm, temperature, aqi)

        result = {
            "success": True,
            "event_detected": is_triggered,
            "trigger_count": len(triggers),
            "trigger_conditions": triggers,
            "event_types": event_types,
            "severity": severity,
        }

        if is_triggered:
            result["primary_event"] = event_types[0] if event_types else "Unknown"
            result["message"] = f"🚨 Event detected: {result['primary_event']}"
        else:
            result["message"] = "✅ No disruption events detected. Conditions are safe."

        # Store in history
        self.triggers_history.append({
            "timestamp": __import__('datetime').datetime.now(),
            "rainfall_mm": rainfall_mm,
            "temperature": temperature,
            "aqi": aqi,
            "triggered": is_triggered,
            "triggers": triggers,
        })

        return result

    def _check_text_alerts(self, alert_texts: List[str]) -> Dict[str, str] | None:
        """
        Check text-based government/news alerts.

        Args:
            alert_texts: List of alert text strings

        Returns:
            Alert trigger info or None
        """
        alert_keywords = {
            "flood": {"event_type": "Flooding", "severity": "High"},
            "curfew": {"event_type": "Curfew", "severity": "High"},
            "heatwave": {"event_type": "Heatwave", "severity": "High"},
            "severe weather": {"event_type": "Severe Weather", "severity": "High"},
            "storm": {"event_type": "Severe Weather", "severity": "High"},
            "cyclone": {"event_type": "Severe Weather", "severity": "Critical"},
            "lockdown": {"event_type": "Movement Restriction", "severity": "High"},
        }

        for text in alert_texts:
            text_lower = text.lower()
            for keyword, info in alert_keywords.items():
                if keyword in text_lower:
                    return {
                        "trigger": f"Alert: {text[:50]}...",
                        "event_type": info["event_type"],
                        "severity": info["severity"]
                    }

        return None

    def _calculate_severity(self, rainfall_mm: float, temperature: float,
                           aqi: float) -> str:
        """
        Calculate overall event severity.

        Args:
            rainfall_mm: Rainfall in mm
            temperature: Temperature in Celsius
            aqi: Air Quality Index

        Returns:
            Severity level ("None", "Low", "Medium", "High", "Critical")
        """
        severity_score = 0

        # Rainfall severity
        if rainfall_mm > 50:
            severity_score += 1
        if rainfall_mm > 100:
            severity_score += 1
        if rainfall_mm > 150:
            severity_score += 1

        # Temperature severity
        if temperature > 42:
            severity_score += 1
        if temperature > 45:
            severity_score += 1

        # AQI severity
        if aqi > 300:
            severity_score += 1
        if aqi > 400:
            severity_score += 1

        if severity_score == 0:
            return "None"
        elif severity_score <= 1:
            return "Low"
        elif severity_score <= 3:
            return "Medium"
        elif severity_score <= 5:
            return "High"
        else:
            return "Critical"

    def get_current_conditions(self, rainfall_mm: float, temperature: float,
                              aqi: float) -> Dict[str, Any]:
        """
        Get current weather condition summary.

        Args:
            rainfall_mm: Rainfall in mm
            temperature: Temperature in Celsius
            aqi: Air Quality Index

        Returns:
            Current conditions summary
        """
        return {
            "rainfall": {
                "value": rainfall_mm,
                "unit": "mm",
                "status": "Safe" if rainfall_mm <= RAINFALL_THRESHOLD_MM else "Alert",
                "threshold": RAINFALL_THRESHOLD_MM,
            },
            "temperature": {
                "value": temperature,
                "unit": "°C",
                "status": "Safe" if temperature <= TEMPERATURE_THRESHOLD_C else "Alert",
                "threshold": TEMPERATURE_THRESHOLD_C,
            },
            "aqi": {
                "value": aqi,
                "unit": "AQI",
                "status": "Safe" if aqi <= AQI_THRESHOLD else "Alert",
                "threshold": AQI_THRESHOLD,
            }
        }
