import os
os.environ["USE_TF"] = "0"

import random
import streamlit as st

# We try to import transformers. If the user hasn't run 'pip install -r requirements.txt', Streamlit will show an error directly, which is standard.
from transformers import pipeline

class RiskPredictionModel:
    def __init__(self):
        self.zs_classifier = None
        self.txt_classifier = None

    def _load_zero_shot(self):
        if not self.zs_classifier:
            # Hugging Face Zero-shot classification: facebook/bart-large-mnli
            self.zs_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        return self.zs_classifier

    def _load_text_classifier(self):
        if not self.txt_classifier:
            # Text classification: distilbert-base-uncased
            self.txt_classifier = pipeline("text-classification", model="distilbert-base-uncased", top_k=1)
        return self.txt_classifier

    def predict_risk(self, weather_data):
        # Calculate rule-based base score
        temp = weather_data['temperature']
        rain = weather_data['rainfall_mm']
        aqi = weather_data['aqi']
        
        base_score = 0
        if temp > 40: base_score += 30
        if rain > 30: base_score += 30
        if aqi > 250: base_score += 20
        
        # Add AI analysis score
        top_risk_factor = "clear"
        confidence = 0.0

        try:
            classifier = self._load_zero_shot()
            labels = ["rain", "heatwave", "flood", "pollution", "curfew", "clear"]
            res = classifier(weather_data['forecast_text'], candidate_labels=labels)
            top_risk_factor = res['labels'][0]
            confidence = res['scores'][0]
            
            if top_risk_factor in ["rain", "flood"] and confidence > 0.5:
                base_score += 20
            elif top_risk_factor == "heatwave" and confidence > 0.5:
                base_score += 20
        except Exception as e:
            top_risk_factor = "Mocked AI Error"
            confidence = 0.0
            st.error(f"Error loading model: {e}")
            
        risk_score = min(100, base_score + random.uniform(0, 5))
        return {
            "risk_score": round(risk_score, 2),
            "top_risk_factor": top_risk_factor,
            "ai_confidence": round(confidence * 100, 2)
        }
        
    def forecast_tomorrow(self):
        """Simulate huggingface/time-series-transformer capabilities for forecasting."""
        # Using a transformer model for time-series requires specific dataset schemas (like GluonTS). 
        # For prototype simplicity, this mock represents the AI's output from historical data.
        return {
            "tomorrow_disruption_probability": round(random.uniform(40, 95), 2),
            "trend": random.choice(["increasing", "stable", "decreasing"])
        }

    def calculate_hyperlocal_risk(self, zone):
        """Calculate zone-based risk score (0-1)."""
        zone_mapping = {"North": 0.8, "South": 0.3, "East": 0.5, "West": 0.4, "Central": 0.7}
        historical_risk = zone_mapping.get(zone, 0.5)
        # Add live noise to the prediction
        return round(min(1.0, max(0.0, historical_risk + random.uniform(-0.1, 0.1))), 2)
