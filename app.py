import os
# Force Transformers to use PyTorch and ignore broken TensorFlow installation
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

import streamlit as st
import pandas as pd
from data_loader import load_simulated_data, get_current_weather
from risk_model import RiskPredictionModel
from trigger_engine import check_triggers
from income_estimator import estimate_loss
from fraud_detector import FraudDetector
from payout_engine import process_payout, recommend_weekly_premium
import dashboard

st.set_page_config(page_title="GigShield AI", layout="wide", page_icon="🛡️")

# --- INITIALIZATION & MODEL LOADING ---
@st.cache_resource(show_spinner="Loading AI Models (Downloading Hugging Face weights on first run)...")
def init_models():
    # Cache the models to prevent reloading their weights on every UI interaction
    return RiskPredictionModel(), FraudDetector()

risk_model, fraud_model = init_models()
workers_df, logs_df, env_texts = load_simulated_data()

# --- HEADER SECTION ---
st.title("🛡️ GigShield AI — Parametric Income Protection")
st.markdown("An AI-driven micro-insurance platform that automatically protects food delivery workers from income loss caused by weather and environmental disruptions.")

# --- SIDEBAR ---
worker = dashboard.render_worker_sidebar(workers_df)

# --- PANEL 1: CURRENT CONDITIONS ---
weather_data = get_current_weather()

st.header("1. Risk Prediction Model")
cols = st.columns(4)
cols[0].metric("Temperature", f"{weather_data['temperature']} °C")
cols[1].metric("Rainfall", f"{weather_data['rainfall_mm']} mm")
cols[2].metric("AQI", f"{weather_data['aqi']}")
cols[3].metric("AI Forecast Scan", weather_data['forecast_text'])

# --- PANEL 2: AI INSIGHTS & RISK ---
st.markdown("### Hugging Face Analysis")
col_a, col_b = st.columns([2, 1])

with col_a:
    with st.spinner("Analyzing environment using Text & Zero-Shot Classification..."):
        risk_res = risk_model.predict_risk(weather_data)
        forecast = risk_model.forecast_tomorrow()
        zone_risk = risk_model.calculate_hyperlocal_risk(worker['zone'])
        
    st.markdown(f"""
    - **Primary Hazard Detected:** `{risk_res['top_risk_factor'].title()}` (AI Confidence: {risk_res['ai_confidence']}%)
    - **Tomorrow's Disruption Probability:** `{forecast['tomorrow_disruption_probability']}%` (Trend: {forecast['trend']})
    - **Hyperlocal Risk ({worker['zone']} Zone):** `{zone_risk}` (0.0 to 1.0)
    """)
    premium = recommend_weekly_premium(risk_res['risk_score'])
    st.info(f"💡 **AI Recommendation:** Suggested Weekly Premium for this worker profile: ₹{premium}")

with col_b:
    dashboard.render_risk_gauge(risk_res['risk_score'])


st.divider()

# --- PANEL 3: TRIGGER & PAYOUT ENGINE ---
st.header("2. Parametric Trigger & Payout Engine")

col_t1, col_t2 = st.columns(2)

with col_t1:
    st.subheader("Event Detection Settings")
    duration = st.slider("Simulate Disruption Duration (Hours)", 1, 12, 4, help="How long the worker couldn't work due to disruption.")
    
    st.markdown("Adjust GPS Movement to test the **Fraud Detection Engine**:")
    gps_movement = st.slider("Worker GPS Movement Score", 0, 15, 2, help="Score matching distance traveled. High movement during a 'disruption' indicates the worker might still be taking orders. (Anomalies get flagged as fraud)")
    
    is_triggered, triggers = check_triggers(weather_data, env_texts)
    
    if is_triggered:
        st.error("🚨 **Parametric Triggers Activated!**")
        for t in triggers:
            st.write(f"- {t}")
    else:
        st.success("✅ **No conditions met.** Weather is within safe working limits.")

with col_t2:
    st.subheader("Income Loss & Payout Pipeline")
    if is_triggered:
        loss = estimate_loss(worker['avg_hourly_earning'], duration)
        st.metric("Estimated Income Loss", f"₹{loss}")
        
        with st.spinner("Running Fraud Detection..."):
            is_fraud = fraud_model.detect_fraud(duration, loss, gps_movement)
            
        payout = process_payout(worker['worker_id'], triggers, loss, is_fraud)
        
        if is_fraud:
            st.warning(f"⚠️ **Fraud Alert:** {payout['message']}")
        else:
            st.success(f"✅ **Payout Approved!**")
            st.write(payout['message'])
            st.code(f"Simulated UPI Transaction: {payout['upi_txn_id']}")
    else:
        st.write("Awaiting trigger activation to analyze claims.")

st.divider()

# --- PANEL 4: COMMAND CENTER (MAP & LOGS) ---
st.header("3. Command Center")
col_c1, col_c2 = st.columns(2)

with col_c1:
    dashboard.render_heatmap()
    
with col_c2:
    st.subheader("Recent Delivery Logs")
    w_logs = logs_df[logs_df['worker_id'] == worker['worker_id']]
    st.dataframe(w_logs, use_container_width=True)

st.markdown("---")
st.caption("Powered by Transformers, Scikit-Learn, Streamlit, and FastAPI Backend Capabilities. Built for Hackathon.")
