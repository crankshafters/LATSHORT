import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import polyline
import json
import os
import time

# 1. SETUP PAGE CONFIG
st.set_page_config(layout="wide", page_title="SafePath Delhi")

# 2. SESSION STATE INITIALIZATION
if 'show_home' not in st.session_state:
    st.session_state.show_home = True
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

# --- CONFIG FOR BACKEND ---
BACKEND_BASE_URL = os.environ.get("BACKEND_SERVICE_URL", "http://127.0.0.1:5000")
BACKEND_URL = BACKEND_BASE_URL + "/get_safest_path"

# ==========================================
# 🏠 HOME SCREEN (LIQUID GLASS THEME)
# ==========================================
def show_home_screen():
    st.markdown("""
        <style>
        /* Overall Page Background - Deep Black */
        .stApp {
            background-color: #000000;
            background-image: radial-gradient(circle at 50% 50%, #111111 0%, #000000 100%);
        }
        
        /* Hide standard streamlit elements on home */
        [data-testid="stHeader"] {visibility: hidden;}
        
        /* Container for the Glass Effect */
        .glass-container {
            position: relative;
            height: 80vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }

        /* The Animated Liquid Blobs */
        .blob {
            position: absolute;
            filter: blur(60px);
            z-index: 0;
            opacity: 0.6;
            animation: float 10s infinite ease-in-out alternate;
        }
        .blob-1 {
            top: 20%;
            left: 30%;
            width: 300px;
            height: 300px;
            background: linear-gradient(135deg, #0052D4, #4364F7);
            border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%;
        }
        .blob-2 {
            bottom: 20%;
            right: 30%;
            width: 350px;
            height: 350px;
            background: linear-gradient(135deg, #6FB1FC, #0052D4);
            border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
            animation-delay: -5s;
        }

        @keyframes float {
            0% { transform: translate(0, 0) rotate(0deg); }
            100% { transform: translate(30px, 50px) rotate(20deg); }
        }

        /* The Glossy Glass Card */
        .glass-card {
            z-index: 1;
            background: rgba(20, 20, 20, 0.4);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-top: 1px solid rgba(255, 255, 255, 0.3); /* Glossy top edge */
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.9);
            padding: 60px;
            border-radius: 24px;
            text-align: center;
            max-width: 600px;
            width: 90%;
            animation: fadeInUp 1.2s ease-out;
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .title-text {
            font-family: 'Segoe UI', sans-serif;
            font-size: 4rem;
            font-weight: 800;
            background: linear-gradient(to right, #ffffff, #a5b4fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            letter-spacing: -2px;
            text-shadow: 0 0 30px rgba(66, 135, 245, 0.3);
        }

        .subtitle-text {
            color: #94a3b8;
            font-size: 1.2rem;
            margin-bottom: 40px;
            font-weight: 300;
            letter-spacing: 1px;
        }

        </style>
        
        <div class="glass-container">
            <div class="blob blob-1"></div>
            <div class="blob blob-2"></div>
            <div class="glass-card">
                <div class="title-text">SafePath</div>
                <div class="subtitle-text">INTELLIGENT URBAN NAVIGATION FOR DELHI</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Centered Button Logic using columns to center strictly in Streamlit
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # We use a little empty space to push the button visually into the card area
        st.write("") 
        if st.button("🚀 ENTER SECURE MODE", use_container_width=True):
            st.session_state.show_home = False
            st.rerun()

# ==========================================
# 🚦 MAIN APPLICATION LOGIC
# ==========================================

if st.session_state.show_home:
    show_home_screen()

else:
    # --- ORIGINAL APP STYLES ---
    st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
        }
        h1, h2, h3 {
            color: #ffffff;
            font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
        }
        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            min-width: 170px;
            background-color: #1e293b;
            border-radius: 4px 4px 0px 0px;
            gap: 2px;
            padding-top: 10px;
            padding-bottom: 10px;
            color: white;
        }
        .stTabs [aria-selected="true"] {
            background-color: #3b82f6;
            color: white;
        }
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #1a1d24;
            border-right: 1px solid #333;
        }
        /* Input & Button Styling */
        .stTextInput > div > div > input {
            border-radius: 8px;
            color: white;
            background-color: #262730;
            border: 1px solid #4a4a4a;
        }
        .stButton > button {
            border-radius: 8px;
            background-color: #3b82f6;
            color: white;
            border: none;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #2563eb;
            transform: scale(1.02);
        }
        </style>
        """, unsafe_allow_html=True)

    # --- HEADER WITH ANIMATION ---
    st.markdown("## 🛡️ SafePath: <span style='color:#3b82f6'>Delhi</span>", unsafe_allow_html=True)

    # --- NAVIGATION TABS ---
    tab1, tab2, tab3 = st.tabs(["🗺️ Route Finder", "ℹ️ How Algorithm Works", "👥 About Us"])

    current_dir = r"https://github.com/crankshafters/LATSHORT.git"
    json_path = "delhi_data.json"

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

    # --- TAB 1: MAIN MAP APPLICATION ---
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

        # --- MAIN MAP ---
        m = folium.Map(location=[28.6139, 77.2090], zoom_start=11)

        # --- SIDEBAR CONTROLS ---
        st.sidebar.title("⚙️ Settings")
        
        # Add Home Button to Sidebar to go back
        if st.sidebar.button("🏠 Back to Home"):
            st.session_state.show_home = True
            st.rerun()

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

        output = st_folium(m, width=1400, height=500)

        # Handle Map Clicks
        if output and output.get('last_clicked'):
            clicked_lat = output['last_clicked']['lat']
            clicked_lng = output['last_clicked']['lng']
            
            if st.session_state.start_point is None:
                st.session_state.start_point = [clicked_lat, clicked_lng]
                st.rerun()
            elif st.session_state.end_point is None:
                st.session_state.end_point = [clicked_lat, clicked_lng]
                st.rerun()

        # Reset Map Button (Moved here for better flow)
        if st.button("🔄 Reset Map Selection"):
            st.session_state.start_point = None
            st.session_state.end_point = None
            st.session_state.routes = []
            st.session_state.analyzed = False
            st.session_state.start_options = []
            st.session_state.end_options = []
            st.rerun()

        # Route Analysis Button & Logic
        if st.session_state.start_point and st.session_state.end_point:
            
            st.sidebar.markdown("---")
            st.sidebar.subheader("🕒 Time of Travel")
            travel_hour = st.sidebar.slider("Hour (24h)", 0, 23, 14, help="Affects safety score based on lighting")
            
            if st.button("🚀 Analyze Safest Route", type="primary"):
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

    # --- TAB 2: EXPLAINER FOR JUDGES ---
    with tab2:
        st.header("How SafePath Works")
        st.markdown("""
        SafePath isn't just a map; it's a **Risk Assessment Engine**. Unlike Google Maps which optimizes for *Speed*, we optimize for *Safety*.
        
        ### 1. Hybrid Data Engine
        We combine three data sources to calculate safety:
        * **Local Police Data:** GeoJSON polygons defining high-crime zones (Red zones on map).
        * **Latlong.ai Intelligence:** We scan every 50 meters of the route for real-time infrastructure (Police Stations, Liquor Stores, ATMs).
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

    # --- TAB 3: ABOUT ---
    with tab3:
        st.header("Team SafePath")
        st.write("Built for the Hackathon 2025.")
        st.info("Our mission is to make urban navigation safer for pedestrians.")
