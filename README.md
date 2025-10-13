<p align="center">
  <img src="static/@logo.png" alt="QuickFill Logo" width="400" height="auto">
</p>

# Smart CNG - Intelligent CNG Station Finder & Management Platform 🚗⛽

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-lightgrey)](https://flask.palletsprojects.com/)

Smart CNG is a comprehensive, intelligent platform for finding CNG stations globally, comparing prices in real-time, booking queue slots, and managing your CNG vehicle's fuel economy. Built with advanced AI-powered wait time prediction and location optimization.

## 🌟 Key Features

### 🗺️ **Real-Time Global CNG Station Network**
- **Multi-Source Integration**: Fetch real-time CNG station data from:
  - Google Places API
  - OpenStreetMap (Overpass API)
  - Indian government sources (Indian Oil, GAIL)
  - Community-contributed data
- **Global Coverage**: CNG stations from India and worldwide
- **Smart Deduplication**: Intelligent merging of data from multiple sources
- **Live Availability**: Real-time stock levels, operational status, and queue information

### 💰 **Price Comparison & Alerts**
- **Real-Time Price Tracking**: Compare CNG prices across stations in your area
- **Price Drop Alerts**: Get notified via email/SMS when prices drop
- **Historical Trends**: View 30-day price history charts
- **Best Deal Finder**: Automatically find the cheapest CNG near you

### 📊 **Advanced Analytics Dashboard**
- **Savings Calculator**: Track fuel savings after CNG conversion
- **Environmental Impact**: Monitor CO₂ reduction and tree equivalents
- **Usage Patterns**: Visualize your fueling habits over time
- **Station Heatmaps**: See popular stations and peak hours

### 🎯 **Smart Queue & Booking System**
- **Live Queue Status**: See real-time queue length and estimated wait times
- **Advance Booking**: Reserve your spot in the queue
- **Queue Notifications**: Get alerts when it's your turn
- **Time Slot Management**: Choose convenient filling times

### ⭐ **Reviews & Ratings**
- **Station Reviews**: Read and write reviews for CNG stations
- **Multi-Criteria Ratings**: Rate service quality, wait time, pricing, cleanliness
- **Verified Visits**: Mark reviews from actual visits
- **Community Feedback**: Report price discrepancies and service issues

### 🚗 **CNG Conversion Calculator**
- **ROI Analysis**: Calculate payback period for CNG conversion
- **Vehicle-Specific Costs**: Accurate conversion costs by vehicle type
- **Savings Projections**: Monthly and annual fuel savings estimates
- **Kit Comparisons**: Compare sequential vs. venturi CNG kits

### 📍 **Location Optimization**
- **AI-Powered Recommendations**: Find optimal locations for new CNG stations
- **Demand Analysis**: Identify underserved areas
- **Traffic Pattern Integration**: Consider peak hours and traffic density
- **Geographic Restrictions**: Avoid water bodies and restricted zones

### 🛣️ **Route Planner**
- **Multi-Stop Planning**: Plan routes with CNG fill-up stops
- **Range Calculator**: Estimate fuel needs based on vehicle specs
- **Alternative Routes**: Find routes with better station availability
- **Real-Time Rerouting**: Adjust for closed or full stations

### 🔔 **Smart Notifications**
- **Multi-Channel Alerts**: Email, SMS, and push notifications
- **Personalized Alerts**:
  - Price drops at favorite stations
  - New stations opening nearby
  - Queue time reductions
  - Booking confirmations
- **Customizable Frequency**: Choose notification preferences

### 👤 **User Features**
- **Profile Management**: Track multiple vehicles
- **Favorite Stations**: Save frequently visited stations
- **Fuel Logs**: Maintain detailed refueling history
- **Preferences**: Customize search radius, notification settings

## 📑 Table of Contents

- [Features](#key-features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask 2.0+
- **Database**: SQLAlchemy with SQLite/PostgreSQL
- **Authentication**: Flask-Login
- **APIs**: RESTful API design
- **Task Queue**: Background job processing (planned)

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript**: Vanilla JS + AJAX
- **Maps**: Leaflet.js for interactive maps
- **Charts**: Chart.js for analytics visualization
- **UI**: Custom CSS with SweetAlert2 for modals

### AI/ML
- **Wait Time Prediction**: Custom ML model using historical data
- **Location Optimization**: Algorithm considering multiple factors
- **Demand Forecasting**: Time-series analysis

### External Integrations
- **Google Places API**: Station data enrichment
- **OpenStreetMap**: Free geographic data
- **Twilio**: SMS notifications (optional)
- **SendGrid/SMTP**: Email notifications
- **Firebase**: Push notifications (planned)

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/jayanthansenthilkumar/Smart_CNG.git
cd Smart_CNG
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables
Create a `.env` file in the project root:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production
FLASK_APP=app.py
FLASK_ENV=development

# Database
DATABASE_URL=sqlite:///instance/fuelexa.db

# Google Places API (Optional but recommended)
GOOGLE_PLACES_API_KEY=your-google-api-key

# Email Notifications (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# SMS Notifications (Optional)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# Firebase Push Notifications (Optional)
FIREBASE_API_KEY=your-firebase-key
```

### Step 5: Initialize Database
```bash
python app.py
# This will create all necessary database tables
```

### Step 6: Load Sample Data (Optional)
```bash
# Place your CNG station CSV file in the project root
# The app will automatically detect and use:
# - CNG_pumps_with_Erlang-C_waiting_times_250.csv
# - Or any other CSV with lat/lng columns
```

## ⚙️ Configuration

### API Keys Setup

#### Google Places API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "Places API"
4. Create credentials (API Key)
5. Add to `.env` file

#### Twilio SMS (Optional)
1. Sign up at [Twilio](https://www.twilio.com/)
2. Get Account SID and Auth Token
3. Purchase a phone number
4. Add credentials to `.env`

## 💻 Usage

### Start the Development Server
```bash
python app.py
# Server runs on http://localhost:5000
```

### Default Login Credentials
```
Username: Syraa
Password: Syraa
```
**⚠️ Change these in production!**

### Access Different Features

1. **Dashboard**: `http://localhost:5000/`
2. **Find Stations**: `http://localhost:5000/stations`
3. **Route Planner**: `http://localhost:5000/route-planner`
4. **CNG Calculator**: `http://localhost:5000/cng-switch`
5. **Location Optimizer**: `http://localhost:5000/location-optimizer`
6. **Analytics**: `http://localhost:5000/analytics`

## 📡 API Documentation

### Station Endpoints

#### Get Real-Time Stations
```http
GET /api/realtime-stations/<lat>/<lng>?radius=50
```
Fetches CNG stations from all sources (Google, OSM, government).

**Parameters:**
- `lat`: Latitude (required)
- `lng`: Longitude (required)
- `radius`: Search radius in km (optional, default: 50)

**Response:**
```json
{
  "stations": [
    {
      "name": "Indian Oil CNG Station",
      "lat": 28.6139,
      "lng": 77.2090,
      "address": "Connaught Place, New Delhi",
      "operator": "Indian Oil",
      "is_operational": true,
      "queue_length": 3,
      "wait_time": 15,
      "stock_level": "high",
      "rating": 4.5,
      "source": "google_places,openstreetmap"
    }
  ],
  "count": 1
}
```

#### Get Station Details
```http
GET /api/station-details/<station_id>
```

#### Compare Prices
```http
GET /api/compare-prices?lat=28.6139&lng=77.2090&radius=10
```

#### Get Price Trends
```http
GET /api/price-trends/<fuel_type>?city=Delhi&days=30
```

### User Endpoints

#### Add Station Review
```http
POST /api/station-review
Authorization: Bearer <token>

{
  "station_id": 1,
  "rating": 5,
  "text": "Great service!",
  "service_quality": 5,
  "wait_time_rating": 4,
  "price_rating": 5,
  "cleanliness_rating": 5
}
```

#### Create Booking
```http
POST /api/station-booking
Authorization: Bearer <token>

{
  "station_id": 1,
  "estimated_arrival": "2025-10-07T14:30:00",
  "vehicle_id": 1,
  "estimated_fill_amount": 10
}
```

#### Create Price Alert
```http
POST /api/price-alert
Authorization: Bearer <token>

{
  "fuel_type": "cng",
  "city": "Delhi",
  "threshold": 70.0,
  "notification_method": "email"
}
```

#### Add to Favorites
```http
POST /api/favorite-station/<station_id>
Authorization: Bearer <token>

{
  "notes": "Near my office"
}
```

## 🗄️ Database Schema

### Core Tables
- **users**: User accounts and authentication
- **vehicles**: User's vehicles with CNG conversion status
- **stations**: CNG station information
- **fuel_logs**: Refueling history

### New Tables (Enhanced Features)
- **station_prices**: Real-time fuel prices per station
- **station_availability**: Live stock and queue status
- **station_reviews**: User ratings and reviews
- **station_bookings**: Queue booking system
- **price_alerts**: User price drop notifications
- **favorite_stations**: Saved stations per user
- **price_trends**: Historical price data for analytics

## 📁 Project Structure

```
Smart_CNG/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── instance/
│   └── fuelexa.db                 # SQLite database
│
├── models/
│   ├── __init__.py
│   ├── cng_calculator.py          # Database models (ENHANCED)
│   ├── location_optimizer.py     # Location optimization algorithms
│   ├── wait_time_predictor.py    # ML wait time prediction
│   └── station_calculating_model.py
│
├── services/
│   ├── cng_calculator.py          # CNG savings calculator
│   ├── realtime_station_fetcher.py # NEW: Multi-source station fetcher
│   └── notification_service.py     # NEW: Email/SMS/Push notifications
│
├── static/
│   ├── css/                       # Stylesheets
│   ├── js/                        # JavaScript files
│   └── images/                    # Static images
│
└── templates/                     # HTML templates
    ├── dashboard.html
    ├── nearby_stations.html
    ├── route_planner.html
    ├── cng_switch.html
    ├── location_optimizer.html
    └── analytics.html
```

## 🔧 Advanced Features

### 1. Real-Time Station Data Fetching

The `RealtimeCNGStationFetcher` service combines data from multiple sources:

```python
from services.realtime_station_fetcher import realtime_fetcher

# Fetch stations from all sources
stations = realtime_fetcher.fetch_all_sources(lat=28.6139, lng=77.2090, radius_km=50)
```

### 2. AI-Powered Wait Time Prediction

Uses historical data and Erlang-C queuing theory:

```python
from models.wait_time_predictor import WaitTimePredictor

predictor = WaitTimePredictor()
predictor.train_from_csv('CNG_pumps_with_Erlang-C_waiting_times_250.csv')

predictions = predictor.predict_wait_time([{
    'active_chargers': 2,
    'current_queue_length': 5,
    'hour_of_day': 14,
    'is_weekend': 0
}])
```

### 3. Notification System

Send alerts via multiple channels:

```python
from services.notification_service import notification_service

# Send price drop alert
notification_service.send_price_alert(
    user=user,
    fuel_type='cng',
    new_price=72.50,
    station=station
)
```

## 📊 Data Sources

### Indian CNG Stations
- **Coverage**: 280+ cities across India
- **Major Operators**: Indian Oil, GAIL, Adani Gas, Gujarat Gas
- **Update Frequency**: Real-time via APIs + daily data refresh

### Global CNG Stations
- **OpenStreetMap**: Community-contributed global data
- **Google Places**: Verified business listings worldwide
- **Government APIs**: Country-specific official sources

### Data Quality
- Automatic deduplication (within 100m radius)
- Multi-source verification
- Community reporting for updates
- Regular data validation

## 🌍 Internationalization

Support for multiple languages (planned):
- 🇮🇳 Hindi
- 🇮🇳 Regional languages (Tamil, Telugu, Bengali, Marathi, etc.)
- 🇬🇧 English
- 🇪🇸 Spanish
- 🇨🇳 Chinese

## 📱 Mobile Support

### Progressive Web App (PWA) Features (Planned)
- Offline station data caching
- GPS-based auto-location
- Add to home screen
- Push notifications
- Background sync

## 🔐 Security Features

- Password hashing with Werkzeug
- Session-based authentication
- CSRF protection
- SQL injection prevention via SQLAlchemy
- XSS protection
- Rate limiting (planned)

## 🚦 Performance Optimization

- Database indexing on lat/lng columns
- Query result caching
- Lazy loading of station data
- CDN for static assets (planned)
- API response compression

## 🧪 Testing

```bash
# Run tests (coming soon)
python -m pytest tests/

# Run specific test
python -m pytest tests/test_station_fetcher.py

# Coverage report
python -m pytest --cov=.
```

## 📈 Roadmap

### Phase 1: Core Features (✅ Completed)
- [x] Basic station finder
- [x] Wait time prediction
- [x] Route planning
- [x] CNG conversion calculator

### Phase 2: Enhanced Features (✅ Current)
- [x] Real-time multi-source data fetching
- [x] Price comparison & alerts
- [x] Reviews & ratings system
- [x] Booking/queue system
- [x] Notification service

### Phase 3: Advanced Features (🚧 In Progress)
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] Payment integration
- [ ] Loyalty rewards program
- [ ] Fleet management tools

### Phase 4: Enterprise Features (📋 Planned)
- [ ] B2B API access
- [ ] White-label solutions
- [ ] Advanced analytics dashboard
- [ ] Predictive maintenance alerts
- [ ] Integration with vehicle telematics

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Open a Pull Request**

### Contribution Guidelines
- Follow PEP 8 style guide for Python code
- Write clear commit messages
- Add tests for new features
- Update documentation
- Ensure all tests pass before submitting PR

## 🐛 Bug Reports

Found a bug? Please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)
- Your environment (OS, Python version, browser)

## 💡 Feature Requests

Have an idea? We'd love to hear it! Create an issue with:
- Clear description of the feature
- Use case/problem it solves
- Proposed solution (optional)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Jayanth Senthilkumar** - *Lead Developer* - [@jayanthansenthilkumar](https://github.com/jayanthansenthilkumar)

## 🙏 Acknowledgments

- OpenStreetMap contributors for geographic data
- Google Places API for enriched station information
- Indian Oil Corporation and GAIL for CNG infrastructure data
- The open-source community for various libraries and tools

## 📞 Contact

**Project Link**: [https://github.com/jayanthansenthilkumar/Smart_CNG](https://github.com/jayanthansenthilkumar/Smart_CNG)

For support or queries:
- Create an issue on GitHub
- Email: [Add your email]
- Twitter: [Add your Twitter]

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐️!

## 📝 Changelog

### Version 2.0.0 (Current)
- ✨ Added real-time multi-source station fetching
- ✨ Implemented price comparison and alerts
- ✨ Added reviews and ratings system
- ✨ Introduced booking/queue management
- ✨ Built notification service (Email/SMS/Push)
- 🗄️ Enhanced database schema with 7 new tables
- 📡 Added 10+ new API endpoints
- 📚 Comprehensive documentation update

### Version 1.0.0
- 🎉 Initial release
- Basic station finder
- Wait time prediction
- Route planning
- CNG conversion calculator

---

**Made with ❤️ for CNG vehicle owners worldwide**