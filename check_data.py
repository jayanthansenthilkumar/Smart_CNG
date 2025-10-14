"""
Quick Data Check Script
"""

import json
import os

print("="*60)
print("DATA VALIDATION CHECK")
print("="*60)

# Check vehicle database
try:
    with open('data/vehicle_database.json', 'r') as f:
        vdata = json.load(f)
    print(f"\n[OK] Vehicle Database")
    print(f"  - Vehicles: {len(vdata.get('vehicles', []))}")
    print(f"  - Fuel types: {', '.join(vdata.get('fuel_prices', {}).keys())}")
    print(f"  - Conversion kits: {len(vdata.get('cng_conversion_kits', []))}")
except Exception as e:
    print(f"\n[ERROR] Vehicle Database: {e}")

# Check CNG stations
try:
    with open('data/cng_stations.json', 'r') as f:
        stations = json.load(f)
    cities = set(s.get('city') for s in stations)
    print(f"\n[OK] CNG Stations")
    print(f"  - Total stations: {len(stations)}")
    print(f"  - Cities: {', '.join(sorted(cities))}")
except Exception as e:
    print(f"\n[ERROR] CNG Stations: {e}")

# Check routes
try:
    with open('data/routes_database.json', 'r') as f:
        routes = json.load(f)
    print(f"\n[OK] Routes Database")
    print(f"  - Routes: {len(routes.get('popular_routes', []))}")
except Exception as e:
    print(f"\n[ERROR] Routes: {e}")

# Check tips
try:
    with open('data/tips_recommendations.json', 'r', encoding='utf-8') as f:
        tips = json.load(f)
    print(f"\n[OK] Tips & Recommendations")
    print(f"  - Driving tips: {len(tips.get('driving_tips', []))}")
    print(f"  - Common issues: {len(tips.get('common_issues', []))}")
except Exception as e:
    print(f"\n[ERROR] Tips: {e}")

# Check service centers
try:
    with open('data/service_centers.json', 'r') as f:
        centers = json.load(f)
    print(f"\n[OK] Service Centers")
    print(f"  - Centers: {len(centers.get('service_centers', []))}")
except Exception as e:
    print(f"\n[ERROR] Service Centers: {e}")

# Check services
print(f"\n[INFO] Service Files")
services = ['conversion_calculator_service.py', 'service_center_service.py', 
            'vehicle_comparison_service.py', 'trip_cost_calculator.py', 
            'maintenance_service.py']
for svc in services:
    path = f'services/{svc}'
    if os.path.exists(path):
        print(f"  [OK] {svc}")
    else:
        print(f"  [MISSING] {svc}")

# Check templates
print(f"\n[INFO] Template Files")
templates = ['dashboard.html', 'conversion_calculator.html', 
             'vehicle_comparison.html', 'trip_calculator.html',
             'maintenance_tracker.html', 'fuel_history.html']
for tmpl in templates:
    path = f'templates/{tmpl}'
    if os.path.exists(path):
        print(f"  [OK] {tmpl}")
    else:
        print(f"  [MISSING] {tmpl}")

print("\n" + "="*60)
print("VALIDATION COMPLETE")
print("="*60)
