import streamlit as st
import folium
from streamlit_folium import st_folium

def render_admin_map(city_data: list, source_status: str = "LIVE API"):
    """
    Renders Folium Map using OpenStreetMap. No API keys required.
    city_data = [{"city": "Mumbai", "lat": 19.0760, "lon": 72.8777, "status": "SAFE", "aqi": 120, "rain": 0, "risk_score": 0.2, "zone_status": "🟢 SAFE"}]
    """
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles="OpenStreetMap")
    
    for d in city_data:
        color = 'green' if d['status'] == 'SAFE' else ('orange' if d['status'] == 'WATCH' else 'red')
        
        # Calculate radius scaled on risk_score (assuming max around 1.0)
        risk = float(d.get('risk_score', 0))
        radius = max(10, min(50, risk * 100)) # scale properly 
        
        popup_html = f"<b>{d['city']}</b><br/>AQI: {d['aqi']}<br/>Rain: {d['rain']}mm<br/>Risk: {d['risk_score']}<br/>Status: {d['zone_status']}"
        
        # Add basic marker pin
        folium.Marker(
            location=[d['lat'], d['lon']],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=d['city'],
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)
        
        # Add expanding circle for visual radius based on risk
        folium.CircleMarker(
            location=[d['lat'], d['lon']],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.3
        ).add_to(m)

    st_folium(m, use_container_width=True, height=500, returned_objects=[])

    legend_col1, legend_col2 = st.columns([1, 1.5])
    with legend_col1:
        st.caption(f"**Map Pipeline Trace:** `{source_status}`")
    with legend_col2:
        st.markdown("""
            <div style="display: flex; justify-content: flex-end; gap: 20px; font-size: 14px; padding-top: 5px;">
                <span>🟢 <b>Safe</b></span>
                <span>🟡 <b>Watch</b></span>
                <span>🔴 <b>Critical</b></span>
            </div>
        """, unsafe_allow_html=True)

def render_worker_map(lat: float, lon: float, city: str, source_status: str = "LIVE API"):
    """Worker local focused zone visualization."""
    st.caption(f"**Map Pipeline Trace:** `{source_status}`")
    m = folium.Map(location=[lat, lon], zoom_start=12, tiles="OpenStreetMap")
    
    folium.Marker(
        location=[lat, lon],
        popup=city,
        tooltip=city,
        icon=folium.Icon(color="red", icon="home")
    ).add_to(m)
    
    folium.CircleMarker(
        location=[lat, lon],
        radius=50,
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=0.2
    ).add_to(m)

    st_folium(m, use_container_width=True, height=400, returned_objects=[])
