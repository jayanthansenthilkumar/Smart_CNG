"""
User Analytics Model
Tracks and analyzes user behavior, charging patterns, and environmental impact
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List
import random


class UserAnalytics:
    """Analyze user charging patterns and provide insights"""
    
    def __init__(self):
        """Initialize analytics with sample data"""
        self.sample_data = self._generate_sample_data()
    
    def _generate_sample_data(self, days: int = 90) -> List[Dict[str, Any]]:
        """Generate realistic sample charging data for demonstration"""
        data = []
        current_date = datetime.now()
        for i in range(days):
            date = current_date - timedelta(days=days - i)
            day_of_week = date.weekday()
            is_weekend = day_of_week >= 5
            num_charges = random.randint(0, 1) if is_weekend else random.randint(1, 2)
            
            for charge_num in range(num_charges):
                if charge_num == 0:
                    hour = random.randint(7, 9)
                else:
                    hour = random.randint(17, 20)
                
                charge_time = date.replace(hour=hour, minute=random.randint(0, 59))
                
                charge_amount = round(random.uniform(3.0, 12.0), 2)
                
                # Calculate costs
                cost_per_kg = 75.0
                total_cost = round(charge_amount * cost_per_kg, 2)
                
                # Station types
                station_types = ['Market', 'Highway', 'Office', 'Residential']
                station_weights = [0.4, 0.2, 0.3, 0.1]
                
                # Wait times (minutes) - varies by time
                if 7 <= hour <= 9 or 17 <= hour <= 20:
                    wait_time = random.randint(5, 20)  # Peak hours
                else:
                    wait_time = random.randint(2, 8)   # Off-peak
                
                # Distance traveled since last charge (km)
                distance = round(charge_amount * random.uniform(22, 28), 2)  # CNG efficiency
                
                data.append({
                    'timestamp': charge_time.isoformat(),
                    'date': date.date().isoformat(),
                    'day_of_week': day_of_week,
                    'hour': hour,
                    'is_weekend': is_weekend,
                    'charge_amount_kg': charge_amount,
                    'cost': total_cost,
                    'wait_time_minutes': wait_time,
                    'station_type': random.choices(station_types, weights=station_weights)[0],
                    'distance_km': distance,
                    'efficiency_km_per_kg': round(distance / charge_amount, 2) if charge_amount > 0 else 0
                })
        
        return data
    
    def get_overview_stats(self, username: str = "User") -> Dict[str, Any]:
        """Get comprehensive overview statistics"""
        if not self.sample_data:
            return self._empty_stats()
        
        total_charges = len(self.sample_data)
        total_amount = sum(d['charge_amount_kg'] for d in self.sample_data)
        total_cost = sum(d['cost'] for d in self.sample_data)
        total_distance = sum(d['distance_km'] for d in self.sample_data)
        avg_wait_time = np.mean([d['wait_time_minutes'] for d in self.sample_data])
        
        # Calculate CO2 savings compared to petrol
        petrol_emissions = total_distance * 0.154  # kg CO2 per km for petrol
        cng_emissions = total_amount * 1.86        # kg CO2 per kg CNG
        co2_saved = petrol_emissions - cng_emissions
        
        # Calculate cost savings vs petrol
        petrol_cost = total_distance * (105 / 15)  # Petrol price per km
        savings = petrol_cost - total_cost
        
        # Time periods
        days_active = (datetime.now() - datetime.fromisoformat(self.sample_data[0]['timestamp'])).days + 1
        
        return {
            'username': username,
            'period_days': days_active,
            'total_charges': total_charges,
            'total_cng_kg': round(total_amount, 2),
            'total_cost': round(total_cost, 2),
            'total_distance_km': round(total_distance, 2),
            'avg_charge_amount': round(total_amount / total_charges, 2) if total_charges > 0 else 0,
            'avg_cost_per_charge': round(total_cost / total_charges, 2) if total_charges > 0 else 0,
            'avg_wait_time': round(avg_wait_time, 2),
            'environmental_impact': {
                'co2_saved_kg': round(co2_saved, 2),
                'trees_equivalent': round(co2_saved / 21.77, 2),
                'petrol_liters_saved': round(total_distance / 15, 2)
            },
            'financial_savings': {
                'vs_petrol': round(savings, 2),
                'savings_percentage': round((savings / petrol_cost) * 100, 2) if petrol_cost > 0 else 0
            }
        }
    
    def get_usage_patterns(self) -> Dict[str, Any]:
        """Analyze usage patterns"""
        if not self.sample_data:
            return {}
        
        # Daily pattern
        hourly_charges = [0] * 24
        for record in self.sample_data:
            hourly_charges[record['hour']] += 1
        
        # Weekly pattern
        daily_charges = [0] * 7
        daily_amounts = [0.0] * 7
        for record in self.sample_data:
            dow = record['day_of_week']
            daily_charges[dow] += 1
            daily_amounts[dow] += record['charge_amount_kg']
        
        # Peak hours
        peak_hour = hourly_charges.index(max(hourly_charges))
        
        # Preferred stations
        station_counts = {}
        for record in self.sample_data:
            station_type = record['station_type']
            station_counts[station_type] = station_counts.get(station_type, 0) + 1
        
        return {
            'hourly_distribution': hourly_charges,
            'daily_distribution': daily_charges,
            'daily_amounts': [round(a, 2) for a in daily_amounts],
            'peak_hour': peak_hour,
            'peak_day': daily_charges.index(max(daily_charges)),
            'preferred_stations': dict(sorted(station_counts.items(), key=lambda x: x[1], reverse=True)),
            'weekday_vs_weekend': {
                'weekday_charges': sum(1 for d in self.sample_data if not d['is_weekend']),
                'weekend_charges': sum(1 for d in self.sample_data if d['is_weekend']),
                'weekday_avg_amount': round(np.mean([d['charge_amount_kg'] for d in self.sample_data if not d['is_weekend']]), 2),
                'weekend_avg_amount': round(np.mean([d['charge_amount_kg'] for d in self.sample_data if d['is_weekend']]), 2)
            }
        }
    
    def get_efficiency_analysis(self) -> Dict[str, Any]:
        """Analyze fuel efficiency"""
        if not self.sample_data:
            return {}
        
        efficiencies = [d['efficiency_km_per_kg'] for d in self.sample_data if d['efficiency_km_per_kg'] > 0]
        
        if not efficiencies:
            return {}
        
        # Calculate trends
        recent_30 = [d['efficiency_km_per_kg'] for d in self.sample_data[-30:] if d['efficiency_km_per_kg'] > 0]
        previous_30 = [d['efficiency_km_per_kg'] for d in self.sample_data[-60:-30] if d['efficiency_km_per_kg'] > 0]
        
        recent_avg = np.mean(recent_30) if recent_30 else 0
        previous_avg = np.mean(previous_30) if previous_30 else 0
        trend = 'improving' if recent_avg > previous_avg else 'declining' if recent_avg < previous_avg else 'stable'
        
        return {
            'average_efficiency': round(np.mean(efficiencies), 2),
            'best_efficiency': round(max(efficiencies), 2),
            'worst_efficiency': round(min(efficiencies), 2),
            'std_deviation': round(np.std(efficiencies), 2),
            'recent_30_days_avg': round(recent_avg, 2),
            'previous_30_days_avg': round(previous_avg, 2),
            'trend': trend,
            'trend_percentage': round(((recent_avg - previous_avg) / previous_avg) * 100, 2) if previous_avg > 0 else 0
        }
    
    def get_cost_analysis(self) -> Dict[str, Any]:
        """Analyze spending patterns"""
        if not self.sample_data:
            return {}
        
        # Monthly breakdown
        monthly_data = {}
        for record in self.sample_data:
            date = datetime.fromisoformat(record['timestamp'])
            month_key = date.strftime('%Y-%m')
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {'cost': 0, 'amount': 0, 'count': 0}
            
            monthly_data[month_key]['cost'] += record['cost']
            monthly_data[month_key]['amount'] += record['charge_amount_kg']
            monthly_data[month_key]['count'] += 1
        
        # Sort by month
        sorted_months = sorted(monthly_data.keys())
        
        monthly_breakdown = []
        for month in sorted_months:
            data = monthly_data[month]
            monthly_breakdown.append({
                'month': month,
                'total_cost': round(data['cost'], 2),
                'total_amount_kg': round(data['amount'], 2),
                'num_charges': data['count'],
                'avg_cost_per_charge': round(data['cost'] / data['count'], 2) if data['count'] > 0 else 0
            })
        
        # Total and averages
        total_cost = sum(d['cost'] for d in self.sample_data)
        avg_monthly = total_cost / len(monthly_breakdown) if monthly_breakdown else 0
        
        return {
            'total_spent': round(total_cost, 2),
            'average_monthly': round(avg_monthly, 2),
            'monthly_breakdown': monthly_breakdown,
            'highest_month': max(monthly_breakdown, key=lambda x: x['total_cost']) if monthly_breakdown else None,
            'lowest_month': min(monthly_breakdown, key=lambda x: x['total_cost']) if monthly_breakdown else None
        }
    
    def get_wait_time_analysis(self) -> Dict[str, Any]:
        """Analyze wait time patterns"""
        if not self.sample_data:
            return {}
        
        wait_times = [d['wait_time_minutes'] for d in self.sample_data]
        
        # By hour
        hourly_waits = {}
        for record in self.sample_data:
            hour = record['hour']
            if hour not in hourly_waits:
                hourly_waits[hour] = []
            hourly_waits[hour].append(record['wait_time_minutes'])
        
        hourly_avg = {hour: round(np.mean(times), 2) for hour, times in hourly_waits.items()}
        
        # By station type
        station_waits = {}
        for record in self.sample_data:
            stype = record['station_type']
            if stype not in station_waits:
                station_waits[stype] = []
            station_waits[stype].append(record['wait_time_minutes'])
        
        station_avg = {stype: round(np.mean(times), 2) for stype, times in station_waits.items()}
        
        return {
            'average_wait_time': round(np.mean(wait_times), 2),
            'min_wait_time': round(min(wait_times), 2),
            'max_wait_time': round(max(wait_times), 2),
            'hourly_average': hourly_avg,
            'by_station_type': station_avg,
            'peak_wait_hours': [hour for hour, avg in hourly_avg.items() if avg > np.mean(list(hourly_avg.values()))]
        }
    
    def get_recommendations(self) -> List[Dict[str, str]]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Analyze patterns
        patterns = self.get_usage_patterns()
        efficiency = self.get_efficiency_analysis()
        wait_analysis = self.get_wait_time_analysis()
        
        if patterns:
            # Peak hour recommendation
            peak_hour = patterns.get('peak_hour', 0)
            if 7 <= peak_hour <= 9 or 17 <= peak_hour <= 20:
                recommendations.append({
                    'type': 'timing',
                    'icon': 'clock',
                    'title': 'Optimize Charging Times',
                    'message': f'You often charge during peak hours ({peak_hour}:00). Consider charging during off-peak times (10 AM - 4 PM) to reduce wait times.'
                })
        
        if efficiency:
            # Efficiency trend
            if efficiency.get('trend') == 'declining':
                recommendations.append({
                    'type': 'efficiency',
                    'icon': 'chart-line',
                    'title': 'Efficiency Declining',
                    'message': f'Your fuel efficiency has decreased by {abs(efficiency.get("trend_percentage", 0)):.1f}% recently. Consider vehicle maintenance or driving habit adjustments.'
                })
            elif efficiency.get('trend') == 'improving':
                recommendations.append({
                    'type': 'efficiency',
                    'icon': 'trophy',
                    'title': 'Great Progress!',
                    'message': f'Your fuel efficiency improved by {efficiency.get("trend_percentage", 0):.1f}%! Keep up the good driving habits.'
                })
        
        if wait_analysis:
            # Wait time optimization
            avg_wait = wait_analysis.get('average_wait_time', 0)
            if avg_wait > 10:
                recommendations.append({
                    'type': 'wait_time',
                    'icon': 'hourglass',
                    'title': 'Reduce Wait Times',
                    'message': f'Your average wait time is {avg_wait:.0f} minutes. Try using our route planner to find less crowded stations.'
                })
        
        # Environmental achievement
        stats = self.get_overview_stats()
        co2_saved = stats.get('environmental_impact', {}).get('co2_saved_kg', 0)
        if co2_saved > 100:
            recommendations.append({
                'type': 'environmental',
                'icon': 'leaf',
                'title': 'Environmental Champion!',
                'message': f'You\'ve saved {co2_saved:.0f} kg of CO2 emissions! That\'s equivalent to {stats.get("environmental_impact", {}).get("trees_equivalent", 0):.1f} trees.'
            })
        
        return recommendations
    
    def _empty_stats(self) -> Dict[str, Any]:
        """Return empty stats structure"""
        return {
            'username': 'User',
            'period_days': 0,
            'total_charges': 0,
            'total_cng_kg': 0,
            'total_cost': 0,
            'total_distance_km': 0,
            'avg_charge_amount': 0,
            'avg_cost_per_charge': 0,
            'avg_wait_time': 0,
            'environmental_impact': {
                'co2_saved_kg': 0,
                'trees_equivalent': 0,
                'petrol_liters_saved': 0
            },
            'financial_savings': {
                'vs_petrol': 0,
                'savings_percentage': 0
            }
        }
    
    def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent charging activity"""
        if not self.sample_data:
            return []
        
        recent = sorted(self.sample_data, key=lambda x: x['timestamp'], reverse=True)[:limit]
        
        return [
            {
                'date': r['timestamp'],
                'amount_kg': r['charge_amount_kg'],
                'cost': r['cost'],
                'station_type': r['station_type'],
                'wait_time': r['wait_time_minutes'],
                'efficiency': r['efficiency_km_per_kg']
            }
            for r in recent
        ]
