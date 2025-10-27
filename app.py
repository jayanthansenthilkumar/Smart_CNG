from flask import Flask, render_template, jsonify, send_from_directory, request, redirect, url_for, session
import requests
import json
from datetime import datetime
import numpy as np
import time
from models.location_optimizer import LocationOptimizer
from models.wait_time_predictor import WaitTimePredictor
from dataclasses import dataclass
from typing import Dict, Any
from models.station_calculating_model import ChargingStationCalculator
import os
import pandas as pd
import math

app = Flask(__name__, static_url_path='/static')

# Initialize models
station_calculator = ChargingStationCalculator()
wait_time_predictor = WaitTimePredictor()
try:
    wt_path_candidates = [
        os.path.join(os.path.dirname(__file__), 'CNG_pumps_with_Erlang-C_waiting_times.csv'),
        os.path.join(os.path.dirname(__file__), 'waiting_times.csv')
    ]
    for p in wt_path_candidates:
        if os.path.exists(p):
            wait_time_predictor.train_from_csv(p)
            print(f"Wait time model trained from {os.path.basename(p)}")
            break
except Exception as e:
    print(f"Wait time model training failed: {e}")

# Initialize location optimizer with data
data_file_path = os.path.join(os.path.dirname(__file__), 'CNG_pumps_with_Erlang-C_waiting_times_250.csv')
location_optimizer_instance = LocationOptimizer(data_file_path)

# Define water bodies and restricted areas in NCR
RESTRICTED_AREAS = [
    # Yamuna River and floodplains - more detailed polygon
    {
        'name': 'Yamuna River and Floodplains',
        'polygon': [
            {'lat': 28.6890, 'lng': 77.2170},  # North Delhi
            {'lat': 28.6800, 'lng': 77.2220},
            {'lat': 28.6700, 'lng': 77.2250},
            {'lat': 28.6600, 'lng': 77.2280},
            {'lat': 28.6500, 'lng': 77.2300},
            {'lat': 28.6400, 'lng': 77.2320},
            {'lat': 28.6300, 'lng': 77.2340},
            {'lat': 28.6200, 'lng': 77.2360},
            {'lat': 28.6100, 'lng': 77.2380},
            {'lat': 28.6000, 'lng': 77.2400},
            {'lat': 28.5900, 'lng': 77.2420},
            {'lat': 28.5800, 'lng': 77.2440},
            {'lat': 28.5700, 'lng': 77.2460},  # South Delhi
            # West bank
            {'lat': 28.5700, 'lng': 77.2360},
            {'lat': 28.5800, 'lng': 77.2340},
            {'lat': 28.5900, 'lng': 77.2320},
            {'lat': 28.6000, 'lng': 77.2300},
            {'lat': 28.6100, 'lng': 77.2280},
            {'lat': 28.6200, 'lng': 77.2260},
            {'lat': 28.6300, 'lng': 77.2240},
            {'lat': 28.6400, 'lng': 77.2220},
            {'lat': 28.6500, 'lng': 77.2200},
            {'lat': 28.6600, 'lng': 77.2180},
            {'lat': 28.6700, 'lng': 77.2160},
            {'lat': 28.6800, 'lng': 77.2140},
            {'lat': 28.6890, 'lng': 77.2170}  # Close the polygon
        ]
    },
    # Add other water bodies
    {
        'name': 'Okhla Bird Sanctuary',
        'polygon': [
            {'lat': 28.5680, 'lng': 77.3000},
            {'lat': 28.5700, 'lng': 77.3100},
            {'lat': 28.5600, 'lng': 77.3150},
            {'lat': 28.5550, 'lng': 77.3050},
            {'lat': 28.5680, 'lng': 77.3000}
        ]
    }
]

# Define CNG models data structure
cng_models = {
    'tesla_model_3': {
        'name': "Tesla Model 3",
        'battery_capacity': 82,  # kWh
        'range': 358,  # km
        'filling_speed': 250,  # kg/min
        'consumption': 0.229  # kWh/km
    },
    'nissan_leaf': {
        'name': "Nissan Leaf",
        'battery_capacity': 62,
        'range': 385,
        'filling_speed': 100,
        'consumption': 0.161
    },
    'chevy_bolt': {
        'name': "Chevrolet Bolt",
        'battery_capacity': 65,
        'range': 417,
        'filling_speed': 55,
        'consumption': 0.156
    }
}

def point_in_polygon(point, polygon):
    """Ray casting algorithm to determine if point is in polygon"""
    x, y = point['lng'], point['lat']
    inside = False
    j = len(polygon) - 1
    
    for i in range(len(polygon)):
        if ((polygon[i]['lng'] > x) != (polygon[j]['lng'] > x) and
            y < (polygon[j]['lat'] - polygon[i]['lat']) * 
            (x - polygon[i]['lng']) / 
            (polygon[j]['lng'] - polygon[i]['lng']) + 
            polygon[i]['lat']):
            inside = not inside
        j = i
    
    return inside

def is_valid_location(lat, lng):
    """Enhanced location validation with buffer zone"""
    point = {'lat': lat, 'lng': lng}
    
    # Add a buffer zone around restricted areas (approximately 100 meters)
    BUFFER = 0.001  # roughly 100 meters in degrees
    
    for area in RESTRICTED_AREAS:
        # Check if point is in restricted area or buffer zone
        for i in range(len(area['polygon'])):
            p1 = area['polygon'][i]
            p2 = area['polygon'][(i + 1) % len(area['polygon'])]
            
            # Calculate distance to line segment
            if distance_to_line_segment(point, p1, p2) < BUFFER:
                return False
    
    return True

def distance_to_line_segment(p, p1, p2):
    """Calculate distance from point to line segment"""
    x, y = p['lng'], p['lat']
    x1, y1 = p1['lng'], p1['lat']
    x2, y2 = p2['lng'], p2['lat']
    
    A = x - x1
    B = y - y1
    C = x2 - x1
    D = y2 - y1
    
    dot = A * C + B * D
    len_sq = C * C + D * D
    
    if len_sq == 0:
        return np.sqrt(A * A + B * B)
        
    param = dot / len_sq
    
    if param < 0:
        return np.sqrt(A * A + B * B)
    elif param > 1:
        return np.sqrt((x - x2) * (x - x2) + (y - y2) * (y - y2))
    
    return abs(A * D - C * B) / np.sqrt(len_sq)

def get_time_info():
    """Get current time information"""
    current_time = datetime.now()
    hour = current_time.hour
    
    # Determine time of day
    if 6 <= hour < 12:
        time_of_day = 'morning'
    elif 12 <= hour < 17:
        time_of_day = 'afternoon'
    else:
        time_of_day = 'evening'
    
    return {
        'is_weekend': current_time.weekday() >= 5,
        'time_of_day': time_of_day,
        'hour': hour,
        'day_of_week': current_time.weekday()
    }

def fetch_gas_stations(lat, lng, radius=3000):
    """Fetch gas stations and convert them to nodes for optimization"""
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    overpass_query = f"""
    [out:json][timeout:25];
    (
        node["amenity"="fuel"](around:{radius},{lat},{lng});
        way["amenity"="fuel"](around:{radius},{lat},{lng});
    );
    out body;
    >;
    out skel qt;
    """
    
    try:
        response = requests.post(overpass_url, data=overpass_query)
        data = response.json()
        
        nodes = []
        for element in data.get('elements', []):
            if element.get('type') == 'node':
                node = {
                    'lat': element.get('lat'),
                    'lng': element.get('lon'),
                    'type': determine_area_type(element),
                    'name': element.get('tags', {}).get('name', 'Unnamed Station')
                }
                if is_valid_location(node['lat'], node['lng']):
                    nodes.append(node)
        return nodes
    except Exception as e:
        print(f"Error fetching gas stations: {e}")
        return []

def determine_area_type(element):
    """Determine area type based on surroundings"""
    tags = element.get('tags', {})
    
    if tags.get('shop') in ['mall', 'supermarket']:
        return 'Market'
    elif tags.get('building') in ['commercial', 'office']:
        return 'Office'
    elif tags.get('amenity') in ['hospital', 'clinic']:
        return 'Hospital'
    elif tags.get('amenity') in ['school', 'university']:
        return 'School'
    elif tags.get('industrial') == 'yes':
        return 'Factory'
    else:
        return 'Market'  # Default to market for gas stations

def analyze_location_suitability(gas_station, existing_stations):
    """Enhanced location suitability analysis"""
    if not is_valid_location(gas_station['lat'], gas_station['lng']):
        return 0
    
    # Check minimum distance from existing stations
    MIN_DISTANCE = 0.005  # roughly 500m
    for existing in existing_stations:
        dist = np.sqrt(
            (gas_station['lat'] - existing['lat'])**2 + 
            (gas_station['lng'] - existing['lng'])**2
        )
        if dist < MIN_DISTANCE:
            return 0
    
    # Base score
    score = 1.0
    
    # Factors affecting suitability
    if gas_station.get('near_highway', False):
        score *= 1.3  # Prefer locations near major roads
    
    if gas_station.get('in_commercial', False):
        score *= 1.2  # Prefer commercial areas
    
    if '24/7' in gas_station.get('opening_hours', ''):
        score *= 1.2  # Prefer 24/7 locations
    
    if gas_station.get('brand', 'Unknown') != 'Unknown':
        score *= 1.1  # Prefer established brands
    
    return score

app.secret_key = 'your-secret-key-here'  # Replace with a secure secret key in production

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == "Codex" and password == "codex":
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/api/stations/<lat>/<lng>')
def get_nearby_stations(lat, lng):
    """Return stations from CSV/XLSX near the provided lat/lng, optional radius in km."""
    lat, lng = float(lat), float(lng)
    try:
        radius_km = float(request.args.get('radius', 5))
    except Exception:
        radius_km = 5.0

    data = _read_stations_file()
    stations_file = data.get('stations', [])
    if not stations_file:
        return jsonify({'error': data.get('error', 'No stations data'), 'stations': []}), 400

    def haversine_km(lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        return float(R * c)

    result = []
    for s in stations_file:
        pos = s.get('position') or {}
        slat = pos.get('lat')
        slng = pos.get('lng')
        if slat is None or slng is None:
            continue
        d = haversine_km(lat, lng, slat, slng)
        if d <= radius_km:
            result.append({
                'id': f"{slat:.6f},{slng:.6f}",
                'name': s.get('name', 'CNG Station'),
                'position': {'lat': slat, 'lng': slng},
                'distance_km': round(d, 3),
                'active_chargers': 1,
                'total_chargers': 2,
            })

    # Predict wait times
    timeinfo = get_time_info()
    feature_recs = []
    for st in result:
        feature_recs.append({
            'id': st['id'],
            'active_chargers': st.get('active_chargers', 1),
            'total_chargers': st.get('total_chargers', 2),
            'current_queue_length': max(0, int(round(np.random.poisson(1)))),
            'hour_of_day': timeinfo['hour'],
            'day_of_week': timeinfo['day_of_week'],
            'is_weekend': 1 if timeinfo['is_weekend'] else 0,
            'traffic_density': 0.5,
            'historical_avg_wait_time': 10.0
        })
    preds = wait_time_predictor.predict_wait_time(feature_recs)
    pred_map = {p['station_id']: p for p in preds}

    for st in result:
        pm = pred_map.get(st['id'])
        if pm:
            st['predicted_wait'] = round(float(pm['predicted_wait']), 2)
            st['prediction_confidence'] = round(float(pm['confidence']), 2)

    # Sort by predicted wait then distance
    result.sort(key=lambda x: (x.get('predicted_wait', 9999), x['distance_km']))
    return jsonify({'stations': result})

@app.route('/api/stations-with-wait/<lat>/<lng>')
def get_nearby_stations_with_wait(lat, lng):
    # Proxy to existing endpoint logic
    return get_nearby_stations(lat, lng)

def get_random_connectors():
    connector_types = ["Type 2", "CCS", "CHAdeMO"]
    num_connectors = np.random.randint(1, len(connector_types) + 1)
    return np.random.choice(connector_types, num_connectors, replace=False).tolist()

def get_random_power():
    power_options = ["50kW", "100kW", "150kW", "350kW"]
    return np.random.choice(power_options)

@app.route('/api/optimize-locations/<lat>/<lng>')
def get_optimal_locations(lat, lng):
    """Get optimal locations for new CNG stations"""
    try:
        lat, lng = float(lat), float(lng)
        radius_km = float(request.args.get('radius', 10.0))
        num_stations = int(request.args.get('num_stations', 3))
        
        # Get time information
        time_info = get_time_info()
        
        # Get optimal locations
        optimal_locations = location_optimizer_instance.optimize_station_locations(
            center_lat=lat,
            center_lng=lng,
            radius_km=radius_km,
            num_stations=num_stations,
            time_info=time_info
        )
        
        # Format response
        candidates = []
        for i, location in enumerate(optimal_locations):
            candidates.append({
                'id': f"optimal_{i+1}",
                'name': f"Recommended CNG Station {i+1}",
                'position': {'lat': location['lat'], 'lng': location['lng']},
                'area_type': location['area_type'],
                'total_score': round(location['total_score'], 3),
                'demand_score': round(location['demand_score'], 3),
                'accessibility_score': round(location['accessibility_score'], 3),
                'economic_score': round(location['economic_score'], 3),
                'competition_score': round(location['competition_score'], 3),
                'distance_from_center': round(location['distance_from_center'], 2),
                'recommendation_reason': _get_recommendation_reason(location)
            })
        
        return jsonify({
            'candidates': candidates,
            'center': {'lat': lat, 'lng': lng},
            'radius_km': radius_km,
            'num_stations': num_stations,
            'time_info': time_info
        })
        
    except Exception as e:
        print(f"Error in get_optimal_locations: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/analyze-location/<lat>/<lng>')
def analyze_location(lat, lng):
    """Analyze a specific location for CNG station placement"""
    try:
        lat, lng = float(lat), float(lng)
        time_info = get_time_info()
        
        # Calculate individual scores
        demand_score = location_optimizer_instance.calculate_demand_score(lat, lng, time_info)
        accessibility_score = location_optimizer_instance.calculate_accessibility_score(lat, lng)
        
        # Determine area type
        area_type = location_optimizer_instance._classify_area_type(lat, lng)
        economic_score = location_optimizer_instance.calculate_economic_viability(lat, lng, area_type)
        competition_score = location_optimizer_instance.calculate_competition_score(lat, lng)
        
        # Calculate total score
        total_score = (
            0.3 * demand_score +
            0.25 * accessibility_score +
            0.25 * economic_score +
            0.2 * competition_score
        )
        
        # Find nearby existing stations
        nearby_stations = []
        for station in location_optimizer_instance.existing_stations:
            distance = location_optimizer_instance._haversine_distance(lat, lng, station['lat'], station['lng'])
            if distance <= 5.0:  # Within 5km
                nearby_stations.append({
                    'name': station['name'],
                    'distance_km': round(distance, 2),
                    'utilization': round(station['utilization'], 3),
                    'wait_time': station['wait_time_overall'],
                    'arrivals_per_hour': station['overall_arrivals']
                })
        
        # Sort by distance
        nearby_stations.sort(key=lambda x: x['distance_km'])
        
        return jsonify({
            'location': {'lat': lat, 'lng': lng},
            'area_type': area_type,
            'scores': {
                'total_score': round(total_score, 3),
                'demand_score': round(demand_score, 3),
                'accessibility_score': round(accessibility_score, 3),
                'economic_score': round(economic_score, 3),
                'competition_score': round(competition_score, 3)
            },
            'nearby_stations': nearby_stations[:5],  # Top 5 nearest
            'recommendation': _get_location_recommendation(total_score),
            'time_info': time_info
        })
        
    except Exception as e:
        print(f"Error in analyze_location: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/station-demand-analysis')
def station_demand_analysis():
    """Analyze demand patterns across all existing stations"""
    try:
        if not location_optimizer_instance.existing_stations:
            return jsonify({'error': 'No station data available'}), 400
        
        # Analyze demand patterns
        stations_data = []
        for station in location_optimizer_instance.existing_stations:
            stations_data.append({
                'name': station['name'],
                'position': {'lat': station['lat'], 'lng': station['lng']},
                'morning_arrivals': station['morning_arrivals'],
                'evening_arrivals': station['evening_arrivals'],
                'overall_arrivals': station['overall_arrivals'],
                'utilization': round(station['utilization'], 3),
                'wait_time_overall': station['wait_time_overall'],
                'rush_pattern': station['rush_pattern'],
                'servers': station['servers']
            })
        
        # Calculate statistics
        total_stations = len(stations_data)
        avg_utilization = np.mean([s['utilization'] for s in stations_data])
        avg_demand = np.mean([s['overall_arrivals'] for s in stations_data])
        high_demand_stations = [s for s in stations_data if s['overall_arrivals'] > avg_demand * 1.5]
        high_utilization_stations = [s for s in stations_data if s['utilization'] > 0.8]
        
        return jsonify({
            'total_stations': total_stations,
            'statistics': {
                'avg_utilization': round(avg_utilization, 3),
                'avg_demand': round(avg_demand, 3),
                'high_demand_count': len(high_demand_stations),
                'high_utilization_count': len(high_utilization_stations)
            },
            'stations': stations_data,
            'high_demand_stations': high_demand_stations[:10],  # Top 10
            'high_utilization_stations': high_utilization_stations[:10]  # Top 10
        })
        
    except Exception as e:
        print(f"Error in station_demand_analysis: {e}")
        return jsonify({'error': str(e)}), 400

def _get_recommendation_reason(location):
    """Generate a human-readable recommendation reason"""
    scores = {
        'demand': location['demand_score'],
        'accessibility': location['accessibility_score'],
        'economic': location['economic_score'],
        'competition': location['competition_score']
    }
    
    # Find the highest scoring factor
    best_factor = max(scores, key=scores.get)
    best_score = scores[best_factor]
    
    reasons = {
        'demand': f"High demand potential (score: {best_score:.2f}) - good location for customer volume",
        'accessibility': f"Excellent accessibility (score: {best_score:.2f}) - well-positioned for easy access",
        'economic': f"Strong economic viability (score: {best_score:.2f}) - profitable location",
        'competition': f"Low competition (score: {best_score:.2f}) - less saturated market"
    }
    
    return reasons.get(best_factor, "Good overall location for CNG station placement")

def _get_location_recommendation(total_score):
    """Get recommendation based on total score"""
    if total_score >= 0.8:
        return "Excellent location - highly recommended for CNG station"
    elif total_score >= 0.6:
        return "Good location - recommended with some considerations"
    elif total_score >= 0.4:
        return "Moderate location - consider carefully before proceeding"
    else:
        return "Poor location - not recommended for CNG station"

@app.route('/nearby-stations')
def nearby_stations():
    return render_template('index.html')

@app.route('/route-planner')
def route_planner():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('route_planner.html', username=session.get('username'))

@app.route('/stations')
def stations():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html', username=session.get('username'))

@app.route('/favorites')
def favorites():
    return render_template('favorites.html')  # You'll need to create this

@app.route('/analytics')
def analytics():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('analytics_soon.html', username=session.get('username'))

@app.route('/cng-switch')
def cng_switch():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('cng_switch_soon.html', username=session.get('username'))

@app.route('/ev-switcher')
def ev_switcher():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('cng_switch_soon.html', username=session.get('username'))

@app.route('/location-optimizer')
def location_optimizer():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('location_optimizer.html', username=session.get('username'))

@app.route('/api/route-plan', methods=['POST'])
def plan_route():
    data = request.json
    
    # Extract route data
    route = {
        'distance': data['route']['distance'],
        'coordinates': data['route']['coordinates']
    }
    # Accept both old and new payload shapes
    ev_model = data.get('evModel', {}).get('name') or data.get('cngModel', {}).get('name') or 'CNG Vehicle'
    current_charge = float(data.get('currentCharge') or data.get('currentFuel'))
    
    # Create CNG specs from the received data
    cng_payload = data.get('cngModel') or {}
    cng_specs = {
        'tankCapacity': float(cng_payload.get('tankCapacity', 60)),
        'range': float(cng_payload.get('range', 320)),
        'fillingSpeed': float(cng_payload.get('fillingSpeed', 10)),
        'consumption': float(cng_payload.get('consumption', 0.2))
    }
    
    try:
        # Map CNG specs to calculator's expected EV spec keys
        ev_specs_mapped = {
            'batteryCapacity': float(cng_specs['tankCapacity']),
            'chargingSpeed': float(cng_specs['fillingSpeed']),
            'consumption': float(cng_specs['consumption']),
            'range': float(cng_specs['range'])
        }

        filling_stops = station_calculator.calculate_charging_stops(
            route_data=route,
            ev_specs=ev_specs_mapped,
            current_charge=current_charge,
            available_stations=fetch_stations_in_bbox(calculate_route_bbox(route['coordinates']))
        )
        
        # Convert stops to JSON-serializable format
        stops_data = [
            {
                'name': stop.name,
                'lat': stop.lat,
                'lng': stop.lng,
                'arrivalFuel': stop.arrival_charge,
                'departureFuel': stop.departure_charge,
                'fillTime': stop.charge_time,
                'distanceFromStart': stop.distance_from_start,
                'type': stop.type
            }
            for stop in filling_stops
        ]
        
        return jsonify({
            'fillingStops': stops_data
        })
        
    except Exception as e:
        print(f"Route planning error: {str(e)}")  # Add logging
        return jsonify({'error': str(e)}), 400

def calculate_route_bbox(coordinates):
    """Calculate the bounding box for a set of coordinates"""
    lats = [coord[0] for coord in coordinates]
    lngs = [coord[1] for coord in coordinates]
    
    # Add some padding to the bbox (about 5km)
    padding = 0.045  # roughly 5km in degrees
    
    return {
        'min_lat': min(lats) - padding,
        'max_lat': max(lats) + padding,
        'min_lng': min(lngs) - padding,
        'max_lng': max(lngs) + padding
    }

def fetch_stations_in_bbox(bbox):
    """Fetch CNG stations within a bounding box using provided file data"""
    data = _read_stations_file()
    stations = data.get('stations', [])
    filtered_stations = []
    center_lat = (bbox['min_lat'] + bbox['max_lat']) / 2
    center_lng = (bbox['min_lng'] + bbox['max_lng']) / 2
    for s in stations:
        pos = s.get('position') or {}
        lat = pos.get('lat')
        lng = pos.get('lng')
        if lat is None or lng is None:
            continue
        if (bbox['min_lat'] <= lat <= bbox['max_lat'] and
            bbox['min_lng'] <= lng <= bbox['max_lng']):
            filtered_stations.append({
                'name': s.get('name', 'CNG Station'),
                'lat': lat,
                'lng': lng,
                'type': 'CNG Pump',
                'power': 'N/A',
                'active_chargers': 1,
                'total_chargers': 1
            })
    if filtered_stations:
        return filtered_stations

    # Fallback: pick nearest stations to bbox center if none in bbox
    def haversine_km(lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    scored = []
    for s in stations:
        pos = s.get('position') or {}
        lat = pos.get('lat')
        lng = pos.get('lng')
        if lat is None or lng is None:
            continue
        dist = haversine_km(center_lat, center_lng, lat, lng)
        scored.append((dist, s))
    scored.sort(key=lambda x: x[0])
    nearest = []
    for _, s in scored[:25]:
        pos = s['position']
        nearest.append({
            'name': s.get('name', 'CNG Station'),
            'lat': pos['lat'],
            'lng': pos['lng'],
            'type': 'CNG Pump',
            'power': 'N/A',
            'active_chargers': 1,
            'total_chargers': 1
        })
    return nearest

def _read_stations_file():
    """Read stations from the provided Excel file and return as JSON.
    Attempts to infer latitude/longitude/name columns case-insensitively.
    """
    try:
        # Resolve file path relative to app root
        # Try multiple known filenames in order
        candidates = [
            'CNG_pumps_with_Erlang-C_waiting_times_250.csv',
            'Trimmed_CNG_Pump_Data (1).csv',
            'Trimmed_CNG_Pump_Data (1).xlsx',
            'Trimmed_CNG_Pump_Data.csv',
            'Trimmed_CNG_Pump_Data.xlsx'
        ]
        base_dir = os.path.dirname(__file__)
        use_path = None
        for name in candidates:
            p = os.path.join(base_dir, name)
            if os.path.exists(p):
                use_path = p
                break
        if not use_path:
            return { 'error': 'File not found: ' + ', '.join(candidates), 'stations': [] }
        filename = os.path.basename(use_path)
        file_path = use_path

        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        # Normalize columns
        lower_cols = { str(c).strip().lower(): c for c in df.columns }

        # Heuristic detection of columns (including prefixed variants like @lat/@lon)
        lat_col = next((lower_cols[c] for c in lower_cols if c in ['lat', 'latitude', 'latitutde', '@lat']), None)
        lng_candidates = ['lng', 'lon', 'long', 'longitude', '@lon']
        lng_col = next((lower_cols[c] for c in lower_cols if c in lng_candidates), None)
        name_col = next((lower_cols[c] for c in lower_cols if c in ['name', '@name', 'station', 'station name', 'pump', 'cng pump', 'cng station', 'station_name']), None)

        if not lat_col or not lng_col:
            return { 'error': 'Latitude/Longitude columns not found in file', 'stations': [] }

        # Build station list with robust numeric coercion and range checks
        def coerce_num(val):
            try:
                if pd.isna(val):
                    return None
                if isinstance(val, (int, float)):
                    return float(val)
                s = str(val).strip().replace(',', '')
                return float(s)
            except Exception:
                return None

        stations = []
        for _, row in df.iterrows():
            lat = coerce_num(row.get(lat_col))
            lng = coerce_num(row.get(lng_col))
            if lat is None or lng is None:
                continue
            if not (-90 <= lat <= 90 and -180 <= lng <= 180):
                continue
            name = str(row.get(name_col)).strip() if name_col and pd.notnull(row.get(name_col)) else 'CNG Station'
            stations.append({ 'name': name, 'position': { 'lat': lat, 'lng': lng } })

        return { 'stations': stations }
    except Exception as e:
        return { 'error': str(e), 'stations': [] }

@app.route('/api/stations-from-file')
def stations_from_file():
    data = _read_stations_file()
    status = 200
    if data.get('error'):
        status = 400 if 'not found' not in data['error'].lower() else 404
    return jsonify(data), status

if __name__ == '__main__':
    app.run(debug=True)