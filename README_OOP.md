# Smart CNG - OOP Refactored Architecture

## Overview
This project has been refactored using Object-Oriented Programming (OOP) principles for better code organization, maintainability, and scalability.

## 🏗️ New Architecture

### Core Module (`core/`)
The heart of the application - all data models and business logic organized using OOP principles.

#### Data Models (`core/data_models.py`)
All JSON data is now represented as Python classes with methods:

- **CNGStation**: CNG station with location, pricing, facilities
  - Methods: `calculate_cost()`, `is_open_at()`, `accepts_payment()`, `get_efficiency_score()`
  
- **Vehicle**: Vehicle specifications and fuel efficiency
  - Methods: `get_efficiency()`, `get_maintenance_cost()`, `calculate_fuel_cost()`, `supports_fuel_type()`
  
- **Route**: Route information with waypoints and stations
  - Methods: `calculate_total_cost()`, distance calculations
  
- **ServiceCenter**: Service center details
  - Methods: `provides_service()`, `supports_brand()`
  
- **TipRecommendation**: Tips and recommendations
  - Methods: `applies_to_vehicle()`
  
- **Location**: Geographic location with distance calculations
  - Methods: `distance_to()`, coordinate handling

- **Enums**: `FuelType`, `PaymentMethod` for type safety

#### Data Manager (`core/data_manager.py`)
Singleton pattern for centralized data management:

```python
from core import DataManager

# Get instance (always same instance)
dm = DataManager()

# Query stations
nearby_stations = dm.get_nearby_stations(location, radius_km=10)
cheapest_stations = dm.get_cheapest_stations(limit=10)
city_stations = dm.get_stations_by_city("Delhi")

# Query vehicles
cng_vehicles = dm.get_vehicles_by_fuel_type(FuelType.CNG)
efficient_vehicles = dm.get_most_efficient_vehicles(FuelType.CNG, limit=5)

# Query routes, service centers, tips
routes = dm.get_routes_with_stations()
centers = dm.get_service_centers_by_brand("Maruti")
tips = dm.get_high_priority_tips()
```

#### Base Services (`core/base_services.py`)
Abstract base classes for service architecture:

- **BaseService**: Base class with caching
- **CalculatorService**: For calculation services with history
- **LocationBasedService**: For location-based operations

#### Unified Services (`core/services.py`)
All business logic consolidated into service classes:

1. **FuelCostCalculator**
   ```python
   calculator = FuelCostCalculator(fuel_prices)
   trip_cost = calculator.calculate_trip_cost(vehicle, distance_km, fuel_type)
   monthly_cost = calculator.calculate_monthly_cost(vehicle, monthly_km, fuel_type)
   savings = calculator.calculate_conversion_savings(vehicle, monthly_km, current_fuel, conversion_cost)
   ```

2. **StationFinderService**
   ```python
   finder = StationFinderService()
   nearby = finder.find_nearby(latitude, longitude, radius_km)
   cheapest = finder.find_cheapest(latitude, longitude)
   best_rated = finder.find_best_rated(latitude, longitude, min_rating=4.0)
   ```

3. **VehicleComparisonService**
   ```python
   comparison = VehicleComparisonService()
   result = comparison.compare_vehicles(vehicle1, vehicle2, annual_km, fuel_prices)
   best_for_budget = comparison.find_best_vehicle_for_budget(max_budget, category)
   ```

4. **RouteOptimizerService**
   ```python
   optimizer = RouteOptimizerService()
   optimized = optimizer.optimize_route_with_refueling(route, vehicle, initial_fuel_kg)
   ```

5. **MaintenanceService**
   ```python
   maintenance = MaintenanceService()
   schedule = maintenance.calculate_maintenance_schedule(vehicle, odometer, annual_km)
   ```

## 📁 New Directory Structure

```
Smart_CNG/
├── core/                          # NEW: Core OOP module
│   ├── __init__.py               # Module exports
│   ├── data_models.py            # All data classes
│   ├── data_manager.py           # Singleton data manager
│   ├── base_services.py          # Abstract base classes
│   └── services.py               # Business logic services
│
├── data/                         # JSON data files
│   ├── cng_stations.json
│   ├── vehicle_database.json
│   ├── routes_database.json
│   ├── service_centers.json
│   └── tips_recommendations.json
│
├── models/                       # Database models (SQLAlchemy)
│   ├── cng_calculator.py        # User, Vehicle, Station DB models
│   ├── location_optimizer.py
│   ├── wait_time_predictor.py
│   └── station_calculating_model.py
│
├── services/                     # Legacy services (backward compatibility)
│   ├── cng_calculator.py        # Redirects to core services
│   ├── notification_service.py
│   └── realtime_station_fetcher.py
│
├── templates/                    # HTML templates
├── static/                       # CSS, JS, images
│
├── app.py                        # Original app (legacy)
├── app_refactored.py            # NEW: Refactored app with OOP
├── requirements.txt
└── README.md                     # This file
```

## 🚀 Key Improvements

### 1. **Separation of Concerns**
- Data models separate from business logic
- Services separate from API routes
- Clear boundaries between layers

### 2. **Code Reusability**
- Base classes reduce code duplication
- Services can be used independently
- Data models can be reused across services

### 3. **Type Safety**
- Enums for fuel types and payment methods
- Type hints throughout
- Dataclasses for structured data

### 4. **Performance**
- Singleton pattern for data manager (single load)
- Caching in base services
- Efficient queries with indexed methods

### 5. **Maintainability**
- Single Responsibility Principle
- Open/Closed Principle (extend, don't modify)
- Clear class hierarchies

### 6. **Testability**
- Services can be unit tested independently
- Mock data manager for testing
- Clear interfaces

## 📚 Usage Examples

### Example 1: Find Cheapest Nearby Station and Calculate Cost
```python
from core import DataManager, StationFinderService, FuelCostCalculator, FuelType

# Initialize
dm = DataManager()
finder = StationFinderService()
calculator = FuelCostCalculator({'cng': 75.61})

# Find cheapest station
stations = finder.find_cheapest(28.6139, 77.2090, radius_km=20)
cheapest = stations[0]

# Get vehicle
vehicle = dm.get_vehicle_by_model("Maruti Suzuki", "WagonR")

# Calculate trip cost
cost = calculator.calculate_trip_cost(vehicle, 100, FuelType.CNG)
print(f"Trip cost: ₹{cost['fuel_cost']}")
```

### Example 2: Compare Two Vehicles
```python
from core import DataManager, VehicleComparisonService

dm = DataManager()
comparison_service = VehicleComparisonService()

v1 = dm.get_vehicle_by_model("Maruti Suzuki", "Alto")
v2 = dm.get_vehicle_by_model("Hyundai", "Grand i10")

result = comparison_service.compare_vehicles(
    v1, v2, 
    annual_km=15000, 
    fuel_prices={'cng': 75.61, 'petrol': 96.72}
)

print(f"Winner (cheaper): {result['winner']['cheaper_cng']}")
print(f"Winner (efficient): {result['winner']['more_efficient']}")
```

### Example 3: Calculate Conversion Savings
```python
from core import DataManager, FuelCostCalculator, FuelType

dm = DataManager()
calculator = FuelCostCalculator({'cng': 75.61, 'petrol': 96.72})

vehicle = dm.get_vehicle_by_model("Maruti Suzuki", "Ertiga")

savings = calculator.calculate_conversion_savings(
    vehicle=vehicle,
    monthly_km=1500,
    current_fuel=FuelType.PETROL,
    conversion_cost=50000,
    years=5
)

print(f"Annual savings: ₹{savings['annual_savings']}")
print(f"Breakeven: {savings['breakeven_years']} years")
print(f"ROI: {savings['roi_percentage']}%")
```

## 🔄 Migration from Old to New

### Old Code:
```python
# Direct JSON manipulation
with open('data/cng_stations.json') as f:
    stations = json.load(f)

# Manual distance calculation
for station in stations:
    dist = calculate_distance(lat, lng, station['latitude'], station['longitude'])
    if dist < 10:
        nearby.append(station)
```

### New Code:
```python
# OOP approach
from core import DataManager, Location

dm = DataManager()
location = Location(lat, lng, "", "", "", "")
nearby = dm.get_nearby_stations(location, radius_km=10)
```

## 🧪 Running the Application

### Using Refactored App:
```bash
python app_refactored.py
```

### Using Original App (Legacy):
```bash
python app.py
```

## 📦 Dependencies
See `requirements.txt` for all dependencies.

## 🎯 Benefits Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Code Organization** | Scattered functions | Organized classes |
| **Data Handling** | Direct JSON access | Object-oriented models |
| **Business Logic** | Mixed with routes | Separate service classes |
| **Reusability** | Copy-paste code | Inherit and extend |
| **Testing** | Difficult | Easy unit testing |
| **Maintenance** | Hard to modify | Easy to extend |
| **Type Safety** | Minimal | Type hints + Enums |
| **Performance** | Multiple file reads | Singleton + caching |

## 🔮 Future Enhancements

1. **Database Integration**: Move from JSON to database with ORM
2. **API Versioning**: RESTful API with versioning
3. **Async Operations**: Use async/await for I/O operations
4. **Testing Suite**: Comprehensive unit and integration tests
5. **Documentation**: Auto-generated API documentation
6. **Monitoring**: Add logging and performance monitoring
7. **Microservices**: Split services into microservices architecture

## 📝 Contributing

When adding new features:
1. Add data models to `core/data_models.py`
2. Add business logic to `core/services.py`
3. Use services in API routes in `app_refactored.py`
4. Follow OOP principles and existing patterns

## 📄 License
[Your License Here]

## 👥 Authors
[Your Name/Team]

---
**Note**: The old `app.py` is kept for backward compatibility. New development should use `app_refactored.py` and the `core` module.
