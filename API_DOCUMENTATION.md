# Smart CNG - API Documentation 📡

Complete API reference for integrating with the Smart CNG platform.

## Base URL
```
Development: http://localhost:5000
Production: https://your-domain.com
```

## Authentication

Most endpoints require authentication via Flask-Login session cookies.

### Login
```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=Syraa&password=Syraa
```

**Response:**
```http
302 Redirect to /dashboard
Set-Cookie: session=...
```

---

## Station Endpoints

### 1. Get Nearby Stations (Legacy)
Fetches stations from CSV file within radius.

```http
GET /api/stations/<lat>/<lng>?radius=<km>
```

**Parameters:**
- `lat` (required): Latitude
- `lng` (required): Longitude
- `radius` (optional): Search radius in kilometers (default: 5)

**Example:**
```http
GET /api/stations/28.6139/77.2090?radius=10
```

**Response:**
```json
{
  "stations": [
    {
      "id": "28.613900,77.209000",
      "name": "CNG Station",
      "position": {"lat": 28.6139, "lng": 77.209},
      "distance_km": 0.5,
      "active_chargers": 1,
      "total_chargers": 2,
      "predicted_wait": 12.5,
      "prediction_confidence": 0.85
    }
  ]
}
```

### 2. Get Real-Time Stations (NEW)
Fetches stations from multiple sources (Google, OSM, Government).

```http
GET /api/realtime-stations/<lat>/<lng>?radius=<km>
```

**Parameters:**
- `lat` (required): Latitude
- `lng` (required): Longitude
- `radius` (optional): Search radius in kilometers (default: 50)

**Example:**
```http
GET /api/realtime-stations/28.6139/77.2090?radius=50
```

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
      "brand": "IndianOil",
      "phone": "+91-11-12345678",
      "website": "https://iocl.com",
      "opening_hours": "24/7",
      "source": "google_places,openstreetmap",
      "id": 42,
      "rating": 4.5,
      "total_reviews": 128,
      "is_operational": true,
      "queue_length": 3,
      "wait_time": 15,
      "stock_level": "high"
    }
  ],
  "count": 1
}
```

### 3. Get Station Details
Detailed information about a specific station.

```http
GET /api/station-details/<station_id>
```

**Example:**
```http
GET /api/station-details/42
```

**Response:**
```json
{
  "id": 42,
  "name": "Indian Oil CNG Station",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "address": "Connaught Place, New Delhi",
  "city": "New Delhi",
  "operating_hours": "24/7",
  "is_24x7": true,
  "operator": "Indian Oil",
  "phone": "+91-11-12345678",
  "website": "https://iocl.com",
  "amenities": {
    "payment_methods": ["cash", "card", "upi"],
    "facilities": ["restroom", "air_pump", "convenience_store"]
  },
  "rating": 4.5,
  "total_reviews": 128,
  "prices": {
    "cng": {
      "price": 74.59,
      "currency": "INR",
      "updated": "2025-10-07T10:30:00"
    }
  },
  "availability": {
    "operational": true,
    "queue_length": 3,
    "wait_minutes": 15,
    "available_pumps": 2,
    "total_pumps": 3,
    "stock_level": "high"
  },
  "recent_reviews": [
    {
      "id": 1,
      "rating": 5,
      "text": "Excellent service!",
      "user": "john_doe",
      "created": "2025-10-06T14:20:00"
    }
  ]
}
```

### 4. Compare Station Prices
Compare CNG prices across multiple stations.

```http
GET /api/compare-prices?lat=<lat>&lng=<lng>&radius=<km>
```

**Example:**
```http
GET /api/compare-prices?lat=28.6139&lng=77.2090&radius=10
```

**Response:**
```json
{
  "stations": [
    {
      "station_id": 42,
      "name": "Indian Oil CNG Station",
      "latitude": 28.6139,
      "longitude": 77.2090,
      "price": 74.59,
      "updated": "2025-10-07T10:30:00",
      "rating": 4.5
    },
    {
      "station_id": 43,
      "name": "GAIL CNG Pump",
      "latitude": 28.6200,
      "longitude": 77.2100,
      "price": 75.20,
      "updated": "2025-10-07T09:15:00",
      "rating": 4.2
    }
  ]
}
```

### 5. Get Stations from File
Load stations from CSV file.

```http
GET /api/stations-from-file
```

**Response:**
```json
{
  "stations": [
    {
      "name": "CNG Station",
      "position": {"lat": 28.6139, "lng": 77.2090}
    }
  ]
}
```

---

## User Endpoints

### 6. Add Station Review
Submit a review for a station (requires authentication).

```http
POST /api/station-review
Content-Type: application/json
Authorization: Required (session)
```

**Request Body:**
```json
{
  "station_id": 42,
  "rating": 5,
  "text": "Excellent service and very clean!",
  "service_quality": 5,
  "wait_time_rating": 4,
  "price_rating": 5,
  "cleanliness_rating": 5
}
```

**Response:**
```json
{
  "message": "Review added successfully",
  "review_id": 123
}
```

### 7. Create Station Booking
Book a queue slot at a station (requires authentication).

```http
POST /api/station-booking
Content-Type: application/json
Authorization: Required (session)
```

**Request Body:**
```json
{
  "station_id": 42,
  "estimated_arrival": "2025-10-07T14:30:00",
  "vehicle_id": 5,
  "estimated_fill_amount": 10.5
}
```

**Response:**
```json
{
  "message": "Booking created successfully",
  "booking_id": 456,
  "queue_number": 7
}
```

### 8. Create Price Alert
Set up price drop notifications (requires authentication).

```http
POST /api/price-alert
Content-Type: application/json
Authorization: Required (session)
```

**Request Body:**
```json
{
  "fuel_type": "cng",
  "city": "Delhi",
  "station_id": 42,
  "threshold": 70.0,
  "notification_method": "email"
}
```

**Response:**
```json
{
  "message": "Price alert created successfully",
  "alert_id": 789
}
```

### 9. Toggle Favorite Station
Add or remove station from favorites (requires authentication).

```http
POST /api/favorite-station/<station_id>
Content-Type: application/json
Authorization: Required (session)
```

**Request Body (POST):**
```json
{
  "notes": "Near my office, best prices"
}
```

**Response:**
```json
{
  "message": "Station added to favorites"
}
```

**Delete Favorite:**
```http
DELETE /api/favorite-station/<station_id>
Authorization: Required (session)
```

**Response:**
```json
{
  "message": "Station removed from favorites"
}
```

### 10. Get User Favorites
List user's favorite stations (requires authentication).

```http
GET /api/user/favorites
Authorization: Required (session)
```

**Response:**
```json
{
  "favorites": [
    {
      "id": 42,
      "name": "Indian Oil CNG Station",
      "latitude": 28.6139,
      "longitude": 77.2090,
      "address": "Connaught Place",
      "rating": 4.5,
      "notes": "Near my office",
      "added_on": "2025-09-15T10:00:00"
    }
  ]
}
```

### 11. Get User Vehicles
List user's registered vehicles (requires authentication).

```http
GET /api/user-vehicles
Authorization: Required (session)
```

**Response:**
```json
{
  "vehicles": [
    {
      "id": 5,
      "make": "Maruti",
      "model": "WagonR",
      "year": 2020,
      "fuel_type": "cng",
      "avg_mileage": 26.5,
      "monthly_usage": 800,
      "is_cng_converted": true
    }
  ]
}
```

---

## Analytics Endpoints

### 12. Get Price Trends
Historical price data for charts.

```http
GET /api/price-trends/<fuel_type>?city=<city>&days=<days>
```

**Parameters:**
- `fuel_type` (required): "cng", "petrol", or "diesel"
- `city` (optional): City name (default: "Delhi")
- `days` (optional): Number of days (default: 30)

**Example:**
```http
GET /api/price-trends/cng?city=Delhi&days=30
```

**Response:**
```json
{
  "trends": [
    {
      "date": "2025-09-07T00:00:00",
      "price": 74.59,
      "city": "Delhi"
    },
    {
      "date": "2025-09-08T00:00:00",
      "price": 74.75,
      "city": "Delhi"
    }
  ]
}
```

### 13. Get Station Statistics
Aggregated platform statistics.

```http
GET /api/station-statistics
```

**Response:**
```json
{
  "totalUsers": 1234,
  "activeCNGVehicles": 567,
  "totalStations": 890,
  "averageWaitTime": 12.5,
  "monthlySavings": 45000,
  "annualSavings": 540000,
  "co2Reduced": 1250.5,
  "treesEquivalent": 56.8
}
```

---

## CNG Calculator Endpoints

### 14. Calculate CNG Savings
Comprehensive savings analysis (requires authentication).

```http
POST /api/calculate-cng-savings
Content-Type: application/json
Authorization: Required (session)
```

**Request Body:**
```json
{
  "vehicleType": "sedan",
  "currentFuel": "petrol",
  "monthlyDistance": 1000,
  "currentMileage": 15,
  "kitType": "sequential"
}
```

**Response:**
```json
{
  "conversion_cost": {
    "kit_cost": 35000,
    "installation": 5000,
    "total": 40000
  },
  "monthly_savings": 3750,
  "annual_savings": 45000,
  "payback_period_months": 10.67,
  "environmental_impact": {
    "co2_reduction_kg_per_year": 850,
    "trees_equivalent": 38.6
  },
  "cost_comparison": {
    "current_monthly_cost": 6000,
    "cng_monthly_cost": 2250,
    "savings_percentage": 62.5
  }
}
```

### 15. Get Fuel Prices
Current fuel prices by city.

```http
GET /api/fuel-prices?city=<city>
```

**Example:**
```http
GET /api/fuel-prices?city=Delhi
```

**Response:**
```json
{
  "prices": {
    "petrol": 96.72,
    "diesel": 89.62,
    "cng": 74.59
  }
}
```

### 16. Get Conversion Costs
CNG conversion kit pricing.

```http
GET /api/conversion-costs
```

**Response:**
```json
{
  "costs": [
    {
      "vehicle_type": "sedan",
      "base_cost": 35000,
      "labor_cost": 5000,
      "kit_type": "sequential",
      "warranty_period": 60
    },
    {
      "vehicle_type": "suv",
      "base_cost": 45000,
      "labor_cost": 7000,
      "kit_type": "sequential",
      "warranty_period": 60
    }
  ]
}
```

---

## Route Planning Endpoints

### 17. Plan Route with CNG Stops
Calculate optimal CNG filling stops along a route.

```http
POST /api/route-plan
Content-Type: application/json
```

**Request Body:**
```json
{
  "route": {
    "distance": 450.5,
    "coordinates": [
      [28.6139, 77.2090],
      [28.7041, 77.1025]
    ]
  },
  "cngModel": {
    "name": "Maruti WagonR",
    "tankCapacity": 60,
    "range": 320,
    "fillingSpeed": 10,
    "consumption": 0.2
  },
  "currentFuel": 40
}
```

**Response:**
```json
{
  "fillingStops": [
    {
      "name": "Indian Oil CNG Station",
      "lat": 28.6500,
      "lng": 77.1500,
      "arrivalFuel": 25.5,
      "departureFuel": 60,
      "fillTime": 3.5,
      "distanceFromStart": 150.2,
      "type": "CNG Pump"
    }
  ]
}
```

---

## Location Optimizer Endpoints

### 18. Get Optimal Locations
AI-powered recommendations for new station locations.

```http
GET /api/optimize-locations/<lat>/<lng>
```

**Example:**
```http
GET /api/optimize-locations/28.6139/77.2090
```

**Response:**
```json
{
  "candidates": [
    {
      "lat": 28.6200,
      "lng": 77.2150,
      "score": 0.85,
      "demand": "high",
      "coverage_gap": true,
      "traffic_density": 0.75
    }
  ]
}
```

---

## Error Responses

All endpoints may return error responses:

### 400 Bad Request
```json
{
  "error": "Missing required field: station_id"
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required"
}
```

### 404 Not Found
```json
{
  "error": "Station not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Failed to fetch stations"
}
```

---

## Rate Limiting

Currently not implemented, but recommended for production:
- 60 requests per minute per IP
- 1000 requests per day per user

---

## Webhooks (Planned)

Future support for webhooks to notify external systems:
- Price changes
- New station additions
- Queue status updates

---

## SDKs (Planned)

Official SDKs coming soon:
- Python SDK
- JavaScript/Node.js SDK
- React Native SDK

---

## Support

For API support:
- GitHub Issues: https://github.com/jayanthansenthilkumar/Smart_CNG/issues
- Email: [Add your email]

---

**API Version: 2.0.0**
**Last Updated: October 7, 2025**
