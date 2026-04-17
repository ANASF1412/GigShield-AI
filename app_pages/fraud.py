"""
Fraud Defense Dashboard - Phase 3 Final Polish
"""
import streamlit as st
import pandas as pd

def show():
    st.title("🛡️ Integrity Guard Intelligence")
    st.caption("Active monitoring of behavioral signatures to preserve system trust.")

    # 🔥 SECTION 4: FRAUD EXPLANATION BLOCK
    st.warning("""
    **Intelligence Insight:** Claims are evaluated using Isolation Forest and Multi-Sensor Fusion. 
    A claim is flagged if the kinetic signature or GPS displacement does not match the environmental disruption event.
    """)

    # FRAUD METRICS
    f1, f2, f3, f4 = st.columns(4)
    # 🔥 SECTION 4: FRAUD CONFIDENCE SCORE
    f1.metric("Fraud Confidence", "82%", help="System certainty in identifying adversarial patterns.")
    f2.metric("Anomalies Blocked", "42")
    f3.metric("Syndicate Risk", "Low")
    f4.metric("Engine Up-time", "100%")

    st.markdown("---")

    # GPS ANOMALY
    st.subheader("🕵️ Device Telemetry Analysis")
    gps_data = [
        {"Worker": "WP_992", "Variance": "4.1 km", "Status": "🚩 FLAG", "Insight": "Synthethic Stillness Detected"},
        {"Worker": "WP_110", "Variance": "0.2 km", "Status": "✅ OK", "Insight": "Verified Movement"},
        {"Worker": "WP_441", "Variance": "6.5 km", "Status": "🚩 FLAG", "Insight": "GPS Spoofing Pattern"},
    ]
    st.table(gps_data)
    
    # 🔥 SECTION 4: HUMAN-LIKE INSIGHT
    st.caption("💡 **System Insight:** Pattern matches known spoofing behavior from clustered claims in flood-simulated zones.")

    st.markdown("---")

    # WEATHER VALIDATION
    st.subheader("⛈️ Cross-Sensor Verification")
    w_col1, w_col2 = st.columns(2)
    
    with w_col1:
        with st.container(border=True):
            st.write("**Claim ID: CLM_88712**")
            st.metric("Rain (Claimed)", "65 mm")
            st.metric("Rain (Sensor)", "62 mm")
            st.success("VERIFIED: Correlation Coefficient 0.98")
        
    with w_col2:
        with st.container(border=True):
            st.write("**Claim ID: CLM_99212**")
            st.metric("Heat (Claimed)", "45°C")
            st.metric("Heat (Sensor)", "32°C")
            st.error("CONFLICT: Divergence Detected (>10°C)")

    st.markdown("---")
    st.subheader("🔗 Network Syndicate Watch")
    ring_data = [
        {"Zone": "DEL-NORTH", "Devices": 8, "Verdict": "🚩 SYNDICATE SUSPECTED", "Reason": "Identical IP Subnet"},
        {"Zone": "MUM-AND", "Devices": 12, "Verdict": "⚠️ MONITORING", "Reason": "Device ID Spikes"},
    ]
    st.dataframe(pd.DataFrame(ring_data), use_container_width=True, hide_index=True)
