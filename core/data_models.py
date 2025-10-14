"""
Core Data Models - OOP-based classes for all JSON data handling
This module provides object-oriented interfaces for all data entities
"""
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class FuelType(Enum):
    """Enumeration for fuel types"""
    CNG = "CNG"
    PETROL = "Petrol"
    DIESEL = "Diesel"
    HYBRID = "Hybrid"


class PaymentMethod(Enum):
    """Enumeration for payment methods"""
    CASH = "Cash"
    CARD = "Card"
    UPI = "UPI"
    WALLET = "Wallet"


@dataclass
class Location:
    """Base location class"""
    latitude: float
    longitude: float
    address: str
    city: str
    state: str
    pincode: str
    
    def distance_to(self, other: 'Location') -> float:
        """Calculate distance to another location in km using Haversine formula"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in km
        
        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other.latitude), radians(other.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode
        }


@dataclass
class CNGStation:
    """CNG Station with all properties and methods"""
    id: int
    name: str
    location: Location
    phone: str
    operating_hours: str
    number_of_pumps: int
    avg_wait_time_minutes: int
    current_price_per_kg: float
    payment_methods: List[PaymentMethod]
    facilities: List[str]
    rating: float
    total_reviews: int
    last_updated: datetime
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'CNGStation':
        """Create CNGStation from JSON data"""
        location = Location(
            latitude=data['latitude'],
            longitude=data['longitude'],
            address=data['address'],
            city=data['city'],
            state=data['state'],
            pincode=data['pincode']
        )
        
        payment_methods = [PaymentMethod(pm) for pm in data.get('payment_methods', [])]
        
        last_updated = datetime.fromisoformat(data['last_updated'].replace('Z', '+00:00'))
        
        return cls(
            id=data['id'],
            name=data['name'],
            location=location,
            phone=data['phone'],
            operating_hours=data['operating_hours'],
            number_of_pumps=data['number_of_pumps'],
            avg_wait_time_minutes=data['avg_wait_time_minutes'],
            current_price_per_kg=data['current_price_per_kg'],
            payment_methods=payment_methods,
            facilities=data.get('facilities', []),
            rating=data['rating'],
            total_reviews=data['total_reviews'],
            last_updated=last_updated
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            **self.location.to_dict(),
            'phone': self.phone,
            'operating_hours': self.operating_hours,
            'number_of_pumps': self.number_of_pumps,
            'avg_wait_time_minutes': self.avg_wait_time_minutes,
            'current_price_per_kg': self.current_price_per_kg,
            'payment_methods': [pm.value for pm in self.payment_methods],
            'facilities': self.facilities,
            'rating': self.rating,
            'total_reviews': self.total_reviews,
            'last_updated': self.last_updated.isoformat()
        }
    
    def is_open_at(self, time: datetime) -> bool:
        """Check if station is open at given time"""
        if self.operating_hours == "24x7":
            return True
        # Add logic for parsing operating hours
        return True
    
    def calculate_cost(self, kg: float) -> float:
        """Calculate cost for given kg of CNG"""
        return kg * self.current_price_per_kg
    
    def accepts_payment(self, method: PaymentMethod) -> bool:
        """Check if station accepts given payment method"""
        return method in self.payment_methods
    
    def get_efficiency_score(self) -> float:
        """Calculate efficiency score based on wait time and pumps"""
        return (self.number_of_pumps * 10) / max(self.avg_wait_time_minutes, 1)


@dataclass
class Vehicle:
    """Vehicle with fuel efficiency and cost details"""
    make: str
    model: str
    year: int
    fuel_types: List[FuelType]
    cng_efficiency: float  # km per kg
    petrol_efficiency: float  # km per liter
    price: float
    insurance_annual: float
    maintenance_annual_cng: float
    maintenance_annual_petrol: float
    depreciation_rate: float
    co2_per_km_petrol: float
    co2_per_km_cng: float
    category: str
    diesel_efficiency: Optional[float] = None
    maintenance_annual_diesel: Optional[float] = None
    co2_per_km_diesel: Optional[float] = None
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Vehicle':
        """Create Vehicle from JSON data"""
        fuel_types = [FuelType(ft) for ft in data['fuel_types']]
        
        return cls(
            make=data['make'],
            model=data['model'],
            year=data['year'],
            fuel_types=fuel_types,
            cng_efficiency=data['cng_efficiency'],
            petrol_efficiency=data['petrol_efficiency'],
            price=data['price'],
            insurance_annual=data['insurance_annual'],
            maintenance_annual_cng=data['maintenance_annual_cng'],
            maintenance_annual_petrol=data['maintenance_annual_petrol'],
            depreciation_rate=data['depreciation_rate'],
            co2_per_km_petrol=data['co2_per_km_petrol'],
            co2_per_km_cng=data['co2_per_km_cng'],
            category=data['category'],
            diesel_efficiency=data.get('diesel_efficiency'),
            maintenance_annual_diesel=data.get('maintenance_annual_diesel'),
            co2_per_km_diesel=data.get('co2_per_km_diesel')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'fuel_types': [ft.value for ft in self.fuel_types],
            'cng_efficiency': self.cng_efficiency,
            'petrol_efficiency': self.petrol_efficiency,
            'price': self.price,
            'insurance_annual': self.insurance_annual,
            'maintenance_annual_cng': self.maintenance_annual_cng,
            'maintenance_annual_petrol': self.maintenance_annual_petrol,
            'depreciation_rate': self.depreciation_rate,
            'co2_per_km_petrol': self.co2_per_km_petrol,
            'co2_per_km_cng': self.co2_per_km_cng,
            'category': self.category
        }
        
        if self.diesel_efficiency:
            result['diesel_efficiency'] = self.diesel_efficiency
        if self.maintenance_annual_diesel:
            result['maintenance_annual_diesel'] = self.maintenance_annual_diesel
        if self.co2_per_km_diesel:
            result['co2_per_km_diesel'] = self.co2_per_km_diesel
            
        return result
    
    def get_efficiency(self, fuel_type: FuelType) -> float:
        """Get efficiency for specific fuel type"""
        if fuel_type == FuelType.CNG:
            return self.cng_efficiency
        elif fuel_type == FuelType.PETROL:
            return self.petrol_efficiency
        elif fuel_type == FuelType.DIESEL and self.diesel_efficiency:
            return self.diesel_efficiency
        else:
            raise ValueError(f"Efficiency not available for {fuel_type}")
    
    def get_maintenance_cost(self, fuel_type: FuelType) -> float:
        """Get annual maintenance cost for specific fuel type"""
        if fuel_type == FuelType.CNG:
            return self.maintenance_annual_cng
        elif fuel_type == FuelType.PETROL:
            return self.maintenance_annual_petrol
        elif fuel_type == FuelType.DIESEL and self.maintenance_annual_diesel:
            return self.maintenance_annual_diesel
        else:
            raise ValueError(f"Maintenance cost not available for {fuel_type}")
    
    def get_co2_emission(self, fuel_type: FuelType) -> float:
        """Get CO2 emission per km for specific fuel type"""
        if fuel_type == FuelType.CNG:
            return self.co2_per_km_cng
        elif fuel_type == FuelType.PETROL:
            return self.co2_per_km_petrol
        elif fuel_type == FuelType.DIESEL and self.co2_per_km_diesel:
            return self.co2_per_km_diesel
        else:
            raise ValueError(f"CO2 emission not available for {fuel_type}")
    
    def calculate_fuel_cost(self, distance_km: float, fuel_type: FuelType, fuel_price: float) -> float:
        """Calculate fuel cost for given distance"""
        efficiency = self.get_efficiency(fuel_type)
        fuel_consumed = distance_km / efficiency
        return fuel_consumed * fuel_price
    
    def supports_fuel_type(self, fuel_type: FuelType) -> bool:
        """Check if vehicle supports given fuel type"""
        return fuel_type in self.fuel_types


@dataclass
class Route:
    """Route information"""
    route_id: str
    name: str
    start_location: Location
    end_location: Location
    distance_km: float
    estimated_time_minutes: int
    waypoints: List[Location] = field(default_factory=list)
    cng_stations_enroute: List[int] = field(default_factory=list)  # Station IDs
    toll_cost: float = 0.0
    highway_percentage: float = 0.0
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Route':
        """Create Route from JSON data"""
        start_loc = Location(**data['start_location'])
        end_loc = Location(**data['end_location'])
        
        waypoints = [Location(**wp) for wp in data.get('waypoints', [])]
        
        return cls(
            route_id=data['route_id'],
            name=data['name'],
            start_location=start_loc,
            end_location=end_loc,
            distance_km=data['distance_km'],
            estimated_time_minutes=data['estimated_time_minutes'],
            waypoints=waypoints,
            cng_stations_enroute=data.get('cng_stations_enroute', []),
            toll_cost=data.get('toll_cost', 0.0),
            highway_percentage=data.get('highway_percentage', 0.0)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'route_id': self.route_id,
            'name': self.name,
            'start_location': self.start_location.to_dict(),
            'end_location': self.end_location.to_dict(),
            'distance_km': self.distance_km,
            'estimated_time_minutes': self.estimated_time_minutes,
            'waypoints': [wp.to_dict() for wp in self.waypoints],
            'cng_stations_enroute': self.cng_stations_enroute,
            'toll_cost': self.toll_cost,
            'highway_percentage': self.highway_percentage
        }
    
    def calculate_total_cost(self, vehicle: Vehicle, fuel_type: FuelType, fuel_price: float) -> float:
        """Calculate total trip cost including fuel and toll"""
        fuel_cost = vehicle.calculate_fuel_cost(self.distance_km, fuel_type, fuel_price)
        return fuel_cost + self.toll_cost


@dataclass
class ServiceCenter:
    """Service center information"""
    center_id: int
    name: str
    location: Location
    phone: str
    email: str
    operating_hours: str
    services: List[str]
    specialization: List[str]
    rating: float
    authorized_brands: List[str]
    emergency_service: bool
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ServiceCenter':
        """Create ServiceCenter from JSON data"""
        location = Location(
            latitude=data['latitude'],
            longitude=data['longitude'],
            address=data['address'],
            city=data['city'],
            state=data['state'],
            pincode=data['pincode']
        )
        
        return cls(
            center_id=data['center_id'],
            name=data['name'],
            location=location,
            phone=data['phone'],
            email=data['email'],
            operating_hours=data['operating_hours'],
            services=data['services'],
            specialization=data['specialization'],
            rating=data['rating'],
            authorized_brands=data['authorized_brands'],
            emergency_service=data['emergency_service']
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'center_id': self.center_id,
            'name': self.name,
            **self.location.to_dict(),
            'phone': self.phone,
            'email': self.email,
            'operating_hours': self.operating_hours,
            'services': self.services,
            'specialization': self.specialization,
            'rating': self.rating,
            'authorized_brands': self.authorized_brands,
            'emergency_service': self.emergency_service
        }
    
    def provides_service(self, service_type: str) -> bool:
        """Check if center provides specific service"""
        return service_type.lower() in [s.lower() for s in self.services]
    
    def supports_brand(self, brand: str) -> bool:
        """Check if center is authorized for brand"""
        return brand.lower() in [b.lower() for b in self.authorized_brands]


@dataclass
class TipRecommendation:
    """Tip or recommendation"""
    tip_id: int
    category: str
    title: str
    description: str
    priority: str
    applicable_vehicles: List[str]
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'TipRecommendation':
        """Create TipRecommendation from JSON data"""
        return cls(
            tip_id=data['tip_id'],
            category=data['category'],
            title=data['title'],
            description=data['description'],
            priority=data['priority'],
            applicable_vehicles=data.get('applicable_vehicles', [])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'tip_id': self.tip_id,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'applicable_vehicles': self.applicable_vehicles
        }
    
    def applies_to_vehicle(self, vehicle: Vehicle) -> bool:
        """Check if tip applies to given vehicle"""
        if not self.applicable_vehicles:
            return True
        return vehicle.category.lower() in [av.lower() for av in self.applicable_vehicles]
