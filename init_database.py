"""
Database Initialization Script
Seeds the database with comprehensive vehicle, fuel, and CNG station data
"""

import json
import os
from datetime import datetime, timedelta
from app import app, db
from models.cng_calculator import (
    User, Vehicle, FuelLog, Station, WaitTime, UserPreference,
    CNGConversionCost, FuelPrice, StationPrice, StationAvailability,
    StationReview, StationBooking, PriceAlert, FavoriteStation, PriceTrend,
    MaintenanceRecord, MaintenanceReminder
)

def load_json_data(filename):
    """Load data from JSON file"""
    filepath = os.path.join('data', filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None

def init_database():
    """Initialize database with comprehensive data"""
    
    with app.app_context():
        # Drop all tables and recreate
        print("Creating database tables...")
        db.drop_all()
        db.create_all()
        
        # Load data from JSON files
        vehicle_data = load_json_data('vehicle_database.json')
        stations_data = load_json_data('cng_stations.json')
        
        if not vehicle_data or not stations_data:
            print("Error: Data files not found!")
            return
        
        # 1. Create demo users
        print("Creating demo users...")
        demo_users = [
            User(
                username='demo_user',
                email='demo@smartcng.com',
                password_hash='pbkdf2:sha256:260000$demo$5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
                phone='+91-9876543210'
            ),
            User(
                username='test_driver',
                email='driver@smartcng.com',
                password_hash='pbkdf2:sha256:260000$test$5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
                phone='+91-9876543211'
            )
        ]
        
        for user in demo_users:
            db.session.add(user)
        db.session.commit()
        print(f"Created {len(demo_users)} demo users")
        
        # 2. Create CNG stations
        print("Creating CNG stations...")
        stations_created = []
        for station_data in stations_data:
            # Combine facilities and payment methods into amenities JSON
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
        
        # 3. Create fuel prices for cities
        print("Creating fuel prices...")
        fuel_prices_data = vehicle_data.get('fuel_prices', {})
        
        for fuel_type, price_data in fuel_prices_data.items():
            for city, price in price_data.get('city_prices', {}).items():
                fuel_price = FuelPrice(
                    city=city,
                    fuel_type=fuel_type,
                    price=price,
                    updated_at=datetime.now()
                )
                db.session.add(fuel_price)
        
        db.session.commit()
        print("Created fuel prices for all cities")
        
        # 4. Create station prices
        print("Creating station-specific prices...")
        for station in stations_created:
            city = station.city
            cng_price = fuel_prices_data['CNG']['city_prices'].get(city, 75.61)
            
            station_price = StationPrice(
                station_id=station.id,
                fuel_type='CNG',
                price=cng_price,
                last_updated=datetime.now()
            )
            db.session.add(station_price)
        
        db.session.commit()
        print(f"Created prices for {len(stations_created)} stations")
        
        # 5. Create wait times for stations
        print("Creating wait time data...")
        for station in stations_created:
            for hour in range(6, 23, 2):  # Every 2 hours from 6 AM to 11 PM
                wait_time = WaitTime(
                    station_id=station.id,
                    hour=hour,
                    avg_wait_minutes=station_data.get('avg_wait_time_minutes', 5) + (hour % 3)
                )
                db.session.add(wait_time)
        
        db.session.commit()
        print("Created wait time predictions")
        
        # 6. Create station availability
        print("Creating station availability...")
        for station in stations_created:
            availability = StationAvailability(
                station_id=station.id,
                is_operational=True,
                available_pumps=station.available_pumps,
                total_pumps=station.total_pumps,
                last_updated=datetime.now()
            )
            db.session.add(availability)
        
        db.session.commit()
        print("Created availability data")
        
        # 7. Create sample reviews for stations
        print("Creating sample reviews...")
        sample_reviews = [
            "Great service, minimal wait time!",
            "Clean facilities and friendly staff.",
            "Convenient location, always operational.",
            "Good prices, well-maintained pumps.",
            "24x7 service is very helpful.",
            "Quick refueling, no issues.",
            "Staff could be more helpful.",
            "Sometimes long queues during peak hours.",
            "Excellent facility with all amenities.",
            "Best CNG station in the area!"
        ]
        
        import random
        for station in stations_created[:10]:  # Reviews for first 10 stations
            for i in range(5):
                review = StationReview(
                    station_id=station.id,
                    user_id=random.choice([1, 2]),
                    rating=random.randint(3, 5),
                    review_text=random.choice(sample_reviews),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 90))
                )
                db.session.add(review)
        
        db.session.commit()
        print("Created sample reviews")
        
        # 8. Create CNG conversion costs
        print("Creating CNG conversion cost data...")
        conversion_costs = vehicle_data.get('cng_conversion_costs', {})
        
        for kit_type, kit_data in conversion_costs.items():
            conversion = CNGConversionCost(
                kit_type=kit_data['name'],
                kit_cost=kit_data['cost'],
                installation_cost=kit_data['installation'],
                total_cost=kit_data['cost'] + kit_data['installation'],
                cylinder_type=kit_data['cylinder_type'],
                warranty_years=kit_data['warranty_years'],
                suitable_vehicles=','.join(kit_data['suitable_for'])
            )
            db.session.add(conversion)
        
        db.session.commit()
        print("Created CNG conversion cost data")
        
        # 9. Create sample vehicles for demo users
        print("Creating sample vehicles...")
        sample_vehicles = [
            {
                'user_id': 1,
                'make': 'Maruti Suzuki',
                'model': 'WagonR',
                'year': 2023,
                'registration_number': 'DL01AB1234',
                'fuel_type': 'CNG',
                'efficiency': 34.05,
                'tank_capacity': 60,
                'purchase_date': datetime(2023, 1, 15),
                'current_odometer': 12500
            },
            {
                'user_id': 1,
                'make': 'Hyundai',
                'model': 'Grand i10 Nios',
                'year': 2024,
                'registration_number': 'DL01CD5678',
                'fuel_type': 'CNG',
                'efficiency': 29.38,
                'tank_capacity': 60,
                'purchase_date': datetime(2024, 6, 1),
                'current_odometer': 3200
            },
            {
                'user_id': 2,
                'make': 'Tata',
                'model': 'Tiago',
                'year': 2023,
                'registration_number': 'MH02EF9012',
                'fuel_type': 'CNG',
                'efficiency': 28.06,
                'tank_capacity': 60,
                'purchase_date': datetime(2023, 8, 20),
                'current_odometer': 8900
            }
        ]
        
        for vehicle_data in sample_vehicles:
            vehicle = Vehicle(**vehicle_data)
            db.session.add(vehicle)
        
        db.session.commit()
        print("Created sample vehicles")
        
        # 10. Create sample fuel logs
        print("Creating sample fuel logs...")
        vehicles = Vehicle.query.all()
        
        for vehicle in vehicles:
            # Create 10 fuel logs for each vehicle over the past 90 days
            for i in range(10):
                days_ago = i * 9  # Every 9 days
                log_date = datetime.now() - timedelta(days=days_ago)
                
                fuel_log = FuelLog(
                    user_id=vehicle.user_id,
                    vehicle_id=vehicle.id,
                    date=log_date,
                    fuel_type=vehicle.fuel_type,
                    quantity=random.uniform(8, 12),  # 8-12 kg
                    price_per_unit=random.uniform(74, 77),
                    total_cost=0,  # Will be calculated
                    odometer_reading=vehicle.current_odometer - (9 - i) * random.randint(250, 350),
                    station_id=random.choice(stations_created).id,
                    is_full_tank=random.choice([True, False])
                )
                fuel_log.total_cost = fuel_log.quantity * fuel_log.price_per_unit
                db.session.add(fuel_log)
        
        db.session.commit()
        print("Created sample fuel logs")
        
        # 11. Create sample maintenance records
        print("Creating sample maintenance records...")
        maintenance_types = [
            'CNG Kit Inspection',
            'Cylinder Hydro Test',
            'Pressure Regulator Service',
            'CNG Filter Replacement',
            'Leak Test',
            'Engine Oil Change',
            'Air Filter Replacement'
        ]
        
        for vehicle in vehicles:
            for i in range(5):
                days_ago = i * 30  # Every 30 days
                record_date = datetime.now() - timedelta(days=days_ago)
                
                maintenance = MaintenanceRecord(
                    vehicle_id=vehicle.id,
                    user_id=vehicle.user_id,
                    maintenance_type=random.choice(maintenance_types),
                    date=record_date,
                    odometer_reading=vehicle.current_odometer - (4 - i) * random.randint(400, 600),
                    cost=random.uniform(500, 2500),
                    service_center=f"{'IGL' if random.random() > 0.5 else 'AutoCare'} Service Center",
                    notes=f"Regular {random.choice(['scheduled', 'preventive', 'routine'])} maintenance"
                )
                db.session.add(maintenance)
        
        db.session.commit()
        print("Created sample maintenance records")
        
        # 12. Create maintenance reminders
        print("Creating maintenance reminders...")
        upcoming_maintenance = [
            ('CNG Kit Inspection', 30, 5500),
            ('Cylinder Hydro Test', 180, None),
            ('Pressure Regulator Service', 45, 10200),
            ('CNG Filter Replacement', 60, 15000)
        ]
        
        for vehicle in vehicles:
            for reminder_type, days_from_now, due_odometer in upcoming_maintenance:
                reminder = MaintenanceReminder(
                    vehicle_id=vehicle.id,
                    user_id=vehicle.user_id,
                    reminder_type=reminder_type,
                    due_date=datetime.now() + timedelta(days=days_from_now),
                    due_odometer=due_odometer,
                    is_completed=False
                )
                db.session.add(reminder)
        
        db.session.commit()
        print("Created maintenance reminders")
        
        # 13. Create price trends
        print("Creating price trend data...")
        cities = ['Delhi', 'Mumbai', 'Pune', 'Bangalore', 'Hyderabad']
        
        for city in cities:
            for i in range(30):  # Last 30 days
                trend_date = datetime.now() - timedelta(days=29-i)
                
                cng_trend = PriceTrend(
                    city=city,
                    fuel_type='CNG',
                    price=random.uniform(74, 77),
                    date=trend_date
                )
                db.session.add(cng_trend)
                
                petrol_trend = PriceTrend(
                    city=city,
                    fuel_type='Petrol',
                    price=random.uniform(95, 107),
                    date=trend_date
                )
                db.session.add(petrol_trend)
        
        db.session.commit()
        print("Created price trend data")
        
        # 14. Create user preferences
        print("Creating user preferences...")
        for user in demo_users:
            preference = UserPreference(
                user_id=user.id,
                preferred_fuel_type='CNG',
                max_detour_km=5,
                preferred_stations=','.join([str(s.id) for s in stations_created[:3]]),
                price_alert_threshold=76.0,
                notification_enabled=True
            )
            db.session.add(preference)
        
        db.session.commit()
        print("Created user preferences")
        
        # 15. Create favorite stations
        print("Creating favorite stations...")
        for user in demo_users:
            for station in stations_created[:5]:
                favorite = FavoriteStation(
                    user_id=user.id,
                    station_id=station.id,
                    notes=f"Convenient location near {'home' if station.id % 2 == 0 else 'office'}"
                )
                db.session.add(favorite)
        
        db.session.commit()
        print("Created favorite stations")
        
        print("\n" + "="*60)
        print("DATABASE INITIALIZATION COMPLETE!")
        print("="*60)
        print(f"✓ Users: {User.query.count()}")
        print(f"✓ Stations: {Station.query.count()}")
        print(f"✓ Vehicles: {Vehicle.query.count()}")
        print(f"✓ Fuel Logs: {FuelLog.query.count()}")
        print(f"✓ Maintenance Records: {MaintenanceRecord.query.count()}")
        print(f"✓ Maintenance Reminders: {MaintenanceReminder.query.count()}")
        print(f"✓ Fuel Prices: {FuelPrice.query.count()}")
        print(f"✓ Station Prices: {StationPrice.query.count()}")
        print(f"✓ Wait Times: {WaitTime.query.count()}")
        print(f"✓ Reviews: {StationReview.query.count()}")
        print(f"✓ Price Trends: {PriceTrend.query.count()}")
        print("="*60)
        print("\nDemo Users:")
        print("  Username: demo_user | Password: demo123")
        print("  Username: test_driver | Password: test123")
        print("="*60)

if __name__ == '__main__':
    print("Starting database initialization...")
    init_database()
    print("\nDatabase is ready to use!")
