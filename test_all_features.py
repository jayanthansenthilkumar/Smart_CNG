#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive Feature Test Suite
Tests all major features and data integrity
"""
import json
import os

print("\n" + "="*60)
print("SMART CNG APPLICATION - FEATURE TEST SUITE")
print("="*60)

# Test 1: Data Files
print("\n[TEST 1] Data Files Integrity")
print("-" * 60)
data_files = [
    'data/vehicle_database.json',
    'data/cng_stations.json',
    'data/routes_database.json',
    'data/tips_recommendations.json',
    'data/service_centers.json'
]

for file_path in data_files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ {os.path.basename(file_path)}: OK")
    except Exception as e:
        print(f"✗ {os.path.basename(file_path)}: FAILED - {e}")

# Test 2: Services
print("\n[TEST 2] Service Files")
print("-" * 60)
service_files = [
    'services/conversion_calculator_service.py',
    'services/service_center_service.py',
    'services/vehicle_comparison_service.py',
    'services/trip_cost_calculator.py',
    'services/maintenance_service.py',
    'services/cng_calculator.py'
]

for file_path in service_files:
    if os.path.exists(file_path):
        print(f"✓ {os.path.basename(file_path)}: Present")
    else:
        print(f"✗ {os.path.basename(file_path)}: Missing")

# Test 3: CNG Conversion Calculator
print("\n[TEST 3] CNG Conversion Calculator")
print("-" * 60)
try:
    from services.conversion_calculator_service import conversion_calculator_service
    result = conversion_calculator_service.calculate_conversion_roi(
        'Maruti Suzuki WagonR', 
        'Mumbai', 
        1500, 
        'petrol'
    )
    monthly_savings = result['monthly_analysis']['monthly_savings']
    payback = result['conversion_options'][0]['payback_period']['months']
    verdict = result['recommendation']['verdict']
    
    print(f"✓ Service loaded successfully")
    print(f"  - Vehicle: {result['vehicle']['make']} {result['vehicle']['model']}")
    print(f"  - Monthly savings: ₹{monthly_savings:.2f}")
    print(f"  - Payback period: {payback:.1f} months")
    print(f"  - Verdict: {verdict}")
    print(f"  - Conversion kits: {len(result['conversion_options'])}")
except Exception as e:
    print(f"✗ Conversion Calculator FAILED: {e}")

# Test 4: Service Center Locator
print("\n[TEST 4] Service Center Locator")
print("-" * 60)
try:
    from services.service_center_service import service_center_service
    centers = service_center_service.get_centers_by_city('Mumbai')
    recommendations = service_center_service.recommend_centers('Mumbai', 'Sequential Kit', 50000)
    
    print(f"✓ Service loaded successfully")
    print(f"  - Centers in Mumbai: {len(centers)}")
    print(f"  - Recommendations: {len(recommendations)}")
    if recommendations:
        print(f"  - Top recommendation: {recommendations[0]['name']}")
        print(f"  - Match score: {recommendations[0]['score']:.1f}%")
except Exception as e:
    print(f"✗ Service Center Locator FAILED: {e}")

# Test 5: Vehicle Data Validation
print("\n[TEST 5] Vehicle Data Structure")
print("-" * 60)
try:
    with open('data/vehicle_database.json', 'r', encoding='utf-8') as f:
        vehicle_data = json.load(f)
    
    # Check vehicles
    vehicles = vehicle_data.get('vehicles', [])
    print(f"✓ Total vehicles: {len(vehicles)}")
    
    # Check first vehicle structure
    if vehicles:
        v = vehicles[0]
        required_fields = ['make', 'model', 'year', 'petrol_efficiency', 'cng_efficiency']
        missing = [f for f in required_fields if f not in v]
        if missing:
            print(f"✗ Missing fields: {missing}")
        else:
            print(f"✓ Vehicle structure: Valid")
    
    # Check fuel prices
    fuel_prices = vehicle_data.get('fuel_prices', {})
    cities = list(fuel_prices.keys())
    print(f"✓ Cities with fuel prices: {len(cities)}")
    
    # Check first city fuel prices
    if cities:
        city_data = fuel_prices[cities[0]]
        required_fuels = ['cng', 'petrol', 'diesel']
        missing_fuels = [f for f in required_fuels if f not in city_data]
        if missing_fuels:
            print(f"✗ Missing fuel types: {missing_fuels}")
        else:
            print(f"✓ Fuel price keys: Lowercase (correct)")
    
    # Check conversion kits
    kits = vehicle_data.get('cng_conversion_kits', [])
    print(f"✓ Conversion kits available: {len(kits)}")
    if kits:
        for kit in kits:
            print(f"  - {kit['type']}: ₹{kit['price']:,}")
    
except Exception as e:
    print(f"✗ Vehicle Data Validation FAILED: {e}")

# Test 6: CNG Stations Data
print("\n[TEST 6] CNG Stations Data")
print("-" * 60)
try:
    with open('data/cng_stations.json', 'r', encoding='utf-8') as f:
        stations = json.load(f)
    
    print(f"✓ Total stations: {len(stations)}")
    
    # Group by city
    cities = {}
    for station in stations:
        city = station.get('city', 'Unknown')
        cities[city] = cities.get(city, 0) + 1
    
    print(f"✓ Cities covered: {len(cities)}")
    for city, count in sorted(cities.items()):
        print(f"  - {city}: {count} stations")
    
except Exception as e:
    print(f"✗ CNG Stations Data FAILED: {e}")

# Test 7: Tips & Recommendations
print("\n[TEST 7] Tips & Recommendations")
print("-" * 60)
try:
    with open('data/tips_recommendations.json', 'r', encoding='utf-8') as f:
        tips = json.load(f)
    
    print(f"✓ Driving tips: {len(tips.get('driving_tips', []))}")
    print(f"✓ CNG facts: {len(tips.get('cng_facts', []))}")
    print(f"✓ Common issues: {len(tips.get('common_issues', []))}")
    print(f"✓ Myths vs facts: {len(tips.get('myths_vs_facts', []))}")
    
    if tips.get('driving_tips'):
        tip = tips['driving_tips'][0]
        print(f"  Sample tip: \"{tip['title']}\"")
    
except Exception as e:
    print(f"✗ Tips & Recommendations FAILED: {e}")

# Test 8: Routes Database
print("\n[TEST 8] Routes Database")
print("-" * 60)
try:
    with open('data/routes_database.json', 'r', encoding='utf-8') as f:
        routes = json.load(f)
    
    print(f"✓ Total routes: {len(routes)}")
    
    if routes:
        route = routes[0]
        print(f"  Sample route: {route['origin']} → {route['destination']}")
        print(f"  Distance: {route['distance']} km")
        print(f"  CNG stations on route: {len(route['cng_stations_on_route'])}")
    
except Exception as e:
    print(f"✗ Routes Database FAILED: {e}")

# Test 9: Template Files
print("\n[TEST 9] Template Files")
print("-" * 60)
templates = [
    'templates/dashboard.html',
    'templates/conversion_calculator.html',
    'templates/vehicle_comparison.html',
    'templates/trip_calculator.html',
    'templates/maintenance_tracker.html',
    'templates/nearby_stations.html',
    'templates/route_planner.html'
]

for template in templates:
    if os.path.exists(template):
        # Check if it has content
        size = os.path.getsize(template)
        print(f"✓ {os.path.basename(template)}: {size:,} bytes")
    else:
        print(f"✗ {os.path.basename(template)}: Missing")

# Summary
print("\n" + "="*60)
print("TEST SUITE COMPLETE")
print("="*60)
print("\nAll critical features have been tested.")
print("Review any ✗ marks above for issues that need attention.")
print("\nNext steps:")
print("1. Start Flask app: python app.py")
print("2. Visit: http://localhost:5000")
print("3. Test features in browser")
print("="*60 + "\n")
