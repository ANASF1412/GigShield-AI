from datasets import load_dataset
import pandas as pd
import random
from datetime import datetime, timedelta
import streamlit as st

@st.cache_data
def load_simulated_data():
    """Load Hugging Face dataset and mock worker profiles/logs."""
    try:
        # Load a tiny slice of climate_fever to fulfill requirement
        dataset = load_dataset("climate_fever", split='test[:20]')
        texts = [item['claim'] for item in dataset]
    except Exception:
        texts = [
            "Heavy rain and severe flood alert for the coastal region.",
            "Temperature expected to rise above 40°C causing severe heatwave.",
            "Air quality index drops to severe category.",
            "Curfew in effect due to severe weather conditions."
        ]

    # Generate mock worker profiles
    workers = []
    for i in range(1, 11):
        workers.append({
            "worker_id": f"W{i:03d}",
            "name": f"Worker {i}",
            "avg_hourly_earning": round(random.uniform(80, 150), 2),
            "zone": random.choice(["North", "South", "East", "West", "Central"]),
            "rating": round(random.uniform(3.5, 5.0), 1)
        })

    # Generate recent delivery logs
    logs = []
    platforms = ["Zomato", "Swiggy"]
    for w in workers:
        for _ in range(5):
            logs.append({
                "worker_id": w["worker_id"],
                "platform": random.choice(platforms),
                "date": (datetime.now() - timedelta(days=random.randint(0, 5))).strftime("%Y-%m-%d"),
                "deliveries": random.randint(5, 20),
                "earnings": round(random.uniform(300, 1500), 2)
            })

    return pd.DataFrame(workers), pd.DataFrame(logs), texts

def get_current_weather():
    """Simulate real-time weather data for the dashboard."""
    return {
        "temperature": round(random.uniform(30, 45), 1),
        "rainfall_mm": round(random.uniform(0, 100), 1),
        "aqi": round(random.uniform(100, 350), 1),
        "forecast_text": random.choice([
            "Heavy rain expected tomorrow", 
            "Clear skies, sunny day", 
            "Severe heatwave alert", 
            "High pollution levels, poor visibility",
            "Monsoon expected to cause severe flood"
        ])
    }
