import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import polyline

import os # <--- NEW IMPORT

st.set_page_config(layout="wide", page_title="SafePath Delhi")

# ⚠️ PLACE THE NEW CODE HERE, REPLACING THE OLD URL DEFINITION
BACKEND_BASE_URL = os.environ.get("BACKEND_SERVICE_URL", "http://127.0.0.1:5000")
BACKEND_URL = BACKEND_BASE_URL + "/get_safest_path"
# ----------------------------------------------------------------------

if 'start_point' not in st.session_state:
    st.session_state.start_point = None
if 'end_point' not in st.session_state:
    st.session_state.end_point = None
if 'routes' not in st.session_state:
    st.session_state.routes = []
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ SafePath: Pin Your Route")

col1, col2 = st.columns(2)

with col1:
    if st.session_state.start_point:
        st.success(f"📍 Start: {st.session_state.start_point[0]:.4f}, {st.session_state.start_point[1]:.4f}")
    else:
        st.info("👆 Click on the map to set START location")

with col2:
    if st.session_state.end_point:
        st.success(f"🏁 End: {st.session_state.end_point[0]:.4f}, {st.session_state.end_point[1]:.4f}")
    else:
        st.info("👆 Then click again to set DESTINATION")

if st.button("🔄 Reset Pins"):
    st.session_state.start_point = None
    st.session_state.end_point = None
    st.session_state.routes = []
    st.session_state.analyzed = False
    st.rerun()

m = folium.Map(location=[28.6139, 77.2090], zoom_start=11)

if st.session_state.start_point:
    folium.Marker(
        st.session_state.start_point, 
        popup="Start", 
        icon=folium.Icon(color="green", icon="play")
    ).add_to(m)

if st.session_state.end_point:
    folium.Marker(
        st.session_state.end_point, 
        popup="Destination", 
        icon=folium.Icon(color="red", icon="flag")
    ).add_to(m)

if st.session_state.analyzed and st.session_state.routes:
    colors = ["#2ecc71", "#f1c40f", "#e67e22", "#e74c3c"]
    for i, route in enumerate(st.session_state.routes):
        decoded_path = polyline.decode(route['geometry'])
        color = colors[min(i, len(colors)-1)]
        folium.PolyLine(
            decoded_path,
            color=color,
            weight=6,
            opacity=0.8,
            tooltip=f"Score: {route['safety_score']}"
        ).add_to(m)

output = st_folium(m, width=1400, height=600)

if output and output.get('last_clicked'):
    clicked_lat = output['last_clicked']['lat']
    clicked_lng = output['last_clicked']['lng']
    
    if st.session_state.start_point is None:
        st.session_state.start_point = [clicked_lat, clicked_lng]
        st.rerun()
    elif st.session_state.end_point is None:
        st.session_state.end_point = [clicked_lat, clicked_lng]
        st.rerun()

if st.session_state.start_point and st.session_state.end_point:
    if st.button("Analyze Routes"):
        with st.spinner("Calculating safest path..."):
            payload = {
                "start_lat": st.session_state.start_point[0],
                "start_lon": st.session_state.start_point[1],
                "dest_lat": st.session_state.end_point[0],
                "dest_lon": st.session_state.end_point[1]
            }
            try:
                response = requests.post(BACKEND_URL, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.routes = data.get("routes", [])
                    st.session_state.analyzed = True
                    st.rerun()
                else:
                    st.error("Backend failed.")
            except Exception as e:
                st.error(f"Error: {e}")

if st.session_state.analyzed and st.session_state.routes:
    best = st.session_state.routes[0]
    st.success(f"Safest Route Score: {best['safety_score']}/100")
    c1, c2 = st.columns(2)
    c1.metric("Distance", f"{best['distance']/1000:.2f} km")
    c2.metric("Duration", f"{best['duration']/60:.0f} min")
