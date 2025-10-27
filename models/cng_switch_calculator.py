"""
CNG Switch Calculator Model
Calculates the financial and environmental benefits of switching from petrol/diesel to CNG
"""

import numpy as np
from typing import Dict, Any
from datetime import datetime, timedelta


class CNGSwitchCalculator:
    """Calculate cost savings and ROI for switching to CNG"""
    
    # Current average fuel prices in India (INR per liter/kg)
    PETROL_PRICE = 105.0  # INR per liter
    DIESEL_PRICE = 92.0   # INR per liter
    CNG_PRICE = 75.0      # INR per kg
    
    # Average mileage (km per unit)
    PETROL_MILEAGE = 15.0  # km per liter
    DIESEL_MILEAGE = 20.0  # km per liter
    CNG_MILEAGE = 25.0     # km per kg
    
    # Conversion kit costs (INR)
    CONVERSION_COSTS = {
        'hatchback': 40000,
        'sedan': 50000,
        'suv': 65000,
        'commercial': 80000
    }
    
    # Maintenance costs (annual, INR)
    MAINTENANCE_COSTS = {
        'petrol': 15000,
        'diesel': 18000,
        'cng': 12000
    }
    
    # Emission factors (kg CO2 per unit)
    EMISSION_FACTORS = {
        'petrol': 2.31,  # kg CO2 per liter
        'diesel': 2.68,  # kg CO2 per liter
        'cng': 1.86      # kg CO2 per kg
    }
    
    def __init__(self):
        """Initialize the CNG switch calculator"""
        pass
    
    def calculate_savings(self, 
                         vehicle_type: str,
                         current_fuel: str,
                         daily_km: float,
                         current_mileage: float = None) -> Dict[str, Any]:
        """
        Calculate comprehensive savings analysis
        
        Args:
            vehicle_type: Type of vehicle (hatchback, sedan, suv, commercial)
            current_fuel: Current fuel type (petrol, diesel)
            daily_km: Average daily kilometers driven
            current_mileage: Current vehicle mileage (optional)
        
        Returns:
            Dictionary with detailed savings analysis
        """
        # Use default mileage if not provided
        if current_mileage is None:
            current_mileage = self.PETROL_MILEAGE if current_fuel == 'petrol' else self.DIESEL_MILEAGE
        
        # Calculate annual distance
        annual_km = daily_km * 365
        
        # Current fuel costs
        current_fuel_price = self.PETROL_PRICE if current_fuel == 'petrol' else self.DIESEL_PRICE
        current_annual_fuel_cost = (annual_km / current_mileage) * current_fuel_price
        
        # CNG fuel costs
        cng_annual_fuel_cost = (annual_km / self.CNG_MILEAGE) * self.CNG_PRICE
        
        # Maintenance costs
        current_maintenance = self.MAINTENANCE_COSTS.get(current_fuel, 15000)
        cng_maintenance = self.MAINTENANCE_COSTS['cng']
        
        # Total annual costs
        current_annual_total = current_annual_fuel_cost + current_maintenance
        cng_annual_total = cng_annual_fuel_cost + cng_maintenance
        
        # Annual savings
        annual_fuel_savings = current_annual_fuel_cost - cng_annual_fuel_cost
        annual_maintenance_savings = current_maintenance - cng_maintenance
        total_annual_savings = annual_fuel_savings + annual_maintenance_savings
        
        # Conversion cost and ROI
        conversion_cost = self.CONVERSION_COSTS.get(vehicle_type, 50000)
        
        # Calculate payback period (months)
        if total_annual_savings > 0:
            payback_months = (conversion_cost / total_annual_savings) * 12
        else:
            payback_months = float('inf')
        
        # 5-year savings
        five_year_savings = (total_annual_savings * 5) - conversion_cost
        
        # Environmental impact
        current_emissions = self._calculate_emissions(annual_km, current_fuel, current_mileage)
        cng_emissions = self._calculate_emissions(annual_km, 'cng', self.CNG_MILEAGE)
        emissions_reduction = current_emissions - cng_emissions
        trees_equivalent = emissions_reduction / 21.77  # One tree absorbs ~21.77 kg CO2/year
        
        return {
            'current_costs': {
                'fuel': round(current_annual_fuel_cost, 2),
                'maintenance': round(current_maintenance, 2),
                'total': round(current_annual_total, 2)
            },
            'cng_costs': {
                'fuel': round(cng_annual_fuel_cost, 2),
                'maintenance': round(cng_maintenance, 2),
                'total': round(cng_annual_total, 2),
                'conversion': round(conversion_cost, 2)
            },
            'savings': {
                'annual_fuel': round(annual_fuel_savings, 2),
                'annual_maintenance': round(annual_maintenance_savings, 2),
                'total_annual': round(total_annual_savings, 2),
                'monthly': round(total_annual_savings / 12, 2),
                'five_year': round(five_year_savings, 2)
            },
            'roi': {
                'conversion_cost': round(conversion_cost, 2),
                'payback_months': round(payback_months, 2) if payback_months != float('inf') else 0,
                'payback_years': round(payback_months / 12, 2) if payback_months != float('inf') else 0,
                'roi_percentage': round((five_year_savings / conversion_cost) * 100, 2) if conversion_cost > 0 else 0
            },
            'environmental': {
                'current_emissions_kg': round(current_emissions, 2),
                'cng_emissions_kg': round(cng_emissions, 2),
                'annual_reduction_kg': round(emissions_reduction, 2),
                'five_year_reduction_kg': round(emissions_reduction * 5, 2),
                'trees_equivalent': round(trees_equivalent, 2),
                'reduction_percentage': round((emissions_reduction / current_emissions) * 100, 2) if current_emissions > 0 else 0
            },
            'recommendation': self._get_recommendation(payback_months, five_year_savings, emissions_reduction),
            'monthly_breakdown': self._calculate_monthly_breakdown(
                total_annual_savings, conversion_cost, 60
            )
        }
    
    def _calculate_emissions(self, annual_km: float, fuel_type: str, mileage: float) -> float:
        """Calculate annual CO2 emissions"""
        fuel_consumed = annual_km / mileage
        emission_factor = self.EMISSION_FACTORS.get(fuel_type, 2.0)
        return fuel_consumed * emission_factor
    
    def _get_recommendation(self, payback_months: float, five_year_savings: float, 
                           emissions_reduction: float) -> Dict[str, Any]:
        """Generate recommendation based on analysis"""
        if payback_months == float('inf') or payback_months <= 0:
            return {
                'recommended': False,
                'rating': 1,
                'message': 'Not recommended - savings insufficient to justify conversion',
                'reasons': ['Low savings potential', 'Long payback period']
            }
        
        score = 0
        reasons = []
        
        # Financial factors
        if payback_months <= 12:
            score += 3
            reasons.append('Excellent payback period (< 1 year)')
        elif payback_months <= 24:
            score += 2
            reasons.append('Good payback period (< 2 years)')
        elif payback_months <= 36:
            score += 1
            reasons.append('Reasonable payback period (< 3 years)')
        
        if five_year_savings > 100000:
            score += 2
            reasons.append(f'High 5-year savings (₹{five_year_savings:,.0f})')
        elif five_year_savings > 50000:
            score += 1
            reasons.append(f'Good 5-year savings (₹{five_year_savings:,.0f})')
        
        # Environmental factors
        if emissions_reduction > 1000:
            score += 1
            reasons.append(f'Significant emission reduction ({emissions_reduction:.0f} kg CO2/year)')
        
        # Rating (1-5 stars)
        rating = min(5, max(1, score))
        
        if rating >= 4:
            recommended = True
            message = 'Highly recommended - Excellent financial and environmental benefits'
        elif rating >= 3:
            recommended = True
            message = 'Recommended - Good overall benefits'
        elif rating >= 2:
            recommended = True
            message = 'Consider switching - Moderate benefits'
        else:
            recommended = False
            message = 'Not strongly recommended - Limited benefits'
        
        return {
            'recommended': recommended,
            'rating': rating,
            'message': message,
            'reasons': reasons
        }
    
    def _calculate_monthly_breakdown(self, annual_savings: float, 
                                     conversion_cost: float, months: int) -> list:
        """Calculate month-by-month cumulative savings"""
        monthly_savings = annual_savings / 12
        breakdown = []
        cumulative = -conversion_cost  # Start with negative (investment)
        
        for month in range(1, months + 1):
            cumulative += monthly_savings
            breakdown.append({
                'month': month,
                'monthly_saving': round(monthly_savings, 2),
                'cumulative_saving': round(cumulative, 2),
                'breakeven': cumulative >= 0
            })
        
        return breakdown
    
    def compare_scenarios(self, base_params: Dict[str, Any]) -> Dict[str, Any]:
        """Compare different usage scenarios"""
        scenarios = {
            'conservative': {'daily_km': base_params['daily_km'] * 0.7},
            'current': {'daily_km': base_params['daily_km']},
            'increased': {'daily_km': base_params['daily_km'] * 1.3}
        }
        
        results = {}
        for scenario_name, params in scenarios.items():
            scenario_params = {**base_params, **params}
            results[scenario_name] = self.calculate_savings(**scenario_params)
        
        return results
    
    def get_fuel_prices(self) -> Dict[str, float]:
        """Get current fuel prices"""
        return {
            'petrol': self.PETROL_PRICE,
            'diesel': self.DIESEL_PRICE,
            'cng': self.CNG_PRICE
        }
    
    def get_vehicle_types(self) -> Dict[str, Any]:
        """Get available vehicle types with conversion costs"""
        return {
            vtype: {
                'name': vtype.title(),
                'conversion_cost': cost,
                'typical_usage_km': {
                    'hatchback': 30,
                    'sedan': 40,
                    'suv': 50,
                    'commercial': 100
                }.get(vtype, 40)
            }
            for vtype, cost in self.CONVERSION_COSTS.items()
        }
