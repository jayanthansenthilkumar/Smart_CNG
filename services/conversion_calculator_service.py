"""
CNG Conversion Calculator Service
Helps users decide if CNG conversion is worth it with detailed ROI analysis
"""

import json
import os
from datetime import datetime, timedelta

class ConversionCalculatorService:
    def __init__(self):
        self.load_vehicle_data()
    
    def load_vehicle_data(self):
        """Load vehicle and fuel data from JSON"""
        try:
            with open('data/vehicle_database.json', 'r') as f:
                data = json.load(f)
                self.vehicles = data.get('vehicles', [])
                self.fuel_prices = data.get('fuel_prices', {})
                self.conversion_kits = data.get('cng_conversion_kits', [])
        except Exception as e:
            print(f"Error loading vehicle data: {e}")
            self.vehicles = []
            self.fuel_prices = {}
            self.conversion_kits = []
    
    def calculate_conversion_roi(self, vehicle_model, city, monthly_km, current_fuel_type='petrol'):
        """
        Calculate comprehensive ROI for CNG conversion
        
        Args:
            vehicle_model: Name of the vehicle model
            city: City for fuel prices
            monthly_km: Monthly kilometers driven
            current_fuel_type: Current fuel type (petrol/diesel)
        
        Returns:
            dict: Detailed ROI analysis
        """
        
        # Find vehicle data
        vehicle = self._find_vehicle(vehicle_model)
        if not vehicle:
            return {'error': 'Vehicle not found'}
        
        # Get fuel prices
        cng_price = self._get_fuel_price('cng', city)
        current_fuel_price = self._get_fuel_price(current_fuel_type, city)
        
        if not cng_price or not current_fuel_price:
            return {'error': 'Fuel prices not available for this city'}
        
        # Get vehicle efficiencies
        current_efficiency = vehicle.get(f'{current_fuel_type}_efficiency', 15)
        cng_efficiency = vehicle.get('cng_efficiency', 20)
        
        # Calculate monthly costs
        current_monthly_cost = (monthly_km / current_efficiency) * current_fuel_price
        cng_monthly_cost = (monthly_km / cng_efficiency) * cng_price
        monthly_savings = current_monthly_cost - cng_monthly_cost
        
        # Get conversion costs
        kit_options = self._get_kit_recommendations(vehicle)
        
        results = {
            'vehicle': {
                'make': vehicle.get('make'),
                'model': vehicle.get('model'),
                'year': vehicle.get('year'),
                'current_efficiency': current_efficiency,
                'cng_efficiency': cng_efficiency
            },
            'fuel_prices': {
                'cng': cng_price,
                current_fuel_type: current_fuel_price,
                'city': city
            },
            'monthly_analysis': {
                'distance': monthly_km,
                'current_fuel_cost': round(current_monthly_cost, 2),
                'cng_fuel_cost': round(cng_monthly_cost, 2),
                'monthly_savings': round(monthly_savings, 2),
                'savings_percentage': round((monthly_savings / current_monthly_cost) * 100, 2)
            },
            'yearly_analysis': {
                'current_fuel_cost': round(current_monthly_cost * 12, 2),
                'cng_fuel_cost': round(cng_monthly_cost * 12, 2),
                'yearly_savings': round(monthly_savings * 12, 2)
            },
            'conversion_options': [],
            'recommendation': None
        }
        
        # Calculate ROI for each kit option
        for kit in kit_options:
            kit_cost = kit.get('price', 45000)
            payback_months = kit_cost / monthly_savings if monthly_savings > 0 else 999
            payback_years = payback_months / 12
            
            # 5-year analysis
            total_savings_5y = (monthly_savings * 12 * 5) - kit_cost
            roi_5y = (total_savings_5y / kit_cost) * 100 if kit_cost > 0 else 0
            
            kit_analysis = {
                'kit_type': kit.get('type'),
                'kit_cost': kit_cost,
                'installation_included': True,
                'warranty': kit.get('warranty', '3 years / 50,000 km'),
                'payback_period': {
                    'months': round(payback_months, 1),
                    'years': round(payback_years, 2)
                },
                'roi_analysis': {
                    '1_year': {
                        'savings': round(monthly_savings * 12, 2),
                        'net_benefit': round((monthly_savings * 12) - kit_cost, 2),
                        'roi_percentage': round(((monthly_savings * 12) / kit_cost) * 100, 2)
                    },
                    '3_years': {
                        'savings': round(monthly_savings * 12 * 3, 2),
                        'net_benefit': round((monthly_savings * 12 * 3) - kit_cost, 2),
                        'roi_percentage': round(((monthly_savings * 12 * 3) / kit_cost) * 100, 2)
                    },
                    '5_years': {
                        'savings': round(monthly_savings * 12 * 5, 2),
                        'net_benefit': round(total_savings_5y, 2),
                        'roi_percentage': round(roi_5y, 2)
                    }
                },
                'pros': kit.get('pros', []),
                'cons': kit.get('cons', [])
            }
            
            results['conversion_options'].append(kit_analysis)
        
        # Generate recommendation
        results['recommendation'] = self._generate_recommendation(
            monthly_km, monthly_savings, payback_months, vehicle
        )
        
        # Additional considerations
        results['additional_considerations'] = self._get_additional_considerations(
            vehicle, monthly_km, city
        )
        
        return results
    
    def _find_vehicle(self, vehicle_model):
        """Find vehicle by model name"""
        for vehicle in self.vehicles:
            if vehicle_model.lower() in f"{vehicle.get('make', '')} {vehicle.get('model', '')}".lower():
                return vehicle
        return None
    
    def _get_fuel_price(self, fuel_type, city):
        """Get fuel price for city"""
        fuel_data = self.fuel_prices.get(fuel_type, {})
        city_prices = fuel_data.get('city_prices', {})
        return city_prices.get(city, fuel_data.get('national_avg', 0))
    
    def _get_kit_recommendations(self, vehicle):
        """Get recommended conversion kits"""
        if not self.conversion_kits:
            return [
                {
                    'type': 'Sequential Kit',
                    'price': 45000,
                    'warranty': '3 years / 50,000 km',
                    'pros': ['Best performance', 'Good efficiency'],
                    'cons': ['Higher cost']
                }
            ]
        return self.conversion_kits
    
    def _generate_recommendation(self, monthly_km, monthly_savings, payback_months, vehicle):
        """Generate conversion recommendation"""
        
        recommendation = {
            'verdict': '',
            'reason': '',
            'best_kit': '',
            'when_to_convert': '',
            'conditions': []
        }
        
        # Decision logic
        if monthly_km < 1000:
            recommendation['verdict'] = 'Not Recommended'
            recommendation['reason'] = 'Low monthly usage makes conversion uneconomical'
            recommendation['conditions'] = [
                'Consider conversion if monthly usage increases to 1500+ km',
                'Current savings would be minimal',
                'Payback period would be too long'
            ]
        elif monthly_km < 1500:
            recommendation['verdict'] = 'Consider Carefully'
            recommendation['reason'] = 'Moderate usage - conversion may work if you plan to keep vehicle long-term'
            recommendation['conditions'] = [
                'Payback period will be moderate (2-3 years)',
                'Suitable if you plan to keep vehicle for 5+ years',
                'Consider Venturi kit for lower initial cost'
            ]
            recommendation['best_kit'] = 'Venturi Kit'
        else:
            recommendation['verdict'] = 'Highly Recommended'
            recommendation['reason'] = 'High usage makes CNG conversion very economical'
            recommendation['conditions'] = [
                f'Monthly savings of ₹{round(monthly_savings, 0)}',
                f'Payback in {round(payback_months, 1)} months',
                'Significant long-term savings',
                'Environmental benefits'
            ]
            recommendation['best_kit'] = 'Sequential Kit'
        
        # Age consideration
        vehicle_year = vehicle.get('year', 2020)
        current_year = datetime.now().year
        vehicle_age = current_year - vehicle_year
        
        if vehicle_age > 8:
            recommendation['verdict'] = 'Not Recommended'
            recommendation['reason'] += ' - Vehicle is too old for conversion'
        
        return recommendation
    
    def _get_additional_considerations(self, vehicle, monthly_km, city):
        """Get additional factors to consider"""
        
        considerations = {
            'positive_factors': [],
            'negative_factors': [],
            'requirements': [],
            'maintenance': {}
        }
        
        # Positive factors
        if monthly_km >= 1500:
            considerations['positive_factors'].append('High monthly usage ensures quick ROI')
        
        considerations['positive_factors'].extend([
            f"CNG price in {city} is competitive",
            'Lower maintenance costs due to cleaner fuel',
            'Reduced carbon emissions (25-30% less CO2)',
            'Government incentives may be available',
            'Increased vehicle resale value in some markets'
        ])
        
        # Negative factors
        considerations['negative_factors'].extend([
            'Initial investment required',
            'Slight reduction in boot space',
            'Limited CNG stations compared to petrol pumps',
            'Refueling time slightly longer',
            'Power output reduced by 5-10%'
        ])
        
        # Requirements
        considerations['requirements'] = [
            'Vehicle must be in good mechanical condition',
            'Engine should have no major issues',
            'Valid registration and insurance',
            'RTO approval and RC endorsement required',
            'Choose ARAI/ICAT approved kit and installer'
        ]
        
        # Maintenance
        considerations['maintenance'] = {
            'additional_costs': '₹1,500-3,000 per year',
            'service_interval': 'Every 10,000 km or 6 months',
            'major_services': [
                'CNG filter replacement (₹500-800)',
                'Spark plug replacement (₹800-1,500)',
                'Cylinder hydrotesting every 3 years (₹1,500-3,000)'
            ],
            'savings_offset': 'Maintenance costs easily offset by fuel savings'
        }
        
        return considerations
    
    def compare_scenarios(self, vehicle_model, city, scenarios):
        """
        Compare multiple usage scenarios
        
        Args:
            vehicle_model: Vehicle model name
            city: City name
            scenarios: List of monthly km values
        
        Returns:
            dict: Comparison of different scenarios
        """
        
        comparisons = []
        
        for monthly_km in scenarios:
            result = self.calculate_conversion_roi(vehicle_model, city, monthly_km)
            if 'error' not in result:
                comparisons.append({
                    'monthly_km': monthly_km,
                    'monthly_savings': result['monthly_analysis']['monthly_savings'],
                    'yearly_savings': result['yearly_analysis']['yearly_savings'],
                    'payback_months': result['conversion_options'][0]['payback_period']['months'],
                    'verdict': result['recommendation']['verdict']
                })
        
        return {
            'vehicle': vehicle_model,
            'city': city,
            'scenarios': comparisons
        }
    
    def get_break_even_analysis(self, vehicle_model, city, kit_cost=45000):
        """Calculate break-even usage"""
        
        vehicle = self._find_vehicle(vehicle_model)
        if not vehicle:
            return {'error': 'Vehicle not found'}
        
        cng_price = self._get_fuel_price('cng', city)
        petrol_price = self._get_fuel_price('petrol', city)
        
        petrol_efficiency = vehicle.get('petrol_efficiency', 15)
        cng_efficiency = vehicle.get('cng_efficiency', 20)
        
        # Calculate savings per km
        petrol_cost_per_km = petrol_price / petrol_efficiency
        cng_cost_per_km = cng_price / cng_efficiency
        savings_per_km = petrol_cost_per_km - cng_cost_per_km
        
        # Break-even kilometers
        break_even_km = kit_cost / savings_per_km if savings_per_km > 0 else 0
        break_even_months_1000 = break_even_km / 1000  # At 1000 km/month
        break_even_months_1500 = break_even_km / 1500  # At 1500 km/month
        break_even_months_2000 = break_even_km / 2000  # At 2000 km/month
        
        return {
            'vehicle': f"{vehicle.get('make')} {vehicle.get('model')}",
            'city': city,
            'kit_cost': kit_cost,
            'savings_per_km': round(savings_per_km, 2),
            'break_even_distance': round(break_even_km, 0),
            'break_even_scenarios': {
                '1000_km_monthly': {
                    'months': round(break_even_months_1000, 1),
                    'years': round(break_even_months_1000 / 12, 2)
                },
                '1500_km_monthly': {
                    'months': round(break_even_months_1500, 1),
                    'years': round(break_even_months_1500 / 12, 2)
                },
                '2000_km_monthly': {
                    'months': round(break_even_months_2000, 1),
                    'years': round(break_even_months_2000 / 12, 2)
                }
            }
        }

# Singleton instance
conversion_calculator_service = ConversionCalculatorService()
