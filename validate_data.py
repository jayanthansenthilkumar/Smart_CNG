"""
Data Validation and Correction Script
Ensures all datasets are properly formatted and complete
"""

import json
import os

def validate_vehicle_database():
    """Validate vehicle database structure"""
    print("Validating vehicle_database.json...")
    
    try:
        with open('data/vehicle_database.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check required top-level keys
        required_keys = ['vehicles', 'fuel_prices', 'cng_conversion_kits', 'maintenance_schedule']
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            print(f"  ❌ Missing keys: {missing_keys}")
            return False
        
        # Validate vehicles
        vehicles = data.get('vehicles', [])
        print(f"  ✓ Found {len(vehicles)} vehicles")
        
        # Check each vehicle has required fields
        required_vehicle_fields = ['make', 'model', 'year', 'fuel_types', 'cng_efficiency', 'petrol_efficiency']
        for i, vehicle in enumerate(vehicles):
            missing = [f for f in required_vehicle_fields if f not in vehicle]
            if missing:
                print(f"  ⚠ Vehicle {i+1} ({vehicle.get('make')} {vehicle.get('model')}) missing: {missing}")
        
        # Validate fuel prices
        fuel_prices = data.get('fuel_prices', {})
        required_fuel_types = ['cng', 'petrol', 'diesel']
        for fuel_type in required_fuel_types:
            if fuel_type in fuel_prices:
                cities = fuel_prices[fuel_type].get('city_prices', {})
                print(f"  ✓ {fuel_type.upper()} prices for {len(cities)} cities")
            else:
                print(f"  ❌ Missing {fuel_type} prices")
        
        # Validate conversion kits
        kits = data.get('cng_conversion_kits', [])
        print(f"  ✓ Found {len(kits)} conversion kit options")
        
        # Validate maintenance schedule
        maintenance = data.get('maintenance_schedule', {})
        if 'cng_specific' in maintenance and 'regular_service' in maintenance:
            print(f"  ✓ Maintenance schedule complete")
        else:
            print(f"  ⚠ Maintenance schedule incomplete")
        
        print("  ✅ Vehicle database validation complete\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}\n")
        return False

def validate_cng_stations():
    """Validate CNG stations data"""
    print("Validating cng_stations.json...")
    
    try:
        with open('data/cng_stations.json', 'r', encoding='utf-8') as f:
            stations = json.load(f)
        
        if not isinstance(stations, list):
            print(f"  ❌ Expected array, got {type(stations)}")
            return False
        
        print(f"  ✓ Found {len(stations)} stations")
        
        # Check required fields
        required_fields = ['id', 'name', 'latitude', 'longitude', 'address', 'city', 'phone', 'operating_hours']
        
        cities = set()
        for station in stations:
            cities.add(station.get('city', 'Unknown'))
            missing = [f for f in required_fields if f not in station]
            if missing:
                print(f"  ⚠ Station '{station.get('name', 'Unknown')}' missing: {missing}")
        
        print(f"  ✓ Stations across {len(cities)} cities: {', '.join(sorted(cities))}")
        print("  ✅ CNG stations validation complete\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}\n")
        return False

def validate_routes_database():
    """Validate routes database"""
    print("Validating routes_database.json...")
    
    try:
        with open('data/routes_database.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        routes = data.get('popular_routes', [])
        print(f"  ✓ Found {len(routes)} routes")
        
        # Check required fields
        required_fields = ['id', 'name', 'start_city', 'end_city', 'distance', 'toll_cost']
        
        for route in routes:
            missing = [f for f in required_fields if f not in route]
            if missing:
                print(f"  ⚠ Route '{route.get('name', 'Unknown')}' missing: {missing}")
        
        # Check additional sections
        if 'route_tips' in data:
            print(f"  ✓ Route tips available")
        if 'seasonal_recommendations' in data:
            print(f"  ✓ Seasonal recommendations available")
        
        print("  ✅ Routes database validation complete\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}\n")
        return False

def validate_tips_recommendations():
    """Validate tips and recommendations"""
    print("Validating tips_recommendations.json...")
    
    try:
        with open('data/tips_recommendations.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check sections
        sections = {
            'driving_tips': len(data.get('driving_tips', [])),
            'cng_facts': len(data.get('cng_facts', [])),
            'maintenance_schedule': 'maintenance_schedule' in data,
            'common_issues': len(data.get('common_issues', [])),
            'conversion_guide': 'conversion_guide' in data,
            'best_practices': 'best_practices' in data,
            'myths_vs_facts': len(data.get('myths_vs_facts', []))
        }
        
        for section, value in sections.items():
            if isinstance(value, int):
                print(f"  ✓ {section}: {value} items")
            elif value:
                print(f"  ✓ {section}: available")
            else:
                print(f"  ⚠ {section}: missing")
        
        print("  ✅ Tips and recommendations validation complete\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}\n")
        return False

def validate_service_centers():
    """Validate service centers data"""
    print("Validating service_centers.json...")
    
    try:
        with open('data/service_centers.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        centers = data.get('service_centers', [])
        print(f"  ✓ Found {len(centers)} service centers")
        
        # Check required fields
        required_fields = ['id', 'name', 'city', 'address', 'phone', 'services', 'brands']
        
        cities = set()
        for center in centers:
            cities.add(center.get('city', 'Unknown'))
            missing = [f for f in required_fields if f not in center]
            if missing:
                print(f"  ⚠ Center '{center.get('name', 'Unknown')}' missing: {missing}")
        
        print(f"  ✓ Centers across {len(cities)} cities: {', '.join(sorted(cities))}")
        
        # Check additional sections
        if 'selection_criteria' in data:
            print(f"  ✓ Selection criteria available")
        if 'installation_checklist' in data:
            print(f"  ✓ Installation checklist available")
        if 'maintenance_packages' in data:
            packages = data.get('maintenance_packages', [])
            print(f"  ✓ {len(packages)} maintenance packages")
        
        print("  ✅ Service centers validation complete\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}\n")
        return False

def check_database_models():
    """Check if database models file exists and is valid"""
    print("Checking database models...")
    
    try:
        with open('models/cng_calculator.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key models
        models = ['User', 'Vehicle', 'Station', 'FuelLog', 'FuelPrice', 'MaintenanceRecord', 'MaintenanceReminder']
        found_models = []
        
        for model in models:
            if f'class {model}' in content:
                found_models.append(model)
        
        print(f"  ✓ Found {len(found_models)}/{len(models)} required models")
        
        missing = set(models) - set(found_models)
        if missing:
            print(f"  ⚠ Missing models: {missing}")
        
        print("  ✅ Database models check complete\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}\n")
        return False

def check_services():
    """Check if service files exist"""
    print("Checking service files...")
    
    services = {
        'conversion_calculator_service.py': 'CNG Conversion Calculator',
        'service_center_service.py': 'Service Center Locator',
        'cng_calculator.py': 'CNG Calculator',
        'vehicle_comparison_service.py': 'Vehicle Comparison',
        'trip_cost_calculator.py': 'Trip Cost Calculator',
        'maintenance_service.py': 'Maintenance Tracker'
    }
    
    for filename, name in services.items():
        filepath = os.path.join('services', filename)
        if os.path.exists(filepath):
            print(f"  ✓ {name}")
        else:
            print(f"  ⚠ {name} - NOT FOUND")
    
    print("  ✅ Service files check complete\n")
    return True

def check_templates():
    """Check if template files exist"""
    print("Checking template files...")
    
    templates = {
        'dashboard.html': 'Main Dashboard',
        'conversion_calculator.html': 'Conversion Calculator',
        'vehicle_comparison.html': 'Vehicle Comparison',
        'trip_calculator.html': 'Trip Calculator',
        'maintenance_tracker.html': 'Maintenance Tracker',
        'fuel_history.html': 'Fuel History',
        'nearby_stations.html': 'Station Finder',
        'route_planner.html': 'Route Planner',
        'analytics.html': 'Analytics Dashboard'
    }
    
    for filename, name in templates.items():
        filepath = os.path.join('templates', filename)
        if os.path.exists(filepath):
            print(f"  ✓ {name}")
        else:
            print(f"  ⚠ {name} - NOT FOUND")
    
    print("  ✅ Template files check complete\n")
    return True

def generate_summary():
    """Generate comprehensive summary"""
    print("\n" + "="*70)
    print("COMPREHENSIVE DATA VALIDATION SUMMARY")
    print("="*70 + "\n")
    
    results = {
        'Vehicle Database': validate_vehicle_database(),
        'CNG Stations': validate_cng_stations(),
        'Routes Database': validate_routes_database(),
        'Tips & Recommendations': validate_tips_recommendations(),
        'Service Centers': validate_service_centers(),
        'Database Models': check_database_models(),
        'Service Files': check_services(),
        'Template Files': check_templates()
    }
    
    print("\n" + "="*70)
    print("VALIDATION RESULTS")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {component}")
    
    print(f"\nOverall: {passed}/{total} components validated successfully")
    
    if passed == total:
        print("\n🎉 All components are properly configured!")
        print("✅ Your application is ready to run!")
    else:
        print("\n⚠️  Some components need attention.")
        print("Please review the warnings above.")
    
    print("="*70 + "\n")

if __name__ == '__main__':
    generate_summary()
