"""
Database Models - Simple consolidated file
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Vehicle(db.Model):
    """Vehicle model"""
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    year = db.Column(db.Integer)
    fuel_type = db.Column(db.String(20))
    efficiency = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FuelLog(db.Model):
    """Fuel log model"""
    __tablename__ = 'fuel_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    fuel_type = db.Column(db.String(20))
    amount = db.Column(db.Float)
    cost = db.Column(db.Float)
    odometer = db.Column(db.Float)


class Station(db.Model):
    """Station model"""
    __tablename__ = 'stations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    rating = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
