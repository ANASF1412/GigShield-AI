"""
MODULE 5.4: DYNAMIC FRAUD INTELLIGENCE ENGINE
Advanced non-scripted risk assessment using behavioral and environmental cross-signals.
"""
from typing import Dict, Any, List
import numpy as np

class FraudChecker:
    """Production-grade dynamic fraud detection and explainability engine."""

    def __init__(self):
        """Initialize with detection thresholds."""
        pass

    def check_fraud(self, 
                    disruption_hours: float, 
                    estimated_loss: float,
                    gps_movement_score: float, 
                    temporal_cluster_flag: bool = False,
                    sensor_consistency_score: float = 1.0) -> Dict[str, Any]:
        """
        Compute dynamic fraud score from real behavioral signals.
        
        Logic:
        - GPS Displacement: High movement during claimed disruption.
        - Loss/Duration Ratio: Unusually high loss for short duration.
        - Temporal Anomaly: Multiple claims in same zone (cluster risk).
        - Sensor Integrity: Discrepancies in local weather reports.
        """
        explanations = []
        
        # 1. GPS MOVEMENT PENALTY (Base weight: 3x score)
        # Higher score = more movement while person was supposedly disrupted.
        gps_penalty = gps_movement_score * 3.0
        if gps_movement_score > 10:
            explanations.append("🚨 Critical GPS displacement detected during disruption window")
        elif gps_movement_score > 5:
            explanations.append("⚠️ Unusual movement recorded during claimed downtime")

        # 2. FINANCIAL ANOMALY (estimated_loss / 100)
        financial_penalty = estimated_loss / 100.0
        if estimated_loss > (disruption_hours * 500): # Hard cap for demo logic
             financial_penalty += 15
             explanations.append("💼 Loss amount is statistically high relative to disruption duration")

        # 3. TEMPORAL CLUSTER GUARD (Cluster Risk: +10)
        cluster_penalty = 10.0 if temporal_cluster_flag else 0.0
        if temporal_cluster_flag:
            explanations.append("📊 Cluster Anomaly: Multiple concurrent triggers in this zone detected")

        # 4. SENSOR CONSISTENCY GUARD (Inconsistency: +15)
        # Lower sensor_consistency_score means higher inconsistency
        sensor_inconsistency = (1.0 - sensor_consistency_score) * 20.0
        if sensor_consistency_score < 0.7:
            sensor_inconsistency += 15
            explanations.append("📡 Sensor Guard: Inconsistent data signatures across hyperlocal nodes")

        # TOTAL SCORE COMPUTATION
        fraud_score = gps_penalty + financial_penalty + cluster_penalty + sensor_inconsistency
        fraud_score = min(100.0, max(0.0, fraud_score))

        # FRAUD LEVEL GATING
        if fraud_score > 60:
            fraud_level = "CRITICAL"
            recommendation = "BLOCK"
        elif fraud_score >= 30:
            fraud_level = "WATCH"
            recommendation = "REVIEW"
        else:
            fraud_level = "SAFE"
            recommendation = "APPROVE"

        if not explanations:
            explanations.append("✅ Behavioral signatures within normal operational baseline")

        return {
            "success": True,
            "fraud_score": round(fraud_score, 2),
            "fraud_level": fraud_level,
            "recommendation": recommendation,
            "explanations": explanations,
            "details": {
                "gps_penalty": round(gps_penalty, 2),
                "financial_penalty": round(financial_penalty, 2),
                "cluster_penalty": cluster_penalty,
                "sensor_inconsistency": round(sensor_inconsistency, 2)
            }
        }
