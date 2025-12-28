"""
Google Maps Integration Module
Naija-Prop-Intel - Africa's #1 Property Intelligence Platform

Features:
- Satellite view for properties
- Street view integration
- Distance calculations
- Route-based property search
- GPS coordinate lookups

API: Google Maps JavaScript & Python API
Cost: $200/month (28,000 free map loads)
"""

import os
import json
import googlemaps
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class MapsIntegration:
    """Google Maps API wrapper for property intelligence."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Google Maps client.
        
        Args:
            api_key: Google Maps API key. If None, loads from environment.
        """
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Google Maps API key required. Set GOOGLE_MAPS_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.gmaps = googlemaps.Client(key=self.api_key)
        self.zones_data = self._load_zones()
    
    def _load_zones(self) -> Dict:
        """Load zones data from JSON file."""
        zones_path = os.path.join(os.path.dirname(__file__), 'data', 'zones.json')
        with open(zones_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_satellite_view_url(self, lat: float, lng: float, zoom: int = 18) -> str:
        """
        Generate Google Maps satellite view URL.
        
        Args:
            lat: Latitude
            lng: Longitude
            zoom: Zoom level (1-20, default 18 for property detail)
        
        Returns:
            Satellite view URL
        """
        return (
            f"https://www.google.com/maps/@?api=1&map_action=map"
            f"&center={lat},{lng}&zoom={zoom}&basemap=satellite"
        )
    
    def get_street_view_url(self, lat: float, lng: float, heading: int = 0) -> str:
        """
        Generate Google Street View URL.
        
        Args:
            lat: Latitude
            lng: Longitude
            heading: Camera heading (0-360 degrees)
        
        Returns:
            Street View URL
        """
        return (
            f"https://www.google.com/maps/@?api=1&map_action=pano"
            f"&viewpoint={lat},{lng}&heading={heading}"
        )
    
    def get_directions_url(self, origin: str, destination: str) -> str:
        """
        Generate Google Maps directions URL.
        
        Args:
            origin: Starting location
            destination: Ending location
        
        Returns:
            Directions URL
        """
        return (
            f"https://www.google.com/maps/dir/?api=1"
            f"&origin={origin.replace(' ', '+')}"
            f"&destination={destination.replace(' ', '+')}"
        )
    
    def calculate_distance(
        self, 
        origin_coords: Tuple[float, float], 
        dest_coords: Tuple[float, float],
        mode: str = "driving"
    ) -> Dict:
        """
        Calculate distance and travel time between two points.
        
        Args:
            origin_coords: (latitude, longitude) of origin
            dest_coords: (latitude, longitude) of destination
            mode: Travel mode - driving, walking, transit, bicycling
        
        Returns:
            Dict with distance (km) and duration (minutes)
        """
        try:
            result = self.gmaps.distance_matrix(
                origins=[origin_coords],
                destinations=[dest_coords],
                mode=mode,
                departure_time=datetime.now()
            )
            
            if result['rows'][0]['elements'][0]['status'] == 'OK':
                distance_m = result['rows'][0]['elements'][0]['distance']['value']
                duration_s = result['rows'][0]['elements'][0]['duration']['value']
                
                return {
                    'distance_km': round(distance_m / 1000, 2),
                    'duration_minutes': round(duration_s / 60, 1),
                    'mode': mode,
                    'status': 'OK'
                }
            else:
                return {'status': 'NOT_FOUND', 'error': 'Route not available'}
        
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)}
    
    def get_property_map_data(self, zone_name: str) -> Dict:
        """
        Get comprehensive map data for a property zone.
        
        Args:
            zone_name: Name of zone from zones.json
        
        Returns:
            Dict with map URLs, coordinates, and location data
        """
        zones = self.zones_data.get('zones', {})
        
        if zone_name not in zones:
            return {'error': f'Zone "{zone_name}" not found in database'}
        
        zone_data = zones[zone_name]
        coords = zone_data['coordinates']
        lat, lng = coords['lat'], coords['lng']
        
        return {
            'zone_name': zone_name,
            'location': zone_data['location'],
            'coordinates': coords,
            'satellite_view': self.get_satellite_view_url(lat, lng),
            'street_view': self.get_street_view_url(lat, lng),
            'google_maps_link': f"https://www.google.com/maps/search/?api=1&query={lat},{lng}",
            'flood_risk': zone_data['flood_risk'],
            'security': zone_data['security'],
            'infrastructure': zone_data['infrastructure']
        }
    
    def find_nearby_zones(
        self, 
        center_zone: str, 
        max_distance_km: float = 10
    ) -> List[Dict]:
        """
        Find zones within a radius of a center zone.
        
        Args:
            center_zone: Name of center zone
            max_distance_km: Maximum distance in kilometers
        
        Returns:
            List of nearby zones with distances
        """
        zones = self.zones_data.get('zones', {})
        
        if center_zone not in zones:
            return []
        
        center_coords = zones[center_zone]['coordinates']
        center_lat, center_lng = center_coords['lat'], center_coords['lng']
        
        nearby = []
        
        for zone_name, zone_data in zones.items():
            if zone_name == center_zone:
                continue
            
            zone_coords = zone_data['coordinates']
            zone_lat, zone_lng = zone_coords['lat'], zone_coords['lng']
            
            # Calculate distance
            distance_data = self.calculate_distance(
                (center_lat, center_lng),
                (zone_lat, zone_lng)
            )
            
            if distance_data['status'] == 'OK':
                distance_km = distance_data['distance_km']
                
                if distance_km <= max_distance_km:
                    nearby.append({
                        'zone_name': zone_name,
                        'location': zone_data['location'],
                        'distance_km': distance_km,
                        'duration_minutes': distance_data['duration_minutes'],
                        'coordinates': zone_coords,
                        'avg_price_per_sqm': zone_data['market_data']['avg_price_per_sqm']
                    })
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance_km'])
        
        return nearby
    
    def search_corridor_properties(
        self, 
        origin: str, 
        destination: str, 
        corridor_width_km: float = 5
    ) -> List[Dict]:
        """
        Find properties along a route corridor (e.g., "Ajah to Lekki").
        
        Args:
            origin: Starting zone name
            destination: Ending zone name
            corridor_width_km: Width of corridor to search (km from route)
        
        Returns:
            List of properties along the route
        """
        zones = self.zones_data.get('zones', {})
        
        if origin not in zones or destination not in zones:
            return []
        
        origin_coords = zones[origin]['coordinates']
        dest_coords = zones[destination]['coordinates']
        
        # Get route distance
        route_data = self.calculate_distance(
            (origin_coords['lat'], origin_coords['lng']),
            (dest_coords['lat'], dest_coords['lng'])
        )
        
        if route_data['status'] != 'OK':
            return []
        
        # Find zones along corridor
        corridor_zones = []
        
        for zone_name, zone_data in zones.items():
            zone_coords = zone_data['coordinates']
            
            # Calculate distance from origin
            from_origin = self.calculate_distance(
                (origin_coords['lat'], origin_coords['lng']),
                (zone_coords['lat'], zone_coords['lng'])
            )
            
            # Calculate distance to destination
            to_dest = self.calculate_distance(
                (zone_coords['lat'], zone_coords['lng']),
                (dest_coords['lat'], dest_coords['lng'])
            )
            
            if from_origin['status'] == 'OK' and to_dest['status'] == 'OK':
                # Check if zone is roughly along the route
                total_via_zone = from_origin['distance_km'] + to_dest['distance_km']
                direct_distance = route_data['distance_km']
                
                # If detour is within corridor width, include it
                if abs(total_via_zone - direct_distance) <= corridor_width_km:
                    corridor_zones.append({
                        'zone_name': zone_name,
                        'location': zone_data['location'],
                        'from_origin_km': from_origin['distance_km'],
                        'to_destination_km': to_dest['distance_km'],
                        'coordinates': zone_coords,
                        'market_data': zone_data['market_data'],
                        'flood_risk': zone_data['flood_risk']['score'],
                        'security': zone_data['security']['score']
                    })
        
        # Sort by distance from origin
        corridor_zones.sort(key=lambda x: x['from_origin_km'])
        
        return corridor_zones


def demo_maps_integration():
    """Demo the maps integration features."""
    print("🗺️  NAIJA-PROP-INTEL - Google Maps Integration Demo\n")
    print("=" * 60)
    
    # Note: Requires GOOGLE_MAPS_API_KEY environment variable
    try:
        maps = MapsIntegration()
        
        # Demo 1: Get property map data
        print("\n1️⃣  Property Map Data - Lekki Phase 1")
        print("-" * 60)
        lekki_data = maps.get_property_map_data("Lekki Phase 1")
        print(f"Location: {lekki_data['location']}")
        print(f"Coordinates: {lekki_data['coordinates']}")
        print(f"Satellite View: {lekki_data['satellite_view']}")
        print(f"Street View: {lekki_data['street_view']}")
        
        # Demo 2: Find nearby zones
        print("\n2️⃣  Zones within 10km of Ajah")
        print("-" * 60)
        nearby = maps.find_nearby_zones("Ajah", max_distance_km=10)
        for zone in nearby[:3]:
            print(f"  • {zone['zone_name']}: {zone['distance_km']}km away "
                  f"({zone['duration_minutes']} mins drive)")
        
        # Demo 3: Corridor search
        print("\n3️⃣  Properties along Ajah → Lekki Phase 1 corridor")
        print("-" * 60)
        corridor = maps.search_corridor_properties("Ajah", "Lekki Phase 1")
        for zone in corridor[:3]:
            print(f"  • {zone['zone_name']}: {zone['from_origin_km']}km from origin")
            print(f"    Price: ₦{zone['market_data']['avg_price_per_sqm']:,}/sqm")
        
        print("\n" + "=" * 60)
        print("✅ Maps integration operational!")
        
    except ValueError as e:
        print(f"\n⚠️  {e}")
        print("\nTo use this module, set your Google Maps API key:")
        print("  export GOOGLE_MAPS_API_KEY='your-api-key-here'")


if __name__ == "__main__":
    demo_maps_integration()
