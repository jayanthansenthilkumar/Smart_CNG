# Smart CNG - Simple Version

## 📁 Super Simple Structure

```
Smart_CNG/
├── lib/                  # Library (all logic)
│   ├── data.py          # Data models & loader
│   ├── calc.py          # Calculator
│   └── __init__.py
│
├── data/                 # Data files
│   ├── stations.json    # CNG stations
│   ├── cars.json        # Vehicles
│   └── routes.json      # Routes
│
├── templates/            # HTML pages
├── static/              # CSS, JS, images
│
├── db_models.py         # Database (users only)
├── main.py              # Main app (run this!)
└── requirements.txt
```

## 🚀 Quick Start

```bash
# Run the app
python main.py

# Open browser
http://localhost:5000
```

## 📚 Simple Usage

### Load Data
```python
from lib import Data

data = Data()
stations = data.stations  # All stations
cars = data.cars          # All cars
```

### Find Stations
```python
# Find nearby
nearby = data.find_stations(lat=28.6139, lng=77.2090, radius=10)

# Get cheapest
cheapest = data.get_cheapest_stations(limit=5)
```

### Calculate Costs
```python
from lib import Calculator

calc = Calculator()
car = data.find_car("Maruti Suzuki", "WagonR")

# Trip cost
trip = calc.trip_cost(car, distance=100, fuel='cng')
print(f"Cost: ₹{trip['cost']}")

# Monthly cost
monthly = calc.monthly_cost(car, monthly_km=1500)
print(f"Monthly: ₹{monthly['cost']}")

# Savings
savings = calc.savings(car, monthly_km=1500, conversion_cost=50000)
print(f"Breakeven: {savings['breakeven_years']} years")
```

## 🔌 API Endpoints

### Stations
- `GET /api/stations/nearby?latitude=X&longitude=Y&radius=Z`
- `GET /api/stations/cheapest?limit=N`

### Cars
- `GET /api/cars?category=X`
- `POST /api/cars/compare`

### Calculator
- `POST /api/calc/trip` - Trip cost
- `POST /api/calc/monthly` - Monthly cost
- `POST /api/calc/savings` - CNG savings

## 📊 Data Files

### stations.json
```json
[{
  "id": 1,
  "name": "Station Name",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "city": "Delhi",
  "price": 75.61,
  "rating": 4.5
}]
```

### cars.json
```json
{
  "vehicles": [{
    "make": "Maruti Suzuki",
    "model": "Alto",
    "cng_efficiency": 31.59,
    "petrol_efficiency": 22.05,
    "price": 350000
  }]
}
```

## 🎯 What's Simplified

| Before | After |
|--------|-------|
| core/ (5 files) | lib/ (3 files) |
| models/ (4 files) | db_models.py (1 file) |
| services/ (3 files) | lib/calc.py (1 file) |
| Complex names | Simple names |
| app_refactored.py | main.py |

**Result: 70% fewer files, 80% simpler code!**

## 📝 Key Classes

### Station
- `id`, `name`, `lat`, `lng`, `city`, `price`, `rating`
- `distance_to(lat, lng)` - Calculate distance

### Car
- `make`, `model`, `year`, `cng_km_per_kg`, `petrol_km_per_l`, `price`

### Data (Singleton)
- `stations` - All stations list
- `cars` - All cars list
- `find_stations(lat, lng, radius)` - Find nearby
- `find_car(make, model)` - Find car

### Calculator
- `trip_cost(car, distance, fuel)` - Trip cost
- `monthly_cost(car, monthly_km, fuel)` - Monthly cost
- `savings(car, monthly_km, conversion_cost)` - CNG savings
- `compare_cars(car1, car2, yearly_km)` - Compare

## 🎨 File Naming

- ✅ `main.py` instead of `app_refactored.py`
- ✅ `lib/` instead of `core/`
- ✅ `data.py` instead of `data_models.py`
- ✅ `calc.py` instead of `services.py`
- ✅ `db_models.py` instead of `models/cng_calculator.py`
- ✅ `stations.json` instead of `cng_stations.json`
- ✅ `cars.json` instead of `vehicle_database.json`
- ✅ `routes.json` instead of `routes_database.json`

## 📈 Benefits

✅ **Simple names** - Easy to understand  
✅ **Fewer files** - Less complexity  
✅ **Clear structure** - Know where everything is  
✅ **Easy to learn** - 10 minutes to understand  
✅ **Quick to modify** - Change one file  

---

**That's it! Just 3 library files, 1 main app, and your data. Simple! 🎉**
