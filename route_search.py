"""
Route-Based Property Search Module
Naija-Prop-Intel

Search for properties along routes and corridors.
Perfect for: "Show me properties from Ajah to Eleco"
            "Properties along Lekki-Epe Expressway"
            "Homes within 5km of Ajah-Victoria Island route"
"""

import os
import json
import googlemaps
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class RouteSearcher:
    """Search for properties along routes and corridors."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Route Searcher with Google Maps API.
        
        Args:
            api_key: Google Maps API key. If None, loads from environment.
        """
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Google Maps API key required. Set GOOGLE_MAPS_API_KEY environment variable."
            )
        
        self.gmaps = googlemaps.Client(key=self.api_key)
        self.zones_data = self._load_zones()
    
    def _load_zones(self) -> Dict:
        """Load zones data from JSON file."""
        zones_path = os.path.join(os.path.dirname(__file__), 'data', 'zones.json')
        with open(zones_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def search_route_corridor(
        self,
        origin: str,
        destination: str,
        corridor_width_km: float = 5,
        max_price_per_sqm: Optional[int] = None,
        min_security_score: int = 50,
        max_flood_risk: int = 70
    ) -> Dict:
        """
        Search for properties along a route corridor.
        
        Args:
            origin: Starting point (zone name or address)
            destination: Ending point (zone name or address)
            corridor_width_km: Width of corridor to search (km)
            max_price_per_sqm: Maximum price per square meter
            min_security_score: Minimum security score (0-100)
            max_flood_risk: Maximum acceptable flood risk score (0-100)
        
        Returns:
            Dict with route info and matching properties
        """
        zones = self.zones_data.get('zones', {})
        
        # Get coordinates for origin and destination
        origin_coords = self._get_coordinates(origin, zones)
        dest_coords = self._get_coordinates(destination, zones)
        
        if not origin_coords or not dest_coords:
            return {
                'status': 'ERROR',
                'error': 'Could not find coordinates for origin or destination'
            }
        
        # Get route details
        route_info = self._get_route_details(origin_coords, dest_coords)
        
        if route_info['status'] != 'OK':
            return route_info
        
        # Find properties along corridor
        corridor_properties = []
        
        for zone_name, zone_data in zones.items():
            zone_coords = zone_data['coordinates']
            
            # Check if zone is along the route
            if self._is_along_route(
                origin_coords, dest_coords, 
                (zone_coords['lat'], zone_coords['lng']),
                corridor_width_km
            ):
                # Apply filters
                market_data = zone_data['market_data']
                security = zone_data['security']['score']
                flood_risk = zone_data['flood_risk']['score']
                price = market_data['avg_price_per_sqm']
                
                # Check filters
                if max_price_per_sqm and price > max_price_per_sqm:
                    continue
                if security < min_security_score:
                    continue
                if flood_risk > max_flood_risk:
                    continue
                
                # Calculate distance from origin
                from_origin = self._calculate_distance(
                    origin_coords,
                    (zone_coords['lat'], zone_coords['lng'])
                )
                
                corridor_properties.append({
                    'zone_name': zone_name,
                    'location': zone_data['location'],
                    'distance_from_origin_km': from_origin,
                    'coordinates': zone_coords,
                    'price_per_sqm': price,
                    'price_range': market_data['price_range'],
                    'security_score': security,
                    'flood_risk_score': flood_risk,
                    'infrastructure_score': zone_data['infrastructure']['score'],
                    'rental_yield': market_data['rental_yield'],
                    'appreciation_5yr': market_data['5yr_appreciation'],
                    'smart_score': self._calculate_smart_score(zone_data)
                })
        
        # Sort by distance from origin
        corridor_properties.sort(key=lambda x: x['distance_from_origin_km'])
        
        return {
            'status': 'OK',
            'route': {
                'origin': origin,
                'destination': destination,
                'distance_km': route_info['distance_km'],
                'duration_minutes': route_info['duration_minutes']
            },
            'search_params': {
                'corridor_width_km': corridor_width_km,
                'max_price_per_sqm': max_price_per_sqm,
                'min_security_score': min_security_score,
                'max_flood_risk': max_flood_risk
            },
            'properties_found': len(corridor_properties),
            'properties': corridor_properties
        }
    
    def _get_coordinates(self, location: str, zones: Dict) -> Optional[Tuple[float, float]]:
        """Get coordinates from zone name or geocode address."""
        # Check if it's a zone name
        if location in zones:
            coords = zones[location]['coordinates']
            return (coords['lat'], coords['lng'])
        
        # Try geocoding
        try:
            geocode_result = self.gmaps.geocode(location + ', Nigeria')
            if geocode_result:
                loc = geocode_result[0]['geometry']['location']
                return (loc['lat'], loc['lng'])
        except:
            pass
        
        return None
    
    def _get_route_details(
        self,
        origin_coords: Tuple[float, float],
        dest_coords: Tuple[float, float]
    ) -> Dict:
        """Get distance and duration for route."""
        try:
            result = self.gmaps.distance_matrix(
                origins=[origin_coords],
                destinations=[dest_coords],
                mode='driving',
                departure_time=datetime.now()
            )
            
            if result['rows'][0]['elements'][0]['status'] == 'OK':
                distance_m = result['rows'][0]['elements'][0]['distance']['value']
                duration_s = result['rows'][0]['elements'][0]['duration']['value']
                
                return {
                    'status': 'OK',
                    'distance_km': round(distance_m / 1000, 2),
                    'duration_minutes': round(duration_s / 60, 1)
                }
            else:
                return {'status': 'NOT_FOUND'}
        
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)}
    
    def _is_along_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        point: Tuple[float, float],
        corridor_width_km: float
    ) -> bool:
        """Check if point is along the route within corridor width."""
        # Calculate distances
        dist_origin_point = self._calculate_distance(origin, point)
        dist_point_dest = self._calculate_distance(point, destination)
        dist_origin_dest = self._calculate_distance(origin, destination)
        
        # If point is roughly along the route (within corridor width)
        total_via_point = dist_origin_point + dist_point_dest
        detour = abs(total_via_point - dist_origin_dest)
        
        return detour <= corridor_width_km
    
    def _calculate_distance(
        self,
        coord1: Tuple[float, float],
        coord2: Tuple[float, float]
    ) -> float:
        """Calculate distance between two coordinates using Haversine formula."""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in km
        
        lat1, lng1 = coord1
        lat2, lng2 = coord2
        
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return round(R * c, 2)
    
    def _calculate_smart_score(self, zone_data: Dict) -> int:
        """Calculate overall smart score for property (0-100)."""
        security = zone_data['security']['score']
        infrastructure = zone_data['infrastructure']['score']
        flood_risk = 100 - zone_data['flood_risk']['score']  # Invert (lower is better)
        
        # Weighted average
        smart_score = (
            security * 0.35 +
            infrastructure * 0.35 +
            flood_risk * 0.30
        )
        
        return round(smart_score)
    
    def search_by_budget_along_route(
        self,
        origin: str,
        destination: str,
        budget: int,
        bedrooms: int = 3,
        corridor_width_km: float = 5
    ) -> Dict:
        """
        Find properties along route within budget.
        
        Args:
            origin: Starting point
            destination: Ending point
            budget: Total budget in Naira
            bedrooms: Number of bedrooms (default 3)
            corridor_width_km: Corridor width
        
        Returns:
            Dict with matching properties
        """
        # Average property size for 3-bedroom: 120 sqm
        sqm_estimate = {2: 80, 3: 120, 4: 160, 5: 200}
        estimated_sqm = sqm_estimate.get(bedrooms, 120)
        
        max_price_per_sqm = budget / estimated_sqm
        
        return self.search_route_corridor(
            origin=origin,
            destination=destination,
            corridor_width_km=corridor_width_km,
            max_price_per_sqm=int(max_price_per_sqm)
        )
    
    def compare_routes(
        self,
        origin: str,
        destinations: List[str]
    ) -> List[Dict]:
        """
        Compare multiple routes from one origin.
        
        Args:
            origin: Starting point
            destinations: List of ending points to compare
        
        Returns:
            List of route comparisons with property counts
        """
        comparisons = []
        
        for dest in destinations:
            result = self.search_route_corridor(origin, dest)
            
            if result['status'] == 'OK':
                comparisons.append({
                    'destination': dest,
                    'distance_km': result['route']['distance_km'],
                    'duration_minutes': result['route']['duration_minutes'],
                    'properties_found': result['properties_found'],
                    'avg_price_per_sqm': self._calculate_avg_price(result['properties']) if result['properties'] else 0,
                    'best_property': result['properties'][0] if result['properties'] else None
                })
        
        # Sort by properties found (descending)
        comparisons.sort(key=lambda x: x['properties_found'], reverse=True)
        
        return comparisons
    
    def _calculate_avg_price(self, properties: List[Dict]) -> int:
        """Calculate average price per sqm from properties list."""
        if not properties:
            return 0
        
        total = sum(p['price_per_sqm'] for p in properties)
        return round(total / len(properties))


def demo_route_search():
    """Demo the route search features."""
    print("🛣️  NAIJA-PROP-INTEL - Route Search Demo\n")
    print("=" * 60)
    
    try:
        searcher = RouteSearcher()
        
        # Demo 1: Search corridor
        print("\n1️⃣  Properties along Ajah → Lekki Phase 1 corridor")
        print("-" * 60)
        result = searcher.search_route_corridor(
            origin="Ajah",
            destination="Lekki Phase 1",
            corridor_width_km=5,
            max_price_per_sqm=200000,
            min_security_score=60
        )
        
        if result['status'] == 'OK':
            print(f"Route: {result['route']['distance_km']}km "
                  f"({result['route']['duration_minutes']} mins)")
            print(f"Properties found: {result['properties_found']}\n")
            
            for prop in result['properties'][:3]:
                print(f"  • {prop['zone_name']}")
                print(f"    {prop['distance_from_origin_km']}km from origin")
                print(f"    ₦{prop['price_per_sqm']:,}/sqm | Security: {prop['security_score']}")
                print(f"    Smart Score: {prop['smart_score']}/100")
                print()
        
        # Demo 2: Budget search
        print("\n2️⃣  Properties within ₦50M budget (Ajah → Victoria Island)")
        print("-" * 60)
        budget_result = searcher.search_by_budget_along_route(
            origin="Ajah",
            destination="Victoria Island",
            budget=50000000,  # ₦50M
            bedrooms=3
        )
        
        if budget_result['status'] == 'OK':
            print(f"Properties found: {budget_result['properties_found']}")
            if budget_result['properties']:
                best = budget_result['properties'][0]
                print(f"Best option: {best['zone_name']}")
                print(f"  Price range: {best['price_range']}")
                print(f"  Rental yield: {best['rental_yield']*100}%")
        
        # Demo 3: Route comparison
        print("\n3️⃣  Compare routes from Ikeja GRA")
        print("-" * 60)
        comparisons = searcher.compare_routes(
            origin="Ikeja GRA",
            destinations=["Lekki Phase 1", "Victoria Island", "Ikoyi"]
        )
        
        for comp in comparisons:
            print(f"  • To {comp['destination']}: {comp['distance_km']}km")
            print(f"    {comp['properties_found']} properties | "
                  f"Avg ₦{comp['avg_price_per_sqm']:,}/sqm")
        
        print("\n" + "=" * 60)
        print("✅ Route search operational!")
        
    except ValueError as e:
        print(f"\n⚠️  {e}")
        print("\nTo use this module, set your Google Maps API key:")
        print("  export GOOGLE_MAPS_API_KEY='your-api-key-here'")


if __name__ == "__main__":
    demo_route_search()
