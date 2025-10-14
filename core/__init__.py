"""
Core Module - OOP-based data models and services
"""
from .data_models import (
    CNGStation, Vehicle, Route, ServiceCenter, TipRecommendation,
    Location, FuelType, PaymentMethod
)
from .data_manager import DataManager
from .base_services import BaseService, CalculatorService, LocationBasedService
from .services import (
    FuelCostCalculator, StationFinderService, VehicleComparisonService,
    RouteOptimizerService, MaintenanceService
)

__all__ = [
    # Data Models
    'CNGStation', 'Vehicle', 'Route', 'ServiceCenter', 'TipRecommendation',
    'Location', 'FuelType', 'PaymentMethod',
    
    # Data Manager
    'DataManager',
    
    # Base Services
    'BaseService', 'CalculatorService', 'LocationBasedService',
    
    # Services
    'FuelCostCalculator', 'StationFinderService', 'VehicleComparisonService',
    'RouteOptimizerService', 'MaintenanceService'
]
