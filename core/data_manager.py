"""
Data Manager - Handles loading and managing all JSON data as objects
Implements Singleton pattern for centralized data management
"""
import json
import os
from typing import List, Dict, Optional
from pathlib import Path
from .data_models import (
    CNGStation, Vehicle, Route, ServiceCenter, 
    TipRecommendation, Location, FuelType
)


class DataManager:
    """Singleton Data Manager for all JSON data"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._data_dir = Path(__file__).parent.parent / 'data'
        self._cng_stations: List[CNGStation] = []
        self._vehicles: List[Vehicle] = []
        self._routes: List[Route] = []
        self._service_centers: List[ServiceCenter] = []
        self._tips: List[TipRecommendation] = []
        
        # Load all data
        self.reload_all()
    
    def reload_all(self):
        """Reload all data from JSON files"""
        self._load_cng_stations()
        self._load_vehicles()
        self._load_routes()
        self._load_service_centers()
        self._load_tips()
    
    def _load_json_file(self, filename: str) -> any:
        """Load JSON file from data directory"""
        filepath = self._data_dir / filename
        if not filepath.exists():
            print(f"Warning: {filename} not found")
            return None
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return None
    
    def _load_cng_stations(self):
        """Load CNG stations from JSON"""
        data = self._load_json_file('cng_stations.json')
        if data:
            self._cng_stations = [CNGStation.from_json(station) for station in data]
            print(f"Loaded {len(self._cng_stations)} CNG stations")
    
    def _load_vehicles(self):
        """Load vehicles from JSON"""
        data = self._load_json_file('vehicle_database.json')
        if data and 'vehicles' in data:
            self._vehicles = [Vehicle.from_json(vehicle) for vehicle in data['vehicles']]
            print(f"Loaded {len(self._vehicles)} vehicles")
    
    def _load_routes(self):
        """Load routes from JSON"""
        data = self._load_json_file('routes_database.json')
        if data and 'routes' in data:
            self._routes = [Route.from_json(route) for route in data['routes']]
            print(f"Loaded {len(self._routes)} routes")
    
    def _load_service_centers(self):
        """Load service centers from JSON"""
        data = self._load_json_file('service_centers.json')
        if data and 'service_centers' in data:
            self._service_centers = [ServiceCenter.from_json(center) for center in data['service_centers']]
            print(f"Loaded {len(self._service_centers)} service centers")
    
    def _load_tips(self):
        """Load tips and recommendations from JSON"""
        data = self._load_json_file('tips_recommendations.json')
        if data and 'tips' in data:
            self._tips = [TipRecommendation.from_json(tip) for tip in data['tips']]
            print(f"Loaded {len(self._tips)} tips")
    
    # CNG Stations Methods
    def get_all_stations(self) -> List[CNGStation]:
        """Get all CNG stations"""
        return self._cng_stations.copy()
    
    def get_station_by_id(self, station_id: int) -> Optional[CNGStation]:
        """Get station by ID"""
        for station in self._cng_stations:
            if station.id == station_id:
                return station
        return None
    
    def get_stations_by_city(self, city: str) -> List[CNGStation]:
        """Get stations in a specific city"""
        return [s for s in self._cng_stations if s.location.city.lower() == city.lower()]
    
    def get_nearby_stations(self, location: Location, radius_km: float = 10) -> List[CNGStation]:
        """Get stations within radius of location"""
        nearby = []
        for station in self._cng_stations:
            distance = location.distance_to(station.location)
            if distance <= radius_km:
                nearby.append(station)
        return sorted(nearby, key=lambda s: location.distance_to(s.location))
    
    def get_stations_with_min_rating(self, min_rating: float) -> List[CNGStation]:
        """Get stations with minimum rating"""
        return [s for s in self._cng_stations if s.rating >= min_rating]
    
    def get_cheapest_stations(self, limit: int = 10) -> List[CNGStation]:
        """Get cheapest stations"""
        return sorted(self._cng_stations, key=lambda s: s.current_price_per_kg)[:limit]
    
    # Vehicles Methods
    def get_all_vehicles(self) -> List[Vehicle]:
        """Get all vehicles"""
        return self._vehicles.copy()
    
    def get_vehicle_by_model(self, make: str, model: str) -> Optional[Vehicle]:
        """Get vehicle by make and model"""
        for vehicle in self._vehicles:
            if vehicle.make.lower() == make.lower() and vehicle.model.lower() == model.lower():
                return vehicle
        return None
    
    def get_vehicles_by_category(self, category: str) -> List[Vehicle]:
        """Get vehicles by category"""
        return [v for v in self._vehicles if v.category.lower() == category.lower()]
    
    def get_vehicles_by_fuel_type(self, fuel_type: FuelType) -> List[Vehicle]:
        """Get vehicles supporting specific fuel type"""
        return [v for v in self._vehicles if v.supports_fuel_type(fuel_type)]
    
    def get_most_efficient_vehicles(self, fuel_type: FuelType, limit: int = 10) -> List[Vehicle]:
        """Get most efficient vehicles for fuel type"""
        eligible = [v for v in self._vehicles if v.supports_fuel_type(fuel_type)]
        return sorted(eligible, key=lambda v: v.get_efficiency(fuel_type), reverse=True)[:limit]
    
    # Routes Methods
    def get_all_routes(self) -> List[Route]:
        """Get all routes"""
        return self._routes.copy()
    
    def get_route_by_id(self, route_id: str) -> Optional[Route]:
        """Get route by ID"""
        for route in self._routes:
            if route.route_id == route_id:
                return route
        return None
    
    def get_routes_by_city(self, city: str) -> List[Route]:
        """Get routes starting or ending in city"""
        return [r for r in self._routes 
                if r.start_location.city.lower() == city.lower() 
                or r.end_location.city.lower() == city.lower()]
    
    def get_routes_with_stations(self) -> List[Route]:
        """Get routes with CNG stations en route"""
        return [r for r in self._routes if len(r.cng_stations_enroute) > 0]
    
    # Service Centers Methods
    def get_all_service_centers(self) -> List[ServiceCenter]:
        """Get all service centers"""
        return self._service_centers.copy()
    
    def get_service_center_by_id(self, center_id: int) -> Optional[ServiceCenter]:
        """Get service center by ID"""
        for center in self._service_centers:
            if center.center_id == center_id:
                return center
        return None
    
    def get_service_centers_by_city(self, city: str) -> List[ServiceCenter]:
        """Get service centers in city"""
        return [sc for sc in self._service_centers if sc.location.city.lower() == city.lower()]
    
    def get_nearby_service_centers(self, location: Location, radius_km: float = 20) -> List[ServiceCenter]:
        """Get service centers within radius"""
        nearby = []
        for center in self._service_centers:
            distance = location.distance_to(center.location)
            if distance <= radius_km:
                nearby.append(center)
        return sorted(nearby, key=lambda c: location.distance_to(c.location))
    
    def get_service_centers_by_brand(self, brand: str) -> List[ServiceCenter]:
        """Get authorized service centers for brand"""
        return [sc for sc in self._service_centers if sc.supports_brand(brand)]
    
    def get_emergency_service_centers(self) -> List[ServiceCenter]:
        """Get service centers with emergency service"""
        return [sc for sc in self._service_centers if sc.emergency_service]
    
    # Tips Methods
    def get_all_tips(self) -> List[TipRecommendation]:
        """Get all tips"""
        return self._tips.copy()
    
    def get_tips_by_category(self, category: str) -> List[TipRecommendation]:
        """Get tips by category"""
        return [t for t in self._tips if t.category.lower() == category.lower()]
    
    def get_tips_for_vehicle(self, vehicle: Vehicle) -> List[TipRecommendation]:
        """Get tips applicable to vehicle"""
        return [t for t in self._tips if t.applies_to_vehicle(vehicle)]
    
    def get_high_priority_tips(self) -> List[TipRecommendation]:
        """Get high priority tips"""
        return [t for t in self._tips if t.priority.lower() == 'high']
    
    # Statistics Methods
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        return {
            'total_stations': len(self._cng_stations),
            'total_vehicles': len(self._vehicles),
            'total_routes': len(self._routes),
            'total_service_centers': len(self._service_centers),
            'total_tips': len(self._tips),
            'cities_covered': len(set(s.location.city for s in self._cng_stations)),
            'average_station_rating': sum(s.rating for s in self._cng_stations) / len(self._cng_stations) if self._cng_stations else 0,
            'average_price_per_kg': sum(s.current_price_per_kg for s in self._cng_stations) / len(self._cng_stations) if self._cng_stations else 0
        }
