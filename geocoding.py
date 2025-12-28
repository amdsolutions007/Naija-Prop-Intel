"""
Geocoding Module - Address to Coordinates Converter
Naija-Prop-Intel

Convert Nigerian addresses to GPS coordinates and vice versa.
Uses Google Geocoding API for accurate location mapping.
"""

import os
import json
import googlemaps
from typing import Dict, List, Optional, Tuple


class Geocoder:
    """Convert addresses to coordinates and vice versa."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Geocoder with Google Maps API.
        
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
    
    def address_to_coordinates(self, address: str) -> Dict:
        """
        Convert Nigerian address to GPS coordinates.
        
        Args:
            address: Street address (e.g., "15 Admiralty Way, Lekki Phase 1, Lagos")
        
        Returns:
            Dict with coordinates, formatted address, and location details
        """
        try:
            # Ensure Nigeria is in the address
            if 'Nigeria' not in address and 'Lagos' not in address and 'Abuja' not in address:
                address += ', Nigeria'
            
            geocode_result = self.gmaps.geocode(address)
            
            if not geocode_result:
                return {
                    'status': 'NOT_FOUND',
                    'error': 'Address not found',
                    'query': address
                }
            
            result = geocode_result[0]
            location = result['geometry']['location']
            
            return {
                'status': 'OK',
                'coordinates': {
                    'lat': location['lat'],
                    'lng': location['lng']
                },
                'formatted_address': result['formatted_address'],
                'place_id': result['place_id'],
                'address_components': self._parse_address_components(result['address_components']),
                'location_type': result['geometry']['location_type'],
                'query': address
            }
        
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'query': address
            }
    
    def coordinates_to_address(self, lat: float, lng: float) -> Dict:
        """
        Convert GPS coordinates to Nigerian address (reverse geocoding).
        
        Args:
            lat: Latitude
            lng: Longitude
        
        Returns:
            Dict with formatted address and location details
        """
        try:
            reverse_geocode_result = self.gmaps.reverse_geocode((lat, lng))
            
            if not reverse_geocode_result:
                return {
                    'status': 'NOT_FOUND',
                    'error': 'Address not found for coordinates',
                    'coordinates': {'lat': lat, 'lng': lng}
                }
            
            result = reverse_geocode_result[0]
            
            return {
                'status': 'OK',
                'formatted_address': result['formatted_address'],
                'place_id': result['place_id'],
                'address_components': self._parse_address_components(result['address_components']),
                'coordinates': {'lat': lat, 'lng': lng}
            }
        
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'coordinates': {'lat': lat, 'lng': lng}
            }
    
    def _parse_address_components(self, components: List[Dict]) -> Dict:
        """Parse Google's address components into readable format."""
        parsed = {
            'street_number': None,
            'route': None,
            'locality': None,
            'lga': None,
            'state': None,
            'country': None,
            'postal_code': None
        }
        
        for component in components:
            types = component['types']
            
            if 'street_number' in types:
                parsed['street_number'] = component['long_name']
            elif 'route' in types:
                parsed['route'] = component['long_name']
            elif 'locality' in types or 'sublocality' in types:
                parsed['locality'] = component['long_name']
            elif 'administrative_area_level_2' in types:
                parsed['lga'] = component['long_name']
            elif 'administrative_area_level_1' in types:
                parsed['state'] = component['long_name']
            elif 'country' in types:
                parsed['country'] = component['long_name']
            elif 'postal_code' in types:
                parsed['postal_code'] = component['long_name']
        
        return parsed
    
    def find_zone_by_address(self, address: str) -> Optional[Dict]:
        """
        Find matching zone in database from address.
        
        Args:
            address: Street address
        
        Returns:
            Zone data if found, None otherwise
        """
        coords_data = self.address_to_coordinates(address)
        
        if coords_data['status'] != 'OK':
            return None
        
        coords = coords_data['coordinates']
        return self.find_zone_by_coordinates(coords['lat'], coords['lng'])
    
    def find_zone_by_coordinates(self, lat: float, lng: float, threshold_km: float = 5) -> Optional[Dict]:
        """
        Find closest zone in database from coordinates.
        
        Args:
            lat: Latitude
            lng: Longitude
            threshold_km: Maximum distance to consider (default 5km)
        
        Returns:
            Dict with zone data and distance, or None if no zone within threshold
        """
        from math import radians, sin, cos, sqrt, atan2
        
        def haversine_distance(lat1, lng1, lat2, lng2):
            """Calculate distance between two points using Haversine formula."""
            R = 6371  # Earth's radius in km
            
            lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
            dlat = lat2 - lat1
            dlng = lng2 - lng1
            
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            
            return R * c
        
        zones = self.zones_data.get('zones', {})
        closest_zone = None
        min_distance = float('inf')
        
        for zone_name, zone_data in zones.items():
            zone_coords = zone_data['coordinates']
            distance = haversine_distance(
                lat, lng,
                zone_coords['lat'], zone_coords['lng']
            )
            
            if distance < min_distance and distance <= threshold_km:
                min_distance = distance
                closest_zone = {
                    'zone_name': zone_name,
                    'zone_data': zone_data,
                    'distance_km': round(distance, 2)
                }
        
        return closest_zone
    
    def batch_geocode_addresses(self, addresses: List[str]) -> List[Dict]:
        """
        Geocode multiple addresses at once.
        
        Args:
            addresses: List of addresses to geocode
        
        Returns:
            List of geocoding results
        """
        results = []
        
        for address in addresses:
            result = self.address_to_coordinates(address)
            results.append(result)
        
        return results
    
    def validate_nigerian_address(self, address: str) -> Dict:
        """
        Validate if address is in Nigeria and return detailed info.
        
        Args:
            address: Address to validate
        
        Returns:
            Dict with validation status and location details
        """
        coords_data = self.address_to_coordinates(address)
        
        if coords_data['status'] != 'OK':
            return {
                'valid': False,
                'reason': coords_data.get('error', 'Unknown error'),
                'address': address
            }
        
        components = coords_data['address_components']
        
        if components['country'] != 'Nigeria':
            return {
                'valid': False,
                'reason': f'Address is in {components["country"]}, not Nigeria',
                'address': address,
                'coordinates': coords_data['coordinates']
            }
        
        # Check if we have a matching zone
        zone = self.find_zone_by_coordinates(
            coords_data['coordinates']['lat'],
            coords_data['coordinates']['lng']
        )
        
        return {
            'valid': True,
            'address': address,
            'formatted_address': coords_data['formatted_address'],
            'coordinates': coords_data['coordinates'],
            'state': components['state'],
            'lga': components['lga'],
            'locality': components['locality'],
            'nearest_zone': zone['zone_name'] if zone else None,
            'distance_to_zone_km': zone['distance_km'] if zone else None
        }


def demo_geocoding():
    """Demo the geocoding features."""
    print("📍 NAIJA-PROP-INTEL - Geocoding Demo\n")
    print("=" * 60)
    
    try:
        geocoder = Geocoder()
        
        # Demo 1: Address to coordinates
        print("\n1️⃣  Address to Coordinates")
        print("-" * 60)
        address = "Admiralty Way, Lekki Phase 1, Lagos, Nigeria"
        result = geocoder.address_to_coordinates(address)
        if result['status'] == 'OK':
            print(f"Address: {result['formatted_address']}")
            print(f"Coordinates: {result['coordinates']['lat']}, {result['coordinates']['lng']}")
            print(f"State: {result['address_components']['state']}")
        
        # Demo 2: Coordinates to address
        print("\n2️⃣  Coordinates to Address")
        print("-" * 60)
        lat, lng = 6.4378, 3.4730
        result = geocoder.coordinates_to_address(lat, lng)
        if result['status'] == 'OK':
            print(f"Coordinates: {lat}, {lng}")
            print(f"Address: {result['formatted_address']}")
        
        # Demo 3: Find zone by address
        print("\n3️⃣  Find Zone from Address")
        print("-" * 60)
        zone = geocoder.find_zone_by_address("Lekki Phase 1, Lagos")
        if zone:
            print(f"Nearest Zone: {zone['zone_name']}")
            print(f"Distance: {zone['distance_km']}km")
            print(f"Avg Price: ₦{zone['zone_data']['market_data']['avg_price_per_sqm']:,}/sqm")
        
        # Demo 4: Validate Nigerian address
        print("\n4️⃣  Validate Nigerian Address")
        print("-" * 60)
        validation = geocoder.validate_nigerian_address("Victoria Island, Lagos")
        print(f"Valid: {validation['valid']}")
        if validation['valid']:
            print(f"State: {validation['state']}")
            print(f"Nearest Zone: {validation['nearest_zone']}")
        
        print("\n" + "=" * 60)
        print("✅ Geocoding operational!")
        
    except ValueError as e:
        print(f"\n⚠️  {e}")
        print("\nTo use this module, set your Google Maps API key:")
        print("  export GOOGLE_MAPS_API_KEY='your-api-key-here'")


if __name__ == "__main__":
    demo_geocoding()
