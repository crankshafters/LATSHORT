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
# 💎 ULTRA-GLOSSY CSS STYLING
# ==========================================
def inject_glass_styles():
    st.markdown("""
        <style>
        /* MAIN BACKGROUND - Deep Space Black */
        .stApp {
            background: #000000;
            background-image: 
                radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
                radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
                radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
        }

        /* 1. GLASS CONTAINERS (Tabs, Sidebar, Cards) */
        .stTabs [data-baseweb="tab-list"], 
        [data-testid="stSidebar"],
        .element-container,
        .stDataFrame {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        }

        /* 2. SIDEBAR SPECIFIC */
        [data-testid="stSidebar"] {
            background: rgba(10, 10, 10, 0.6);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        /* 3. INPUT FIELDS (Text Input, Selectbox) */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > div {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            color: white !important;
            border-radius: 12px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        .stTextInput > div > div > input:focus {
            border-color: #4facfe !important;
            box-shadow: 0 0 15px rgba(79, 172, 254, 0.3);
            background: rgba(255, 255, 255, 0.1) !important;
        }

        /* 4. BUTTONS - Liquid Neon */
        .stButton > button {
            background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
            color: white;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 12px;
            backdrop-filter: blur(4px);
            transition: all 0.4s ease;
            text-shadow: 0 0 10px rgba(255,255,255,0.3);
            box-shadow: inset 0 0 20px rgba(255,255,255,0.05);
        }
        .stButton > button:hover {
            border-color: #4facfe;
            box-shadow: 0 0 20px rgba(79, 172, 254, 0.4), inset 0 0 20px rgba(79, 172, 254, 0.2);
            transform: translateY(-2px);
            color: #4facfe;
        }
        
        /* Primary Action Button (Analyze) */
        button[kind="primary"] {
            background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%) !important;
            border: none !important;
            box-shadow: 0 0 20px rgba(0, 114, 255, 0.5) !important;
        }

        /* 5. TABS */
        .stTabs [data-baseweb="tab-list"] {
            background: transparent;
            gap: 10px;
            border: none;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.05);
            color: #ccc;
        }
        .stTabs [aria-selected="true"] {
            background: rgba(255, 255, 255, 0.15) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            color: white !important;
            box-shadow: 0 0 15px rgba(255,255,255,0.1);
        }

        /* 6. TYPOGRAPHY & HEADERS */
        h1, h2, h3 {
            background: linear-gradient(to right, #ffffff, #b3cdd1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }

        /* 7. ALERTS (Success/Error/Info) - Glass Style */
        .stAlert {
            background: rgba(20, 20, 20, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
        }
        
        /* Remove default streamlit white top bar */
        header[data-testid="stHeader"] {
            background: transparent;
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🏠 HOME SCREEN (LIQUID GLASS THEME)
# ==========================================
def show_home_screen():
    st.markdown("""
        <style>
        .stApp {
            background-color: #000000;
            overflow: hidden;
        }
        
        /* Container for the Glass Effect */
        .glass-container {
            position: relative;
            height: 90vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        /* The Animated Liquid Blobs */
        .blob {
            position: absolute;
            filter: blur(80px);
            z-index: 0;
            opacity: 0.7;
            animation: float 12s infinite ease-in-out alternate;
        }
        .blob-1 {
            top: 10%;
            left: 20%;
            width: 500px;
            height: 500px;
            background: linear-gradient(180deg, #4facfe 0%, #00f2fe 100%);
            border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%;
        }
        .blob-2 {
            bottom: 10%;
            right: 20%;
            width: 600px;
            height: 600px;
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
            animation-delay: -5s;
        }
        .blob-3 {
            top: 40%;
            left: 40%;
            width: 300px;
            height: 300px;
            background: #ffffff;
            opacity: 0.15;
            border-radius: 50%;
            filter: blur(60px);
        }

        @keyframes float {
            0% { transform: translate(0, 0) rotate(0deg) scale(1); }
            50% { transform: translate(30px, 20px) rotate(10deg) scale(1.05); }
            100% { transform: translate(-20px, 40px) rotate(-5deg) scale(0.95); }
        }

        /* The Glossy Glass Card */
        .glass-card {
            z-index: 10;
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-top: 1px solid rgba(255, 255, 255, 0.4);
            border-left: 1px solid rgba(255, 255, 255, 0.4);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
            padding: 80px;
            border-radius: 30px;
            text-align: center;
            max-width: 700px;
            width: 90%;
            animation: fadeInUp 1.5s cubic-bezier(0.2, 0.8, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        /* Shimmer effect on card */
        .glass-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transition: 0.5s;
            animation: shimmer 3s infinite;
        }

        @keyframes shimmer {
            0% { left: -150%; }
            50% { left: 150%; }
            100% { left: 150%; }
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(50px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .title-text {
            font-family: 'Segoe UI', sans-serif;
            font-size: 5rem;
            font-weight: 900;
            background: linear-gradient(135deg, #ffffff 0%, #a5b4fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0px;
            letter-spacing: -3px;
            filter: drop-shadow(0 0 20px rgba(255,255,255,0.3));
        }

        .subtitle-text {
            color: rgba(255,255,255,0.8);
            font-size: 1.3rem;
            margin-bottom: 50px;
            font-weight: 300;
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        </style>
        
        <div class="glass-container">
            <div class="blob blob-1"></div>
            <div class="blob blob-2"></div>
            <div class="blob blob-3"></div>
            <div class="glass-card">
                <div class="title-text">SafePath</div>
                <div class="subtitle-text">Next-Gen Urban Navigation</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.write("") 
        # Using a container width button that will inherit our new neon glass styles
        if st.button("🚀 ENTER SECURE MODE", use_container_width=True):
            st.session_state.show_home = False
            st.rerun()

# ==========================================
# 🚦 MAIN APPLICATION LOGIC
# ==========================================

if st.session_state.show_home:
    show_home_screen()

else:
    # Inject the heavy glass styles only when not on home screen
    inject_glass_styles()

    # --- HEADER ---
    st.markdown("## 🛡️ SafePath: <span style='text-shadow: 0 0 10px #3b82f6; color:#3b82f6'>Delhi</span>", unsafe_allow_html=True)

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
        # Wrap input section in a card
        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 📍 Start Location")
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

            with col2:
                st.markdown("### 🏁 Destination")
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

        st.write("") # Spacer

        # --- MAIN MAP ---
        m = folium.Map(location=[28.6139, 77.2090], zoom_start=11, tiles='cartodbdark_matter') # DARK MODE MAP TILES

        # --- SIDEBAR CONTROLS ---
        st.sidebar.title("⚙️ Settings")
        
        if st.sidebar.button("🏠 Home"):
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
                            "fillColor": "#ff0044",
                            "color": "#ff0044",
                            "weight": 1,
                            "fillOpacity": 0.4,
                        },
                        tooltip="High Crime Zone"
                    ).add_to(m)
                except Exception as e:
                    st.sidebar.error(f"Error loading heatmap: {e}")

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
            colors = ["#00ff88", "#ffee00", "#ff8800", "#ff0055"]
            for i, route in enumerate(st.session_state.routes):
                decoded_path = polyline.decode(route['geometry'])
                color = colors[min(i, len(colors)-1)]
                folium.PolyLine(
                    decoded_path,
                    color=color,
                    weight=6,
                    opacity=0.9,
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

        # Reset Map
        if st.button("🔄 Clear Selection"):
            st.session_state.start_point = None
            st.session_state.end_point = None
            st.session_state.routes = []
            st.session_state.analyzed = False
            st.session_state.start_options = []
            st.session_state.end_options = []
            st.rerun()

        # Route Analysis
        if st.session_state.start_point and st.session_state.end_point:
            
            st.sidebar.markdown("---")
            st.sidebar.subheader("🕒 Time of Travel")
            travel_hour = st.sidebar.slider("Hour (24h)", 0, 23, 14)
            
            # Using primary button kind which we styled heavily in CSS
            if st.button("🚀 Analyze Safest Route", type="primary"):
                with st.spinner("Processing satellite & crime data..."):
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
                            st.error("Backend connection failed.")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")

        if st.session_state.analyzed and st.session_state.routes:
            best = st.session_state.routes[0]
            st.markdown("---")
            st.markdown("### 🏆 Recommended Route")
            
            # Custom Metric Cards
            m1, m2, m3 = st.columns(3)
            m1.markdown(f"""
                <div style="background:rgba(0,255,136,0.1); border:1px solid rgba(0,255,136,0.3); padding:20px; border-radius:15px; text-align:center;">
                    <h3 style="margin:0; color:#00ff88;">{best['safety_score']}/100</h3>
                    <p style="margin:0; color:white; opacity:0.7;">Safety Score</p>
                </div>
            """, unsafe_allow_html=True)
            
            m2.markdown(f"""
                <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); padding:20px; border-radius:15px; text-align:center;">
                    <h3 style="margin:0; color:white;">{best['distance']/1000:.2f} km</h3>
                    <p style="margin:0; color:white; opacity:0.7;">Distance</p>
                </div>
            """, unsafe_allow_html=True)

            m3.markdown(f"""
                <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); padding:20px; border-radius:15px; text-align:center;">
                    <h3 style="margin:0; color:white;">{best['duration']/60:.0f} min</h3>
                    <p style="margin:0; color:white; opacity:0.7;">Duration</p>
                </div>
            """, unsafe_allow_html=True)

    # --- TAB 2: EXPLAINER ---
    with tab2:
        st.header("How SafePath Works")
        st.markdown("""
        <div style="background:rgba(255,255,255,0.05); padding:30px; border-radius:20px; border:1px solid rgba(255,255,255,0.1);">
            <p>SafePath isn't just a map; it's a <b>Risk Assessment Engine</b>. Unlike Google Maps which optimizes for <i>Speed</i>, we optimize for <i>Safety</i>.</p>
            
            <h3>1. Hybrid Data Engine</h3>
            <ul>
                <li><b>Local Police Data:</b> GeoJSON polygons defining high-crime zones.</li>
                <li><b>Latlong.ai Intelligence:</b> We scan every 50 meters of the route.</li>
                <li><b>Environmental Factors:</b> Time of day and street lighting conditions.</li>
            </ul>

            <h3>2. The Algorithm</h3>
            <ul>
                <li><b>Start:</b> 100 Points.</li>
                <li><b>Penalty:</b> -20 for entering a High Crime Zone.</li>
                <li><b>Penalty:</b> -5 for proximity to liquor stores/bars at night.</li>
                <li><b>Bonus:</b> +2 for proximity to Hospitals, Police Stations.</li>
                <li><b>Time Multiplier:</b> Penalties are 1.5x stricter after 8 PM.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # --- TAB 3: ABOUT ---
    with tab3:
        st.header("Team SafePath")
        st.info("Built for the Hackathon 2025. Our mission is to make urban navigation safer for pedestrians.")
