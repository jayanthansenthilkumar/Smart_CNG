# Smart CNG - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Installation

1. **Navigate to project directory**
```powershell
cd "C:\Users\jayan\OneDrive\Desktop\Backups\Smart_CNG"
```

2. **Create virtual environment (if not exists)**
```powershell
python -m venv venv
```

3. **Activate virtual environment**
```powershell
.\venv\Scripts\Activate
```

4. **Install dependencies**
```powershell
pip install -r requirements.txt
```

5. **Initialize database**
```powershell
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized!')"
```

6. **Run the application**
```powershell
python app.py
```

7. **Access the application**
Open browser and go to: `http://localhost:5000`

### Default Login Credentials
- **Username**: Syraa
- **Password**: Syraa

---

## 🎯 Using New Features

### 1. Vehicle Comparison Tool

**Access**: `http://localhost:5000/vehicle-comparison`

**Steps**:
1. Add vehicles to compare (minimum 2)
2. Enter make, model, fuel type, and mileage
3. Set monthly distance
4. Click "Compare Vehicles"
5. View detailed comparison with costs and rankings

**Example**:
- Vehicle 1: Maruti Swift, Petrol, 18 km/L
- Vehicle 2: Hyundai i20, CNG, 25 km/kg
- Monthly Distance: 1000 km
- Result: See which vehicle is more economical!

### 2. Trip Cost Calculator

**Access**: `http://localhost:5000/trip-calculator`

**Options**:

**A. Single Trip**
1. Enter trip distance
2. Select fuel type and mileage
3. Add toll and parking costs
4. Calculate total cost

**B. Round Trip**
1. Enter one-way distance
2. Add number of stops
3. Calculate total round trip cost

**C. Compare Options**
1. Enter trip details
2. Compare petrol/diesel vs CNG
3. See potential savings

### 3. Maintenance Tracker

**Access**: `http://localhost:5000/maintenance-tracker`

**Features**:
- Add maintenance records
- View upcoming services
- See maintenance history
- Get cost projections
- Receive reminders

### 4. Fuel History

**Access**: `http://localhost:5000/fuel-history`

**Track**:
- Every fuel fill
- Cost per fill
- Monthly expenses
- Fuel efficiency
- Price trends

---

## 📡 Testing APIs

### Using cURL (PowerShell)

**1. Compare Vehicles**
```powershell
$body = @{
    vehicles = @(
        @{make="Maruti"; model="Swift"; fuel_type="petrol"; mileage=18},
        @{make="Hyundai"; model="i20"; fuel_type="cng"; mileage=25}
    )
    monthly_distance = 1000
    period_months = 12
    city = "Delhi"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/compare-vehicles" -Method Post -Body $body -ContentType "application/json"
```

**2. Calculate Trip Cost**
```powershell
$body = @{
    distance_km = 100
    vehicle_mileage = 15
    fuel_type = "cng"
    toll_charges = 200
    parking_charges = 100
    city = "Delhi"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/calculate-trip-cost" -Method Post -Body $body -ContentType "application/json"
```

**3. Get Station Statistics**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/station-statistics" -Method Get
```

---

## 🔧 Common Tasks

### Add a New Vehicle
```powershell
$body = @{
    make = "Maruti"
    model = "Alto"
    year = 2023
    fuel_type = "cng"
    avg_mileage = 24
    monthly_usage = 1000
    is_cng_converted = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/vehicles/add" -Method Post -Body $body -ContentType "application/json" -Headers @{Authorization="Bearer YOUR_TOKEN"}
```

### Add Fuel Log
```powershell
$body = @{
    vehicle_id = 1
    fuel_type = "cng"
    amount = 8.5
    cost = 634
    odometer = 25000
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/fuel-log/add" -Method Post -Body $body -ContentType "application/json"
```

### Get Eco Score
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/eco-score/1" -Method Get
```

---

## 📊 Dashboard Navigation

### Main Menu Options:

1. **Dashboard** - Overview of all features
2. **Find Stations** - Nearby CNG stations with wait times
3. **Route Planner** - Plan trips with filling stops
4. **CNG Switch** - Calculate conversion savings
5. **Vehicle Comparison** - Compare multiple vehicles (NEW)
6. **Trip Calculator** - Calculate trip costs (NEW)
7. **Maintenance Tracker** - Track services (NEW)
8. **Fuel History** - View consumption logs (NEW)
9. **Analytics** - Platform statistics
10. **Location Optimizer** - Optimal station locations

---

## 🐛 Troubleshooting

### Database Errors
```powershell
# Reinitialize database
python -c "from app import app, db; app.app_context().push(); db.drop_all(); db.create_all(); print('Database reset!')"
```

### Port Already in Use
```powershell
# Change port in app.py or kill existing process
Get-Process -Name python | Stop-Process -Force
```

### Module Not Found
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Cannot Import Services
```powershell
# Ensure you're in correct directory
cd "C:\Users\jayan\OneDrive\Desktop\Backups\Smart_CNG"
python app.py
```

---

## 📝 Sample Data

### Add Sample Fuel Prices
Run this after starting the app:
```python
from app import app, db
from models.cng_calculator import FuelPrice
from datetime import datetime

with app.app_context():
    prices = [
        FuelPrice(fuel_type='petrol', price=96.72, city='Delhi'),
        FuelPrice(fuel_type='diesel', price=89.62, city='Delhi'),
        FuelPrice(fuel_type='cng', price=74.59, city='Delhi')
    ]
    for price in prices:
        db.session.add(price)
    db.session.commit()
    print("Sample prices added!")
```

### Add Sample Vehicle
```python
from app import app, db
from models.cng_calculator import Vehicle, User

with app.app_context():
    # Assuming user exists
    vehicle = Vehicle(
        user_id=1,
        make='Maruti',
        model='Swift',
        year=2023,
        fuel_type='petrol',
        avg_mileage=18,
        monthly_usage=1000
    )
    db.session.add(vehicle)
    db.session.commit()
    print(f"Vehicle added with ID: {vehicle.id}")
```

---

## 🎓 Learning Path

### Beginner
1. Explore dashboard
2. Try CNG Switch calculator
3. Use trip calculator
4. View analytics

### Intermediate
1. Add vehicles
2. Track fuel logs
3. Use maintenance tracker
4. Compare vehicles

### Advanced
1. Use all APIs programmatically
2. Create custom reports
3. Integrate with external systems
4. Build mobile app using APIs

---

## 📞 API Documentation

Full API documentation: See `NEW_FEATURES_DOCUMENTATION.md`

Quick API Reference:
- **Base URL**: `http://localhost:5000`
- **Authentication**: Session-based for web, token for API
- **Content-Type**: `application/json`
- **Response Format**: JSON

---

## 🔐 Security Notes

1. Change default login credentials in production
2. Set strong SECRET_KEY in app.py
3. Use environment variables for sensitive data
4. Enable HTTPS in production
5. Implement rate limiting for APIs

---

## 🚀 Production Deployment

### Heroku
```powershell
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Deploy
git init
heroku create smart-cng-app
git push heroku main
```

### Docker
```dockerfile
# Dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

---

## 📈 Next Steps

1. ✅ Run the application
2. ✅ Test all features
3. ✅ Add sample data
4. ✅ Try all calculators
5. ✅ Explore API endpoints
6. 🔄 Customize for your needs
7. 🔄 Deploy to production

---

## 🆘 Getting Help

1. Check `FEATURES_SUMMARY.md` for overview
2. Read `NEW_FEATURES_DOCUMENTATION.md` for details
3. Review error messages in console
4. Check Flask debug output
5. Verify database is initialized

---

## 🎉 You're Ready!

Your Smart CNG platform is fully set up with all features working. Start by logging in and exploring the new tools!

**Happy Coding! 🚗💨**
