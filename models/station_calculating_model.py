import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from math import ceil

@dataclass
class ChargingStop:
    name: str
    lat: float
    lng: float
    arrival_charge: float
    departure_charge: float
    charge_time: int
    distance_from_start: float
    type: str

class ChargingStationCalculator:
    def __init__(self):
        # Constants for calculations
        self.SAFETY_BUFFER = 10  # Minimum charge percentage to maintain
        self.MAX_CHARGE = 90    # Maximum practical charge percentage
        self.OPTIMAL_MIN_CHARGE = 20  # Optimal minimum charge to arrive with
        
        # Temperature impact on battery efficiency (multiplier)
        self.TEMPERATURE_IMPACT = {
            'very_cold': 0.6,   # Below 0°C
            'cold': 0.8,        # 0-10°C
            'normal': 1.0,      # 10-25°C
            'warm': 0.95,       # 25-35°C
            'hot': 0.85         # Above 35°C
        }
        
        # Elevation impact on consumption (kWh/km per degree of slope)
        self.ELEVATION_CONSUMPTION = 0.004
        
        # Speed impact on consumption (multiplier)
        self.SPEED_IMPACT = {
            'urban': 1.0,       # 0-50 km/h
            'suburban': 1.1,    # 50-80 km/h
            'highway': 1.3      # >80 km/h
        }

        # For CNG semantics we treat 'battery_capacity' as tank capacity (kg)
        self.battery_capacity = None

    def calculate_charging_stops(
        self,
        route_data: Dict[str, Any],
        ev_specs: Dict[str, Any],
        current_charge: float,
        available_stations: List[Dict[str, Any]]
    ) -> List[ChargingStop]:
        """Calculate optimal charging stops for the route"""
        # Map CNG to internal fields
        self.battery_capacity = ev_specs['batteryCapacity']  # kg (tank)
        total_distance = route_data['distance']
        route_coordinates = route_data['coordinates']
        consumption_rate = ev_specs['consumption']  # kg/km
        
        # Initialize variables
        current_position = 0
        current_battery = current_charge
        stops = []
        
        # Calculate energy needed per kilometer
        energy_per_km = consumption_rate
        
        # Process each segment
        accumulated_distance = 0
        
        for i, coord in enumerate(route_coordinates[:-1]):
            segment_distance = self._haversine_distance(
                coord[0], coord[1],
                route_coordinates[i+1][0], route_coordinates[i+1][1]
            )
            
            accumulated_distance += segment_distance
            energy_needed = segment_distance * energy_per_km
            battery_drain = (energy_needed / self.battery_capacity) * 100
            current_battery -= battery_drain
            
            # Check if battery is getting too low (below 20%)
            if current_battery < 20 and accumulated_distance < total_distance:
                # Find nearest charging station
                nearest_station = self._find_nearest_station(
                    available_stations,
                    coord[0], coord[1]
                )
                
                if not nearest_station:
                    raise ValueError("No suitable charging station found")
                
                # Calculate optimal charge level
                remaining_distance = total_distance - accumulated_distance
                needed_charge = (remaining_distance * energy_per_km / self.battery_capacity * 100) + 30
                optimal_charge = min(90, max(needed_charge, 80))
                
                # Calculate filling time for CNG (kg/min)
                charging_time = self._calculate_charging_time(
                    current_battery,
                    optimal_charge,
                    ev_specs
                )
                
                stops.append(ChargingStop(
                    name=nearest_station['name'],
                    lat=nearest_station['lat'],
                    lng=nearest_station['lng'],
                    arrival_charge=round(current_battery, 1),
                    departure_charge=round(optimal_charge, 1),
                    charge_time=charging_time,
                    distance_from_start=round(accumulated_distance, 1),
                    type=nearest_station.get('type', 'Unknown')
                ))
                
                current_battery = optimal_charge
        
        return stops

    def _find_nearest_station(self, stations: List[Dict[str, Any]], lat: float, lng: float) -> Optional[Dict[str, Any]]:
        """Find the nearest charging station to a given point"""
        if not stations:
            return None
        
        nearest = min(
            stations,
            key=lambda s: self._haversine_distance(lat, lng, s['lat'], s['lng'])
        )
        
        return nearest

    def _calculate_adjusted_range(
        self,
        base_range: float,
        current_charge: float,
        weather_data: Dict[str, Any] = None
    ) -> float:
        """Calculate range adjusted for weather and battery level"""
        # Basic range based on current charge
        adjusted_range = base_range * (current_charge / 100)
        
        # Apply weather impact if available
        if weather_data:
            temp = weather_data.get('temperature', 20)
            if temp < 0:
                temp_factor = self.TEMPERATURE_IMPACT['very_cold']
            elif temp < 10:
                temp_factor = self.TEMPERATURE_IMPACT['cold']
            elif temp < 25:
                temp_factor = self.TEMPERATURE_IMPACT['normal']
            elif temp < 35:
                temp_factor = self.TEMPERATURE_IMPACT['warm']
            else:
                temp_factor = self.TEMPERATURE_IMPACT['hot']
            
            adjusted_range *= temp_factor
        
        return adjusted_range

    def _calculate_distance_to_next_stop(
        self,
        adjusted_range: float,
        remaining_distance: float,
        current_charge: float
    ) -> float:
        """Calculate optimal distance to next charging stop"""
        # Use 80% of adjusted range as optimal distance
        optimal_distance = adjusted_range * 0.8
        
        # If remaining distance is less than optimal, return remaining
        if remaining_distance <= optimal_distance:
            return remaining_distance
        
        return optimal_distance

    def _find_optimal_station(
        self,
        available_stations: List[Dict[str, Any]],
        current_position: float,
        target_distance: float,
        route_coordinates: List[List[float]]
    ) -> Dict[str, Any]:
        """Find the optimal charging station near the target distance"""
        # Filter stations within acceptable range
        distance_tolerance = 20  # km
        candidate_stations = []
        
        for station in available_stations:
            station_distance = self._calculate_distance_from_route(
                station,
                current_position,
                route_coordinates
            )
            
            if abs(station_distance - target_distance) <= distance_tolerance:
                station['distance_from_current'] = station_distance
                candidate_stations.append(station)
        
        if not candidate_stations:
            return None
        
        # Score stations based on multiple factors
        scored_stations = []
        for station in candidate_stations:
            score = self._score_station(station, target_distance)
            scored_stations.append((score, station))
        
        # Return station with highest score
        return max(scored_stations, key=lambda x: x[0])[1]

    def _calculate_charging_time(
        self,
        arrival_charge: float,
        departure_charge: float,
        ev_specs: Dict[str, Any]
    ) -> int:
        """Calculate CNG filling time in minutes based on tank capacity and fill rate"""
        tank_capacity_kg = ev_specs['batteryCapacity']  # using mapped field
        max_fill_speed = ev_specs['chargingSpeed']      # kg/min
        fuel_needed_kg = (departure_charge - arrival_charge) / 100 * tank_capacity_kg
        # Assume more linear fill vs EV charging curve
        effective_speed = max_fill_speed * 0.9  # small overhead
        fill_time_min = (fuel_needed_kg / max(effective_speed, 0.0001))
        return ceil(fill_time_min)

    def _calculate_arrival_charge(self, current_charge: float, distance: float, consumption_rate: float) -> float:
        """Calculate the expected battery charge upon arrival at the charging station"""
        energy_used = distance * consumption_rate
        arrival_charge = current_charge - (energy_used / self.battery_capacity * 100)
        return max(0, min(100, arrival_charge))  # Ensure charge is between 0 and 100

    def _calculate_optimal_departure_charge(self, remaining_distance: float, consumption_rate: float, base_range: float) -> float:
        """Calculate the optimal charge level to depart with"""
        energy_needed = remaining_distance * consumption_rate
        needed_charge = (energy_needed / self.battery_capacity * 100) + 10  # Add 10% buffer
        return min(100, max(20, needed_charge))  # Ensure between 20% and 100%

    def _score_station(self, station: Dict[str, Any], target_distance: float) -> float:
        """Score a charging station based on multiple factors"""
        # Convert power to float by removing 'kW' and converting
        power_str = str(station.get('power', '50kW')).lower().replace('kw', '').strip()
        try:
            power = float(power_str)
        except ValueError:
            power = 50.0  # Default to 50kW if conversion fails
            
        power_score = min(power / 350, 1)
        
        # Distance score (closer to target distance is better)
        distance_score = 1 - abs(station['distance_from_current'] - target_distance) / target_distance
        
        # Availability score
        availability_score = station.get('active_chargers', 1) / station.get('total_chargers', 1)
        
        # Weighted combination
        return (
            0.4 * distance_score +
            0.3 * availability_score +
            0.3 * power_score
        )

    def _calculate_distance_from_route(
        self,
        station: Dict[str, Any],
        current_position: float,
        route_coordinates: List[List[float]]
    ) -> float:
        """Calculate the distance from a station to the current position on the route"""
        station_lat = station['lat']
        station_lng = station['lng']
        
        # Find the closest point on the route
        min_distance = float('inf')
        route_distance = 0
        prev_point = None
        
        for point in route_coordinates:
            if prev_point:
                segment_length = self._haversine_distance(
                    prev_point[0], prev_point[1],
                    point[0], point[1]
                )
                route_distance += segment_length
                
                if abs(route_distance - current_position) < min_distance:
                    min_distance = abs(route_distance - current_position)
                    closest_point = point
            
            prev_point = point
        
        # Calculate actual distance from station to closest point
        return self._haversine_distance(
            station_lat, station_lng,
            closest_point[0], closest_point[1]
        )

    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate the great circle distance between two points in kilometers"""
        R = 6371  # Earth's radius in kilometers
        
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c 