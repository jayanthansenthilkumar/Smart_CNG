"""
Service Center Locator Service
Find and recommend CNG service centers for installation and maintenance
"""

import json
import os
import math

class ServiceCenterService:
    def __init__(self):
        self.load_service_centers()
    
    def load_service_centers(self):
        """Load service centers from JSON"""
        try:
            with open('data/service_centers.json', 'r') as f:
                data = json.load(f)
                self.service_centers = data.get('service_centers', [])
                self.selection_criteria = data.get('selection_criteria', [])
                self.installation_checklist = data.get('installation_checklist', {})
                self.maintenance_packages = data.get('maintenance_packages', [])
                self.cost_breakdown = data.get('cost_breakdown', {})
        except Exception as e:
            print(f"Error loading service centers: {e}")
            self.service_centers = []
            self.selection_criteria = []
            self.installation_checklist = {}
            self.maintenance_packages = []
            self.cost_breakdown = {}
    
    def find_nearby_centers(self, user_lat, user_lng, city=None, max_distance_km=50):
        """
        Find service centers near user location
        
        Args:
            user_lat: User latitude
            user_lng: User longitude
            city: Optional city filter
            max_distance_km: Maximum distance in kilometers
        
        Returns:
            list: Nearby service centers with distance
        """
        
        nearby_centers = []
        
        for center in self.service_centers:
            # City filter if specified
            if city and center.get('city', '').lower() != city.lower():
                continue
            
            # Calculate distance
            center_lat = center.get('latitude')
            center_lng = center.get('longitude')
            
            if center_lat and center_lng:
                distance = self._calculate_distance(
                    user_lat, user_lng, center_lat, center_lng
                )
                
                if distance <= max_distance_km:
                    center_copy = center.copy()
                    center_copy['distance_km'] = round(distance, 2)
                    nearby_centers.append(center_copy)
        
        # Sort by distance
        nearby_centers.sort(key=lambda x: x['distance_km'])
        
        return nearby_centers
    
    def get_centers_by_city(self, city):
        """Get all service centers in a specific city"""
        return [c for c in self.service_centers if c.get('city', '').lower() == city.lower()]
    
    def get_center_details(self, center_id):
        """Get detailed information about a specific center"""
        for center in self.service_centers:
            if center.get('id') == center_id:
                # Add additional information
                details = center.copy()
                details['selection_criteria'] = self.selection_criteria
                details['installation_checklist'] = self.installation_checklist
                return details
        return None
    
    def recommend_centers(self, city, kit_type='sequential', budget=None):
        """
        Recommend service centers based on requirements
        
        Args:
            city: City name
            kit_type: Type of kit (sequential/venturi/premium)
            budget: Maximum budget
        
        Returns:
            list: Recommended centers with reasons
        """
        
        centers = self.get_centers_by_city(city)
        recommendations = []
        
        for center in centers:
            score = 0
            reasons = []
            
            # Rating score
            rating = center.get('rating', 0)
            if rating >= 4.5:
                score += 30
                reasons.append("Excellent customer ratings (4.5+)")
            elif rating >= 4.0:
                score += 20
                reasons.append("Good customer ratings (4.0+)")
            
            # Authorization score
            authorizations = center.get('authorized_by', [])
            if 'ARAI' in authorizations or 'ICAT' in authorizations:
                score += 25
                reasons.append("ARAI/ICAT authorized - ensures quality")
            
            # Budget match
            cost_range = center.get('installation_cost_range', {}).get(kit_type, {})
            if budget and cost_range:
                min_cost = cost_range.get('min', 0)
                max_cost = cost_range.get('max', 999999)
                if min_cost <= budget <= max_cost:
                    score += 20
                    reasons.append(f"Fits your budget (₹{min_cost:,}-₹{max_cost:,})")
            
            # Warranty score
            warranty = center.get('warranty_offered', '')
            if '3 years' in warranty:
                score += 15
                reasons.append("Excellent warranty (3 years)")
            
            # Experience (number of reviews as proxy)
            total_reviews = center.get('total_reviews', 0)
            if total_reviews > 200:
                score += 10
                reasons.append("High experience (200+ reviews)")
            elif total_reviews > 100:
                score += 5
            
            recommendation = center.copy()
            recommendation['recommendation_score'] = score
            recommendation['recommendation_reasons'] = reasons
            recommendation['recommended_kit'] = kit_type
            recommendation['estimated_cost'] = cost_range
            
            recommendations.append(recommendation)
        
        # Sort by recommendation score
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return recommendations[:5]  # Return top 5
    
    def get_maintenance_packages(self):
        """Get available maintenance packages"""
        return self.maintenance_packages
    
    def compare_centers(self, center_ids):
        """
        Compare multiple service centers
        
        Args:
            center_ids: List of center IDs to compare
        
        Returns:
            dict: Comparison data
        """
        
        centers = []
        for cid in center_ids:
            center = next((c for c in self.service_centers if c.get('id') == cid), None)
            if center:
                centers.append(center)
        
        if not centers:
            return {'error': 'No centers found'}
        
        comparison = {
            'centers': [],
            'comparison_matrix': {
                'rating': [],
                'cost': [],
                'warranty': [],
                'installation_time': [],
                'reviews': []
            }
        }
        
        for center in centers:
            comparison['centers'].append({
                'id': center.get('id'),
                'name': center.get('name'),
                'city': center.get('city')
            })
            
            comparison['comparison_matrix']['rating'].append(center.get('rating', 0))
            comparison['comparison_matrix']['cost'].append(
                center.get('installation_cost_range', {}).get('sequential', {}).get('min', 0)
            )
            comparison['comparison_matrix']['warranty'].append(center.get('warranty_offered', ''))
            comparison['comparison_matrix']['installation_time'].append(center.get('installation_time', ''))
            comparison['comparison_matrix']['reviews'].append(center.get('total_reviews', 0))
        
        # Add winner indicators
        comparison['winners'] = {
            'best_rating': max(range(len(centers)), key=lambda i: comparison['comparison_matrix']['rating'][i]),
            'lowest_cost': min(range(len(centers)), key=lambda i: comparison['comparison_matrix']['cost'][i]),
            'most_reviews': max(range(len(centers)), key=lambda i: comparison['comparison_matrix']['reviews'][i])
        }
        
        return comparison
    
    def get_installation_guide(self):
        """Get complete installation guide"""
        return {
            'checklist': self.installation_checklist,
            'selection_criteria': self.selection_criteria,
            'cost_breakdown': self.cost_breakdown,
            'estimated_timeline': '1-2 days (including installation and RTO process)',
            'documents_required': self.installation_checklist.get('before_installation', [])
        }
    
    def search_centers(self, query, city=None):
        """
        Search service centers by name, brand, or service
        
        Args:
            query: Search query
            city: Optional city filter
        
        Returns:
            list: Matching centers
        """
        
        query_lower = query.lower()
        results = []
        
        for center in self.service_centers:
            # City filter
            if city and center.get('city', '').lower() != city.lower():
                continue
            
            # Search in name
            if query_lower in center.get('name', '').lower():
                results.append(center)
                continue
            
            # Search in brands
            brands = center.get('brands', [])
            if any(query_lower in brand.lower() for brand in brands):
                results.append(center)
                continue
            
            # Search in services
            services = center.get('services', [])
            if any(query_lower in service.lower() for service in services):
                results.append(center)
                continue
        
        return results
    
    def get_cost_estimate(self, kit_type, city, include_rto=True):
        """
        Get detailed cost estimate for CNG conversion
        
        Args:
            kit_type: sequential/venturi/premium
            city: City name
            include_rto: Include RTO costs
        
        Returns:
            dict: Detailed cost breakdown
        """
        
        # Get base cost from breakdown
        kit_costs = self.cost_breakdown.get(f'{kit_type}_kit_components', {})
        base_total = kit_costs.get('total', 45000)
        
        # City-based variations
        city_multipliers = {
            'Delhi': 1.0,
            'Mumbai': 1.15,
            'Bangalore': 1.10,
            'Pune': 1.05,
            'Hyderabad': 1.0,
            'Ahmedabad': 0.95,
            'Lucknow': 0.90,
            'Kanpur': 0.90
        }
        
        multiplier = city_multipliers.get(city, 1.0)
        adjusted_total = base_total * multiplier
        
        estimate = {
            'kit_type': kit_type,
            'city': city,
            'components': kit_costs,
            'base_cost': base_total,
            'city_adjustment': f"{(multiplier - 1) * 100:+.1f}%",
            'adjusted_cost': round(adjusted_total, 0),
            'rto_costs': {
                'fitness_certificate': 500,
                'endorsement_fee': 300,
                'misc_charges': 200,
                'total': 1000
            } if include_rto else None,
            'total_investment': round(adjusted_total + (1000 if include_rto else 0), 0)
        }
        
        return estimate
    
    def _calculate_distance(self, lat1, lng1, lat2, lng2):
        """Calculate distance between two coordinates in km"""
        R = 6371  # Earth's radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlng / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

# Singleton instance
service_center_service = ServiceCenterService()
