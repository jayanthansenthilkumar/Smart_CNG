"""
Smart CNG Application - Refactored with OOP Architecture
Main Flask application using core services
"""
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
from datetime import datetime

# Import core OOP modules
from core import (
    DataManager, FuelCostCalculator, StationFinderService,
    VehicleComparisonService, RouteOptimizerService, MaintenanceService,
    FuelType, Location
)

# Import database models (kept for user authentication)
from models.cng_calculator import (
    User, Vehicle as DBVehicle, FuelLog, Station, db
)
from models.location_optimizer import LocationOptimizer
from models.wait_time_predictor import WaitTimePredictor
from models.station_calculating_model import ChargingStationCalculator

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fuelexa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize database
db.init_app(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize core services (OOP)
data_manager = DataManager()
fuel_prices = {'cng': 75.61, 'petrol': 96.72, 'diesel': 89.62}
fuel_calculator = FuelCostCalculator(fuel_prices)
station_finder = StationFinderService()
vehicle_comparison = VehicleComparisonService()
route_optimizer = RouteOptimizerService()
maintenance_service = MaintenanceService()

# Initialize legacy models (for backward compatibility)
station_calculator = ChargingStationCalculator()
wait_time_predictor = WaitTimePredictor()
location_optimizer_instance = LocationOptimizer()

# Train wait time predictor
try:
    wt_path = os.path.join(os.path.dirname(__file__), 
                          'CNG_pumps_with_Erlang-C_waiting_times_250.csv')
    if os.path.exists(wt_path):
        wait_time_predictor.train_from_csv(wt_path)
        print("Wait time model trained successfully")
except Exception as e:
    print(f"Wait time model training failed: {e}")


# ============================================================================
# ROUTES - Home & Authentication
# ============================================================================

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    """Home page after login"""
    return render_template('home.html', user=current_user)

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    stats = data_manager.get_statistics()
    return render_template('dashboard.html', user=current_user, stats=stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.password_hash == password:  # TODO: Use proper password hashing
            login_user(user)
            return jsonify({'success': True, 'redirect': url_for('dashboard')})
        
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    return redirect(url_for('index'))


# ============================================================================
# API ROUTES - CNG Stations (Using OOP Services)
# ============================================================================

@app.route('/api/stations/nearby', methods=['GET'])
def get_nearby_stations():
    """Get nearby CNG stations using StationFinderService"""
    try:
        lat = float(request.args.get('latitude'))
        lng = float(request.args.get('longitude'))
        radius = float(request.args.get('radius', 10))
        
        stations = station_finder.find_nearby(lat, lng, radius)
        
        return jsonify({
            'success': True,
            'count': len(stations),
            'stations': stations
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/stations/cheapest', methods=['GET'])
def get_cheapest_stations():
    """Get cheapest stations in area"""
    try:
        lat = float(request.args.get('latitude'))
        lng = float(request.args.get('longitude'))
        radius = float(request.args.get('radius', 50))
        
        stations = station_finder.find_cheapest(lat, lng, radius)
        
        return jsonify({
            'success': True,
            'count': len(stations),
            'stations': stations
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/stations/best-rated', methods=['GET'])
def get_best_rated_stations():
    """Get best rated stations"""
    try:
        lat = float(request.args.get('latitude'))
        lng = float(request.args.get('longitude'))
        radius = float(request.args.get('radius', 50))
        min_rating = float(request.args.get('min_rating', 4.0))
        
        stations = station_finder.find_best_rated(lat, lng, radius, min_rating)
        
        return jsonify({
            'success': True,
            'count': len(stations),
            'stations': stations
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/stations/<int:station_id>', methods=['GET'])
def get_station_details(station_id):
    """Get specific station details"""
    try:
        station = data_manager.get_station_by_id(station_id)
        if not station:
            return jsonify({'success': False, 'error': 'Station not found'}), 404
        
        return jsonify({
            'success': True,
            'station': station.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================================================
# API ROUTES - Vehicles & Comparison (Using OOP Services)
# ============================================================================

@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    """Get all vehicles"""
    try:
        category = request.args.get('category')
        fuel_type = request.args.get('fuel_type')
        
        if category:
            vehicles = data_manager.get_vehicles_by_category(category)
        elif fuel_type:
            vehicles = data_manager.get_vehicles_by_fuel_type(FuelType(fuel_type))
        else:
            vehicles = data_manager.get_all_vehicles()
        
        return jsonify({
            'success': True,
            'count': len(vehicles),
            'vehicles': [v.to_dict() for v in vehicles]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/vehicles/compare', methods=['POST'])
def compare_vehicles():
    """Compare two vehicles"""
    try:
        data = request.get_json()
        make1, model1 = data['vehicle1']['make'], data['vehicle1']['model']
        make2, model2 = data['vehicle2']['make'], data['vehicle2']['model']
        annual_km = float(data.get('annual_km', 15000))
        
        vehicle1 = data_manager.get_vehicle_by_model(make1, model1)
        vehicle2 = data_manager.get_vehicle_by_model(make2, model2)
        
        if not vehicle1 or not vehicle2:
            return jsonify({'success': False, 'error': 'Vehicle not found'}), 404
        
        comparison = vehicle_comparison.compare_vehicles(
            vehicle1, vehicle2, annual_km, fuel_prices
        )
        
        return jsonify({
            'success': True,
            'comparison': comparison
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/vehicles/best-for-budget', methods=['GET'])
def get_best_vehicles_for_budget():
    """Find best vehicles within budget"""
    try:
        max_budget = float(request.args.get('budget', 1000000))
        category = request.args.get('category')
        annual_km = float(request.args.get('annual_km', 15000))
        
        vehicles = vehicle_comparison.find_best_vehicle_for_budget(
            max_budget, category, annual_km
        )
        
        return jsonify({
            'success': True,
            'count': len(vehicles),
            'vehicles': vehicles
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================================================
# API ROUTES - Fuel Cost Calculator (Using OOP Services)
# ============================================================================

@app.route('/api/calculate/trip-cost', methods=['POST'])
def calculate_trip_cost():
    """Calculate trip cost"""
    try:
        data = request.get_json()
        make, model = data['vehicle']['make'], data['vehicle']['model']
        distance_km = float(data['distance_km'])
        fuel_type_str = data['fuel_type']
        
        vehicle = data_manager.get_vehicle_by_model(make, model)
        if not vehicle:
            return jsonify({'success': False, 'error': 'Vehicle not found'}), 404
        
        fuel_type = FuelType(fuel_type_str)
        result = fuel_calculator.calculate_trip_cost(vehicle, distance_km, fuel_type)
        
        return jsonify({
            'success': True,
            'calculation': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/calculate/monthly-cost', methods=['POST'])
def calculate_monthly_cost():
    """Calculate monthly fuel cost"""
    try:
        data = request.get_json()
        make, model = data['vehicle']['make'], data['vehicle']['model']
        monthly_km = float(data['monthly_km'])
        fuel_type_str = data['fuel_type']
        
        vehicle = data_manager.get_vehicle_by_model(make, model)
        if not vehicle:
            return jsonify({'success': False, 'error': 'Vehicle not found'}), 404
        
        fuel_type = FuelType(fuel_type_str)
        result = fuel_calculator.calculate_monthly_cost(vehicle, monthly_km, fuel_type)
        
        return jsonify({
            'success': True,
            'calculation': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/calculate/conversion-savings', methods=['POST'])
def calculate_conversion_savings():
    """Calculate CNG conversion savings"""
    try:
        data = request.get_json()
        make, model = data['vehicle']['make'], data['vehicle']['model']
        monthly_km = float(data['monthly_km'])
        current_fuel_str = data['current_fuel']
        conversion_cost = float(data.get('conversion_cost', 50000))
        years = int(data.get('years', 5))
        
        vehicle = data_manager.get_vehicle_by_model(make, model)
        if not vehicle:
            return jsonify({'success': False, 'error': 'Vehicle not found'}), 404
        
        current_fuel = FuelType(current_fuel_str)
        result = fuel_calculator.calculate_conversion_savings(
            vehicle, monthly_km, current_fuel, conversion_cost, years
        )
        
        return jsonify({
            'success': True,
            'savings': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================================================
# API ROUTES - Routes & Optimization (Using OOP Services)
# ============================================================================

@app.route('/api/routes', methods=['GET'])
def get_routes():
    """Get available routes"""
    try:
        city = request.args.get('city')
        
        if city:
            routes = data_manager.get_routes_by_city(city)
        else:
            routes = data_manager.get_all_routes()
        
        return jsonify({
            'success': True,
            'count': len(routes),
            'routes': [r.to_dict() for r in routes]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/routes/optimize', methods=['POST'])
def optimize_route():
    """Optimize route with refueling stops"""
    try:
        data = request.get_json()
        route_id = data['route_id']
        make, model = data['vehicle']['make'], data['vehicle']['model']
        initial_fuel_kg = float(data.get('initial_fuel_kg', 20))
        
        route = data_manager.get_route_by_id(route_id)
        vehicle = data_manager.get_vehicle_by_model(make, model)
        
        if not route or not vehicle:
            return jsonify({'success': False, 'error': 'Route or vehicle not found'}), 404
        
        optimized = route_optimizer.optimize_route_with_refueling(
            route, vehicle, initial_fuel_kg
        )
        
        return jsonify({
            'success': True,
            'optimized_route': optimized
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================================================
# API ROUTES - Service Centers & Maintenance (Using OOP Services)
# ============================================================================

@app.route('/api/service-centers/nearby', methods=['GET'])
def get_nearby_service_centers():
    """Get nearby service centers"""
    try:
        lat = float(request.args.get('latitude'))
        lng = float(request.args.get('longitude'))
        radius = float(request.args.get('radius', 20))
        
        location = Location(lat, lng, "", "", "", "")
        centers = data_manager.get_nearby_service_centers(location, radius)
        
        return jsonify({
            'success': True,
            'count': len(centers),
            'service_centers': [c.to_dict() for c in centers]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/maintenance/schedule', methods=['POST'])
def get_maintenance_schedule():
    """Get maintenance schedule"""
    try:
        data = request.get_json()
        make, model = data['vehicle']['make'], data['vehicle']['model']
        current_odometer = int(data['current_odometer'])
        annual_km = float(data.get('annual_km', 15000))
        
        vehicle = data_manager.get_vehicle_by_model(make, model)
        if not vehicle:
            return jsonify({'success': False, 'error': 'Vehicle not found'}), 404
        
        schedule = maintenance_service.calculate_maintenance_schedule(
            vehicle, current_odometer, annual_km
        )
        
        return jsonify({
            'success': True,
            'schedule': schedule
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================================================
# API ROUTES - Statistics & Tips
# ============================================================================

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get overall statistics"""
    try:
        stats = data_manager.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/tips', methods=['GET'])
def get_tips():
    """Get tips and recommendations"""
    try:
        category = request.args.get('category')
        
        if category:
            tips = data_manager.get_tips_by_category(category)
        else:
            tips = data_manager.get_all_tips()
        
        return jsonify({
            'success': True,
            'count': len(tips),
            'tips': [t.to_dict() for t in tips]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================================================
# PAGE ROUTES
# ============================================================================

@app.route('/nearby-stations')
@login_required
def nearby_stations_page():
    """Nearby stations page"""
    return render_template('nearby_stations.html')

@app.route('/route-planner')
@login_required
def route_planner_page():
    """Route planner page"""
    return render_template('route_planner.html')

@app.route('/vehicle-comparison')
@login_required
def vehicle_comparison_page():
    """Vehicle comparison page"""
    return render_template('vehicle_comparison.html')

@app.route('/conversion-calculator')
@login_required
def conversion_calculator_page():
    """CNG conversion calculator page"""
    return render_template('conversion_calculator.html')

@app.route('/maintenance-tracker')
@login_required
def maintenance_tracker_page():
    """Maintenance tracker page"""
    return render_template('maintenance_tracker.html')

@app.route('/location-optimizer')
@login_required
def location_optimizer_page():
    """Location optimizer page"""
    return render_template('location_optimizer.html')


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created")
        print(f"Loaded {len(data_manager.get_all_stations())} CNG stations")
        print(f"Loaded {len(data_manager.get_all_vehicles())} vehicles")
        print("Smart CNG Application Started")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
