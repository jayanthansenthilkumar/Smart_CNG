"""
Real-time CNG Station Data Fetcher Service
Integrates multiple data sources to fetch CNG station locations globally
"""
import requests
import os
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealtimeCNGStationFetcher:
    """Fetches real-time CNG station data from multiple sources"""
    
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_PLACES_API_KEY', '')
        self.cache_duration = timedelta(hours=1)
        self.cache = {}
    
    def fetch_stations_google_places(self, lat: float, lng: float, radius: int = 50000) -> List[Dict]:
        """
        Fetch CNG stations using Google Places API
        Args:
            lat: Latitude
            lng: Longitude
            radius: Search radius in meters (max 50000)
        """
        if not self.google_api_key:
            logger.warning("Google Places API key not configured")
            return []
        
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f'{lat},{lng}',
                'radius': radius,
                'keyword': 'CNG station OR compressed natural gas',
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            stations = []
            for place in data.get('results', []):
                location = place.get('geometry', {}).get('location', {})
                stations.append({
                    'name': place.get('name', 'CNG Station'),
                    'lat': location.get('lat'),
                    'lng': location.get('lng'),
                    'address': place.get('vicinity', ''),
                    'place_id': place.get('place_id'),
                    'rating': place.get('rating'),
                    'is_open': place.get('opening_hours', {}).get('open_now'),
                    'source': 'google_places'
                })
            
            logger.info(f"Fetched {len(stations)} stations from Google Places")
            return stations
            
        except Exception as e:
            logger.error(f"Error fetching from Google Places: {e}")
            return []
    
    def fetch_stations_overpass(self, lat: float, lng: float, radius_km: float = 50) -> List[Dict]:
        """
        Fetch CNG stations using OpenStreetMap Overpass API
        Args:
            lat: Latitude
            lng: Longitude
            radius_km: Search radius in kilometers
        """
        try:
            radius_m = int(radius_km * 1000)
            overpass_url = "http://overpass-api.de/api/interpreter"
            
            # Query for CNG stations (fuel stations with CNG)
            query = f"""
            [out:json][timeout:25];
            (
                node["amenity"="fuel"]["fuel:cng"="yes"](around:{radius_m},{lat},{lng});
                node["amenity"="compressed_natural_gas"](around:{radius_m},{lat},{lng});
                way["amenity"="fuel"]["fuel:cng"="yes"](around:{radius_m},{lat},{lng});
            );
            out body;
            >;
            out skel qt;
            """
            
            response = requests.post(overpass_url, data=query, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            stations = []
            seen_coords = set()
            
            for element in data.get('elements', []):
                if element.get('type') == 'node':
                    tags = element.get('tags', {})
                    lat_val = element.get('lat')
                    lng_val = element.get('lon')
                    
                    # Avoid duplicates
                    coord_key = f"{lat_val:.6f},{lng_val:.6f}"
                    if coord_key in seen_coords:
                        continue
                    seen_coords.add(coord_key)
                    
                    stations.append({
                        'name': tags.get('name', tags.get('operator', 'CNG Station')),
                        'lat': lat_val,
                        'lng': lng_val,
                        'address': tags.get('addr:full', tags.get('addr:street', '')),
                        'operator': tags.get('operator', ''),
                        'brand': tags.get('brand', ''),
                        'opening_hours': tags.get('opening_hours', ''),
                        'phone': tags.get('phone', ''),
                        'website': tags.get('website', ''),
                        'source': 'openstreetmap'
                    })
            
            logger.info(f"Fetched {len(stations)} stations from OpenStreetMap")
            return stations
            
        except Exception as e:
            logger.error(f"Error fetching from Overpass API: {e}")
            return []
    
    def fetch_stations_india_government(self) -> List[Dict]:
        """
        Fetch CNG stations from Indian government sources
        This is a placeholder for integration with:
        - Indian Oil Corporation API
        - GAIL India API
        - Ministry of Petroleum & Natural Gas data
        """
        stations = []
        
        # Placeholder for Indian Oil CNG stations
        # In production, integrate with official APIs
        indian_oil_stations = self._fetch_indian_oil_stations()
        stations.extend(indian_oil_stations)
        
        # Placeholder for GAIL stations
        gail_stations = self._fetch_gail_stations()
        stations.extend(gail_stations)
        
        logger.info(f"Fetched {len(stations)} stations from Indian government sources")
        return stations
    
    def _fetch_indian_oil_stations(self) -> List[Dict]:
        """Fetch from Indian Oil Corporation (placeholder)"""
        # TODO: Integrate with official Indian Oil API
        # For now, return empty list
        return []
    
    def _fetch_gail_stations(self) -> List[Dict]:
        """Fetch from GAIL India (placeholder)"""
        # TODO: Integrate with official GAIL API
        return []
    
    def fetch_all_sources(self, lat: float, lng: float, radius_km: float = 50) -> List[Dict]:
        """
        Fetch stations from all available sources and merge results
        """
        all_stations = []
        
        # Fetch from OpenStreetMap (free, no API key needed)
        osm_stations = self.fetch_stations_overpass(lat, lng, radius_km)
        all_stations.extend(osm_stations)
        
        # Fetch from Google Places if API key is available
        if self.google_api_key:
            google_stations = self.fetch_stations_google_places(lat, lng, int(radius_km * 1000))
            all_stations.extend(google_stations)
        
        # Fetch from Indian government sources
        if self._is_india_region(lat, lng):
            gov_stations = self.fetch_stations_india_government()
            all_stations.extend(gov_stations)
        
        # Remove duplicates based on proximity (within 100 meters)
        unique_stations = self._deduplicate_stations(all_stations)
        
        logger.info(f"Total unique stations fetched: {len(unique_stations)}")
        return unique_stations
    
    def _is_india_region(self, lat: float, lng: float) -> bool:
        """Check if coordinates are in India"""
        # Rough bounding box for India
        return (6.0 <= lat <= 37.0) and (68.0 <= lng <= 97.0)
    
    def _deduplicate_stations(self, stations: List[Dict], threshold_km: float = 0.1) -> List[Dict]:
        """
        Remove duplicate stations that are within threshold distance
        """
        if not stations:
            return []
        
        unique = []
        
        for station in stations:
            is_duplicate = False
            s_lat = station.get('lat')
            s_lng = station.get('lng')
            
            if s_lat is None or s_lng is None:
                continue
            
            for existing in unique:
                e_lat = existing.get('lat')
                e_lng = existing.get('lng')
                
                distance = self._haversine_distance(s_lat, s_lng, e_lat, e_lng)
                if distance < threshold_km:
                    is_duplicate = True
                    # Merge information from duplicate
                    self._merge_station_info(existing, station)
                    break
            
            if not is_duplicate:
                unique.append(station)
        
        return unique
    
    def _haversine_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points in kilometers"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in km
        
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def _merge_station_info(self, existing: Dict, new: Dict):
        """Merge information from new station into existing"""
        # Prefer non-empty values from new data
        for key, value in new.items():
            if key not in existing or not existing[key]:
                existing[key] = value
            elif key == 'source':
                # Combine sources
                sources = existing.get('source', '').split(',')
                if new.get('source') not in sources:
                    existing['source'] = ','.join(sources + [new.get('source', '')])


# Singleton instance
realtime_fetcher = RealtimeCNGStationFetcher()
