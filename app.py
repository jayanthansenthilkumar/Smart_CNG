from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
from lib import Data, Calculator
from model import User, db

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