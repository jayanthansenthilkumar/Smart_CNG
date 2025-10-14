"""
Simple Database Initialization Script
Seeds the database with essential data for testing
"""

from app import app, db
from models.cng_calculator import User, Vehicle, Station, FuelLog, FuelPrice, StationPrice
from datetime import datetime, timedelta
import json
import random

def init_database():
    """Initialize database with basic test data"""
    
    with app.app_context():
        # Drop all tables and recreate
        print("Creating database tables...")
        db.drop_all()
        db.create_all()
        
        # 1. Create demo users
        print("Creating demo users...")
        demo_user = User(
            username='demo_user',
            email='demo@smartcng.com',
            password_hash='pbkdf2:sha256:260000$demo$5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
            phone='+91-9876543210'
        )
        db.session.add(demo_user)
        
        test_user = User(
            username='test_driver',
            email='driver@smartcng.com',
            password_hash='pbkdf2:sha256:260000$test$5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
            phone='+91-9876543211'
        )
        db.session.add(test_user)
        db.session.commit()
        print(f"Created 2 demo users")
        print(f"  - Username: demo_user, Password: demo123")
        print(f"  - Username: test_driver, Password: test123")
        
        # 2. Load and create stations from JSON
        print("\nCreating CNG stations...")
        try:
            with open('data/cng_stations.json', 'r') as f:
                stations_data = json.load(f)
            
            stations_created = []
            for station_data in stations_data:
                amenities = {
                    'facilities': station_data.get('facilities', []),
                    'payment_methods': station_data.get('payment_methods', [])
                }
                
                station = Station(
                    name=station_data['name'],
                    latitude=station_data['latitude'],
                    longitude=station_data['longitude'],
                    address=station_data['address'],
                    city=station_data['city'],
                    state=station_data.get('state'),
                    phone=station_data.get('phone'),
                    operating_hours=station_data.get('operating_hours', '24x7'),
                    amenities=amenities,
                    is_24x7=(station_data.get('operating_hours', '').lower() == '24 hours'),
                    average_rating=station_data.get('rating', 4.0),
                    total_reviews=station_data.get('total_reviews', 0),
                    operator='CNG',
                    fuel_types='CNG',
                    last_verified=datetime.now()
                )
                db.session.add(station)
                stations_created.append(station)
            
            db.session.commit()
            print(f"Created {len(stations_created)} CNG stations")
        except Exception as e:
            print(f"Error loading stations: {e}")
        
        # 3. Create fuel prices
        print("\nCreating fuel prices...")
        cities = ['Delhi', 'Mumbai', 'Pune', 'Bangalore', 'Hyderabad', 'Ahmedabad', 'Lucknow', 'Kanpur']
        fuel_prices_config = {
            'cng': {
                'Delhi': 75.61, 'Mumbai': 82.0, 'Pune': 83.5, 'Bangalore': 81.0,
                'Hyderabad': 79.0, 'Ahmedabad': 77.0, 'Lucknow': 78.5, 'Kanpur': 78.0
            },
            'petrol': {
                'Delhi': 96.72, 'Mumbai': 106.31, 'Pune': 104.24, 'Bangalore': 102.86,
                'Hyderabad': 109.66, 'Ahmedabad': 96.48, 'Lucknow': 96.57, 'Kanpur': 101.19
            },
            'diesel': {
                'Delhi': 89.62, 'Mumbai': 94.27, 'Pune': 90.96, 'Bangalore': 88.94,
                'Hyderabad': 97.82, 'Ahmedabad': 91.26, 'Lucknow': 89.76, 'Kanpur': 91.88
            }
        }
        
        for fuel_type, city_prices in fuel_prices_config.items():
            for city, price in city_prices.items():
                fuel_price = FuelPrice(
                    city=city,
                    fuel_type=fuel_type,
                    price=price,
                    updated_at=datetime.now()
                )
                db.session.add(fuel_price)
        
        db.session.commit()
        print(f"Created fuel prices for {len(cities)} cities")
        
        # 4. Create demo vehicles
        print("\nCreating demo vehicles...")
        vehicles_config = [
            {
                'user': demo_user,
                'make': 'Maruti Suzuki',
                'model': 'Wagon R CNG',
                'year': 2023,
                'fuel_type': 'cng',
                'efficiency': 26.0,
                'registration_number': 'DL-01-AB-1234',
                'is_cng_converted': False,
                'current_odometer': 15000
            },
            {
                'user': demo_user,
                'make': 'Hyundai',
                'model': 'Grand i10 Nios',
                'year': 2022,
                'fuel_type': 'petrol',
                'efficiency': 18.0,
                'registration_number': 'DL-02-CD-5678',
                'is_cng_converted': True,
                'conversion_date': datetime.now() - timedelta(days=365),
                'conversion_cost': 45000.0,
                'current_odometer': 35000
            },
            {
                'user': test_user,
                'make': 'Tata',
                'model': 'Tiago CNG',
                'year': 2023,
                'fuel_type': 'cng',
                'efficiency': 24.0,
                'registration_number': 'MH-01-EF-9012',
                'is_cng_converted': False,
                'current_odometer': 8000
            }
        ]
        
        vehicles_created = []
        for vehicle_data in vehicles_config:
            vehicle = Vehicle(**vehicle_data)
            db.session.add(vehicle)
            vehicles_created.append(vehicle)
        
        db.session.commit()
        print(f"Created {len(vehicles_created)} demo vehicles")
        
        # 5. Create fuel logs
        print("\nCreating fuel logs...")
        fuel_logs_created = 0
        
        for vehicle in vehicles_created:
            # Create 10 fuel logs for each vehicle over the past 90 days
            for i in range(10):
                days_ago = random.randint(1, 90)
                log_date = datetime.now() - timedelta(days=days_ago)
                
                # Random station from the city
                station = random.choice(stations_created)
                
                # Fuel amount and cost based on fuel type
                if vehicle.fuel_type == 'cng':
                    amount = random.uniform(4, 10)  # kg
                    price_per_unit = random.uniform(75, 85)
                else:
                    amount = random.uniform(20, 40)  # liters
                    price_per_unit = random.uniform(95, 110)
                
                fuel_log = FuelLog(
                    vehicle_id=vehicle.id,
                    station_id=station.id,
                    fuel_type=vehicle.fuel_type,
                    amount=amount,
                    cost=amount * price_per_unit,
                    odometer=vehicle.current_odometer - (i * random.randint(200, 400)),
                    date=log_date
                )
                db.session.add(fuel_log)
                fuel_logs_created += 1
        
        db.session.commit()
        print(f"Created {fuel_logs_created} fuel logs")
        
        # 6. Create station prices
        print("\nCreating station-specific CNG prices...")
        station_prices_created = 0
        
        for station in stations_created:
            # Get the city price as base
            city_price = fuel_prices_config['cng'].get(station.city, 75.0)
            # Add small variation
            station_price_value = city_price + random.uniform(-2, 2)
            
            station_price = StationPrice(
                station_id=station.id,
                fuel_type='cng',
                price=round(station_price_value, 2),
                updated_at=datetime.now()
            )
            db.session.add(station_price)
            station_prices_created += 1
        
        db.session.commit()
        print(f"Created {station_prices_created} station prices")
        
        # Print summary
        print("\n" + "="*60)
        print("DATABASE INITIALIZATION COMPLETE")
        print("="*60)
        print(f"Users created: 2")
        print(f"Stations created: {len(stations_created)}")
        print(f"Fuel prices created: {len(cities) * 3}")
        print(f"Vehicles created: {len(vehicles_created)}")
        print(f"Fuel logs created: {fuel_logs_created}")
        print(f"Station prices created: {station_prices_created}")
        print("\nDemo Login Credentials:")
        print("  Username: demo_user | Password: demo123")
        print("  Username: test_driver | Password: test123")
        print("="*60)

if __name__ == '__main__':
    init_database()
