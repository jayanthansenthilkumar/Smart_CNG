"""
Base Service Classes - OOP foundation for all services
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseService(ABC):
    """Abstract base class for all services"""
    
    def __init__(self):
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
        self._last_cache_clear = datetime.now()
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self._cache:
            cached_item = self._cache[key]
            if (datetime.now() - cached_item['timestamp']).seconds < self._cache_ttl:
                return cached_item['value']
        return None
    
    def _set_cache(self, key: str, value: Any):
        """Set value in cache"""
        self._cache[key] = {
            'value': value,
            'timestamp': datetime.now()
        }
    
    def _clear_cache(self):
        """Clear all cache"""
        self._cache = {}
        self._last_cache_clear = datetime.now()
    
    @abstractmethod
    def get_name(self) -> str:
        """Get service name"""
        pass


class CalculatorService(BaseService):
    """Base class for calculation services"""
    
    def __init__(self):
        super().__init__()
        self._calculation_history = []
    
    def _add_to_history(self, calculation_type: str, inputs: Dict, result: Any):
        """Add calculation to history"""
        self._calculation_history.append({
            'type': calculation_type,
            'inputs': inputs,
            'result': result,
            'timestamp': datetime.now()
        })
    
    def get_history(self, limit: int = 10) -> list:
        """Get calculation history"""
        return self._calculation_history[-limit:]
    
    def clear_history(self):
        """Clear calculation history"""
        self._calculation_history = []


class LocationBasedService(BaseService):
    """Base class for location-based services"""
    
    def __init__(self):
        super().__init__()
        self._default_radius_km = 10
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in km
        
        lat1_rad, lon1_rad = radians(lat1), radians(lon1)
        lat2_rad, lon2_rad = radians(lat2), radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def set_default_radius(self, radius_km: float):
        """Set default search radius"""
        self._default_radius_km = radius_km
