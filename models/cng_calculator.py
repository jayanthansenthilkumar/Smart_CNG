from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    vehicles = relationship('Vehicle', back_populates='user')
    preferences = relationship('UserPreference', back_populates='user', uselist=False)
    reviews = relationship('StationReview', back_populates='user')
    bookings = relationship('StationBooking', back_populates='user')
    alerts = relationship('PriceAlert', back_populates='user')
    favorite_stations = relationship('FavoriteStation', back_populates='user')

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    registration_number = Column(String(20), unique=True)
    fuel_type = Column(String(20), nullable=False)  # petrol, diesel, cng, hybrid
    efficiency = Column(Float)  # km per kg/liter
    avg_mileage = Column(Float)  # km per liter (deprecated, use efficiency)
    monthly_usage = Column(Float)  # km per month
    tank_capacity = Column(Float)  # liters or kg
    current_odometer = Column(Integer)  # current odometer reading
    purchase_date = Column(DateTime)
    purchase_price = Column(Float)
    insurance_expiry = Column(DateTime)
    is_cng_converted = Column(Boolean, default=False)
    conversion_date = Column(DateTime)
    conversion_cost = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship('User', back_populates='vehicles')
    fuel_logs = relationship('FuelLog', back_populates='vehicle')

class FuelLog(db.Model):
    __tablename__ = 'fuel_logs'
    
    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    fuel_type = Column(String(20), nullable=False)
    amount = Column(Float, nullable=False)  # liters/kg
    cost = Column(Float, nullable=False)  # total cost
    odometer = Column(Float)  # current odometer reading
    station_id = Column(Integer, ForeignKey('stations.id'))
    vehicle = relationship('Vehicle', back_populates='fuel_logs')
    station = relationship('Station', back_populates='fuel_logs')

class Station(db.Model):
    __tablename__ = 'stations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(200))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default='India')
    fuel_types = Column(String(100))  # comma-separated list of available fuels
    operating_hours = Column(String(100))
    operator = Column(String(100))  # Indian Oil, GAIL, etc.
    brand = Column(String(100))
    phone = Column(String(20))
    website = Column(String(200))
    amenities = Column(JSON)  # payment methods, facilities, etc.
    is_24x7 = Column(Boolean, default=False)
    has_queue_system = Column(Boolean, default=False)
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    data_source = Column(String(50))  # google, osm, government, manual
    last_verified = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    wait_times = relationship('WaitTime', back_populates='station')
    fuel_logs = relationship('FuelLog', back_populates='station')
    prices = relationship('StationPrice', back_populates='station')
    reviews = relationship('StationReview', back_populates='station')
    bookings = relationship('StationBooking', back_populates='station')
    availability = relationship('StationAvailability', back_populates='station', uselist=False)

class WaitTime(db.Model):
    __tablename__ = 'wait_times'
    
    id = Column(Integer, primary_key=True)
    station_id = Column(Integer, ForeignKey('stations.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    wait_minutes = Column(Integer, nullable=False)
    num_vehicles = Column(Integer)
    station = relationship('Station', back_populates='wait_times')

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    default_radius = Column(Float, default=5.0)  # search radius in km
    preferred_station_id = Column(Integer, ForeignKey('stations.id'))
    notification_enabled = Column(Boolean, default=True)
    user = relationship('User', back_populates='preferences')
    preferred_station = relationship('Station')

class CNGConversionCost(db.Model):
    __tablename__ = 'cng_conversion_costs'
    
    id = Column(Integer, primary_key=True)
    vehicle_type = Column(String(50), nullable=False)
    base_cost = Column(Float, nullable=False)
    labor_cost = Column(Float, nullable=False)
    kit_type = Column(String(50))
    warranty_period = Column(Integer)  # months
    updated_at = Column(DateTime, default=datetime.utcnow)

class FuelPrice(db.Model):
    __tablename__ = 'fuel_prices'
    
    id = Column(Integer, primary_key=True)
    fuel_type = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)
    city = Column(String(50), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    @classmethod
    def get_latest_prices(cls, city):
        """Get the latest fuel prices for a given city"""
        latest_prices = {}
        for fuel_type in ['petrol', 'diesel', 'cng']:
            price = cls.query.filter_by(
                fuel_type=fuel_type, 
                city=city
            ).order_by(
                cls.updated_at.desc()
            ).first()
            if price:
                latest_prices[fuel_type] = price.price
        return latest_prices


class StationPrice(db.Model):
    """Real-time pricing at specific stations"""
    __tablename__ = 'station_prices'
    
    id = Column(Integer, primary_key=True)
    station_id = Column(Integer, ForeignKey('stations.id'), nullable=False)
    fuel_type = Column(String(20), nullable=False)  # cng, petrol, diesel
    price = Column(Float, nullable=False)
    currency = Column(String(10), default='INR')
    effective_date = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    verified_by_users = Column(Integer, default=0)
    
    station = relationship('Station', back_populates='prices')


class StationAvailability(db.Model):
    """Real-time availability status of stations"""
    __tablename__ = 'station_availability'
    
    id = Column(Integer, primary_key=True)
    station_id = Column(Integer, ForeignKey('stations.id'), nullable=False, unique=True)
    is_operational = Column(Boolean, default=True)
    current_queue_length = Column(Integer, default=0)
    estimated_wait_minutes = Column(Integer, default=0)
    available_pumps = Column(Integer, default=1)
    total_pumps = Column(Integer, default=1)
    cng_stock_level = Column(String(20))  # 'high', 'medium', 'low', 'out'
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    station = relationship('Station', back_populates='availability')


class StationReview(db.Model):
    """User reviews and ratings for stations"""
    __tablename__ = 'station_reviews'
    
    id = Column(Integer, primary_key=True)
    station_id = Column(Integer, ForeignKey('stations.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review_text = Column(Text)
    service_quality = Column(Integer)  # 1-5
    wait_time_rating = Column(Integer)  # 1-5
    price_rating = Column(Integer)  # 1-5
    cleanliness_rating = Column(Integer)  # 1-5
    helpful_count = Column(Integer, default=0)
    verified_visit = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    station = relationship('Station', back_populates='reviews')
    user = relationship('User', back_populates='reviews')


class StationBooking(db.Model):
    """Booking/Queue system for CNG stations"""
    __tablename__ = 'station_bookings'
    
    id = Column(Integer, primary_key=True)
    station_id = Column(Integer, ForeignKey('stations.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    booking_time = Column(DateTime, nullable=False)
    estimated_arrival = Column(DateTime, nullable=False)
    queue_number = Column(Integer)
    status = Column(String(20), default='pending')  # pending, confirmed, completed, cancelled
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    estimated_fill_amount = Column(Float)  # kg
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    station = relationship('Station', back_populates='bookings')
    user = relationship('User', back_populates='bookings')
    vehicle = relationship('Vehicle')


class PriceAlert(db.Model):
    """Price drop alerts for users"""
    __tablename__ = 'price_alerts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    fuel_type = Column(String(20), nullable=False)
    city = Column(String(100))
    station_id = Column(Integer, ForeignKey('stations.id'))
    alert_threshold = Column(Float)  # alert when price drops below this
    is_active = Column(Boolean, default=True)
    notification_method = Column(String(20), default='email')  # email, sms, push
    created_at = Column(DateTime, default=datetime.utcnow)
    last_triggered = Column(DateTime)
    
    user = relationship('User', back_populates='alerts')
    station = relationship('Station')


class FavoriteStation(db.Model):
    """User's favorite/saved stations"""
    __tablename__ = 'favorite_stations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    station_id = Column(Integer, ForeignKey('stations.id'), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='favorite_stations')
    station = relationship('Station')


class PriceTrend(db.Model):
    """Historical price trends for analytics"""
    __tablename__ = 'price_trends'
    
    id = Column(Integer, primary_key=True)
    station_id = Column(Integer, ForeignKey('stations.id'))
    city = Column(String(100), nullable=False)
    fuel_type = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    
    station = relationship('Station')


class MaintenanceRecord(db.Model):
    """CNG vehicle maintenance records"""
    __tablename__ = 'maintenance_records'
    
    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    maintenance_type = Column(String(100), nullable=False)
    date = Column(DateTime, nullable=False)
    odometer_reading = Column(Integer)
    cost = Column(Float, nullable=False)
    service_center = Column(String(200))
    technician_name = Column(String(100))
    parts_replaced = Column(Text)
    notes = Column(Text)
    next_service_due = Column(DateTime)
    next_service_odometer = Column(Integer)
    invoice_number = Column(String(50))
    warranty_applicable = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    vehicle = relationship('Vehicle')
    user = relationship('User')


class MaintenanceReminder(db.Model):
    """Maintenance reminders for CNG vehicles"""
    __tablename__ = 'maintenance_reminders'
    
    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    reminder_type = Column(String(100), nullable=False)
    due_date = Column(DateTime)
    due_odometer = Column(Integer)
    reminder_sent = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    is_urgent = Column(Boolean, default=False)
    notification_days_before = Column(Integer, default=7)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    vehicle = relationship('Vehicle')
    user = relationship('User')