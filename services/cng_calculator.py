from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

class CNGCalculator:
    def __init__(self, fuel_prices: Dict[str, float]):
        self.fuel_prices = fuel_prices
        
    def calculate_conversion_cost(self, vehicle_type: str, kit_type: str = "standard") -> float:
        """Calculate the total cost of CNG conversion"""
        from models.cng_calculator import CNGConversionCost
        
        conversion_cost = CNGConversionCost.query.filter_by(
            vehicle_type=vehicle_type,
            kit_type=kit_type
        ).first()
        
        if not conversion_cost:
            raise ValueError(f"No conversion cost data found for {vehicle_type}")
            
        return conversion_cost.base_cost + conversion_cost.labor_cost
    
    def calculate_monthly_savings(
        self,
        monthly_distance: float,
        current_mileage: float,
        current_fuel_type: str,
        cng_mileage: Optional[float] = None
    ) -> Tuple[float, float, float]:
        """
        Calculate monthly fuel cost savings after CNG conversion
        
        Args:
            monthly_distance: Distance traveled per month in km
            current_mileage: Current vehicle mileage in km/L
            current_fuel_type: Current fuel type ('petrol' or 'diesel')
            cng_mileage: CNG mileage in km/kg (if None, will be estimated)
            
        Returns:
            Tuple of (monthly_savings, current_fuel_cost, cng_fuel_cost)
        """
        if current_fuel_type not in ['petrol', 'diesel']:
            raise ValueError("Current fuel type must be 'petrol' or 'diesel'")
            
        # Calculate current fuel consumption and cost
        monthly_fuel_consumption = monthly_distance / current_mileage
        current_fuel_cost = monthly_fuel_consumption * self.fuel_prices[current_fuel_type]
        
        # Estimate CNG mileage if not provided (typically 1.5x petrol mileage)
        if cng_mileage is None:
            cng_mileage = current_mileage * 1.5
            
        # Calculate CNG consumption and cost
        monthly_cng_consumption = monthly_distance / cng_mileage
        cng_fuel_cost = monthly_cng_consumption * self.fuel_prices['cng']
        
        monthly_savings = current_fuel_cost - cng_fuel_cost
        
        return monthly_savings, current_fuel_cost, cng_fuel_cost
    
    def calculate_roi_period(
        self,
        conversion_cost: float,
        monthly_savings: float
    ) -> Tuple[int, float]:
        """
        Calculate the Return on Investment (ROI) period in months
        
        Returns:
            Tuple of (months_to_roi, roi_percentage)
        """
        if monthly_savings <= 0:
            raise ValueError("Monthly savings must be positive for ROI calculation")
            
        months_to_roi = conversion_cost / monthly_savings
        # Calculate 1-year ROI percentage
        annual_savings = monthly_savings * 12
        roi_percentage = (annual_savings - conversion_cost) / conversion_cost * 100
        
        return round(months_to_roi), roi_percentage
    
    def calculate_environmental_impact(
        self,
        monthly_distance: float,
        current_fuel_type: str
    ) -> Dict[str, float]:
        """
        Calculate the environmental impact of switching to CNG
        
        Returns:
            Dictionary containing CO2 reduction and other environmental metrics
        """
        # CO2 emissions in kg/L or kg/kg
        emissions = {
            'petrol': 2.31,  # kg CO2 per liter
            'diesel': 2.68,  # kg CO2 per liter
            'cng': 1.96,     # kg CO2 per kg
        }
        
        # Calculate current emissions
        current_emissions = monthly_distance * emissions[current_fuel_type]
        cng_emissions = monthly_distance * emissions['cng']
        
        # Calculate reductions
        co2_reduction = current_emissions - cng_emissions
        trees_equivalent = co2_reduction * 0.027  # One tree absorbs ~27kg CO2 per year
        
        return {
            'monthly_co2_reduction': co2_reduction,
            'annual_co2_reduction': co2_reduction * 12,
            'trees_equivalent': trees_equivalent,
            'percent_reduction': (co2_reduction / current_emissions) * 100
        }
    
    def generate_savings_report(
        self,
        vehicle_type: str,
        monthly_distance: float,
        current_mileage: float,
        current_fuel_type: str,
        kit_type: str = "standard"
    ) -> Dict:
        """
        Generate a comprehensive savings and impact report
        """
        # Calculate all metrics
        conversion_cost = self.calculate_conversion_cost(vehicle_type, kit_type)
        monthly_savings, current_cost, cng_cost = self.calculate_monthly_savings(
            monthly_distance, current_mileage, current_fuel_type
        )
        months_to_roi, roi_percentage = self.calculate_roi_period(
            conversion_cost, monthly_savings
        )
        environmental_impact = self.calculate_environmental_impact(
            monthly_distance, current_fuel_type
        )
        
        # Calculate 5-year projections
        five_year_savings = monthly_savings * 60 - conversion_cost
        
        return {
            'conversion': {
                'cost': conversion_cost,
                'kit_type': kit_type,
                'warranty_period': 12  # months, typical warranty period
            },
            'monthly': {
                'current_fuel_cost': current_cost,
                'cng_fuel_cost': cng_cost,
                'savings': monthly_savings
            },
            'roi': {
                'months_to_breakeven': months_to_roi,
                'annual_roi_percentage': roi_percentage,
                'five_year_savings': five_year_savings
            },
            'environmental': environmental_impact,
            'assumptions': {
                'fuel_prices': self.fuel_prices,
                'monthly_distance': monthly_distance,
                'current_mileage': current_mileage
            }
        }