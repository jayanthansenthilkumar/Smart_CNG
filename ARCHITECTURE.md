# Smart CNG - System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SMART CNG PLATFORM                               │
│                      Real-Time CNG Station Finder                        │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────┤
│  Web Browser (Desktop/Mobile)                                           │
│  ├── HTML5/CSS3/JavaScript                                              │
│  ├── Leaflet.js (Maps)                                                  │
│  ├── Chart.js (Analytics)                                               │
│  └── SweetAlert2 (Modals)                                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  Flask Web Application (app.py)                                         │
│  ├── Routes & Controllers (20+ endpoints)                               │
│  ├── Authentication (Flask-Login)                                       │
│  ├── Session Management                                                 │
│  └── CORS Configuration                                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                ▼                   ▼                   ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   BUSINESS LOGIC     │  │   DATA SERVICES      │  │  EXTERNAL APIs      │
├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤
│ Wait Time Predictor │  │ Realtime Fetcher    │  │ Google Places API   │
│ Location Optimizer  │  │ Notification Svc    │  │ OpenStreetMap       │
│ CNG Calculator      │  │ Price Tracker       │  │ Indian Govt APIs    │
│ Route Planner       │  │ Queue Manager       │  │ SMTP Server         │
│ Analytics Engine    │  │ Review System       │  │ Twilio SMS          │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATABASE LAYER                                    │
├─────────────────────────────────────────────────────────────────────────┤
│  SQLAlchemy ORM                                                         │
│  ├── Users & Authentication                                             │
│  ├── Stations & Availability                                            │
│  ├── Prices & Trends                                                    │
│  ├── Reviews & Ratings                                                  │
│  ├── Bookings & Queue                                                   │
│  └── Alerts & Favorites                                                 │
│                                                                          │
│  SQLite (Development) / PostgreSQL (Production)                         │
└─────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                            DATA FLOW DIAGRAM
═══════════════════════════════════════════════════════════════════════════

USER REQUEST: "Find CNG stations near me"
     │
     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. User allows location access                                          │
│    Browser gets GPS coordinates (lat: 28.6139, lng: 77.2090)           │
└─────────────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. AJAX Request                                                          │
│    GET /api/realtime-stations/28.6139/77.2090?radius=50                │
└─────────────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. Realtime Station Fetcher Service                                     │
│    ├── Check local database cache                                       │
│    ├── Fetch from Google Places API                                     │
│    ├── Fetch from OpenStreetMap                                         │
│    ├── Fetch from Government sources (if India)                         │
│    ├── Deduplicate results (within 100m)                               │
│    └── Merge station information                                        │
└─────────────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. Enrich with Database Information                                     │
│    For each station:                                                     │
│    ├── Get current price (station_prices table)                         │
│    ├── Get availability status (station_availability table)             │
│    ├── Get average rating (station_reviews aggregation)                 │
│    └── Get queue information (station_bookings count)                   │
└─────────────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 5. Wait Time Prediction (ML Model)                                      │
│    Uses features:                                                        │
│    ├── Current queue length                                             │
│    ├── Active chargers                                                  │
│    ├── Hour of day                                                      │
│    ├── Day of week                                                      │
│    ├── Historical averages                                              │
│    └── Traffic density                                                  │
└─────────────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 6. Sort & Filter Results                                                │
│    ├── Sort by: predicted wait time, then distance                      │
│    ├── Filter: operational stations only                                │
│    └── Limit: top 100 results                                           │
└─────────────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 7. JSON Response                                                         │
│    {                                                                     │
│      "stations": [...],                                                 │
│      "count": 25                                                        │
│    }                                                                     │
└─────────────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 8. Display on Map                                                        │
│    ├── Render markers on Leaflet map                                    │
│    ├── Show station details on click                                    │
│    ├── Display wait time colors (green/yellow/red)                      │
│    └── Enable route to station                                          │
└─────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                          DATABASE SCHEMA
═══════════════════════════════════════════════════════════════════════════

┌────────────────┐        ┌────────────────┐        ┌────────────────┐
│     users      │◄───────│    vehicles    │        │    stations    │
├────────────────┤   1:N  ├────────────────┤        ├────────────────┤
│ id (PK)        │        │ id (PK)        │        │ id (PK)        │
│ username       │        │ user_id (FK)   │        │ name           │
│ email          │        │ make           │        │ latitude       │
│ password_hash  │        │ model          │        │ longitude      │
│ phone          │        │ fuel_type      │        │ operator       │
│ created_at     │        │ is_cng_conv    │        │ rating         │
└────────────────┘        └────────────────┘        │ amenities      │
       │                                             └────────────────┘
       │ 1:N                                                │
       ▼                                                    │ 1:1
┌────────────────┐                              ┌────────────────────┐
│favorite_station│                              │station_availability│
├────────────────┤                              ├────────────────────┤
│ id (PK)        │                              │ id (PK)            │
│ user_id (FK)   │                              │ station_id (FK)    │
│ station_id(FK) │                              │ is_operational     │
│ notes          │                              │ queue_length       │
└────────────────┘                              │ wait_minutes       │
                                                 │ stock_level        │
       │ 1:N                                     └────────────────────┘
       ▼                                                    │
┌────────────────┐                                        │ 1:N
│ price_alerts   │                                        ▼
├────────────────┤                              ┌────────────────────┐
│ id (PK)        │                              │  station_prices    │
│ user_id (FK)   │                              ├────────────────────┤
│ fuel_type      │                              │ id (PK)            │
│ threshold      │                              │ station_id (FK)    │
│ is_active      │                              │ fuel_type          │
└────────────────┘                              │ price              │
                                                 │ updated_at         │
       │ 1:N                                     └────────────────────┘
       ▼                                                    │
┌────────────────┐                                        │ 1:N
│station_reviews │                                        ▼
├────────────────┤                              ┌────────────────────┐
│ id (PK)        │                              │  price_trends      │
│ user_id (FK)   │                              ├────────────────────┤
│ station_id(FK) │                              │ id (PK)            │
│ rating (1-5)   │                              │ station_id (FK)    │
│ review_text    │                              │ fuel_type          │
│ service_rating │                              │ price              │
│ wait_rating    │                              │ date               │
└────────────────┘                              └────────────────────┘

       │ 1:N
       ▼
┌────────────────┐
│station_bookings│
├────────────────┤
│ id (PK)        │
│ user_id (FK)   │
│ station_id(FK) │
│ queue_number   │
│ est_arrival    │
│ status         │
└────────────────┘


═══════════════════════════════════════════════════════════════════════════
                      NOTIFICATION FLOW
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│                     TRIGGER: Price Drop Detected                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. Query active price alerts                                            │
│    SELECT * FROM price_alerts                                           │
│    WHERE fuel_type = 'cng'                                              │
│    AND is_active = TRUE                                                 │
│    AND threshold >= new_price                                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. For each matching alert:                                             │
│    ├── Get user information                                             │
│    ├── Get user's notification preferences                              │
│    └── Get station details (if station-specific)                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
    ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
    │ Email (SMTP) │      │  SMS (Twilio)│      │ Push (FCM)   │
    ├──────────────┤      ├──────────────┤      ├──────────────┤
    │ Compose msg  │      │ Format text  │      │ Build payload│
    │ Add template │      │ Limit 160ch  │      │ Add badge    │
    │ Send via     │      │ Send via API │      │ Send to FCM  │
    │ SMTP server  │      │              │      │              │
    └──────────────┘      └──────────────┘      └──────────────┘
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. Log notification                                                      │
│    ├── Update alert.last_triggered                                      │
│    ├── Increment alert.trigger_count                                    │
│    └── Log to notification_history (if table exists)                    │
└─────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                    DEPLOYMENT ARCHITECTURE (Production)
═══════════════════════════════════════════════════════════════════════════

                             ┌──────────────┐
                             │   Internet   │
                             └──────┬───────┘
                                    │
                                    ▼
                          ┌──────────────────┐
                          │ Cloudflare CDN   │
                          │ (Static Assets)  │
                          └──────┬───────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  Nginx Reverse Proxy     │
                    │  - SSL Termination       │
                    │  - Load Balancing        │
                    │  - Static File Serving   │
                    └──────────┬──────────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
        ┌────────────┐ ┌────────────┐ ┌────────────┐
        │ Gunicorn 1 │ │ Gunicorn 2 │ │ Gunicorn 3 │
        │ Worker     │ │ Worker     │ │ Worker     │
        │ (Flask App)│ │ (Flask App)│ │ (Flask App)│
        └────────────┘ └────────────┘ └────────────┘
                │              │              │
                └──────────────┼──────────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
        ┌────────────┐ ┌────────────┐ ┌────────────┐
        │ PostgreSQL │ │   Redis    │ │   Celery   │
        │ Database   │ │   Cache    │ │   Worker   │
        │            │ │            │ │ (Bkg Jobs) │
        └────────────┘ └────────────┘ └────────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
        ┌────────────┐ ┌────────────┐ ┌────────────┐
        │   Sentry   │ │ Log Files  │ │  Backups   │
        │ (Errors)   │ │ (Logging)  │ │ (Daily)    │
        └────────────┘ └────────────┘ └────────────┘


═══════════════════════════════════════════════════════════════════════════
                         TECHNOLOGY STACK
═══════════════════════════════════════════════════════════════════════════

Frontend:
  └─ HTML5 / CSS3 / JavaScript (ES6+)
     ├─ Leaflet.js (Interactive Maps)
     ├─ Chart.js (Analytics Charts)
     ├─ SweetAlert2 (Modal Dialogs)
     └─ Fetch API (AJAX Requests)

Backend:
  └─ Python 3.8+
     ├─ Flask 3.0 (Web Framework)
     ├─ Flask-SQLAlchemy (ORM)
     ├─ Flask-Login (Authentication)
     ├─ Flask-CORS (Cross-Origin)
     └─ Gunicorn (WSGI Server)

Database:
  ├─ SQLite (Development)
  └─ PostgreSQL (Production)

AI/ML:
  ├─ scikit-learn (Wait Time Prediction)
  ├─ NumPy (Numerical Computing)
  └─ Pandas (Data Processing)

External Services:
  ├─ Google Places API (Station Data)
  ├─ OpenStreetMap (Geographic Data)
  ├─ Twilio (SMS Notifications)
  ├─ SMTP (Email Notifications)
  └─ Firebase (Push Notifications)

DevOps:
  ├─ Git (Version Control)
  ├─ Nginx (Reverse Proxy)
  ├─ SSL/TLS (Security)
  └─ Sentry (Error Tracking)


═══════════════════════════════════════════════════════════════════════════
                        SCALABILITY CONSIDERATIONS
═══════════════════════════════════════════════════════════════════════════

Horizontal Scaling:
  ├─ Multiple Gunicorn workers
  ├─ Load balancing with Nginx
  ├─ Stateless application design
  └─ Session storage in Redis

Caching Strategy:
  ├─ Redis for API responses (1 hour)
  ├─ Browser cache for static assets
  ├─ Database query result caching
  └─ CDN for images/CSS/JS

Database Optimization:
  ├─ Indexes on frequently queried columns
  ├─ Connection pooling
  ├─ Read replicas for analytics
  └─ Periodic data archiving

Background Jobs:
  ├─ Celery for async tasks
  ├─ Price update scheduling
  ├─ Notification queue processing
  └─ Data cleanup tasks

Monitoring:
  ├─ Application performance (Sentry)
  ├─ Database performance (pg_stat_statements)
  ├─ API response times
  └─ Error rates and alerts
```
