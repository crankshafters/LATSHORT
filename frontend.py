import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import polyline
import json
import os

st.set_page_config(layout="wide", page_title="SafePath Delhi")

BACKEND_BASE_URL = os.environ.get("BACKEND_SERVICE_URL", "http://127.0.0.1:5000") 
BACKEND_URL = BACKEND_BASE_URL + "/get_safest_path"

if 'start_point' not in st.session_state:
    st.session_state.start_point = None
if 'end_point' not in st.session_state:
    st.session_state.end_point = None
if 'routes' not in st.session_state:
    st.session_state.routes = []
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'start_options' not in st.session_state:
    st.session_state.start_options = []
if 'end_options' not in st.session_state:
    st.session_state.end_options = []


st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }

    h1, h2, h3 {
        color: #ffffff;
        font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        min-width: 200px;
        white-space: pre-wrap;
        background-color: #1e293b;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: white;
        justify-content: center;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
    }

    [data-testid="stSidebar"] {
        background-color: #1a1d24;
        border-right: 1px solid #333;
    }
    
    [data-testid="column"] {
        background-color: #1e293b;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #334155;
        transition: transform 0.2s;
    }

    .stTextInput > div > div > input, 
    .stSelectbox > div > div > div > div {
        border-radius: 8px;
        color: white;
        background-color: #262730;
        border: 1px solid #4a4a4a;
    }

    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all 0.2s ease-in-out;
        border: none;
        padding: 0.6rem 1rem;
        background-color: #3b82f6;
        color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        background-color: #2563eb;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #10b981;
        font-weight: 700;
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8;
        font-weight: 500;
    }
    
    .stSuccess, .stInfo, .stError, .stWarning {
        border-radius: 8px;
        border-left-width: 5px;
        color: white;
        background-color: #1e293b;
    }
    .stSuccess div[data-testid="stMarkdownContainer"] p, 
    .stInfo div[data-testid="stMarkdownContainer"] p, 
    .stError div[data-testid="stMarkdownContainer"] p,
    .stWarning div[data-testid="stMarkdownContainer"] p {
        color: white !important; 
    }

    .score-key-box {
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 5px;
        color: white;
    }
    .score-key-green { background-color: #2ecc71; }
    .score-key-yellow { background-color: #f1c40f; }
    .score-key-orange { background-color: #e67e22; }
    .score-key-red { background-color: #e74c3c; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ SafePath: Delhi")

tab1, tab2, tab3 = st.tabs(["🗺️ Route Finder", "ℹ️ How Algorithm Works", "👥 About Us"])

current_dir =r"https://github.com/crankshafters/LATSHORT.git"
json_path = os.path.join(current_dir, "delhi_data.json")

def get_suggestions(place_name):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': place_name, 
            'format': 'json', 
            'limit': 5, 
            'addressdetails': 1,
            'countrycodes': 'in'
        }
        headers = {'User-Agent': 'SafePathHackathon/1.0'}
        r = requests.get(url, params=params, headers=headers)
        if r.status_code == 200:
            return r.json()
    except:
        return []
    return []

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📍 Start Location")
        s_col_1, s_col_2 = st.columns([3, 1])
        search_start = s_col_1.text_input("Search Start", placeholder="e.g. Connaught Place", label_visibility="collapsed")
        
        if s_col_2.button("Find", key="btn_find_start"):
            if search_start:
                results = get_suggestions(search_start)
                if results:
                    st.session_state.start_options = results
                else:
                    st.error("No locations found")
                    st.session_state.start_options = []
        
        if st.session_state.start_options:
            start_choices = {item['display_name']: [float(item['lat']), float(item['lon'])] for item in st.session_state.start_options}
            selected_start = st.selectbox("Select specific location:", list(start_choices.keys()), key="sb_start")
            if selected_start:
                st.session_state.start_point = start_choices[selected_start]

        if st.session_state.start_point:
            st.success(f"Selected: {st.session_state.start_point[0]:.4f}, {st.session_state.start_point[1]:.4f}")
        else:
            st.info("👆 Search or Click on map")

    with col2:
        st.subheader("🏁 Destination")
        d_col_1, d_col_2 = st.columns([3, 1])
        search_dest = d_col_1.text_input("Search Dest", placeholder="e.g. McDonalds Anand Vihar", label_visibility="collapsed")
        
        if d_col_2.button("Find", key="btn_find_dest"):
            if search_dest:
                results = get_suggestions(search_dest)
                if results:
                    st.session_state.end_options = results
                else:
                    st.error("No locations found")
                    st.session_state.end_options = []

        if st.session_state.end_options:
            end_choices = {item['display_name']: [float(item['lat']), float(item['lon'])] for item in st.session_state.end_options}
            selected_end = st.selectbox("Select specific location:", list(end_choices.keys()), key="sb_end")
            if selected_end:
                st.session_state.end_point = end_choices[selected_end]

        if st.session_state.end_point:
            st.success(f"Selected: {st.session_state.end_point[0]:.4f}, {st.session_state.end_point[1]:.4f}")
        else:
            st.info("👆 Search or Click on map")

    st.write("")
    if st.button("🔄 Reset Map"):
        st.session_state.start_point = None
        st.session_state.end_point = None
        st.session_state.routes = []
        st.session_state.analyzed = False
        st.session_state.start_options = []
        st.session_state.end_options = []
        st.rerun()

    m = folium.Map(location=[28.6139, 77.2090], zoom_start=11)

    st.sidebar.title("⚙️ Settings")
    st.sidebar.markdown("---")
    
    st.sidebar.subheader("Layer Controls")
    show_heatmap = st.sidebar.checkbox("Show Crime Heatmap", value=True)

    if show_heatmap:
        if os.path.exists(json_path):
            try:
                with open(json_path, "r") as f:
                    geo_data = json.load(f)
                    
                folium.GeoJson(
                    geo_data,
                    name="High Risk Zones",
                    style_function=lambda feature: {
                        "fillColor": "#ff0000",
                        "color": "#ff0000",
                        "weight": 1,
                        "fillOpacity": 0.3,
                    },
                    tooltip="High Crime Zone: Caution Advised"
                ).add_to(m)
            except Exception as e:
                st.sidebar.error(f"Error loading heatmap: {e}")
        else:
            st.sidebar.warning(f"Heatmap data not found.")

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
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("Route Filter")
        
        def get_route_color(score):
            if score >= 75: return "#2ecc71"
            elif score >= 50: return "#f1c40f"
            elif score >= 25: return "#e67e22"
            else: return "#e74c3c"

        min_safety_threshold = st.sidebar.slider("Minimum Safety Score", 0, 100, 50, help="Only routes with a score above this value will be displayed.")

        routes_to_display = [r for r in st.session_state.routes if r['safety_score'] >= min_safety_threshold]
        
        if not routes_to_display:
            st.sidebar.warning("No routes meet the minimum safety threshold.")

        for i, route in enumerate(routes_to_display):
            decoded_path = polyline.decode(route['geometry'])
            color = get_route_color(route['safety_score'])
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
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🕒 Time of Travel")
        travel_hour = st.sidebar.slider("Hour (24h)", 0, 23, 14, help="Affects safety score based on lighting")
        
        if st.button("🚀 Analyze Safest Route"):
            with st.spinner("Analyzing crime data, lighting, and police stations..."):
                payload = {
                    "start_lat": st.session_state.start_point[0],
                    "start_lon": st.session_state.start_point[1],
                    "dest_lat": st.session_state.end_point[0],
                    "dest_lon": st.session_state.end_point[1],
                    "hour": travel_hour
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
        st.markdown("### 🏆 Recommended Route")
        st.success(f"Safest Route Score: {best['safety_score']}/100")
        
        c1, c2 = st.columns(2)
        c1.metric("Distance", f"{best['distance']/1000:.2f} km")
        c2.metric("Duration", f"{best['duration']/60:.0f} min")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Safety Score Key")
    st.sidebar.markdown('<div class="score-key-box score-key-green">75-100: Very Safe (Recommended)</div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="score-key-box score-key-yellow">50-74: Moderate Risk</div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="score-key-box score-key-orange">25-49: High Risk / Low Lighting</div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="score-key-box score-key-red">0-24: Extreme Caution</div>', unsafe_allow_html=True)
    st.sidebar.markdown('Routes are color-coded based on these ranges.')


with tab2:
    st.header("ℹ️ How SafePath Works")
    st.markdown("""
    SafePath isn't just a map; it's a **Risk Assessment Engine**. Unlike Google Maps which optimizes for *Speed*, we optimize for *Safety*.
    
    ### 1. Hybrid Data Engine
    We combine three data sources to calculate safety:
    * **Local Police Data:** GeoJSON polygons defining high-crime zones (Red zones on map).
    * **Latlong.ai Intelligence:** We scan every 50 meters of the route for real-time infrastructure (Police Stations, Hospitals, ATMs).
    * **Environmental Factors:** Time of day and street lighting conditions.

    ### 2. The Algorithm
    For every possible route, we calculate a **Safety Score (0-100)**:
    * **Start:** 100 Points.
    * **Penalty:** -20 for entering a High Crime Zone.
    * **Penalty:** -5 for proximity to liquor stores/bars at night.
    * **Bonus:** +2 for proximity to Hospitals, Police Stations, and Metro Stations.
    * **Time Multiplier:** Penalties are 1.5x stricter after 8 PM.
    
    ### 3. Architecture
    * **Frontend:** Streamlit + Folium
    * **Backend:** Flask API + Shapely (Geometric Calculations)
    * **Routing:** OSRM (Open Source Routing Machine)
    """)

with tab3:
    st.header("👥 About Team SafePath")
    
    st.markdown("### The Vision: Safety-First Navigation")

    st.markdown("""
    **Problem Statement:**
    Traditional route planning is flawed because it prioritizes efficiency (shortest distance or fastest time) over human safety. For pedestrians, especially those traveling late at night, this oversight is critical and potentially dangerous. Current maps are optimized for cars, not people.

    **Our Solution (Goal):**
    To create the first line of defense in urban navigation by providing an **AI-Powered Safe Routing System (SafePath)** that optimizes paths based on **risk minimization**. By combining real-time infrastructure data (from Latlong.ai) with historical crime data and environmental factors (like lighting), we empower users to make informed, safer travel decisions.
    """)
    
    st.markdown("---")

    st.markdown("### Our Team")
    st.write("We are a team of dedicated developers participating in the [Hackathon Name] to build practical solutions leveraging geospatial data.")
    
    col_row_1 = st.columns(2)
    col_row_2 = st.columns(2)

    col_row_1[0].markdown("**Tanay Shah**")
    col_row_1[0].caption("Lead Developer")

    col_row_1[1].markdown("**S Sanjay**")
    col_row_1[1].caption("Front-end Engineer")
    
    col_row_2[0].markdown("**Kishaann Karthik**")
    col_row_2[0].caption("Data Analyst")
    
    col_row_2[1].markdown("**Ishaan Bhatia**")
    col_row_2[1].caption("Back-end Engineer")
    
    st.markdown("---")
    st.markdown("### Key Takeaway for Judges")
    st.info("SafePath moves beyond calculating the *shortest* path—it calculates the **smartest** path.")
