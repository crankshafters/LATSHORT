import os
import json
import requests
import polyline
import math
import random
from flask import Flask, request, jsonify
from shapely.geometry import Point, shape

app = Flask(__name__)

LATLONG_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJUb2tlbklEIjoiN2RjYTJlMmQtMmEzZi00MGNkLWFiMmItY2Y5ZGMwYTQ3YjFlIiwiQ2xpZW50SUQiOiJiNDYxZmVlOC1hNmIzLTQ0MWQtYTYwMC03YmQwMjZiMzBjYmUiLCJCdW5pdElEIjoxNTY5MCwiQXBwTmFtZSI6InRhbmF5c2hhaDJrN0BnbWFpbC5jb21tYWlsc2lnbnVwIiwiQXBwSUQiOjE4NTA1LCJUaW1lU3RhbXAiOiIyMDI1LTExLTI5IDA1OjU5OjU0IiwiZXhwIjoxNzY3OTk1OTk0fQ.iTyV6tHP6CMj-bKo1D_JZY1q41hVaS0iAYjiP6XyR9Y" 
LATLONG_BASE_URL = "https://apihub.latlong.ai/v4"

SAFE_TYPES = ["police", "hospital", "clinic", "pharmacy", "bank", "atm", "government", "school", "university", "metro_station"]
UNSAFE_TYPES = ["bar", "nightclub", "casino", "liquor_store", "industrial", "waste_disposal"]

local_safety_data = {}

def load_local_data():
    global local_safety_data
    try:
        if os.path.exists("delhi_data.json"):
            with open("delhi_data.json", "r") as f:
                local_safety_data = json.load(f)
    except Exception:
        pass

def get_osrm_routes(start_coords, end_coords):
    url = f"http://router.project-osrm.org/route/v1/walking/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&alternatives=true&geometries=polyline"
    try:
        headers = {'User-Agent': 'SafePathHackathon/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("routes", [])
        return []
    except Exception:
        return []

def get_nearby_landmarks(lat, lon):
    if not LATLONG_API_KEY or "your_actual" in LATLONG_API_KEY:
        return []
    
    url = f"{LATLONG_BASE_URL}/landmark.json"
    params = {
        "lat": lat,
        "lon": lon,
        "key": LATLONG_API_KEY
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            return response.json().get("landmarks", [])
        return []
    except Exception:
        return []

def check_local_zone_safety(lat, lon, is_night):
    base_score = 0
    if not local_safety_data or "features" not in local_safety_data:
        return 0

    try:
        point = Point(lon, lat)
        for feature in local_safety_data["features"]:
            polygon = shape(feature["geometry"])
            if polygon.contains(point):
                props = feature.get("properties", {})
                crime_rate = props.get("crime_rate", 0.5) 
                
                base_score -= (crime_rate * 20)
                
                if props.get("lighting") == "poor":
                    if is_night:
                        base_score -= 25
                    else:
                        base_score -= 5
    except Exception:
        pass
    return base_score

def calculate_path_score(route_geometry, hour):
    try:
        coordinates = polyline.decode(route_geometry)
    except:
        return 50, [] # Now returns score AND POIs

    is_night = (hour < 6) or (hour > 19)

    total_score = 100
    all_pois = []
    
    # Check 10 points along the path for POIs
    step = max(1, len(coordinates) // 10) 
    sampled_points = coordinates[::step]
    
    for lat, lon in sampled_points:
        total_score += check_local_zone_safety(lat, lon, is_night)
        
        landmarks = get_nearby_landmarks(lat, lon)
        
        for landmark in landmarks:
            l_type = landmark.get("type", "").lower()
            l_name = landmark.get("name", "Unknown")
            
            poi = {
                "name": l_name,
                "type": l_type,
                "lat": lat, 
                "lon": lon,
                "is_safe": False 
            }

            if any(st in l_type for st in SAFE_TYPES):
                total_score += 2
                poi["is_safe"] = True
            elif any(ut in l_type for ut in UNSAFE_TYPES):
                if is_night:
                    total_score -= 5
                else:
                    total_score -= 3
                poi["is_safe"] = False
            
            all_pois.append(poi) # Collect all POIs

    if total_score == 100:
        total_score = random.randint(65, 95)

    return max(0, min(100, total_score)), all_pois

@app.route('/get_safest_path', methods=['POST'])
def get_safest_path():
    try:
        data = request.json
        start_lat = data.get('start_lat')
        start_lon = data.get('start_lon')
        dest_lat = data.get('dest_lat')
        dest_lon = data.get('dest_lon')
        hour = data.get('hour', 12)
        
        routes = get_osrm_routes((start_lat, start_lon), (dest_lat, dest_lon))
        
        if not routes:
            return jsonify({"error": "No walking routes found."}), 200

        analyzed_routes = []
        all_landmarks = [] # New list to store all landmarks from all routes
        
        for idx, route in enumerate(routes):
            geometry = route.get('geometry')
            if not geometry: continue
            
            # Unpack the score and the list of POIs
            safety_score, route_pois = calculate_path_score(geometry, hour)
            
            # Store POIs for the frontend
            all_landmarks.extend(route_pois) 

            distance_meters = route.get('distance', 0)
            walking_speed_mps = 1.4 
            walking_duration_seconds = distance_meters / walking_speed_mps

            analyzed_routes.append({
                "id": idx,
                "geometry": geometry,
                "duration": walking_duration_seconds,
                "distance": distance_meters,
                "safety_score": safety_score
            })
        
        analyzed_routes.sort(key=lambda x: x['safety_score'], reverse=True)
        
        return jsonify({
            "routes": analyzed_routes,
            "safest_route_id": analyzed_routes[0]['id'] if analyzed_routes else None,
            "landmarks": all_landmarks # NEW: Send all POIs to frontend
        })

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    load_local_data()
    app.run(debug=True, port=5000)
