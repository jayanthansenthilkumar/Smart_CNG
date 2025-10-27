import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from scipy.optimize import minimize
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import math
from typing import List, Dict, Tuple, Optional
import os

class LocationOptimizer:
    def __init__(self, data_file_path: str = None):
        """Initialize the location optimizer with CNG station data"""
        self.area_types = ["Market", "Office", "Residential", "School", "Factory", "Hospital"]
        self.traffic_flow = self._initialize_traffic_flow()
        self.existing_stations = []
        self.demand_data = None
        self.scaler = StandardScaler()
        
        # Load existing station data if available
        if data_file_path and os.path.exists(data_file_path):
            self.load_station_data(data_file_path)
        
    def load_station_data(self, file_path: str):
        """Load existing CNG station data from CSV file"""
        try:
            df = pd.read_csv(file_path)
            self.existing_stations = []
            
            for _, row in df.iterrows():
                station = {
                    'name': row.get('name', 'Unnamed Station'),
                    'lat': float(row['@lat']),
                    'lng': float(row['@lon']),
                    'morning_arrivals': float(row.get('demo_arrivals_per_hr_morning', 0)),
                    'evening_arrivals': float(row.get('demo_arrivals_per_hr_evening', 0)),
                    'overall_arrivals': float(row.get('demo_overall_arrivals_per_hr', 0)),
                    'service_time': float(row.get('demo_avg_service_time_min', 0)),
                    'servers': int(row.get('demo_servers_disp', 1)),
                    'rush_pattern': row.get('demo_rush_pattern', 'Steady'),
                    'wait_time_morning': self._safe_float(row.get('Wq_morning_min', 0)),
                    'wait_time_evening': self._safe_float(row.get('Wq_evening_min', 0)),
                    'wait_time_overall': self._safe_float(row.get('Wq_overall_min', 0)),
                    'total_station_time': self._safe_float(row.get('Expected_total_station_time_min', 0)),
                    'utilization': self._calculate_utilization(row)
                }
                self.existing_stations.append(station)
            
            print(f"Loaded {len(self.existing_stations)} existing stations")
            
        except Exception as e:
            print(f"Error loading station data: {e}")
            self.existing_stations = []
    
    def _safe_float(self, value):
        """Safely convert value to float, handling 'inf' and other edge cases"""
        try:
            if str(value).lower() == 'inf' or str(value) == 'inf':
                return float('inf')
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _calculate_utilization(self, row):
        """Calculate station utilization based on arrival rate and service capacity"""
        try:
            arrival_rate = float(row.get('demo_overall_arrivals_per_hr', 0))
            service_time = float(row.get('demo_avg_service_time_min', 0))
            servers = int(row.get('demo_servers_disp', 1))
            
            if service_time > 0 and servers > 0:
                # Utilization = (arrival_rate * service_time) / (60 * servers)
                utilization = (arrival_rate * service_time) / (60 * servers)
                return min(utilization, 1.0)  # Cap at 100%
            return 0.0
        except:
            return 0.0
        
    def _initialize_traffic_flow(self):
        """Initialize traffic flow patterns for different area types"""
        return {
            'Market': {
                'weekday': {'morning': 0.6, 'afternoon': 0.8, 'evening': 0.9},
                'weekend': {'morning': 0.7, 'afternoon': 0.9, 'evening': 0.8}
            },
            'Office': {
                'weekday': {'morning': 0.9, 'afternoon': 0.5, 'evening': 0.8},
                'weekend': {'morning': 0.2, 'afternoon': 0.1, 'evening': 0.1}
            },
            'Residential': {
                'weekday': {'morning': 0.7, 'afternoon': 0.4, 'evening': 0.8},
                'weekend': {'morning': 0.6, 'afternoon': 0.7, 'evening': 0.6}
            },
            'School': {
                'weekday': {'morning': 0.9, 'afternoon': 0.5, 'evening': 0.3},
                'weekend': {'morning': 0.1, 'afternoon': 0.2, 'evening': 0.1}
            },
            'Factory': {
                'weekday': {'morning': 0.8, 'afternoon': 0.8, 'evening': 0.7},
                'weekend': {'morning': 0.4, 'afternoon': 0.3, 'evening': 0.3}
            },
            'Hospital': {
                'weekday': {'morning': 0.7, 'afternoon': 0.7, 'evening': 0.7},
                'weekend': {'morning': 0.6, 'afternoon': 0.6, 'evening': 0.6}
            }
        }

    def calculate_demand_score(self, lat: float, lng: float, time_info: Dict) -> float:
        """Calculate demand score for a location based on nearby station data"""
        if not self.existing_stations:
            return 0.5  # Default score if no data available
        
        # Find nearby stations within 5km radius
        nearby_stations = []
        for station in self.existing_stations:
            distance = self._haversine_distance(lat, lng, station['lat'], station['lng'])
            if distance <= 5.0:  # 5km radius
                nearby_stations.append((station, distance))
        
        if not nearby_stations:
            return 0.3  # Lower score if no nearby stations (might be underserved)
        
        # Calculate demand indicators
        total_demand = 0
        total_utilization = 0
        total_wait_time = 0
        station_count = len(nearby_stations)
        
        for station, distance in nearby_stations:
            # Weight by distance (closer stations have more influence)
            weight = 1.0 / (distance + 0.1)
            
            # Get demand based on time of day
            if time_info['time_of_day'] == 'morning':
                demand = station['morning_arrivals']
                wait_time = station['wait_time_morning']
            elif time_info['time_of_day'] == 'evening':
                demand = station['evening_arrivals']
                wait_time = station['wait_time_evening']
            else:
                demand = station['overall_arrivals']
                wait_time = station['wait_time_overall']
            
            total_demand += demand * weight
            total_utilization += station['utilization'] * weight
            total_wait_time += wait_time * weight
        
        # Normalize scores
        avg_demand = total_demand / station_count if station_count > 0 else 0
        avg_utilization = total_utilization / station_count if station_count > 0 else 0
        avg_wait_time = total_wait_time / station_count if station_count > 0 else 0
        
        # High demand + high utilization + high wait times = good location for new station
        demand_score = min(avg_demand / 20.0, 1.0)  # Normalize to 0-1
        utilization_score = avg_utilization
        wait_score = min(avg_wait_time / 30.0, 1.0) if avg_wait_time != float('inf') else 1.0
        
        # Combined score
        combined_score = 0.4 * demand_score + 0.3 * utilization_score + 0.3 * wait_score
        return min(combined_score, 1.0)
    
    def calculate_accessibility_score(self, lat: float, lng: float) -> float:
        """Calculate accessibility score based on distance to major roads and existing stations"""
        if not self.existing_stations:
            return 0.5
        
        # Calculate distance to nearest existing station
        min_distance = min(
            self._haversine_distance(lat, lng, station['lat'], station['lng'])
            for station in self.existing_stations
        )
        
        # Optimal distance is 2-5km from existing stations
        if 2.0 <= min_distance <= 5.0:
            accessibility_score = 1.0
        elif min_distance < 2.0:
            # Too close to existing station
            accessibility_score = 0.2
        else:
            # Too far from existing stations
            accessibility_score = max(0.1, 1.0 - (min_distance - 5.0) / 10.0)
        
        return accessibility_score
    
    def calculate_economic_viability(self, lat: float, lng: float, area_type: str) -> float:
        """Calculate economic viability based on area type and nearby station performance"""
        if not self.existing_stations:
            return 0.5
        
        # Find nearby stations
        nearby_stations = []
        for station in self.existing_stations:
            distance = self._haversine_distance(lat, lng, station['lat'], station['lng'])
            if distance <= 10.0:  # 10km radius
                nearby_stations.append(station)
        
        if not nearby_stations:
            return 0.3
        
        # Calculate average performance metrics
        avg_utilization = np.mean([s['utilization'] for s in nearby_stations])
        avg_demand = np.mean([s['overall_arrivals'] for s in nearby_stations])
        
        # Area type multipliers
        area_multipliers = {
            'Market': 1.2,
            'Office': 1.0,
            'Factory': 0.9,
            'Hospital': 1.1,
            'School': 0.8,
            'Residential': 0.7
        }
        
        area_multiplier = area_multipliers.get(area_type, 1.0)
        
        # Economic viability score
        viability_score = (avg_utilization * 0.6 + avg_demand / 20.0 * 0.4) * area_multiplier
        return min(viability_score, 1.0)
    
    def calculate_competition_score(self, lat: float, lng: float) -> float:
        """Calculate competition score - lower is better (less competition)"""
        if not self.existing_stations:
            return 1.0  # No competition if no existing stations
        
        # Count stations within 3km radius
        nearby_count = sum(
            1 for station in self.existing_stations
            if self._haversine_distance(lat, lng, station['lat'], station['lng']) <= 3.0
        )
        
        # Competition score decreases with more nearby stations
        if nearby_count == 0:
            return 1.0
        elif nearby_count == 1:
            return 0.8
        elif nearby_count == 2:
            return 0.5
        else:
            return max(0.1, 1.0 - (nearby_count - 2) * 0.2)
    
    def generate_candidate_locations(self, center_lat: float, center_lng: float, 
                                   radius_km: float = 10.0, num_candidates: int = 20) -> List[Dict]:
        """Generate candidate locations for new CNG stations using grid-based approach"""
        candidates = []
        
        # Create a grid of potential locations
        lat_step = radius_km / 111.0  # Approximate km per degree latitude
        lng_step = radius_km / (111.0 * math.cos(math.radians(center_lat)))
        
        grid_size = int(2 * radius_km / 2.0)  # 2km grid spacing
        
        for i in range(-grid_size, grid_size + 1):
            for j in range(-grid_size, grid_size + 1):
                candidate_lat = center_lat + i * lat_step
                candidate_lng = center_lng + j * lng_step
                
                # Skip if outside radius
                distance = self._haversine_distance(center_lat, center_lng, candidate_lat, candidate_lng)
                if distance > radius_km:
                    continue
                
                # Determine area type (simplified heuristic)
                area_type = self._classify_area_type(candidate_lat, candidate_lng)
                
                # Skip residential areas
                if area_type == 'Residential':
                    continue
                
                candidates.append({
                    'lat': candidate_lat,
                    'lng': candidate_lng,
                    'area_type': area_type,
                    'distance_from_center': distance
                })
        
        return candidates[:num_candidates]
    
    def _classify_area_type(self, lat: float, lng: float) -> str:
        """Classify area type based on location (simplified heuristic)"""
        # This is a simplified classification - in practice, you'd use more sophisticated methods
        # like reverse geocoding or land use data
        
        # Simple heuristic based on coordinates (Delhi NCR area)
        if 28.4 <= lat <= 28.9 and 77.0 <= lng <= 77.5:
            # Random classification for demonstration
            types = ['Market', 'Office', 'Factory', 'Hospital', 'School']
            return np.random.choice(types)
        else:
            return 'Office'  # Default
    
    def optimize_station_locations(self, center_lat: float, center_lng: float, 
                                 radius_km: float = 10.0, num_stations: int = 3,
                                 time_info: Dict = None) -> List[Dict]:
        """Main optimization method to find best locations for new CNG stations"""
        if time_info is None:
            time_info = {'is_weekend': False, 'time_of_day': 'afternoon'}
        
        # Generate candidate locations
        candidates = self.generate_candidate_locations(center_lat, center_lng, radius_km)
        
        if not candidates:
            return []
        
        # Score each candidate
        scored_candidates = []
        for candidate in candidates:
            lat, lng = candidate['lat'], candidate['lng']
            area_type = candidate['area_type']
            
            # Calculate all scores
            demand_score = self.calculate_demand_score(lat, lng, time_info)
            accessibility_score = self.calculate_accessibility_score(lat, lng)
            economic_score = self.calculate_economic_viability(lat, lng, area_type)
            competition_score = self.calculate_competition_score(lat, lng)
            
            # Weighted combined score
            total_score = (
                0.3 * demand_score +
                0.25 * accessibility_score +
                0.25 * economic_score +
                0.2 * competition_score
            )
            
            scored_candidates.append({
                'lat': lat,
                'lng': lng,
                'area_type': area_type,
                'total_score': total_score,
                'demand_score': demand_score,
                'accessibility_score': accessibility_score,
                'economic_score': economic_score,
                'competition_score': competition_score,
                'distance_from_center': candidate['distance_from_center']
            })
        
        # Sort by total score
        scored_candidates.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Apply minimum distance constraint between selected stations
        selected_stations = []
        min_distance_km = 2.0  # Minimum 2km between stations
        
        for candidate in scored_candidates:
            # Check if this candidate is far enough from already selected stations
            is_valid = True
            for selected in selected_stations:
                distance = self._haversine_distance(
                    candidate['lat'], candidate['lng'],
                    selected['lat'], selected['lng']
                )
                if distance < min_distance_km:
                    is_valid = False
                    break
            
            if is_valid:
                selected_stations.append(candidate)
                if len(selected_stations) >= num_stations:
                    break
        
        return selected_stations
    
    def _haversine_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371.0  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lng1_rad = math.radians(lng1)
        lat2_rad = math.radians(lat2)
        lng2_rad = math.radians(lng2)
        
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def get_candidate_locations(self, nodes, time_info, min_distance=0.01):
        """Legacy method for backward compatibility"""
        # Convert nodes to the new format
        candidates = []
        for node in nodes:
            if node['type'] != 'Residential':
                candidates.append({
                    'lat': node['lat'],
                    'lng': node['lng'],
                    'area_type': node['type']
                })
        
        # Use the new optimization method
        if candidates:
            center_lat = np.mean([c['lat'] for c in candidates])
            center_lng = np.mean([c['lng'] for c in candidates])
            return self.optimize_station_locations(center_lat, center_lng, time_info=time_info)
        
        return [] 