from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    created_at = Column(DateTime, default=datetime.utcnow)
    vehicles = relationship('Vehicle', back_populates='user')
    preferences = relationship('UserPreference', back_populates='user', uselist=False)

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    fuel_type = Column(String(20), nullable=False)  # petrol, diesel, cng, hybrid
    avg_mileage = Column(Float)  # km per liter
    monthly_usage = Column(Float)  # km per month
    is_cng_converted = Column(Boolean, default=False)
    conversion_date = Column(DateTime)
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
    fuel_types = Column(String(100))  # comma-separated list of available fuels
    operating_hours = Column(String(100))
    wait_times = relationship('WaitTime', back_populates='station')
    fuel_logs = relationship('FuelLog', back_populates='station')

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