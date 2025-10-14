"""
Smart CNG - Simple Flask App
"""
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os

# Import simple library
from lib import Data, Calculator

# Import database models (for users only)
from db_models import User, db

# Initialize app
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fuelexa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Initialize database
db.init_app(app)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize data and calculator
data = Data()
calc = Calculator()


# ============================================================================
# HOME & AUTH
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html', user=current_user)

@app.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'stations': len(data.stations),
        'cars': len(data.cars),
        'routes': len(data.routes)
    }
    return render_template('dashboard.html', user=current_user, stats=stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        d = request.get_json() if request.is_json else request.form
        user = User.query.filter_by(username=d.get('username')).first()
        if user and user.password_hash == d.get('password'):
            login_user(user)
            return jsonify({'success': True, 'redirect': url_for('dashboard')})
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# ============================================================================
# STATIONS API
# ============================================================================

@app.route('/api/stations/nearby')
def api_stations_nearby():
    """Find nearby stations"""
    try:
        lat = float(request.args.get('latitude'))
        lng = float(request.args.get('longitude'))
        radius = float(request.args.get('radius', 10))
        
        stations = data.find_stations(lat, lng, radius)
        
        return jsonify({
            'success': True,
            'count': len(stations),
            'stations': [{
                'id': s.id, 'name': s.name, 'lat': s.lat, 'lng': s.lng,
                'address': s.address, 'city': s.city, 'phone': s.phone,
                'hours': s.hours, 'pumps': s.pumps, 'wait_time': s.wait_time,
                'price': s.price, 'rating': s.rating,
                'distance': round(s.distance_to(lat, lng), 2)
            } for s in stations]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/stations/cheapest')
def api_stations_cheapest():
    """Get cheapest stations"""
    try:
        limit = int(request.args.get('limit', 10))
        stations = data.get_cheapest_stations(limit)
        
        return jsonify({
            'success': True,
            'count': len(stations),
            'stations': [{
                'id': s.id, 'name': s.name, 'city': s.city,
                'price': s.price, 'rating': s.rating
            } for s in stations]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================================================
# CARS API
# ============================================================================

@app.route('/api/cars')
def api_cars():
    """Get all cars"""
    try:
        category = request.args.get('category')
        cars = data.cars
        
        if category:
            cars = [c for c in cars if c.category.lower() == category.lower()]
        
        return jsonify({
            'success': True,
            'count': len(cars),
            'cars': [{
                'make': c.make, 'model': c.model, 'year': c.year,
                'cng_efficiency': c.cng_km_per_kg,
                'petrol_efficiency': c.petrol_km_per_l,
                'price': c.price, 'category': c.category
            } for c in cars]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/cars/compare', methods=['POST'])
def api_cars_compare():
    """Compare two cars"""
    try:
        d = request.get_json()
        car1 = data.find_car(d['car1']['make'], d['car1']['model'])
        car2 = data.find_car(d['car2']['make'], d['car2']['model'])
        
        if not car1 or not car2:
            return jsonify({'success': False, 'error': 'Car not found'}), 404
        
        yearly_km = float(d.get('yearly_km', 15000))
        result = calc.compare_cars(car1, car2, yearly_km)
        
        return jsonify({'success': True, 'comparison': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================================================
# CALCULATOR API
# ============================================================================

@app.route('/api/calc/trip', methods=['POST'])
def api_calc_trip():
    """Calculate trip cost"""
    try:
        d = request.get_json()
        car = data.find_car(d['car']['make'], d['car']['model'])
        
        if not car:
            return jsonify({'success': False, 'error': 'Car not found'}), 404
        
        distance = float(d['distance'])
        fuel = d.get('fuel', 'cng')
        
        result = calc.trip_cost(car, distance, fuel)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/calc/monthly', methods=['POST'])
def api_calc_monthly():
    """Calculate monthly cost"""
    try:
        d = request.get_json()
        car = data.find_car(d['car']['make'], d['car']['model'])
        
        if not car:
            return jsonify({'success': False, 'error': 'Car not found'}), 404
        
        monthly_km = float(d['monthly_km'])
        fuel = d.get('fuel', 'cng')
        
        result = calc.monthly_cost(car, monthly_km, fuel)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/calc/savings', methods=['POST'])
def api_calc_savings():
    """Calculate CNG conversion savings"""
    try:
        d = request.get_json()
        car = data.find_car(d['car']['make'], d['car']['model'])
        
        if not car:
            return jsonify({'success': False, 'error': 'Car not found'}), 404
        
        monthly_km = float(d['monthly_km'])
        conversion_cost = float(d.get('conversion_cost', 50000))
        
        result = calc.savings(car, monthly_km, conversion_cost)
        return jsonify({'success': True, 'savings': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================================================
# PAGES
# ============================================================================

@app.route('/stations')
@login_required
def page_stations():
    return render_template('nearby_stations.html')

@app.route('/routes')
@login_required
def page_routes():
    return render_template('route_planner.html')

@app.route('/compare')
@login_required
def page_compare():
    return render_template('vehicle_comparison.html')

@app.route('/calculator')
@login_required
def page_calculator():
    return render_template('conversion_calculator.html')


# ============================================================================
# ERRORS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Server error'}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✓ Database ready")
        print(f"✓ Loaded {len(data.stations)} stations")
        print(f"✓ Loaded {len(data.cars)} cars")
        print("✓ Smart CNG started!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
