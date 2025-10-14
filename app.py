from flask import Flask, render_template, jsonify, send_from_directory, request, redirect, url_for, session
from flask_cors import CORS
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
from models.cng_calculator import (
    User, Vehicle, FuelLog, Station, WaitTime, UserPreference,
    CNGConversionCost, FuelPrice, StationPrice, StationAvailability,
    StationReview, StationBooking, PriceAlert, FavoriteStation, PriceTrend, db
)
from services.cng_calculator import CNGCalculator
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
try:
    import pandas as pd
except Exception:
    pd = None
import math

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fuelexa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production

# Initialize SQLAlchemy
db.init_app(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize models
station_calculator = ChargingStationCalculator()
wait_time_predictor = WaitTimePredictor()
try:
    wt_path_candidates = [
        os.path.join(os.path.dirname(__file__), 'CNG_pumps_with_Erlang-C_waiting_times_250.csv'),
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
location_optimizer_instance = LocationOptimizer()

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
        
        if username == "Syraa" and password == "Syraa":
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

@app.route('/conversion-calculator')
def conversion_calculator():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('conversion_calculator.html', username=session.get('username'))

@app.route('/api/conversion/calculate', methods=['POST'])
def calculate_conversion():
    """Calculate CNG conversion ROI"""
    try:
        from services.conversion_calculator_service import conversion_calculator_service
        
        data = request.json
        vehicle = data.get('vehicle')
        city = data.get('city')
        monthly_km = data.get('monthlyKm')
        current_fuel = data.get('currentFuel', 'petrol')
        
        if not all([vehicle, city, monthly_km]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        result = conversion_calculator_service.calculate_conversion_roi(
            vehicle, city, monthly_km, current_fuel
        )
        
        return jsonify(result)
    except Exception as e:
        print(f"Error in conversion calculation: {e}")
        return jsonify({'error': str(e)}), 500

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
    # Dummy node data for demonstration
    nodes = [
        {'id': 1, 'type': 'Market', 'lat': float(lat) + 0.02, 'lng': float(lng) + 0.02},
        {'id': 2, 'type': 'Office', 'lat': float(lat) - 0.02, 'lng': float(lng) - 0.02},
        # Add more nodes...
    ]
    
    # Dummy VSF matrix
    vsf_matrix = np.random.rand(len(nodes), len(nodes))
    
    # Pass realistic time info into the legacy candidate API
    timeinfo = get_time_info()
    candidates = location_optimizer_instance.get_candidate_locations(nodes, timeinfo)
    
    return jsonify({'candidates': candidates})

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




@app.route('/ev-switcher')
def ev_switcher():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('cng_switch_soon.html', username=session.get('username'))

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

        if pd is not None:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
        else:
            # simple csv fallback
            import csv
            rows = []
            with open(file_path, newline='', encoding='utf-8') as fh:
                reader = csv.DictReader(fh)
                for r in reader:
                    rows.append(r)
            # Convert to a simple dataframe-like list
            df = rows
        # Normalize columns
        if pd is not None and hasattr(df, 'columns'):
            lower_cols = { str(c).strip().lower(): c for c in df.columns }
        else:
            # list-of-dicts fallback - inspect first row keys
            first_row = df[0] if isinstance(df, list) and len(df) > 0 else {}
            lower_cols = { str(c).strip().lower(): c for c in (first_row.keys() if isinstance(first_row, dict) else []) }

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
                if pd is not None and pd.isna(val):
                    return None
                if isinstance(val, (int, float)):
                    return float(val)
                s = str(val).strip().replace(',', '')
                return float(s)
            except Exception:
                return None

        stations = []
        # Support both pandas DataFrame and list-of-dicts fallback
        if pd is not None and hasattr(df, 'iterrows'):
            iterator = ((_, row) for _, row in df.iterrows())
        else:
            iterator = ((i, row) for i, row in enumerate(df))

        for _, row in iterator:
            lat = coerce_num(row.get(lat_col) if pd is not None and hasattr(row, 'get') else row.get(lat_col) if isinstance(row, dict) else None)
            lng = coerce_num(row.get(lng_col) if pd is not None and hasattr(row, 'get') else row.get(lng_col) if isinstance(row, dict) else None)
            if lat is None or lng is None:
                continue
            if not (-90 <= lat <= 90 and -180 <= lng <= 180):
                continue
            # Safely get name whether row is pandas Series or dict
            raw_name = None
            if name_col:
                if pd is not None and hasattr(row, 'get') and name_col in getattr(row, 'index', []):
                    raw_name = row.get(name_col)
                elif isinstance(row, dict):
                    raw_name = row.get(name_col)
            name = str(raw_name).strip() if raw_name not in (None, '', 'nan') else 'CNG Station'
            stations.append({
                'name': name,
                'position': {'lat': lat, 'lng': lng}
            })
        return {'stations': stations}
    except Exception as e:
        app.logger.error(f"Error loading stations from file: {str(e)}")
        return {'error': str(e), 'stations': []}

# CNG Switch Calculator Routes
@app.route('/cng-switch')
@login_required
def cng_switch():
    """Route for the CNG switch calculator page"""
    return render_template('cng_switch.html', username=current_user.username)

@app.route('/api/calculate-cng-savings', methods=['POST'])
@login_required
def calculate_cng_savings():
    """API endpoint for calculating CNG conversion savings"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['vehicleType', 'currentFuel', 'monthlyDistance', 'currentMileage', 'kitType']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get current fuel prices for Delhi (hardcoded for now, should be fetched from DB)
        fuel_prices = {
            'petrol': 96.72,
            'diesel': 89.62,
            'cng': 74.59
        }
        
        # Initialize calculator
        calculator = CNGCalculator(fuel_prices)
        
        # Generate comprehensive report
        report = calculator.generate_savings_report(
            vehicle_type=data['vehicleType'],
            monthly_distance=float(data['monthlyDistance']),
            current_mileage=float(data['currentMileage']),
            current_fuel_type=data['currentFuel'],
            kit_type=data['kitType']
        )
        
        # Store calculation in user's history
        if current_user.is_authenticated:
            # Check if user has a vehicle record
            vehicle = Vehicle.query.filter_by(
                user_id=current_user.id,
                make=data['vehicleType']
            ).first()
            
            if not vehicle:
                # Create new vehicle record
                vehicle = Vehicle(
                    user_id=current_user.id,
                    make=data['vehicleType'],
                    model='Not specified',
                    year=datetime.now().year,
                    fuel_type=data['currentFuel'],
                    avg_mileage=data['currentMileage'],
                    monthly_usage=data['monthlyDistance']
                )
                db.session.add(vehicle)
                db.session.commit()
        
        return jsonify(report)
        
    except Exception as e:
        app.logger.error(f"Error calculating CNG savings: {str(e)}")
        return jsonify({'error': 'Failed to calculate savings'}), 500

@app.route('/api/fuel-prices')
def get_fuel_prices():
    """Get current fuel prices for a city"""
    city = request.args.get('city', 'Delhi')
    try:
        prices = FuelPrice.get_latest_prices(city)
        return jsonify({'prices': prices})
    except Exception as e:
        app.logger.error(f"Error fetching fuel prices: {str(e)}")
        return jsonify({'error': 'Failed to fetch fuel prices'}), 500

@app.route('/api/conversion-costs')
def get_conversion_costs():
    """Get CNG conversion costs for different vehicle types"""
    try:
        costs = CNGConversionCost.query.all()
        return jsonify({
            'costs': [
                {
                    'vehicle_type': cost.vehicle_type,
                    'base_cost': cost.base_cost,
                    'labor_cost': cost.labor_cost,
                    'kit_type': cost.kit_type,
                    'warranty_period': cost.warranty_period
                }
                for cost in costs
            ]
        })
    except Exception as e:
        app.logger.error(f"Error fetching conversion costs: {str(e)}")
        return jsonify({'error': 'Failed to fetch conversion costs'}), 500

@app.route('/api/user-vehicles')
@login_required
def get_user_vehicles():
    """Get the current user's vehicles"""
    try:
        vehicles = Vehicle.query.filter_by(user_id=current_user.id).all()
        return jsonify({
            'vehicles': [
                {
                    'id': v.id,
                    'make': v.make,
                    'model': v.model,
                    'year': v.year,
                    'fuel_type': v.fuel_type,
                    'avg_mileage': v.avg_mileage,
                    'monthly_usage': v.monthly_usage,
                    'is_cng_converted': v.is_cng_converted
                }
                for v in vehicles
            ]
        })
    except Exception as e:
        app.logger.error(f"Error fetching user vehicles: {str(e)}")
        return jsonify({'error': 'Failed to fetch vehicles'}), 500

@app.route('/analytics')
def analytics():
    """Route for the analytics dashboard"""
    return render_template('analytics.html', username='Guest')

@app.route('/api/station-statistics')
def get_station_statistics():
    """Get aggregated statistics for the analytics dashboard"""
    try:
        # Verify database connection and tables
        try:
            # Get total users
            total_users = User.query.count()
        except Exception as e:
            app.logger.error(f"Error querying User table: {str(e)}")
            return jsonify({
                'error': 'Database error while fetching user data'
            }), 500
            
        # Get active CNG vehicles
        try:
            active_cng_vehicles = Vehicle.query.filter_by(
                is_cng_converted=True
            ).count()
        except Exception as e:
            app.logger.error(f"Error querying Vehicle table: {str(e)}")
            active_cng_vehicles = 0
        
        # Get total stations
        total_stations = Station.query.count()
        
        # Calculate average wait time
        avg_wait_time = db.session.query(
            db.func.avg(WaitTime.wait_minutes)
        ).scalar() or 0
        
        # Calculate monthly savings
        monthly_savings = 0
        vehicles = Vehicle.query.filter_by(is_cng_converted=True).all()
        for vehicle in vehicles:
            fuel_logs = FuelLog.query.filter_by(
                vehicle_id=vehicle.id
            ).order_by(
                FuelLog.date.desc()
            ).limit(2).all()
            
            if len(fuel_logs) >= 2:
                savings = fuel_logs[0].cost - fuel_logs[1].cost
                monthly_savings += savings
        
        # Calculate environmental impact
        total_co2_reduced = 0
        total_trees_equivalent = 0
        
        # Sum up the impact from all CNG vehicles
        for vehicle in vehicles:
            # Assuming average reduction of 25% in CO2 emissions per vehicle
            monthly_co2_reduction = (vehicle.monthly_usage / vehicle.avg_mileage) * 0.25
            total_co2_reduced += monthly_co2_reduction
            
            # Convert CO2 reduction to equivalent trees (1 tree absorbs about 22kg CO2 per year)
            trees = (monthly_co2_reduction * 12) / 22
            total_trees_equivalent += trees
        
        return jsonify({
            'totalUsers': total_users,
            'activeCNGVehicles': active_cng_vehicles,
            'totalStations': total_stations,
            'averageWaitTime': round(avg_wait_time, 1),
            'monthlySavings': round(monthly_savings),
            'annualSavings': round(monthly_savings * 12),
            'co2Reduced': round(total_co2_reduced, 1),
            'treesEquivalent': round(total_trees_equivalent)
        })
        
    except Exception as e:
        app.logger.error(f"Error fetching station statistics: {str(e)}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500
        
@app.route('/api/stations')
def get_stations():
    try:
        stations = []
        # Code to get stations data will go here
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

@app.route('/location-optimizer')
def location_optimizer():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('location_optimizer.html', username=session.get('username'))

@app.route('/vehicle-comparison')
def vehicle_comparison():
    """Route for vehicle comparison tool"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('vehicle_comparison.html', username=session.get('username'))

@app.route('/trip-calculator')
def trip_calculator():
    """Route for trip cost calculator"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('trip_calculator.html', username=session.get('username'))

@app.route('/maintenance-tracker')
def maintenance_tracker():
    """Route for maintenance tracking"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('maintenance_tracker.html', username=session.get('username'))

@app.route('/fuel-history')
def fuel_history():
    """Route for fuel history tracking"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('fuel_history.html', username=session.get('username'))

# ============ NEW REAL-TIME CNG FEATURES ============

@app.route('/api/realtime-stations/<lat>/<lng>')
def get_realtime_stations(lat, lng):
    """Fetch real-time CNG stations from multiple sources"""
    try:
        from services.realtime_station_fetcher import realtime_fetcher
        
        lat, lng = float(lat), float(lng)
        radius_km = float(request.args.get('radius', 50))
        
        # Fetch from all sources
        stations = realtime_fetcher.fetch_all_sources(lat, lng, radius_km)
        
        # Enrich with database information if available
        for station in stations:
            db_station = Station.query.filter_by(
                latitude=station['lat'],
                longitude=station['lng']
            ).first()
            
            if db_station:
                station['id'] = db_station.id
                station['rating'] = db_station.average_rating
                station['total_reviews'] = db_station.total_reviews
                
                # Get current availability
                if db_station.availability:
                    station['is_operational'] = db_station.availability.is_operational
                    station['queue_length'] = db_station.availability.current_queue_length
                    station['wait_time'] = db_station.availability.estimated_wait_minutes
                    station['stock_level'] = db_station.availability.cng_stock_level
        
        return jsonify({'stations': stations, 'count': len(stations)})
        
    except Exception as e:
        app.logger.error(f"Error fetching realtime stations: {str(e)}")
        return jsonify({'error': str(e), 'stations': []}), 500


@app.route('/api/station-details/<int:station_id>')
def get_station_details(station_id):
    """Get detailed information about a specific station"""
    try:
        station = Station.query.get_or_404(station_id)
        
        # Get current prices
        prices = {}
        for price in station.prices:
            prices[price.fuel_type] = {
                'price': price.price,
                'currency': price.currency,
                'updated': price.updated_at.isoformat()
            }
        
        # Get recent reviews
        recent_reviews = []
        for review in station.reviews[-10:]:  # Last 10 reviews
            recent_reviews.append({
                'id': review.id,
                'rating': review.rating,
                'text': review.review_text,
                'user': review.user.username,
                'created': review.created_at.isoformat()
            })
        
        # Get availability
        availability = None
        if station.availability:
            availability = {
                'operational': station.availability.is_operational,
                'queue_length': station.availability.current_queue_length,
                'wait_minutes': station.availability.estimated_wait_minutes,
                'available_pumps': station.availability.available_pumps,
                'total_pumps': station.availability.total_pumps,
                'stock_level': station.availability.cng_stock_level
            }
        
        return jsonify({
            'id': station.id,
            'name': station.name,
            'latitude': station.latitude,
            'longitude': station.longitude,
            'address': station.address,
            'city': station.city,
            'operating_hours': station.operating_hours,
            'is_24x7': station.is_24x7,
            'operator': station.operator,
            'phone': station.phone,
            'website': station.website,
            'amenities': station.amenities,
            'rating': station.average_rating,
            'total_reviews': station.total_reviews,
            'prices': prices,
            'availability': availability,
            'recent_reviews': recent_reviews
        })
        
    except Exception as e:
        app.logger.error(f"Error fetching station details: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/station-review', methods=['POST'])
@login_required
def add_station_review():
    """Add a review for a station"""
    try:
        data = request.get_json()
        
        review = StationReview(
            station_id=data['station_id'],
            user_id=current_user.id,
            rating=data['rating'],
            review_text=data.get('text', ''),
            service_quality=data.get('service_quality'),
            wait_time_rating=data.get('wait_time_rating'),
            price_rating=data.get('price_rating'),
            cleanliness_rating=data.get('cleanliness_rating')
        )
        
        db.session.add(review)
        
        # Update station average rating
        station = Station.query.get(data['station_id'])
        if station:
            reviews = StationReview.query.filter_by(station_id=station.id).all()
            station.average_rating = sum(r.rating for r in reviews) / len(reviews)
            station.total_reviews = len(reviews)
        
        db.session.commit()
        
        return jsonify({'message': 'Review added successfully', 'review_id': review.id})
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding review: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/station-booking', methods=['POST'])
@login_required
def create_station_booking():
    """Create a booking/queue slot at a station"""
    try:
        data = request.get_json()
        
        booking = StationBooking(
            station_id=data['station_id'],
            user_id=current_user.id,
            booking_time=datetime.now(),
            estimated_arrival=datetime.fromisoformat(data['estimated_arrival']),
            vehicle_id=data.get('vehicle_id'),
            estimated_fill_amount=data.get('estimated_fill_amount')
        )
        
        # Assign queue number
        existing_bookings = StationBooking.query.filter_by(
            station_id=data['station_id'],
            status='pending'
        ).count()
        booking.queue_number = existing_bookings + 1
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'message': 'Booking created successfully',
            'booking_id': booking.id,
            'queue_number': booking.queue_number
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creating booking: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/price-alert', methods=['POST'])
@login_required
def create_price_alert():
    """Create a price drop alert"""
    try:
        data = request.get_json()
        
        alert = PriceAlert(
            user_id=current_user.id,
            fuel_type=data['fuel_type'],
            city=data.get('city'),
            station_id=data.get('station_id'),
            alert_threshold=data['threshold'],
            notification_method=data.get('notification_method', 'email')
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return jsonify({
            'message': 'Price alert created successfully',
            'alert_id': alert.id
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creating price alert: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/favorite-station/<int:station_id>', methods=['POST', 'DELETE'])
@login_required
def toggle_favorite_station(station_id):
    """Add or remove a station from favorites"""
    try:
        if request.method == 'POST':
            favorite = FavoriteStation(
                user_id=current_user.id,
                station_id=station_id,
                notes=request.get_json().get('notes', '')
            )
            db.session.add(favorite)
            db.session.commit()
            return jsonify({'message': 'Station added to favorites'})
        else:
            favorite = FavoriteStation.query.filter_by(
                user_id=current_user.id,
                station_id=station_id
            ).first()
            if favorite:
                db.session.delete(favorite)
                db.session.commit()
            return jsonify({'message': 'Station removed from favorites'})
            
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error toggling favorite: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/price-trends/<fuel_type>')
def get_price_trends(fuel_type):
    """Get historical price trends for analytics"""
    try:
        city = request.args.get('city', 'Delhi')
        days = int(request.args.get('days', 30))
        
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        
        trends = PriceTrend.query.filter(
            PriceTrend.fuel_type == fuel_type,
            PriceTrend.city == city,
            PriceTrend.date >= start_date
        ).order_by(PriceTrend.date).all()
        
        data = [{
            'date': t.date.isoformat(),
            'price': t.price,
            'city': t.city
        } for t in trends]
        
        return jsonify({'trends': data})
        
    except Exception as e:
        app.logger.error(f"Error fetching price trends: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/user/favorites')
@login_required
def get_user_favorites():
    """Get user's favorite stations"""
    try:
        favorites = FavoriteStation.query.filter_by(user_id=current_user.id).all()
        
        stations = []
        for fav in favorites:
            station = fav.station
            stations.append({
                'id': station.id,
                'name': station.name,
                'latitude': station.latitude,
                'longitude': station.longitude,
                'address': station.address,
                'rating': station.average_rating,
                'notes': fav.notes,
                'added_on': fav.created_at.isoformat()
            })
        
        return jsonify({'favorites': stations})
        
    except Exception as e:
        app.logger.error(f"Error fetching favorites: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare-prices')
def compare_station_prices():
    """Compare CNG prices across multiple stations"""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        radius_km = float(request.args.get('radius', 10))
        
        # Find nearby stations
        from sqlalchemy import func
        
        # Haversine formula for distance calculation
        stations = Station.query.filter(
            Station.latitude.between(lat - radius_km/111, lat + radius_km/111),
            Station.longitude.between(lng - radius_km/111, lng + radius_km/111)
        ).all()
        
        comparison = []
        for station in stations:
            # Get latest CNG price
            cng_price = StationPrice.query.filter_by(
                station_id=station.id,
                fuel_type='cng'
            ).order_by(StationPrice.updated_at.desc()).first()
            
            if cng_price:
                comparison.append({
                    'station_id': station.id,
                    'name': station.name,
                    'latitude': station.latitude,
                    'longitude': station.longitude,
                    'price': cng_price.price,
                    'updated': cng_price.updated_at.isoformat(),
                    'rating': station.average_rating
                })
        
        # Sort by price
        comparison.sort(key=lambda x: x['price'])
        
        return jsonify({'stations': comparison})
        
    except Exception as e:
        app.logger.error(f"Error comparing prices: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============ END NEW FEATURES ============

# ============ VEHICLE COMPARISON FEATURES ============

@app.route('/api/compare-vehicles', methods=['POST'])
def compare_vehicles():
    """Compare fuel costs across multiple vehicles"""
    try:
        data = request.get_json()
        
        from services.vehicle_comparison_service import VehicleComparisonService
        
        fuel_prices = FuelPrice.get_latest_prices(data.get('city', 'Delhi'))
        comparison_service = VehicleComparisonService(fuel_prices)
        
        result = comparison_service.compare_vehicles(
            vehicles_data=data['vehicles'],
            monthly_distance=data['monthly_distance'],
            period_months=data.get('period_months', 12)
        )
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error comparing vehicles: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare-fuel-options', methods=['POST'])
def compare_fuel_options():
    """Compare different fuel options for the same vehicle"""
    try:
        data = request.get_json()
        
        from services.vehicle_comparison_service import VehicleComparisonService
        
        fuel_prices = FuelPrice.get_latest_prices(data.get('city', 'Delhi'))
        comparison_service = VehicleComparisonService(fuel_prices)
        
        result = comparison_service.compare_fuel_types_same_vehicle(
            base_vehicle=data['vehicle'],
            monthly_distance=data['monthly_distance'],
            include_conversion=data.get('include_conversion', True)
        )
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error comparing fuel options: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/vehicle-recommendation', methods=['POST'])
def get_vehicle_recommendation():
    """Get personalized vehicle recommendation"""
    try:
        data = request.get_json()
        
        from services.vehicle_comparison_service import VehicleComparisonService
        
        fuel_prices = FuelPrice.get_latest_prices(data.get('city', 'Delhi'))
        comparison_service = VehicleComparisonService(fuel_prices)
        
        result = comparison_service.get_best_vehicle_recommendation(
            monthly_distance=data['monthly_distance'],
            budget=data['budget'],
            priorities=data.get('priorities', ['cost', 'environment'])
        )
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error getting recommendation: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============ TRIP COST CALCULATOR FEATURES ============

@app.route('/api/calculate-trip-cost', methods=['POST'])
def calculate_trip_cost():
    """Calculate cost for a specific trip"""
    try:
        data = request.get_json()
        
        from services.trip_cost_calculator import TripCostCalculator
        
        fuel_prices = FuelPrice.get_latest_prices(data.get('city', 'Delhi'))
        trip_calculator = TripCostCalculator(fuel_prices)
        
        result = trip_calculator.calculate_trip_cost(
            distance_km=data['distance_km'],
            vehicle_mileage=data['vehicle_mileage'],
            fuel_type=data['fuel_type'],
            toll_charges=data.get('toll_charges', 0),
            parking_charges=data.get('parking_charges', 0),
            additional_costs=data.get('additional_costs', 0)
        )
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error calculating trip cost: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare-trip-options', methods=['POST'])
def compare_trip_fuel_options():
    """Compare fuel options for a specific trip"""
    try:
        data = request.get_json()
        
        from services.trip_cost_calculator import TripCostCalculator
        
        fuel_prices = FuelPrice.get_latest_prices(data.get('city', 'Delhi'))
        trip_calculator = TripCostCalculator(fuel_prices)
        
        result = trip_calculator.compare_trip_fuel_options(
            distance_km=data['distance_km'],
            vehicle_data=data['vehicle'],
            toll_charges=data.get('toll_charges', 0),
            parking_charges=data.get('parking_charges', 0)
        )
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error comparing trip options: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/calculate-round-trip', methods=['POST'])
def calculate_round_trip():
    """Calculate round trip costs"""
    try:
        data = request.get_json()
        
        from services.trip_cost_calculator import TripCostCalculator
        
        fuel_prices = FuelPrice.get_latest_prices(data.get('city', 'Delhi'))
        trip_calculator = TripCostCalculator(fuel_prices)
        
        result = trip_calculator.calculate_round_trip(
            one_way_distance=data['one_way_distance'],
            vehicle_mileage=data['vehicle_mileage'],
            fuel_type=data['fuel_type'],
            stops=data.get('stops', 0),
            parking_per_stop=data.get('parking_per_stop', 0)
        )
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error calculating round trip: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/estimate-refueling-stops', methods=['POST'])
def estimate_refueling_stops():
    """Estimate refueling stops for a trip"""
    try:
        data = request.get_json()
        
        from services.trip_cost_calculator import TripCostCalculator
        
        fuel_prices = FuelPrice.get_latest_prices(data.get('city', 'Delhi'))
        trip_calculator = TripCostCalculator(fuel_prices)
        
        result = trip_calculator.estimate_refueling_stops(
            distance_km=data['distance_km'],
            vehicle_mileage=data['vehicle_mileage'],
            tank_capacity=data['tank_capacity'],
            initial_fuel=data['initial_fuel']
        )
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error estimating stops: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare-routes', methods=['POST'])
def compare_routes():
    """Compare costs for different route options"""
    try:
        data = request.get_json()
        
        from services.trip_cost_calculator import TripCostCalculator
        
        fuel_prices = FuelPrice.get_latest_prices(data.get('city', 'Delhi'))
        trip_calculator = TripCostCalculator(fuel_prices)
        
        result = trip_calculator.compare_route_options(
            routes=data['routes'],
            vehicle_mileage=data['vehicle_mileage'],
            fuel_type=data['fuel_type']
        )
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error comparing routes: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============ MAINTENANCE TRACKING FEATURES ============

@app.route('/api/maintenance/add', methods=['POST'])
@login_required
def add_maintenance_record():
    """Add a maintenance record"""
    try:
        data = request.get_json()
        
        from services.maintenance_service import MaintenanceService
        
        maintenance_service = MaintenanceService()
        
        record = maintenance_service.add_maintenance_record(
            vehicle_id=data['vehicle_id'],
            service_type=data['service_type'],
            service_date=datetime.fromisoformat(data['service_date']),
            cost=data['cost'],
            odometer_reading=data.get('odometer_reading'),
            service_center=data.get('service_center'),
            notes=data.get('notes')
        )
        
        return jsonify({
            'message': 'Maintenance record added successfully',
            'record_id': record.id
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding maintenance record: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/maintenance/upcoming/<int:vehicle_id>')
@login_required
def get_upcoming_maintenance(vehicle_id):
    """Get upcoming maintenance for a vehicle"""
    try:
        from services.maintenance_service import MaintenanceService
        
        maintenance_service = MaintenanceService()
        
        days_ahead = int(request.args.get('days', 30))
        current_odometer = request.args.get('odometer', type=float)
        
        upcoming = maintenance_service.get_upcoming_maintenance(
            vehicle_id=vehicle_id,
            days_ahead=days_ahead,
            current_odometer=current_odometer
        )
        
        return jsonify({'upcoming_maintenance': upcoming})
        
    except Exception as e:
        app.logger.error(f"Error fetching upcoming maintenance: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/maintenance/history/<int:vehicle_id>')
@login_required
def get_maintenance_history(vehicle_id):
    """Get maintenance history for a vehicle"""
    try:
        from services.maintenance_service import MaintenanceService
        
        maintenance_service = MaintenanceService()
        
        limit = int(request.args.get('limit', 10))
        history = maintenance_service.get_maintenance_history(vehicle_id, limit)
        
        return jsonify({'maintenance_history': history})
        
    except Exception as e:
        app.logger.error(f"Error fetching maintenance history: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/maintenance/cost-projection/<int:vehicle_id>')
@login_required
def get_maintenance_cost_projection(vehicle_id):
    """Get maintenance cost projection"""
    try:
        from services.maintenance_service import MaintenanceService
        
        maintenance_service = MaintenanceService()
        
        months = int(request.args.get('months', 12))
        projection = maintenance_service.calculate_maintenance_cost_projection(
            vehicle_id, months
        )
        
        return jsonify(projection)
        
    except Exception as e:
        app.logger.error(f"Error calculating projection: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/maintenance/statistics/<int:vehicle_id>')
@login_required
def get_maintenance_statistics(vehicle_id):
    """Get maintenance statistics"""
    try:
        from services.maintenance_service import MaintenanceService
        
        maintenance_service = MaintenanceService()
        stats = maintenance_service.get_maintenance_statistics(vehicle_id)
        
        return jsonify(stats)
        
    except Exception as e:
        app.logger.error(f"Error fetching statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/maintenance/reminder/<int:reminder_id>/complete', methods=['POST'])
@login_required
def complete_maintenance_reminder(reminder_id):
    """Mark a maintenance reminder as completed"""
    try:
        from services.maintenance_service import MaintenanceService
        
        maintenance_service = MaintenanceService()
        maintenance_service.mark_reminder_completed(reminder_id)
        
        return jsonify({'message': 'Reminder marked as completed'})
        
    except Exception as e:
        app.logger.error(f"Error completing reminder: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============ FUEL LOG & HISTORY TRACKING ============

@app.route('/api/fuel-log/add', methods=['POST'])
@login_required
def add_fuel_log():
    """Add a fuel log entry"""
    try:
        data = request.get_json()
        
        log = FuelLog(
            vehicle_id=data['vehicle_id'],
            fuel_type=data['fuel_type'],
            amount=data['amount'],
            cost=data['cost'],
            odometer=data.get('odometer'),
            station_id=data.get('station_id')
        )
        
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'message': 'Fuel log added successfully',
            'log_id': log.id
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding fuel log: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/fuel-log/history/<int:vehicle_id>')
@login_required
def get_fuel_log_history(vehicle_id):
    """Get fuel log history for a vehicle"""
    try:
        limit = int(request.args.get('limit', 50))
        
        logs = FuelLog.query.filter_by(
            vehicle_id=vehicle_id
        ).order_by(
            FuelLog.date.desc()
        ).limit(limit).all()
        
        history = []
        for log in logs:
            history.append({
                'id': log.id,
                'date': log.date.isoformat(),
                'fuel_type': log.fuel_type,
                'amount': log.amount,
                'cost': log.cost,
                'cost_per_unit': round(log.cost / log.amount, 2) if log.amount > 0 else 0,
                'odometer': log.odometer,
                'station_id': log.station_id
            })
        
        return jsonify({'fuel_history': history})
        
    except Exception as e:
        app.logger.error(f"Error fetching fuel history: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/fuel-log/analytics/<int:vehicle_id>')
@login_required
def get_fuel_analytics(vehicle_id):
    """Get fuel consumption analytics"""
    try:
        from datetime import timedelta
        
        # Get logs from last 6 months
        six_months_ago = datetime.now() - timedelta(days=180)
        
        logs = FuelLog.query.filter(
            FuelLog.vehicle_id == vehicle_id,
            FuelLog.date >= six_months_ago
        ).order_by(FuelLog.date).all()
        
        if not logs:
            return jsonify({
                'message': 'No fuel data available',
                'analytics': None
            })
        
        # Calculate analytics
        total_spent = sum(log.cost for log in logs)
        total_fuel = sum(log.amount for log in logs)
        avg_price = total_spent / total_fuel if total_fuel > 0 else 0
        
        # Calculate mileage if odometer data available
        logs_with_odo = [log for log in logs if log.odometer]
        avg_mileage = None
        
        if len(logs_with_odo) >= 2:
            logs_with_odo.sort(key=lambda x: x.date)
            distance = logs_with_odo[-1].odometer - logs_with_odo[0].odometer
            fuel_consumed = sum(log.amount for log in logs_with_odo)
            avg_mileage = distance / fuel_consumed if fuel_consumed > 0 else None
        
        # Monthly breakdown
        monthly_data = {}
        for log in logs:
            month_key = log.date.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'total_cost': 0,
                    'total_fuel': 0,
                    'fill_count': 0
                }
            monthly_data[month_key]['total_cost'] += log.cost
            monthly_data[month_key]['total_fuel'] += log.amount
            monthly_data[month_key]['fill_count'] += 1
        
        return jsonify({
            'analytics': {
                'total_spent': round(total_spent, 2),
                'total_fuel': round(total_fuel, 2),
                'average_price_per_unit': round(avg_price, 2),
                'average_mileage': round(avg_mileage, 2) if avg_mileage else None,
                'fill_count': len(logs),
                'monthly_breakdown': monthly_data
            }
        })
        
    except Exception as e:
        app.logger.error(f"Error calculating analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============ ECO SCORE & ENVIRONMENTAL TRACKING ============

@app.route('/api/eco-score/<int:vehicle_id>')
@login_required
def get_eco_score(vehicle_id):
    """Get environmental impact score for a vehicle"""
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        
        # Calculate based on fuel logs
        logs = FuelLog.query.filter_by(vehicle_id=vehicle_id).all()
        
        if not logs:
            return jsonify({
                'message': 'No data available for eco score calculation',
                'eco_score': None
            })
        
        # CO2 emission factors
        emission_factors = {
            'petrol': 2.31,
            'diesel': 2.68,
            'cng': 1.96
        }
        
        total_co2 = 0
        for log in logs:
            factor = emission_factors.get(log.fuel_type, 2.31)
            total_co2 += log.amount * factor
        
        # Calculate savings if CNG converted
        co2_savings = 0
        if vehicle.is_cng_converted and vehicle.conversion_date:
            # Get logs before and after conversion
            logs_after = [l for l in logs if l.date >= vehicle.conversion_date]
            
            # Estimate what emissions would have been with petrol
            total_cng = sum(l.amount for l in logs_after if l.fuel_type == 'cng')
            would_be_co2 = total_cng * emission_factors['petrol'] * 1.2
            actual_co2 = total_cng * emission_factors['cng']
            co2_savings = would_be_co2 - actual_co2
        
        # Calculate eco score (0-100)
        # Lower emissions = higher score
        eco_score = max(0, 100 - (total_co2 / 100))
        
        trees_equivalent = total_co2 / 22  # Trees needed to offset
        
        return jsonify({
            'eco_score': round(eco_score, 1),
            'total_co2_emitted': round(total_co2, 2),
            'co2_savings': round(co2_savings, 2),
            'trees_equivalent': round(trees_equivalent, 1),
            'is_cng_converted': vehicle.is_cng_converted,
            'grade': (
                'Excellent' if eco_score >= 80 else
                'Good' if eco_score >= 60 else
                'Average' if eco_score >= 40 else
                'Poor'
            )
        })
        
    except Exception as e:
        app.logger.error(f"Error calculating eco score: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============ MULTI-VEHICLE MANAGEMENT ============

@app.route('/api/vehicles/add', methods=['POST'])
@login_required
def add_vehicle():
    """Add a new vehicle for the user"""
    try:
        data = request.get_json()
        
        vehicle = Vehicle(
            user_id=current_user.id,
            make=data['make'],
            model=data['model'],
            year=data['year'],
            fuel_type=data['fuel_type'],
            avg_mileage=data.get('avg_mileage'),
            monthly_usage=data.get('monthly_usage'),
            is_cng_converted=data.get('is_cng_converted', False)
        )
        
        db.session.add(vehicle)
        db.session.commit()
        
        return jsonify({
            'message': 'Vehicle added successfully',
            'vehicle_id': vehicle.id
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding vehicle: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/vehicles/<int:vehicle_id>', methods=['PUT'])
@login_required
def update_vehicle(vehicle_id):
    """Update vehicle information"""
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        
        # Verify ownership
        if vehicle.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        if 'make' in data:
            vehicle.make = data['make']
        if 'model' in data:
            vehicle.model = data['model']
        if 'year' in data:
            vehicle.year = data['year']
        if 'fuel_type' in data:
            vehicle.fuel_type = data['fuel_type']
        if 'avg_mileage' in data:
            vehicle.avg_mileage = data['avg_mileage']
        if 'monthly_usage' in data:
            vehicle.monthly_usage = data['monthly_usage']
        if 'is_cng_converted' in data:
            vehicle.is_cng_converted = data['is_cng_converted']
            if data['is_cng_converted'] and not vehicle.conversion_date:
                vehicle.conversion_date = datetime.now()
        
        db.session.commit()
        
        return jsonify({'message': 'Vehicle updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating vehicle: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/vehicles/<int:vehicle_id>', methods=['DELETE'])
@login_required
def delete_vehicle(vehicle_id):
    """Delete a vehicle"""
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        
        # Verify ownership
        if vehicle.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(vehicle)
        db.session.commit()
        
        return jsonify({'message': 'Vehicle deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting vehicle: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/vehicles/summary')
@login_required
def get_vehicles_summary():
    """Get summary of all user's vehicles"""
    try:
        vehicles = Vehicle.query.filter_by(user_id=current_user.id).all()
        
        summary = []
        for vehicle in vehicles:
            # Get recent fuel log
            recent_log = FuelLog.query.filter_by(
                vehicle_id=vehicle.id
            ).order_by(FuelLog.date.desc()).first()
            
            # Get upcoming maintenance count
            from services.maintenance_service import MaintenanceService
            maintenance_service = MaintenanceService()
            upcoming = maintenance_service.get_upcoming_maintenance(vehicle.id, days_ahead=30)
            
            summary.append({
                'id': vehicle.id,
                'make': vehicle.make,
                'model': vehicle.model,
                'year': vehicle.year,
                'fuel_type': vehicle.fuel_type,
                'is_cng_converted': vehicle.is_cng_converted,
                'avg_mileage': vehicle.avg_mileage,
                'monthly_usage': vehicle.monthly_usage,
                'last_fill_date': recent_log.date.isoformat() if recent_log else None,
                'upcoming_maintenance_count': len(upcoming)
            })
        
        return jsonify({
            'vehicles': summary,
            'total_vehicles': len(vehicles),
            'cng_vehicles': sum(1 for v in vehicles if v.is_cng_converted)
        })
        
    except Exception as e:
        app.logger.error(f"Error fetching vehicles summary: {str(e)}")
        return jsonify({'error': str(e)}), 500


def init_db():
    """Initialize database tables"""
    try:
        db.create_all()
        app.logger.info("Database tables created successfully")
    except Exception as e:
        app.logger.error(f"Error creating database tables: {str(e)}")

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)