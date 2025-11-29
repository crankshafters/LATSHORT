🛡️ SafePath: AI-Powered Safe Route Navigation

Winner/Participant of [Hackathon Name] 2025 > Navigate cities with confidence using safety-first routing algorithms.

💡 The Problem

Most navigation apps (Google Maps, Waze) optimize for speed or distance. They will happily send a pedestrian through a dimly lit industrial area or a high-crime zone at 2 AM just to save 2 minutes.

SafePath changes the metric. We optimize for safety, calculating routes based on:

Real-time Infrastructure Analysis (Police stations vs. Liquor stores).

Historical Crime Data (Police records).

Environmental Factors (Street lighting and time of day).

🚀 Key Features

📍 Pin-Drop Navigation: Easy-to-use map interface to select start and end points.

🧠 Hybrid Safety Engine: * Uses Local Police Data (GeoJSON) for known hot-spots in Delhi.

Uses Latlong.ai API for real-time infrastructure scanning (works globally).

🌙 Dynamic Night Mode: Safety scores automatically adjust based on time of day. "Poor lighting" penalties are 5x stricter at night.

🗺️ Crime Heatmap: Visual layer showing high-risk zones directly on the map.

🚶 Pedestrian-First: Routing engine is tuned for walking paths, avoiding highways and car-only zones.

🛠️ Tech Stack

Frontend: Streamlit, Folium (Interactive Maps)

Backend: Python, Flask

Routing Engine: OSRM (Open Source Routing Machine)

Data & APIs: * Latlong.ai API: For landmark detection (Police, Hospitals, Banks, etc.).

Shapely: For geospatial point-in-polygon calculations.

Custom Dataset: Delhi Crime GeoJSON.

⚙️ How It Works (The Algorithm)

SafePath uses a weighted scoring algorithm to evaluate every route.

Route Fetching: We query OSRM for 3 distinct walking paths between the user's points.

Path Sampling: We divide each path into discrete steps (every ~50 meters).

Scoring Loop: Each step starts with a base safety score, which is modified by:

Infrastructure (+): Police Stations, Hospitals, Metro Stations, ATMs.

Risk Factors (-): Bars, Liquor Stores, Industrial Wastelands.

Zones (-): Known high-crime areas from local police data.

Time Modifier: If Time > 7 PM, risk penalties are multiplied by 1.5x.

Ranking: The path with the highest cumulative score is recommended.

📦 Installation & Setup

Prerequisites

Python 3.8+

A latlong.ai API Key

1. Clone the Repository

git clone [https://github.com/yourusername/safepath.git](https://github.com/yourusername/safepath.git)
cd safepath


2. Install Dependencies

pip install -r requirements.txt


3. Configure API Key

Open backend.py and add your key:

LATLONG_API_KEY = "your_key_here"


4. Run the Application

You need to run the Backend and Frontend in two separate terminals.

Terminal 1 (Backend):

python backend.py
# Server will start on [http://127.0.0.1:5000](http://127.0.0.1:5000)


Terminal 2 (Frontend):

streamlit run frontend.py
# App will open in your browser


📸 Screenshots

(Add screenshots of your app here)

Route Analysis: Green path showing the safest way vs. Red path showing the shortest but dangerous way.

Heatmap: Red zones indicating high crime areas.

🔮 Future Scope

Crowdsourcing: Allow users to report unsafe areas (dark alleys, harassment) in real-time.

SOS Integration: One-tap alert to nearest police station found via Latlong API.

Lighting Data: Integrate satellite imagery to detect street light density automatically.

📄 License

This project is licensed under the MIT License.
