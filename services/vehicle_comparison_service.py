"""
Vehicle Comparison Service
Provides comprehensive comparison between different vehicles and fuel types
"""
from typing import Dict, List, Tuple
from models.cng_calculator import Vehicle, FuelPrice
from services.cng_calculator import CNGCalculator


class VehicleComparisonService:
    """Service for comparing fuel costs and efficiency across different vehicles"""
    
    def __init__(self, fuel_prices: Dict[str, float]):
        self.fuel_prices = fuel_prices
        self.cng_calculator = CNGCalculator(fuel_prices)
    
    def compare_vehicles(
        self,
        vehicles_data: List[Dict],
        monthly_distance: float,
        period_months: int = 12
    ) -> Dict:
        """
        Compare multiple vehicles based on fuel costs
        
        Args:
            vehicles_data: List of vehicle dicts with make, model, fuel_type, mileage
            monthly_distance: Distance traveled per month
            period_months: Comparison period in months
            
        Returns:
            Comprehensive comparison data
        """
        comparisons = []
        
        for vehicle in vehicles_data:
            fuel_type = vehicle['fuel_type']
            mileage = vehicle['mileage']
            
            # Calculate monthly fuel consumption
            monthly_consumption = monthly_distance / mileage
            monthly_cost = monthly_consumption * self.fuel_prices[fuel_type]
            
            # Calculate for period
            total_distance = monthly_distance * period_months
            total_consumption = total_distance / mileage
            total_cost = total_consumption * self.fuel_prices[fuel_type]
            
            # Calculate environmental impact
            co2_emissions = self._calculate_co2_emissions(
                fuel_type,
                monthly_distance,
                period_months
            )
            
            comparisons.append({
                'vehicle': {
                    'make': vehicle.get('make', 'Unknown'),
                    'model': vehicle.get('model', 'Unknown'),
                    'fuel_type': fuel_type,
                    'mileage': mileage
                },
                'costs': {
                    'monthly': round(monthly_cost, 2),
                    'total': round(total_cost, 2),
                    'per_km': round(monthly_cost / monthly_distance, 2)
                },
                'consumption': {
                    'monthly': round(monthly_consumption, 2),
                    'total': round(total_consumption, 2),
                    'unit': self._get_fuel_unit(fuel_type)
                },
                'environmental': {
                    'monthly_co2': round(co2_emissions['monthly'], 2),
                    'total_co2': round(co2_emissions['total'], 2),
                    'trees_equivalent': round(co2_emissions['trees'], 2)
                }
            })
        
        # Rank vehicles by cost
        comparisons.sort(key=lambda x: x['costs']['total'])
        
        # Add rankings
        for i, comp in enumerate(comparisons):
            comp['rank'] = i + 1
            comp['cost_savings_vs_highest'] = (
                comparisons[-1]['costs']['total'] - comp['costs']['total']
            )
        
        return {
            'comparisons': comparisons,
            'period_months': period_months,
            'monthly_distance': monthly_distance,
            'cheapest': comparisons[0] if comparisons else None,
            'most_expensive': comparisons[-1] if comparisons else None,
            'fuel_prices_used': self.fuel_prices
        }
    
    def compare_fuel_types_same_vehicle(
        self,
        base_vehicle: Dict,
        monthly_distance: float,
        include_conversion: bool = True
    ) -> Dict:
        """
        Compare different fuel options for the same vehicle
        Useful for deciding whether to convert to CNG
        """
        results = {
            'base_vehicle': base_vehicle,
            'monthly_distance': monthly_distance,
            'scenarios': []
        }
        
        # Current scenario
        current_fuel = base_vehicle['fuel_type']
        current_mileage = base_vehicle['mileage']
        
        current_cost = (monthly_distance / current_mileage) * self.fuel_prices[current_fuel]
        
        results['scenarios'].append({
            'scenario': 'Current',
            'fuel_type': current_fuel,
            'monthly_cost': round(current_cost, 2),
            'annual_cost': round(current_cost * 12, 2),
            'conversion_cost': 0,
            'payback_period': 0
        })
        
        # CNG conversion scenario (if not already CNG)
        if current_fuel != 'cng' and include_conversion:
            # Estimate CNG mileage (typically 1.5x petrol, 1.3x diesel)
            cng_mileage = current_mileage * (1.5 if current_fuel == 'petrol' else 1.3)
            cng_monthly_cost = (monthly_distance / cng_mileage) * self.fuel_prices['cng']
            monthly_savings = current_cost - cng_monthly_cost
            
            # Get conversion cost
            try:
                conversion_cost = self.cng_calculator.calculate_conversion_cost(
                    base_vehicle.get('type', 'sedan'),
                    'standard'
                )
            except:
                conversion_cost = 40000  # Default estimate
            
            payback_months = conversion_cost / monthly_savings if monthly_savings > 0 else float('inf')
            
            results['scenarios'].append({
                'scenario': 'CNG Conversion',
                'fuel_type': 'cng',
                'monthly_cost': round(cng_monthly_cost, 2),
                'annual_cost': round(cng_monthly_cost * 12, 2),
                'conversion_cost': round(conversion_cost, 2),
                'monthly_savings': round(monthly_savings, 2),
                'annual_savings': round(monthly_savings * 12, 2),
                'payback_period_months': round(payback_months, 1),
                'five_year_savings': round((monthly_savings * 60) - conversion_cost, 2)
            })
        
        return results
    
    def _calculate_co2_emissions(
        self,
        fuel_type: str,
        monthly_distance: float,
        months: int
    ) -> Dict:
        """Calculate CO2 emissions for a fuel type"""
        # CO2 emissions factors (kg CO2 per unit)
        emission_factors = {
            'petrol': 2.31,  # kg CO2 per liter
            'diesel': 2.68,
            'cng': 1.96,     # kg CO2 per kg
            'electric': 0.82  # kg CO2 per kWh (grid average)
        }
        
        factor = emission_factors.get(fuel_type, 2.31)
        monthly_co2 = monthly_distance * factor * 0.05  # Approximation
        total_co2 = monthly_co2 * months
        trees = total_co2 / 22  # One tree absorbs ~22kg CO2 per year
        
        return {
            'monthly': monthly_co2,
            'total': total_co2,
            'trees': trees
        }
    
    def _get_fuel_unit(self, fuel_type: str) -> str:
        """Get the unit for fuel type"""
        units = {
            'petrol': 'L',
            'diesel': 'L',
            'cng': 'kg',
            'electric': 'kWh'
        }
        return units.get(fuel_type, 'L')
    
    def get_best_vehicle_recommendation(
        self,
        monthly_distance: float,
        budget: float,
        priorities: List[str] = None
    ) -> Dict:
        """
        Recommend best vehicle/fuel type based on usage and preferences
        
        priorities: List of priorities like ['cost', 'environment', 'convenience']
        """
        if priorities is None:
            priorities = ['cost', 'environment']
        
        recommendations = []
        
        # Define typical vehicle profiles
        vehicle_profiles = [
            {
                'name': 'Economy Petrol Car',
                'fuel_type': 'petrol',
                'mileage': 18,
                'cost_factor': 1.0
            },
            {
                'name': 'Economy Diesel Car',
                'fuel_type': 'diesel',
                'mileage': 22,
                'cost_factor': 1.0
            },
            {
                'name': 'CNG Sedan',
                'fuel_type': 'cng',
                'mileage': 25,
                'cost_factor': 0.7
            },
            {
                'name': 'Electric Vehicle',
                'fuel_type': 'electric',
                'mileage': 6,  # km per kWh
                'cost_factor': 1.5
            }
        ]
        
        for profile in vehicle_profiles:
            monthly_cost = (monthly_distance / profile['mileage']) * \
                          self.fuel_prices.get(profile['fuel_type'], 100)
            
            # Calculate scores
            cost_score = 100 - (monthly_cost / 50)  # Lower cost = higher score
            env_score = 100 if profile['fuel_type'] in ['cng', 'electric'] else 70
            convenience_score = 100 if profile['fuel_type'] in ['petrol', 'diesel'] else 80
            
            # Weighted score based on priorities
            weights = {
                'cost': 0.5 if 'cost' in priorities else 0.2,
                'environment': 0.3 if 'environment' in priorities else 0.2,
                'convenience': 0.2 if 'convenience' in priorities else 0.1
            }
            
            overall_score = (
                cost_score * weights['cost'] +
                env_score * weights['environment'] +
                convenience_score * weights['convenience']
            )
            
            recommendations.append({
                'vehicle': profile['name'],
                'fuel_type': profile['fuel_type'],
                'monthly_cost': round(monthly_cost, 2),
                'annual_cost': round(monthly_cost * 12, 2),
                'scores': {
                    'overall': round(overall_score, 1),
                    'cost': round(cost_score, 1),
                    'environment': round(env_score, 1),
                    'convenience': round(convenience_score, 1)
                }
            })
        
        # Sort by overall score
        recommendations.sort(key=lambda x: x['scores']['overall'], reverse=True)
        
        return {
            'recommended': recommendations[0],
            'all_options': recommendations,
            'criteria': {
                'monthly_distance': monthly_distance,
                'budget': budget,
                'priorities': priorities
            }
        }
