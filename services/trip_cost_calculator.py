"""
Trip Cost Calculator Service
Calculate and compare costs for specific trips with different fuel options
"""
from typing import Dict, List, Optional, Tuple
import math


class TripCostCalculator:
    """Calculate trip costs for different routes and fuel types"""
    
    def __init__(self, fuel_prices: Dict[str, float]):
        self.fuel_prices = fuel_prices
    
    def calculate_trip_cost(
        self,
        distance_km: float,
        vehicle_mileage: float,
        fuel_type: str,
        toll_charges: float = 0,
        parking_charges: float = 0,
        additional_costs: float = 0
    ) -> Dict:
        """
        Calculate total trip cost
        
        Args:
            distance_km: Total trip distance
            vehicle_mileage: Vehicle mileage (km per L or kg)
            fuel_type: Type of fuel
            toll_charges: Total toll charges
            parking_charges: Parking costs
            additional_costs: Any additional costs
            
        Returns:
            Breakdown of trip costs
        """
        # Calculate fuel needed
        fuel_needed = distance_km / vehicle_mileage
        fuel_cost = fuel_needed * self.fuel_prices[fuel_type]
        
        # Calculate total cost
        total_cost = fuel_cost + toll_charges + parking_charges + additional_costs
        
        # Calculate cost per km
        cost_per_km = total_cost / distance_km if distance_km > 0 else 0
        
        return {
            'distance_km': distance_km,
            'fuel': {
                'type': fuel_type,
                'needed': round(fuel_needed, 2),
                'unit': self._get_fuel_unit(fuel_type),
                'cost': round(fuel_cost, 2),
                'price_per_unit': self.fuel_prices[fuel_type]
            },
            'breakdown': {
                'fuel': round(fuel_cost, 2),
                'tolls': round(toll_charges, 2),
                'parking': round(parking_charges, 2),
                'other': round(additional_costs, 2)
            },
            'total_cost': round(total_cost, 2),
            'cost_per_km': round(cost_per_km, 2)
        }
    
    def compare_trip_fuel_options(
        self,
        distance_km: float,
        vehicle_data: Dict,
        toll_charges: float = 0,
        parking_charges: float = 0
    ) -> Dict:
        """
        Compare trip costs with different fuel options
        
        Args:
            distance_km: Trip distance
            vehicle_data: Dict with current fuel_type and mileage
            toll_charges: Toll costs
            parking_charges: Parking costs
            
        Returns:
            Comparison of different fuel options
        """
        current_fuel = vehicle_data['fuel_type']
        current_mileage = vehicle_data['mileage']
        
        comparisons = []
        
        # Current fuel option
        current_cost = self.calculate_trip_cost(
            distance_km,
            current_mileage,
            current_fuel,
            toll_charges,
            parking_charges
        )
        current_cost['scenario'] = 'Current Fuel'
        comparisons.append(current_cost)
        
        # CNG option (if not already using CNG)
        if current_fuel != 'cng':
            # Estimate CNG mileage
            cng_mileage = current_mileage * (1.5 if current_fuel == 'petrol' else 1.3)
            cng_cost = self.calculate_trip_cost(
                distance_km,
                cng_mileage,
                'cng',
                toll_charges,
                parking_charges
            )
            cng_cost['scenario'] = 'If Using CNG'
            cng_cost['savings'] = round(current_cost['total_cost'] - cng_cost['total_cost'], 2)
            comparisons.append(cng_cost)
        
        # Find cheapest option
        cheapest = min(comparisons, key=lambda x: x['total_cost'])
        
        return {
            'trip_distance': distance_km,
            'options': comparisons,
            'cheapest_option': cheapest['scenario'],
            'max_savings': round(
                max(c['total_cost'] for c in comparisons) - cheapest['total_cost'],
                2
            )
        }
    
    def calculate_round_trip(
        self,
        one_way_distance: float,
        vehicle_mileage: float,
        fuel_type: str,
        stops: int = 0,
        parking_per_stop: float = 0
    ) -> Dict:
        """Calculate round trip costs"""
        total_distance = one_way_distance * 2
        total_parking = parking_per_stop * stops
        
        trip_cost = self.calculate_trip_cost(
            total_distance,
            vehicle_mileage,
            fuel_type,
            parking_charges=total_parking
        )
        
        trip_cost['trip_type'] = 'Round Trip'
        trip_cost['one_way_distance'] = one_way_distance
        trip_cost['stops'] = stops
        
        return trip_cost
    
    def estimate_refueling_stops(
        self,
        distance_km: float,
        vehicle_mileage: float,
        tank_capacity: float,
        initial_fuel: float
    ) -> Dict:
        """
        Estimate number of refueling stops needed
        
        Args:
            distance_km: Trip distance
            vehicle_mileage: Vehicle mileage
            tank_capacity: Tank capacity in L or kg
            initial_fuel: Initial fuel level in L or kg
            
        Returns:
            Refueling stop information
        """
        # Calculate range with initial fuel
        initial_range = initial_fuel * vehicle_mileage
        
        if initial_range >= distance_km:
            return {
                'stops_needed': 0,
                'fuel_remaining': round(initial_fuel - (distance_km / vehicle_mileage), 2),
                'total_fuel_needed': round(distance_km / vehicle_mileage, 2),
                'message': 'No refueling needed for this trip'
            }
        
        # Calculate remaining distance after initial fuel
        remaining_distance = distance_km - initial_range
        
        # Calculate range per full tank
        range_per_tank = tank_capacity * vehicle_mileage
        
        # Calculate stops needed
        stops_needed = math.ceil(remaining_distance / range_per_tank)
        
        # Calculate total fuel needed
        total_fuel_needed = distance_km / vehicle_mileage
        fuel_to_fill = total_fuel_needed - initial_fuel
        
        return {
            'stops_needed': stops_needed,
            'total_fuel_needed': round(total_fuel_needed, 2),
            'fuel_to_fill': round(fuel_to_fill, 2),
            'initial_range': round(initial_range, 2),
            'range_per_tank': round(range_per_tank, 2),
            'fuel_remaining_at_destination': round(
                (stops_needed + 1) * tank_capacity - fuel_to_fill,
                2
            )
        }
    
    def calculate_multi_stop_trip(
        self,
        stops: List[Dict],
        vehicle_mileage: float,
        fuel_type: str
    ) -> Dict:
        """
        Calculate costs for a trip with multiple stops
        
        Args:
            stops: List of stop dicts with distance_km, parking_cost, toll_cost
            vehicle_mileage: Vehicle mileage
            fuel_type: Fuel type
            
        Returns:
            Complete trip breakdown
        """
        total_distance = sum(stop.get('distance_km', 0) for stop in stops)
        total_parking = sum(stop.get('parking_cost', 0) for stop in stops)
        total_tolls = sum(stop.get('toll_cost', 0) for stop in stops)
        
        trip_cost = self.calculate_trip_cost(
            total_distance,
            vehicle_mileage,
            fuel_type,
            total_tolls,
            total_parking
        )
        
        # Add stop-by-stop breakdown
        cumulative_distance = 0
        stop_details = []
        
        for i, stop in enumerate(stops):
            cumulative_distance += stop.get('distance_km', 0)
            stop_fuel = stop.get('distance_km', 0) / vehicle_mileage
            stop_fuel_cost = stop_fuel * self.fuel_prices[fuel_type]
            
            stop_details.append({
                'stop_number': i + 1,
                'name': stop.get('name', f'Stop {i + 1}'),
                'distance_from_previous': stop.get('distance_km', 0),
                'cumulative_distance': round(cumulative_distance, 2),
                'fuel_used': round(stop_fuel, 2),
                'fuel_cost': round(stop_fuel_cost, 2),
                'parking_cost': stop.get('parking_cost', 0),
                'toll_cost': stop.get('toll_cost', 0)
            })
        
        trip_cost['multi_stop_details'] = {
            'total_stops': len(stops),
            'stops': stop_details
        }
        
        return trip_cost
    
    def compare_route_options(
        self,
        routes: List[Dict],
        vehicle_mileage: float,
        fuel_type: str
    ) -> Dict:
        """
        Compare costs for different route options
        
        Args:
            routes: List of route dicts with distance_km, toll_cost, time_minutes
            vehicle_mileage: Vehicle mileage
            fuel_type: Fuel type
            
        Returns:
            Route comparison
        """
        route_comparisons = []
        
        for i, route in enumerate(routes):
            cost = self.calculate_trip_cost(
                route['distance_km'],
                vehicle_mileage,
                fuel_type,
                route.get('toll_cost', 0)
            )
            
            cost['route_name'] = route.get('name', f'Route {i + 1}')
            cost['estimated_time'] = route.get('time_minutes', 0)
            cost['cost_per_minute'] = round(
                cost['total_cost'] / route.get('time_minutes', 1),
                2
            ) if route.get('time_minutes', 0) > 0 else 0
            
            route_comparisons.append(cost)
        
        # Find best options
        cheapest = min(route_comparisons, key=lambda x: x['total_cost'])
        fastest = min(route_comparisons, key=lambda x: x['estimated_time'])
        
        return {
            'routes': route_comparisons,
            'cheapest_route': cheapest['route_name'],
            'fastest_route': fastest['route_name'],
            'recommendations': self._generate_route_recommendation(route_comparisons)
        }
    
    def _generate_route_recommendation(self, routes: List[Dict]) -> str:
        """Generate intelligent route recommendation"""
        cheapest = min(routes, key=lambda x: x['total_cost'])
        fastest = min(routes, key=lambda x: x['estimated_time'])
        
        if cheapest['route_name'] == fastest['route_name']:
            return f"{cheapest['route_name']} is both the cheapest and fastest option."
        
        cost_diff = abs(cheapest['total_cost'] - fastest['total_cost'])
        time_diff = abs(cheapest['estimated_time'] - fastest['estimated_time'])
        
        if cost_diff < 50 and time_diff > 30:
            return f"{fastest['route_name']} is recommended - saves {time_diff} minutes for only ₹{cost_diff:.2f} more."
        elif cost_diff > 100:
            return f"{cheapest['route_name']} is recommended - saves ₹{cost_diff:.2f}."
        else:
            return f"Both routes are comparable. Choose based on your preference."
    
    def _get_fuel_unit(self, fuel_type: str) -> str:
        """Get the unit for fuel type"""
        units = {
            'petrol': 'L',
            'diesel': 'L',
            'cng': 'kg',
            'electric': 'kWh'
        }
        return units.get(fuel_type, 'L')
