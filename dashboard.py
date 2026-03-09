import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import random

def render_worker_sidebar(workers_df):
    """Render the sidebar with worker selection and details."""
    st.sidebar.header("🛵 User Profile")
    selected_id = st.sidebar.selectbox("Select Delivery Worker", workers_df['worker_id'])
    worker = workers_df[workers_df['worker_id'] == selected_id].iloc[0]

    st.sidebar.markdown(f"""
    **Name:** {worker['name']}  
    **ID:** {worker['worker_id']}  
    **Zone:** {worker['zone']}  
    **Avg Hourly Earning:** ₹{worker['avg_hourly_earning']:.2f}  
    **Rating:** ⭐ {worker['rating']}
    """)
    return worker

def render_risk_gauge(risk_score):
    """Render a plotly gauge chart for the risk score."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        title={'text': "Disruption Risk", 'font': {'size': 20}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#1E90FF"},
            'steps': [
                {'range': [0, 40], 'color': "lightgreen"},
                {'range': [40, 70], 'color': "gold"},
                {'range': [70, 100], 'color': "tomato"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)

def render_heatmap():
    """Render a simulated physical heatmap of hyperlocal risk."""
    st.subheader("📍 Hyperlocal Zone Risk Map")
    map_data = pd.DataFrame({
        'lat': [28.6139 + random.uniform(-0.1, 0.1) for _ in range(30)],
        'lon': [77.2090 + random.uniform(-0.1, 0.1) for _ in range(30)],
        'risk': [random.uniform(0.1, 1.0) for _ in range(30)],
    })
    
    fig = px.scatter_mapbox(map_data, lat="lat", lon="lon", color="risk", size="risk",
                            color_continuous_scale=px.colors.sequential.Inferno, size_max=15, zoom=9.5,
                            mapbox_style="carto-positron")
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)
