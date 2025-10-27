from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import json
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2
@dataclass
class Station:
    id: int
    name: str
    lat: float
    lng: float
    address: str
    city: str
    state: str
    pincode: str
    phone: str
    hours: str
    pumps: int
    wait_time: int
    price: float
    payment: List[str]
    facilities: List[str]
    rating: float
    
    def distance_to(self, lat: float, lng: float) -> float:
        R = 6371  # Earth radius in km
        lat1, lon1 = radians(self.lat), radians(self.lng)
        lat2, lon2 = radians(lat), radians(lng)
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c


@dataclass
class Car:
    make: str
    model: str
    year: int
    cng_km_per_kg: float
    petrol_km_per_l: float
    price: float
    category: str


@dataclass
class Route:
    id: str
    name: str
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    distance: float
    time: int
class Data:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance
    
    def __init__(self):
        if self._loaded:
            return
        self._loaded = True
        self.stations: List[Station] = []
        self.cars: List[Car] = []
        self.routes: List[Route] = []
        self._load()
    
    def _load(self):
        """Load all data from data.json"""
        data_file = Path(__file__).parent / 'data.json'
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load stations
            if 'stations' in data:
                for s in data['stations']:
                    self.stations.append(Station(
                        id=s['id'], name=s['name'], lat=s['latitude'], lng=s['longitude'],
                        address=s['address'], city=s['city'], state=s['state'],
                        pincode=s['pincode'], phone=s['phone'], hours=s['operating_hours'],
                        pumps=s['number_of_pumps'], wait_time=s['avg_wait_time_minutes'],
                        price=s['current_price_per_kg'], payment=s.get('payment_methods', []),
                        facilities=s.get('facilities', []), rating=s['rating']
                    ))
            
            # Load cars
            if 'cars' in data:
                for c in data['cars']:
                    self.cars.append(Car(
                        make=c['make'], model=c['model'], year=c['year'],
                        cng_km_per_kg=c['cng_efficiency'], petrol_km_per_l=c['petrol_efficiency'],
                        price=c['price'], category=c['category']
                    ))
            
            # Load routes
            if 'routes' in data:
                for r in data['routes']:
                    self.routes.append(Route(
                        id=r['route_id'], name=r['name'],
                        start_lat=r['start_location']['latitude'],
                        start_lng=r['start_location']['longitude'],
                        end_lat=r['end_location']['latitude'],
                        end_lng=r['end_location']['longitude'],
                        distance=r['distance_km'], time=r['estimated_time_minutes']
                    ))
            
            print(f"✓ Loaded {len(self.stations)} stations, {len(self.cars)} cars, {len(self.routes)} routes")
        
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def find_stations(self, lat: float, lng: float, radius: float = 10) -> List[Station]:
        """Find stations within radius"""
        nearby = []
        for s in self.stations:
            dist = s.distance_to(lat, lng)
            if dist <= radius:
                nearby.append((s, dist))
        nearby.sort(key=lambda x: x[1])
        return [s for s, _ in nearby]
    
    def find_car(self, make: str, model: str) -> Optional[Car]:
        """Find car by make and model"""
        for c in self.cars:
            if c.make.lower() == make.lower() and c.model.lower() == model.lower():
                return c
        return None
    
    def get_cheapest_stations(self, limit: int = 10) -> List[Station]:
        """Get cheapest stations"""
        return sorted(self.stations, key=lambda s: s.price)[:limit]
    
    def get_all_stations(self) -> List[Station]:
        """Get all stations"""
        return self.stations
    
    def get_all_cars(self) -> List[Car]:
        """Get all cars"""
        return self.cars
    
    def get_all_routes(self) -> List[Route]:
        """Get all routes"""
        return self.routes
class Calculator:
    def __init__(self, prices: Dict[str, float] = None):
        self.prices = prices or {'cng': 75.61, 'petrol': 96.72, 'diesel': 89.62}
    
    def trip_cost(self, car: Car, distance: float, fuel: str = 'cng') -> Dict:
        if fuel == 'cng':
            fuel_used = distance / car.cng_km_per_kg
            cost = fuel_used * self.prices['cng']
        else:
            fuel_used = distance / car.petrol_km_per_l
            cost = fuel_used * self.prices['petrol']
        
        return {
            'distance': distance,
            'fuel_used': round(fuel_used, 2),
            'cost': round(cost, 2),
            'cost_per_km': round(cost / distance, 2) if distance > 0 else 0
        }
    
    def monthly_cost(self, car: Car, monthly_km: float, fuel: str = 'cng') -> Dict:
        trip = self.trip_cost(car, monthly_km, fuel)
        return {
            'monthly_km': monthly_km,
            'fuel': fuel,
            'cost': trip['cost'],
            'yearly_cost': round(trip['cost'] * 12, 2)
        }
    
    def savings(self, car: Car, monthly_km: float, conversion_cost: float = 50000) -> Dict:

        petrol_cost = self.monthly_cost(car, monthly_km, 'petrol')
        cng_cost = self.monthly_cost(car, monthly_km, 'cng')
        
        yearly_saving = petrol_cost['yearly_cost'] - cng_cost['yearly_cost']
        breakeven_months = conversion_cost / (yearly_saving / 12) if yearly_saving > 0 else 999
        
        return {
            'conversion_cost': conversion_cost,
            'petrol_yearly': petrol_cost['yearly_cost'],
            'cng_yearly': cng_cost['yearly_cost'],
            'yearly_saving': round(yearly_saving, 2),
            'breakeven_months': round(breakeven_months, 1),
            'breakeven_years': round(breakeven_months / 12, 1),
            'roi': round((yearly_saving * 5 - conversion_cost) / conversion_cost * 100, 1) if conversion_cost > 0 else 0
        }
    
    def compare_cars(self, car1: Car, car2: Car, yearly_km: float = 15000) -> Dict:
        c1_cng = self.monthly_cost(car1, yearly_km / 12, 'cng')
        c2_cng = self.monthly_cost(car2, yearly_km / 12, 'cng')
        
        return {
            'car1': {
                'name': f"{car1.make} {car1.model}",
                'yearly_cost': c1_cng['yearly_cost'],
                'price': car1.price
            },
            'car2': {
                'name': f"{car2.make} {car2.model}",
                'yearly_cost': c2_cng['yearly_cost'],
                'price': car2.price
            },
            'cheaper': car1.make if c1_cng['yearly_cost'] < c2_cng['yearly_cost'] else car2.make
        }