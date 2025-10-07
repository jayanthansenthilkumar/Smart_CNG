import json
from models.location_optimizer import LocationOptimizer
from models.wait_time_predictor import WaitTimePredictor
from models.station_calculating_model import ChargingStationCalculator

print('Testing LocationOptimizer')
lo = LocationOptimizer()
try:
    cands = lo.generate_candidate_locations(28.65, 77.2, radius_km=5, num_candidates=3)
    print('generate_candidate_locations OK, samples:')
    print(json.dumps(cands[:3], indent=2))
except Exception as e:
    print('LocationOptimizer.generate_candidate_locations ERROR:', e)

print('\nTesting WaitTimePredictor')
wt = WaitTimePredictor()
try:
    sample = [{'id':'s1','active_chargers':1,'total_chargers':2,'current_queue_length':1,'hour_of_day':10,'day_of_week':2,'is_weekend':0,'traffic_density':0.5,'historical_avg_wait_time':10.0}]
    preds = wt.predict_wait_time(sample)
    print('predict_wait_time OK:')
    print(json.dumps(preds, indent=2))
except Exception as e:
    print('WaitTimePredictor ERROR:', e)

print('\nTesting ChargingStationCalculator')
cs = ChargingStationCalculator()
try:
    route = {'distance': 10.0, 'coordinates': [[28.65,77.2],[28.66,77.21],[28.67,77.22]]}
    ev_specs = {'batteryCapacity':60,'chargingSpeed':10,'consumption':0.02,'range':320}
    stops = cs.calculate_charging_stops(route_data=route, ev_specs=ev_specs, current_charge=50, available_stations=[{'name':'S1','lat':28.655,'lng':77.205,'type':'CNG Pump','power':'50kW','active_chargers':1,'total_chargers':1}])
    print('calculate_charging_stops OK:')
    print(stops)
except Exception as e:
    print('ChargingStationCalculator ERROR:', e)
