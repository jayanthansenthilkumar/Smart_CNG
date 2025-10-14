"""
Unified Services Module - OOP-based services consolidation
All business logic organized in cohesive service classes
"""
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from .base_services import CalculatorService, LocationBasedService
from .data_manager import DataManager
from .data_models import Vehicle, CNGStation, Route, FuelType, Location


class FuelCostCalculator(CalculatorService):
    """Calculate fuel costs and savings"""
    
    def __init__(self, fuel_prices: Dict[str, float]):
        super().__init__()
        self.fuel_prices = fuel_prices
        self.data_manager = DataManager()
    
    def get_name(self) -> str:
        return "Fuel Cost Calculator"
    
    def calculate_trip_cost(self, vehicle: Vehicle, distance_km: float, 
                           fuel_type: FuelType) -> Dict[str, Any]:
        """Calculate cost for a trip"""
        cache_key = f"trip_{vehicle.make}_{vehicle.model}_{distance_km}_{fuel_type.value}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        fuel_price = self.fuel_prices.get(fuel_type.value.lower(), 0)
        fuel_cost = vehicle.calculate_fuel_cost(distance_km, fuel_type, fuel_price)
        
        efficiency = vehicle.get_efficiency(fuel_type)
        fuel_consumed = distance_km / efficiency
        
        result = {
            'distance_km': distance_km,
            'fuel_type': fuel_type.value,
            'fuel_consumed': round(fuel_consumed, 2),
            'fuel_cost': round(fuel_cost, 2),
            'efficiency': efficiency,
            'cost_per_km': round(fuel_cost / distance_km, 2) if distance_km > 0 else 0
        }
        
        self._set_cache(cache_key, result)
        self._add_to_history('trip_cost', 
                            {'vehicle': f"{vehicle.make} {vehicle.model}", 'distance': distance_km}, 
                            result)
        return result
    
    def calculate_monthly_cost(self, vehicle: Vehicle, monthly_km: float, 
                               fuel_type: FuelType) -> Dict[str, Any]:
        """Calculate monthly fuel cost"""
        fuel_price = self.fuel_prices.get(fuel_type.value.lower(), 0)
        monthly_cost = vehicle.calculate_fuel_cost(monthly_km, fuel_type, fuel_price)
        maintenance_cost = vehicle.get_maintenance_cost(fuel_type) / 12
        
        return {
            'monthly_km': monthly_km,
            'fuel_type': fuel_type.value,
            'fuel_cost': round(monthly_cost, 2),
            'maintenance_cost': round(maintenance_cost, 2),
            'total_monthly_cost': round(monthly_cost + maintenance_cost, 2),
            'annual_projection': round((monthly_cost + maintenance_cost) * 12, 2)
        }
    
    def compare_fuel_types(self, vehicle: Vehicle, distance_km: float) -> Dict[str, Any]:
        """Compare costs across different fuel types"""
        comparison = {}
        
        for fuel_type in vehicle.fuel_types:
            try:
                cost_data = self.calculate_trip_cost(vehicle, distance_km, fuel_type)
                comparison[fuel_type.value] = cost_data
            except ValueError:
                continue
        
        # Find cheapest option
        if comparison:
            cheapest = min(comparison.items(), key=lambda x: x[1]['fuel_cost'])
            comparison['recommended'] = cheapest[0]
        
        return comparison
    
    def calculate_conversion_savings(self, vehicle: Vehicle, monthly_km: float,
                                    current_fuel: FuelType, conversion_cost: float,
                                    years: int = 5) -> Dict[str, Any]:
        """Calculate savings from CNG conversion"""
        if not vehicle.supports_fuel_type(FuelType.CNG):
            return {'error': 'Vehicle does not support CNG'}
        
        # Current fuel costs
        current_annual = self.calculate_monthly_cost(vehicle, monthly_km, current_fuel)['total_monthly_cost'] * 12
        
        # CNG costs
        cng_annual = self.calculate_monthly_cost(vehicle, monthly_km, FuelType.CNG)['total_monthly_cost'] * 12
        
        # Savings calculation
        annual_savings = current_annual - cng_annual
        total_savings_over_period = annual_savings * years
        net_savings = total_savings_over_period - conversion_cost
        
        # Breakeven calculation
        breakeven_months = conversion_cost / (annual_savings / 12) if annual_savings > 0 else float('inf')
        
        return {
            'conversion_cost': conversion_cost,
            'current_fuel': current_fuel.value,
            'current_annual_cost': round(current_annual, 2),
            'cng_annual_cost': round(cng_annual, 2),
            'annual_savings': round(annual_savings, 2),
            'total_savings_over_period': round(total_savings_over_period, 2),
            'net_savings': round(net_savings, 2),
            'breakeven_months': round(breakeven_months, 1),
            'breakeven_years': round(breakeven_months / 12, 1),
            'roi_percentage': round((net_savings / conversion_cost) * 100, 1) if conversion_cost > 0 else 0
        }


class StationFinderService(LocationBasedService):
    """Find and filter CNG stations"""
    
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
    
    def get_name(self) -> str:
        return "Station Finder Service"
    
    def find_nearby(self, latitude: float, longitude: float, 
                   radius_km: Optional[float] = None) -> List[Dict[str, Any]]:
        """Find nearby stations"""
        if radius_km is None:
            radius_km = self._default_radius_km
        
        location = Location(latitude, longitude, "", "", "", "")
        stations = self.data_manager.get_nearby_stations(location, radius_km)
        
        result = []
        for station in stations:
            distance = self.calculate_distance(latitude, longitude, 
                                               station.location.latitude, 
                                               station.location.longitude)
            
            station_dict = station.to_dict()
            station_dict['distance_km'] = round(distance, 2)
            result.append(station_dict)
        
        return result
    
    def find_cheapest(self, latitude: float, longitude: float, 
                     radius_km: float = 50) -> List[Dict[str, Any]]:
        """Find cheapest stations within radius"""
        nearby = self.find_nearby(latitude, longitude, radius_km)
        return sorted(nearby, key=lambda s: s['current_price_per_kg'])[:10]
    
    def find_best_rated(self, latitude: float, longitude: float,
                       radius_km: float = 50, min_rating: float = 4.0) -> List[Dict[str, Any]]:
        """Find best rated stations"""
        nearby = self.find_nearby(latitude, longitude, radius_km)
        filtered = [s for s in nearby if s['rating'] >= min_rating]
        return sorted(filtered, key=lambda s: s['rating'], reverse=True)
    
    def find_fastest_service(self, latitude: float, longitude: float,
                           radius_km: float = 20) -> List[Dict[str, Any]]:
        """Find stations with shortest wait times"""
        nearby = self.find_nearby(latitude, longitude, radius_km)
        return sorted(nearby, key=lambda s: s['avg_wait_time_minutes'])[:10]
    
    def find_along_route(self, route: Route, max_detour_km: float = 5) -> List[CNGStation]:
        """Find stations along a route"""
        station_ids = route.cng_stations_enroute
        stations = []
        
        for station_id in station_ids:
            station = self.data_manager.get_station_by_id(station_id)
            if station:
                stations.append(station)
        
        return stations
    
    def get_optimal_refuel_points(self, route: Route, vehicle: Vehicle,
                                 initial_fuel_kg: float) -> List[Dict[str, Any]]:
        """Calculate optimal refueling points along route"""
        max_range = vehicle.cng_efficiency * initial_fuel_kg
        stations_enroute = self.find_along_route(route)
        
        refuel_points = []
        distance_covered = 0
        remaining_fuel = initial_fuel_kg
        
        for station in stations_enroute:
            distance_to_station = 50  # Simplified - would calculate actual distance
            
            if remaining_fuel * vehicle.cng_efficiency < distance_to_station + 50:
                # Need to refuel
                refuel_points.append({
                    'station': station.to_dict(),
                    'distance_from_start': distance_covered + distance_to_station,
                    'fuel_remaining_kg': round(remaining_fuel, 2),
                    'recommended_fill_kg': round(initial_fuel_kg - remaining_fuel, 2)
                })
                remaining_fuel = initial_fuel_kg
            
            distance_covered += distance_to_station
            remaining_fuel -= distance_to_station / vehicle.cng_efficiency
        
        return refuel_points


class VehicleComparisonService(CalculatorService):
    """Compare vehicles across various parameters"""
    
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
    
    def get_name(self) -> str:
        return "Vehicle Comparison Service"
    
    def compare_vehicles(self, vehicle1: Vehicle, vehicle2: Vehicle,
                        annual_km: float, fuel_prices: Dict[str, float]) -> Dict[str, Any]:
        """Comprehensive comparison between two vehicles"""
        
        def calculate_annual_cost(vehicle: Vehicle, fuel_type: FuelType) -> float:
            fuel_price = fuel_prices.get(fuel_type.value.lower(), 0)
            fuel_cost = vehicle.calculate_fuel_cost(annual_km, fuel_type, fuel_price)
            maintenance = vehicle.get_maintenance_cost(fuel_type)
            insurance = vehicle.insurance_annual
            depreciation = vehicle.price * vehicle.depreciation_rate
            return fuel_cost + maintenance + insurance + depreciation
        
        # Compare on CNG
        v1_cng_cost = calculate_annual_cost(vehicle1, FuelType.CNG) if vehicle1.supports_fuel_type(FuelType.CNG) else None
        v2_cng_cost = calculate_annual_cost(vehicle2, FuelType.CNG) if vehicle2.supports_fuel_type(FuelType.CNG) else None
        
        # Compare on Petrol
        v1_petrol_cost = calculate_annual_cost(vehicle1, FuelType.PETROL)
        v2_petrol_cost = calculate_annual_cost(vehicle2, FuelType.PETROL)
        
        # Environmental comparison
        v1_co2_cng = vehicle1.co2_per_km_cng * annual_km if vehicle1.supports_fuel_type(FuelType.CNG) else None
        v2_co2_cng = vehicle2.co2_per_km_cng * annual_km if vehicle2.supports_fuel_type(FuelType.CNG) else None
        
        return {
            'vehicle1': {
                'name': f"{vehicle1.make} {vehicle1.model}",
                'price': vehicle1.price,
                'cng_annual_cost': round(v1_cng_cost, 2) if v1_cng_cost else None,
                'petrol_annual_cost': round(v1_petrol_cost, 2),
                'cng_efficiency': vehicle1.cng_efficiency,
                'co2_cng_annual_kg': round(v1_co2_cng, 2) if v1_co2_cng else None
            },
            'vehicle2': {
                'name': f"{vehicle2.make} {vehicle2.model}",
                'price': vehicle2.price,
                'cng_annual_cost': round(v2_cng_cost, 2) if v2_cng_cost else None,
                'petrol_annual_cost': round(v2_petrol_cost, 2),
                'cng_efficiency': vehicle2.cng_efficiency,
                'co2_cng_annual_kg': round(v2_co2_cng, 2) if v2_co2_cng else None
            },
            'winner': {
                'cheaper_cng': vehicle1.make if (v1_cng_cost and v2_cng_cost and v1_cng_cost < v2_cng_cost) else vehicle2.make if (v1_cng_cost and v2_cng_cost) else "N/A",
                'more_efficient': vehicle1.make if vehicle1.cng_efficiency > vehicle2.cng_efficiency else vehicle2.make,
                'lower_emissions': vehicle1.make if (v1_co2_cng and v2_co2_cng and v1_co2_cng < v2_co2_cng) else vehicle2.make if (v1_co2_cng and v2_co2_cng) else "N/A"
            }
        }
    
    def find_best_vehicle_for_budget(self, max_budget: float, category: Optional[str] = None,
                                    annual_km: float = 15000) -> List[Dict[str, Any]]:
        """Find best vehicles within budget"""
        vehicles = self.data_manager.get_all_vehicles()
        
        if category:
            vehicles = [v for v in vehicles if v.category.lower() == category.lower()]
        
        vehicles = [v for v in vehicles if v.price <= max_budget]
        
        # Sort by CNG efficiency
        vehicles.sort(key=lambda v: v.cng_efficiency if v.supports_fuel_type(FuelType.CNG) else 0, reverse=True)
        
        result = []
        for vehicle in vehicles[:10]:
            result.append({
                'make': vehicle.make,
                'model': vehicle.model,
                'price': vehicle.price,
                'category': vehicle.category,
                'cng_efficiency': vehicle.cng_efficiency,
                'supports_cng': vehicle.supports_fuel_type(FuelType.CNG)
            })
        
        return result


class RouteOptimizerService(LocationBasedService):
    """Optimize routes for CNG vehicles"""
    
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
    
    def get_name(self) -> str:
        return "Route Optimizer Service"
    
    def optimize_route_with_refueling(self, route: Route, vehicle: Vehicle,
                                     initial_fuel_kg: float) -> Dict[str, Any]:
        """Optimize route with refueling stops"""
        station_finder = StationFinderService()
        refuel_points = station_finder.get_optimal_refuel_points(route, vehicle, initial_fuel_kg)
        
        # Calculate total trip details
        total_fuel_needed = route.distance_km / vehicle.cng_efficiency
        total_refuels = len(refuel_points)
        
        # Calculate costs
        fuel_cost_calculator = FuelCostCalculator({'cng': 75.0})  # Default price
        trip_cost = fuel_cost_calculator.calculate_trip_cost(vehicle, route.distance_km, FuelType.CNG)
        
        return {
            'route': route.to_dict(),
            'vehicle': f"{vehicle.make} {vehicle.model}",
            'total_distance_km': route.distance_km,
            'estimated_time_hours': route.estimated_time_minutes / 60,
            'total_fuel_needed_kg': round(total_fuel_needed, 2),
            'initial_fuel_kg': initial_fuel_kg,
            'number_of_refuels': total_refuels,
            'refuel_points': refuel_points,
            'total_cost': trip_cost,
            'toll_cost': route.toll_cost
        }


class MaintenanceService(CalculatorService):
    """Manage vehicle maintenance"""
    
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
    
    def get_name(self) -> str:
        return "Maintenance Service"
    
    def calculate_maintenance_schedule(self, vehicle: Vehicle, 
                                      current_odometer: int,
                                      annual_km: float) -> Dict[str, Any]:
        """Calculate maintenance schedule"""
        service_intervals = {
            'oil_change': 5000,
            'filter_replacement': 10000,
            'major_service': 20000,
            'timing_belt': 60000
        }
        
        schedule = []
        for service_type, interval in service_intervals.items():
            next_service_km = ((current_odometer // interval) + 1) * interval
            km_remaining = next_service_km - current_odometer
            months_remaining = (km_remaining / annual_km) * 12 if annual_km > 0 else 0
            
            schedule.append({
                'service_type': service_type.replace('_', ' ').title(),
                'interval_km': interval,
                'next_service_km': next_service_km,
                'km_remaining': km_remaining,
                'months_remaining': round(months_remaining, 1)
            })
        
        return {
            'vehicle': f"{vehicle.make} {vehicle.model}",
            'current_odometer': current_odometer,
            'annual_km': annual_km,
            'schedule': schedule
        }
