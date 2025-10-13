# 🚗 Smart CNG Platform

<div align="center">

![Smart CNG](https://img.shields.io/badge/Smart%20CNG-v2.0-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

**A comprehensive platform for CNG vehicle management, cost optimization, and environmental tracking**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [API Docs](#api-documentation) • [Contributing](#contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Screenshots](#screenshots)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

---

## 🌟 Overview

Smart CNG is an intelligent platform designed to help CNG vehicle owners and potential converters make informed decisions about fuel costs, maintenance, and environmental impact. The platform provides comprehensive tools for:

- **Cost Analysis**: Compare vehicles, calculate trip costs, and project savings
- **Maintenance Tracking**: Keep track of CNG kit services and get timely reminders
- **Environmental Impact**: Monitor your carbon footprint and eco score
- **Station Finder**: Locate nearby CNG stations with real-time availability
- **Route Planning**: Optimize trips with fuel stop calculations

---

## ✨ Features

### 🚙 Vehicle Comparison Tool
- Compare multiple vehicles side-by-side
- Analyze fuel costs (monthly, yearly, per-km)
- Environmental impact comparison
- Automatic ranking system
- Savings calculator with projections

### 🗺️ Trip Cost Calculator
- Single trip cost calculation
- Round trip planner
- Multi-stop trip planning
- Route comparison
- Fuel stop estimation
- Toll and parking integration

### 🔧 Maintenance Tracking
- CNG kit maintenance logs
- Automatic service reminders
- Maintenance cost tracking
- Service history
- Cost projections (6/12 months)
- India-specific CNG maintenance intervals

### ⛽ Fuel Log & Analytics
- Detailed consumption tracking
- Monthly expense breakdown
- Fuel efficiency monitoring
- Cost per fill analysis
- Visual analytics and charts
- Price trend tracking

### 🌱 Eco Score Dashboard
- Environmental impact score (0-100)
- CO2 emissions tracking
- CNG conversion savings
- Trees equivalent calculation
- Grade system (Excellent/Good/Average/Poor)

### 🚗 Multi-Vehicle Management
- Manage unlimited vehicles
- Individual tracking per vehicle
- Quick vehicle switching
- Vehicle-specific statistics
- Consolidated dashboard

### 📍 Real-time Station Finder
- Live CNG station data
- Wait time predictions
- Price comparison
- Queue length tracking
- Favorite stations

### 💰 CNG Conversion Calculator
- ROI calculation
- Savings projections
- Kit cost estimation
- Payback period analysis
- Environmental impact assessment

---

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 3.0
- **Database**: SQLAlchemy (SQLite/PostgreSQL)
- **Authentication**: Flask-Login
- **APIs**: RESTful architecture

### Frontend
- **HTML5/CSS3**: Responsive design
- **JavaScript**: Vanilla JS with async/await
- **Charts**: Chart.js (optional)
- **Maps**: Google Maps API integration

### Services
- **Vehicle Comparison Service**: Cost analysis engine
- **Trip Calculator Service**: Route and cost optimization
- **Maintenance Service**: Service tracking and reminders
- **Notification Service**: Smart alerts system

### Data Science
- **NumPy**: Numerical calculations
- **Pandas**: Data analysis
- **Scikit-learn**: Predictive models
- **SciPy**: Scientific computing

---

## 💻 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Smart_CNG.git
cd Smart_CNG
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**

Windows:
```powershell
.\venv\Scripts\Activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Initialize database**
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized!')"
```

6. **Run the application**
```bash
python app.py
```

7. **Access the application**
Open your browser and navigate to: `http://localhost:5000`

### Default Credentials
- **Username**: Syraa
- **Password**: Syraa

---

## 🚀 Quick Start

### Using the Platform

1. **Login** with default credentials
2. **Add Your Vehicle** via Dashboard
3. **Compare Vehicles** to find the most economical option
4. **Calculate Trip Costs** for your journeys
5. **Track Fuel Logs** for detailed analytics
6. **Monitor Maintenance** with automatic reminders
7. **View Your Eco Score** and environmental impact

### Using the APIs

Import the Postman collection: `Smart_CNG_API_Collection.postman_collection.json`

Or use cURL:

```bash
# Compare vehicles
curl -X POST http://localhost:5000/api/compare-vehicles \
  -H "Content-Type: application/json" \
  -d '{
    "vehicles": [
      {"make": "Maruti", "model": "Swift", "fuel_type": "petrol", "mileage": 18},
      {"make": "Hyundai", "model": "i20", "fuel_type": "cng", "mileage": 25}
    ],
    "monthly_distance": 1000,
    "period_months": 12,
    "city": "Delhi"
  }'
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:5000
```

### Authentication
Most endpoints require authentication via session or token.

### Endpoints

#### Vehicle Comparison
```
POST   /api/compare-vehicles          # Compare multiple vehicles
POST   /api/compare-fuel-options      # Compare fuel types
POST   /api/vehicle-recommendation    # Get recommendations
```

#### Trip Calculator
```
POST   /api/calculate-trip-cost       # Calculate trip cost
POST   /api/compare-trip-options      # Compare fuel options
POST   /api/calculate-round-trip      # Round trip calculator
POST   /api/estimate-refueling-stops  # Estimate fuel stops
POST   /api/compare-routes            # Compare routes
```

#### Maintenance
```
POST   /api/maintenance/add                          # Add record
GET    /api/maintenance/upcoming/<vehicle_id>        # Get upcoming
GET    /api/maintenance/history/<vehicle_id>         # Get history
GET    /api/maintenance/cost-projection/<vehicle_id> # Get projection
GET    /api/maintenance/statistics/<vehicle_id>      # Get stats
```

#### Fuel Logs
```
POST   /api/fuel-log/add                    # Add log
GET    /api/fuel-log/history/<vehicle_id>   # Get history
GET    /api/fuel-log/analytics/<vehicle_id> # Get analytics
```

#### Eco Score
```
GET    /api/eco-score/<vehicle_id>          # Get eco score
```

#### Vehicle Management
```
POST   /api/vehicles/add            # Add vehicle
PUT    /api/vehicles/<vehicle_id>   # Update vehicle
DELETE /api/vehicles/<vehicle_id>   # Delete vehicle
GET    /api/vehicles/summary         # Get summary
```

For detailed API documentation, see [NEW_FEATURES_DOCUMENTATION.md](NEW_FEATURES_DOCUMENTATION.md)

---

## 📸 Screenshots

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### Vehicle Comparison
![Vehicle Comparison](docs/screenshots/vehicle-comparison.png)

### Trip Calculator
![Trip Calculator](docs/screenshots/trip-calculator.png)

### Maintenance Tracker
![Maintenance](docs/screenshots/maintenance.png)

---

## 📁 Project Structure

```
Smart_CNG/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── instance/
│   └── fuelexa.db             # SQLite database
├── models/
│   ├── __init__.py
│   ├── cng_calculator.py      # Database models
│   ├── location_optimizer.py
│   ├── station_calculating_model.py
│   └── wait_time_predictor.py
├── services/
│   ├── cng_calculator.py              # CNG calculations
│   ├── vehicle_comparison_service.py  # Vehicle comparison
│   ├── trip_cost_calculator.py        # Trip calculations
│   ├── maintenance_service.py         # Maintenance tracking
│   ├── notification_service.py        # Notifications
│   └── realtime_station_fetcher.py    # Station data
├── static/
│   ├── css/                   # Stylesheets
│   ├── js/                    # JavaScript files
│   └── images/                # Images and assets
├── templates/
│   ├── dashboard.html
│   ├── vehicle_comparison.html
│   ├── trip_calculator.html
│   ├── maintenance_tracker.html
│   ├── fuel_history.html
│   └── ...                    # Other templates
├── scripts/
│   └── filter_land_points.py
├── docs/
│   ├── FEATURES_SUMMARY.md
│   ├── NEW_FEATURES_DOCUMENTATION.md
│   ├── QUICK_START.md
│   └── screenshots/
└── Smart_CNG_API_Collection.postman_collection.json
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Write clear commit messages
- Add tests for new features
- Update documentation
- Ensure all tests pass

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

### Documentation
- [Features Summary](FEATURES_SUMMARY.md)
- [API Documentation](NEW_FEATURES_DOCUMENTATION.md)
- [Quick Start Guide](QUICK_START.md)

### Common Issues

**Database Errors**
```bash
python -c "from app import app, db; app.app_context().push(); db.drop_all(); db.create_all()"
```

**Port Already in Use**
```bash
# Windows
Get-Process -Name python | Stop-Process -Force

# Linux/Mac
pkill -f python
```

**Module Not Found**
```bash
pip install -r requirements.txt --force-reinstall
```

### Contact

- **GitHub Issues**: [Open an issue](https://github.com/yourusername/Smart_CNG/issues)
- **Email**: your.email@example.com
- **Twitter**: [@smartcng](https://twitter.com/smartcng)

---

## 🙏 Acknowledgments

- OpenStreetMap for station data
- Flask community for excellent framework
- All contributors and users

---

## 🗺️ Roadmap

### Version 2.1 (Q4 2025)
- [ ] Mobile app (iOS/Android)
- [ ] Push notifications
- [ ] Offline mode
- [ ] Voice commands

### Version 2.2 (Q1 2026)
- [ ] AI-powered predictions
- [ ] Social features
- [ ] Fleet management
- [ ] Advanced analytics

### Version 3.0 (Q2 2026)
- [ ] Blockchain integration
- [ ] Cryptocurrency payments
- [ ] IoT device integration
- [ ] AR navigation

---

## 📊 Statistics

- **Total API Endpoints**: 22+
- **Database Models**: 15+
- **Service Layers**: 6
- **Frontend Pages**: 10+
- **Lines of Code**: 10,000+
- **Test Coverage**: TBD

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/Smart_CNG&type=Date)](https://star-history.com/#yourusername/Smart_CNG&Date)

---

<div align="center">

**Made with ❤️ for CNG enthusiasts**

[⬆ Back to Top](#-smart-cng-platform)

</div>
