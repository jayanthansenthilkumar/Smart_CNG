<<<<<<< HEAD
﻿from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
=======
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
>>>>>>> parent of cce0c35 (Analytics Performed)
import os
from lib import Data, Calculator
from model import User, db

<<<<<<< HEAD
app = Flask(__name__, 
            template_folder='public',
            static_folder='public',
            static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_cng.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret-key'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
=======
app = Flask(__name__, static_url_path='/static')
>>>>>>> parent of cce0c35 (Analytics Performed)

data = Data()
calc = Calculator()

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/nearby_stations')
def nearby_stations():
    return render_template('nearby_stations.html')

@app.route('/route_planner')
def route_planner():
    return render_template('route_planner.html')

<<<<<<< HEAD
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/api/stations/nearby')
def api_nearby_stations():
    lat = float(request.args.get('lat'))
    lng = float(request.args.get('lng'))
    radius = float(request.args.get('radius', 10))
    stations = data.find_stations(lat, lng, radius)
    return jsonify({'success': True, 'stations': [s.__dict__ for s in stations]})

@app.route('/api/calc/trip', methods=['POST'])
def api_calc_trip():
    req = request.get_json()
    car = data.find_car(req['make'], req['model'])
    if not car:
        return jsonify({'success': False, 'error': 'Vehicle not found'}), 404
    result = calc.trip_cost(car, float(req['distance']), req.get('fuel_type', 'cng'))
    return jsonify({'success': True, **result})

if __name__ == '__main__':
    print(f"Loaded: {len(data.stations)} stations, {len(data.cars)} cars")
    app.run(debug=True, host='0.0.0.0', port=5000)
=======
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

@app.route('/location-optimizer')
def location_optimizer():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('location_optimizer.html', username=session.get('username'))

if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> parent of cce0c35 (Analytics Performed)
