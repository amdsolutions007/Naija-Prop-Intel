"""
Naija-Prop-Intel: Google Maps Integration
© 2025 AMD Solutions. All Rights Reserved.

Features:
- Satellite view for properties
- GPS coordinates lookup
- Flood zone visualization
- Street view integration
- Distance calculations
"""

import os
from typing import Dict, Any, Tuple, Optional
import webbrowser


class MapsIntegration:
    """Google Maps and satellite imagery integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Maps Integration
        
        Args:
            api_key: Google Maps API key (optional for basic features)
        """
        self.api_key = api_key or os.environ.get('GOOGLE_MAPS_API_KEY', '')
        self.has_api_key = bool(self.api_key)
        
        # Nigerian property GPS coordinates database
        self.coordinates_db = {
            "Ajah": {
                "lat": 6.4675,
                "lng": 3.5687,
                "bounds": {
                    "north": 6.4800,
                    "south": 6.4550,
                    "east": 3.5850,
                    "west": 3.5524
                }
            },
            "Lekki Phase 1": {
                "lat": 6.4378,
                "lng": 3.4730,
                "bounds": {
                    "north": 6.4500,
                    "south": 6.4256,
                    "east": 3.4900,
                    "west": 3.4560
                }
            },
            "Victoria Island": {
                "lat": 6.4281,
                "lng": 3.4219,
                "bounds": {
                    "north": 6.4400,
                    "south": 6.4162,
                    "east": 3.4400,
                    "west": 3.4038
                }
            },
            "Ikoyi": {
                "lat": 6.4549,
                "lng": 3.4316,
                "bounds": {
                    "north": 6.4650,
                    "south": 6.4448,
                    "east": 3.4450,
                    "west": 3.4182
                }
            },
            "Surulere": {
                "lat": 6.4969,
                "lng": 3.3558,
                "bounds": {
                    "north": 6.5100,
                    "south": 6.4838,
                    "east": 3.3700,
                    "west": 3.3416
                }
            },
            "Maitama": {
                "lat": 9.0820,
                "lng": 7.4897,
                "bounds": {
                    "north": 9.0950,
                    "south": 9.0690,
                    "east": 7.5050,
                    "west": 7.4744
                }
            },
            "Gwarinpa": {
                "lat": 9.1167,
                "lng": 7.4083,
                "bounds": {
                    "north": 9.1300,
                    "south": 9.1034,
                    "east": 7.4250,
                    "west": 7.3916
                }
            },
            "Ikeja GRA": {
                "lat": 6.5964,
                "lng": 3.3515,
                "bounds": {
                    "north": 6.6100,
                    "south": 6.5828,
                    "east": 3.3700,
                    "west": 3.3330
                }
            }
        }
    
    def get_coordinates(self, location: str) -> Optional[Dict[str, float]]:
        """
        Get GPS coordinates for a location
        
        Args:
            location: Location name
        
        Returns:
            Dictionary with lat/lng coordinates
        """
        location_normalized = self._normalize_location(location)
        
        if location_normalized in self.coordinates_db:
            coords = self.coordinates_db[location_normalized]
            return {
                "latitude": coords["lat"],
                "longitude": coords["lng"],
                "location": location_normalized
            }
        
        return None
    
    def open_satellite_view(
        self, 
        location: str, 
        zoom_level: int = 17
    ) -> Dict[str, Any]:
        """
        Open Google Maps satellite view in browser
        
        Args:
            location: Location name or address
            zoom_level: Zoom level (1-20, default: 17 for property view)
        
        Returns:
            Status and URL information
        """
        coords = self.get_coordinates(location)
        
        if not coords:
            return {
                "error": f"Location '{location}' not found in database",
                "available_locations": list(self.coordinates_db.keys())
            }
        
        lat = coords["latitude"]
        lng = coords["longitude"]
        
        # Google Maps satellite view URL
        maps_url = (
            f"https://www.google.com/maps/@{lat},{lng},{zoom_level}z"
            f"/data=!3m1!1e3"  # Satellite layer
        )
        
        # Try to open in browser
        try:
            webbrowser.open(maps_url)
            status = "✅ Opened in browser"
        except Exception as e:
            status = f"⚠️ Could not open browser: {e}"
        
        return {
            "success": True,
            "location": location,
            "coordinates": coords,
            "satellite_url": maps_url,
            "status": status,
            "instructions": "View property location in satellite mode with high-resolution imagery"
        }
    
    def get_street_view_url(
        self, 
        location: str, 
        heading: int = 0,
        pitch: int = 0,
        fov: int = 90
    ) -> str:
        """
        Generate Google Street View URL
        
        Args:
            location: Location name
            heading: Camera heading (0-360 degrees)
            pitch: Camera pitch (-90 to 90 degrees)
            fov: Field of view (10-100 degrees)
        
        Returns:
            Street View URL
        """
        coords = self.get_coordinates(location)
        
        if not coords:
            return ""
        
        lat = coords["latitude"]
        lng = coords["longitude"]
        
        if self.has_api_key:
            # Street View Static API (requires API key)
            return (
                f"https://maps.googleapis.com/maps/api/streetview"
                f"?size=640x480"
                f"&location={lat},{lng}"
                f"&heading={heading}"
                f"&pitch={pitch}"
                f"&fov={fov}"
                f"&key={self.api_key}"
            )
        else:
            # Street View embed URL (free)
            return (
                f"https://www.google.com/maps/@?api=1&map_action=pano"
                f"&viewpoint={lat},{lng}"
                f"&heading={heading}"
                f"&pitch={pitch}"
                f"&fov={fov}"
            )
    
    def calculate_distance(
        self, 
        location1: str, 
        location2: str
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate distance between two locations
        
        Args:
            location1: First location
            location2: Second location
        
        Returns:
            Distance information in kilometers
        """
        coords1 = self.get_coordinates(location1)
        coords2 = self.get_coordinates(location2)
        
        if not coords1 or not coords2:
            return None
        
        # Haversine formula for distance calculation
        from math import radians, sin, cos, sqrt, atan2
        
        lat1 = radians(coords1["latitude"])
        lon1 = radians(coords1["longitude"])
        lat2 = radians(coords2["latitude"])
        lon2 = radians(coords2["longitude"])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        # Earth's radius in kilometers
        radius = 6371
        distance_km = radius * c
        
        return {
            "from": location1,
            "to": location2,
            "distance_km": round(distance_km, 2),
            "distance_miles": round(distance_km * 0.621371, 2),
            "coordinates": {
                "from": coords1,
                "to": coords2
            }
        }
    
    def get_directions_url(
        self, 
        origin: str, 
        destination: str,
        mode: str = "driving"
    ) -> str:
        """
        Generate Google Maps directions URL
        
        Args:
            origin: Starting location
            destination: Destination location
            mode: Travel mode (driving, walking, transit, bicycling)
        
        Returns:
            Directions URL
        """
        coords_origin = self.get_coordinates(origin)
        coords_dest = self.get_coordinates(destination)
        
        if not coords_origin or not coords_dest:
            return ""
        
        lat1, lng1 = coords_origin["latitude"], coords_origin["longitude"]
        lat2, lng2 = coords_dest["latitude"], coords_dest["longitude"]
        
        return (
            f"https://www.google.com/maps/dir/{lat1},{lng1}/{lat2},{lng2}"
            f"/@{lat1},{lng1},12z"
            f"/data=!3m1!4b1!4m2!4m1!3e{self._mode_to_code(mode)}"
        )
    
    def generate_embed_code(
        self, 
        location: str,
        width: int = 600,
        height: int = 450,
        zoom: int = 15
    ) -> str:
        """
        Generate HTML embed code for Google Maps
        
        Args:
            location: Location name
            width: Map width in pixels
            height: Map height in pixels
            zoom: Zoom level
        
        Returns:
            HTML iframe embed code
        """
        coords = self.get_coordinates(location)
        
        if not coords:
            return ""
        
        lat = coords["latitude"]
        lng = coords["longitude"]
        
        embed_code = f'''<iframe
  width="{width}"
  height="{height}"
  frameborder="0"
  style="border:0"
  src="https://www.google.com/maps?q={lat},{lng}&z={zoom}&output=embed"
  allowfullscreen>
</iframe>'''
        
        return embed_code
    
    def _normalize_location(self, location: str) -> str:
        """Normalize location name for database lookup"""
        location = location.strip()
        
        # Handle common variations
        mappings = {
            "vi": "Victoria Island",
            "v.i": "Victoria Island",
            "victoria island": "Victoria Island",
            "lekki": "Lekki Phase 1",
            "lekki 1": "Lekki Phase 1",
            "lekki phase 1": "Lekki Phase 1",
            "ikeja": "Ikeja GRA",
            "ikeja gra": "Ikeja GRA"
        }
        
        location_lower = location.lower()
        if location_lower in mappings:
            return mappings[location_lower]
        
        # Try exact match
        for key in self.coordinates_db.keys():
            if key.lower() == location_lower:
                return key
        
        return location
    
    def _mode_to_code(self, mode: str) -> str:
        """Convert travel mode to Google Maps code"""
        modes = {
            "driving": "0",
            "walking": "2",
            "transit": "3",
            "bicycling": "1"
        }
        return modes.get(mode.lower(), "0")


def test_maps_integration():
    """Test maps integration features"""
    print("🗺️  Testing Naija-Prop-Intel Maps Integration\n")
    
    maps = MapsIntegration()
    
    # Test 1: Get coordinates
    print("1️⃣ Getting GPS coordinates for Lekki Phase 1...")
    coords = maps.get_coordinates("Lekki Phase 1")
    if coords:
        print(f"✅ Latitude: {coords['latitude']}")
        print(f"✅ Longitude: {coords['longitude']}")
    
    print("\n" + "─" * 60)
    
    # Test 2: Satellite view
    print("\n2️⃣ Opening satellite view...")
    result = maps.open_satellite_view("Victoria Island", zoom_level=18)
    print(f"Location: {result.get('location', 'N/A')}")
    print(f"Status: {result.get('status', 'N/A')}")
    print(f"URL: {result.get('satellite_url', 'N/A')}")
    
    print("\n" + "─" * 60)
    
    # Test 3: Distance calculation
    print("\n3️⃣ Calculating distance...")
    distance = maps.calculate_distance("Ajah", "Ikoyi")
    if distance:
        print(f"From: {distance['from']}")
        print(f"To: {distance['to']}")
        print(f"Distance: {distance['distance_km']} km ({distance['distance_miles']} miles)")
    
    print("\n" + "─" * 60)
    
    # Test 4: Generate embed code
    print("\n4️⃣ Generating embed code for Maitama...")
    embed = maps.generate_embed_code("Maitama", width=800, height=600)
    print("✅ Embed code generated")
    print(f"Length: {len(embed)} characters")


if __name__ == "__main__":
    test_maps_integration()
