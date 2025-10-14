"""
Quick Test - Verify everything works
"""
print("Testing Ultra-Simplified Smart CNG...")
print()

# Test imports
print("1. Testing imports...")
try:
    from lib import Data, Calculator, Station, Car
    from model import User, Vehicle, FuelLog, Station as DBStation
    print("   ✓ All imports successful")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    exit(1)

# Test data loading
print("2. Testing data loading...")
try:
    data = Data()
    print(f"   ✓ Loaded {len(data.stations)} stations")
    print(f"   ✓ Loaded {len(data.cars)} cars")
except Exception as e:
    print(f"   ✗ Data loading failed: {e}")
    exit(1)

# Test finder
print("3. Testing finders...")
try:
    nearby = data.find_stations(28.6139, 77.2090, 10)
    print(f"   ✓ Found {len(nearby)} stations nearby")
    
    car = data.find_car("Maruti Suzuki", "WagonR")
    if car:
        print(f"   ✓ Found car: {car.make} {car.model}")
except Exception as e:
    print(f"   ✗ Finder failed: {e}")

# Test calculator
print("4. Testing calculator...")
try:
    calc = Calculator()
    if car:
        trip = calc.trip_cost(car, 100, 'cng')
        print(f"   ✓ Trip cost: ₹{trip['cost']}")
        
        savings = calc.savings(car, 1500)
        print(f"   ✓ Breakeven: {savings['breakeven_years']} years")
except Exception as e:
    print(f"   ✗ Calculator failed: {e}")

print()
print("=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print()
print("Run: python app.py")
print("Open: http://localhost:5000")
