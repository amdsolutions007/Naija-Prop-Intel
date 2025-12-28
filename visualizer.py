"""
Naija-Prop-Intel: Property Map Visualizer
Generates interactive maps with property locations and risk overlays

Features:
- Visual property map generation with Google Maps
- Risk overlay (Flood, Security, Infrastructure)
- Property pinpointing with detailed markers
- Route visualization for corridor searches
- Export maps as HTML/PNG
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

# Google Maps imports
try:
    import googlemaps
    GOOGLE_MAPS_AVAILABLE = True
except ImportError:
    GOOGLE_MAPS_AVAILABLE = False
    print("⚠️  Google Maps not installed. Run: pip install googlemaps")


class PropertyVisualizer:
    """
    Generates visual maps for property intelligence
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        zones_file: str = "data/zones.json"
    ):
        """
        Initialize Property Visualizer
        
        Args:
            api_key: Google Maps API key (or from env GOOGLE_MAPS_API_KEY)
            zones_file: Path to zones.json
        """
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        
        if GOOGLE_MAPS_AVAILABLE and self.api_key:
            self.gmaps = googlemaps.Client(key=self.api_key)
            self.maps_enabled = True
        else:
            self.gmaps = None
            self.maps_enabled = False
        
        # Load zones data
        self.zones = self._load_zones(zones_file)
    
    def _load_zones(self, zones_file: str) -> Dict[str, Any]:
        """Load zones data from JSON file"""
        try:
            with open(zones_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('zones', {})
        except FileNotFoundError:
            print(f"⚠️  {zones_file} not found")
            return {}
    
    def generate_property_map(
        self,
        properties: List[Dict[str, Any]],
        center_location: Optional[str] = None,
        show_risk_overlay: bool = True,
        output_file: str = "property_map.html",
        map_type: str = "roadmap"
    ) -> Dict[str, Any]:
        """
        Generate interactive property map with markers
        
        Args:
            properties: List of property dictionaries with location data
            center_location: Center map on this location (default: first property)
            show_risk_overlay: Show flood/security risk overlay
            output_file: Output HTML file path
            map_type: Map type ('roadmap', 'satellite', 'hybrid', 'terrain')
        
        Returns:
            Dict with map generation results
        """
        if not properties:
            return {
                'status': 'error',
                'message': 'No properties provided'
            }
        
        # Determine center coordinates
        if center_location:
            center = self._get_coordinates(center_location)
        else:
            # Use first property or default to Lagos
            first_prop = properties[0]
            if 'coordinates' in first_prop:
                center = first_prop['coordinates']
            else:
                center = {'lat': 6.5244, 'lng': 3.3792}  # Lagos default
        
        # Generate HTML map
        html_content = self._generate_html_map(
            properties,
            center,
            show_risk_overlay,
            map_type
        )
        
        # Save to file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                'status': 'success',
                'output_file': output_file,
                'properties_count': len(properties),
                'center': center,
                'message': f'Map generated: {output_file}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to save map: {str(e)}'
            }
    
    def _generate_html_map(
        self,
        properties: List[Dict[str, Any]],
        center: Dict[str, float],
        show_risk_overlay: bool,
        map_type: str
    ) -> str:
        """Generate HTML content for interactive map"""
        
        # Prepare property markers JavaScript
        markers_js = []
        
        for i, prop in enumerate(properties):
            # Get coordinates
            if 'coordinates' in prop:
                coords = prop['coordinates']
            elif 'location' in prop or 'zone' in prop:
                location = prop.get('zone') or prop.get('location')
                coords = self._get_coordinates(location)
            else:
                continue
            
            # Property info
            title = prop.get('title', 'Property')
            price = prop.get('price', 0)
            location = prop.get('location', 'Unknown')
            bedrooms = prop.get('bedrooms', 'N/A')
            
            # Risk scores (if available)
            risk_info = ""
            if 'flood_risk' in prop or 'security' in prop:
                flood = prop.get('flood_risk', {}).get('score', 'N/A')
                security = prop.get('security', {}).get('score', 'N/A')
                risk_info = f"<br>🌊 Flood: {flood}/100<br>🛡️ Security: {security}/100"
            
            # Marker color based on risk
            marker_color = self._get_marker_color(prop)
            
            markers_js.append(f"""
                {{
                    position: {{lat: {coords['lat']}, lng: {coords['lng']}}},
                    title: "{title}",
                    content: `
                        <div style="font-family: Arial, sans-serif; max-width: 300px;">
                            <h3 style="margin: 0 0 10px 0;">{title}</h3>
                            <p style="margin: 5px 0;"><strong>💰 Price:</strong> ₦{price:,}</p>
                            <p style="margin: 5px 0;"><strong>📍 Location:</strong> {location}</p>
                            <p style="margin: 5px 0;"><strong>🛏️ Bedrooms:</strong> {bedrooms}</p>
                            {risk_info}
                        </div>
                    `,
                    color: "{marker_color}"
                }}
            """)
        
        markers_array = ",".join(markers_js)
        
        # Risk overlay zones (if enabled)
        risk_zones_js = ""
        if show_risk_overlay and self.zones:
            risk_zones = []
            for zone_name, zone_data in self.zones.items():
                coords = zone_data.get('coordinates', {})
                flood_score = zone_data.get('flood_risk', {}).get('score', 0)
                
                # Color based on flood risk
                if flood_score < 30:
                    color = "#00FF00"  # Green (low risk)
                    opacity = 0.1
                elif flood_score < 60:
                    color = "#FFAA00"  # Orange (medium risk)
                    opacity = 0.2
                else:
                    color = "#FF0000"  # Red (high risk)
                    opacity = 0.3
                
                risk_zones.append(f"""
                    new google.maps.Circle({{
                        strokeColor: "{color}",
                        strokeOpacity: 0.8,
                        strokeWeight: 1,
                        fillColor: "{color}",
                        fillOpacity: {opacity},
                        map: map,
                        center: {{lat: {coords.get('lat', 0)}, lng: {coords.get('lng', 0)}}},
                        radius: 1000
                    }});
                """)
            
            risk_zones_js = "\n".join(risk_zones)
        
        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Naija-Prop-Intel: Property Map</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }}
        #map {{
            height: 100vh;
            width: 100%;
        }}
        .legend {{
            background: white;
            padding: 15px;
            margin: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            font-size: 14px;
        }}
        .legend h4 {{
            margin: 0 0 10px 0;
        }}
        .legend-item {{
            margin: 5px 0;
        }}
        .color-box {{
            display: inline-block;
            width: 20px;
            height: 20px;
            margin-right: 10px;
            vertical-align: middle;
            border: 1px solid #333;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    
    <script>
        let map;
        let infoWindow;
        
        function initMap() {{
            // Initialize map
            map = new google.maps.Map(document.getElementById("map"), {{
                zoom: 12,
                center: {{lat: {center['lat']}, lng: {center['lng']}}},
                mapTypeId: "{map_type}"
            }});
            
            infoWindow = new google.maps.InfoWindow();
            
            // Property markers
            const properties = [{markers_array}];
            
            properties.forEach((prop, index) => {{
                const marker = new google.maps.Marker({{
                    position: prop.position,
                    map: map,
                    title: prop.title,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 8,
                        fillColor: prop.color,
                        fillOpacity: 0.8,
                        strokeColor: "#FFFFFF",
                        strokeWeight: 2
                    }}
                }});
                
                marker.addListener("click", () => {{
                    infoWindow.setContent(prop.content);
                    infoWindow.open(map, marker);
                }});
            }});
            
            // Risk overlay zones
            {risk_zones_js}
            
            // Legend
            const legend = document.createElement("div");
            legend.className = "legend";
            legend.innerHTML = `
                <h4>🗺️ Property Map Legend</h4>
                <div class="legend-item">
                    <span class="color-box" style="background: #00AA00;"></span>
                    <strong>Low Risk Zone</strong> (Flood < 30%)
                </div>
                <div class="legend-item">
                    <span class="color-box" style="background: #FFAA00;"></span>
                    <strong>Medium Risk Zone</strong> (Flood 30-60%)
                </div>
                <div class="legend-item">
                    <span class="color-box" style="background: #FF0000;"></span>
                    <strong>High Risk Zone</strong> (Flood > 60%)
                </div>
                <div class="legend-item" style="margin-top: 10px;">
                    <strong>📍 {len(properties)} Properties Shown</strong>
                </div>
            `;
            
            map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(legend);
        }}
        
        window.initMap = initMap;
    </script>
    
    <script src="https://maps.googleapis.com/maps/api/js?key={self.api_key or 'YOUR_API_KEY_HERE'}&callback=initMap" async defer></script>
</body>
</html>
"""
        return html
    
    def _get_coordinates(self, location: str) -> Dict[str, float]:
        """Get coordinates for a location"""
        # Check zones data first
        for zone_name, zone_data in self.zones.items():
            if zone_name.lower() in location.lower() or location.lower() in zone_name.lower():
                return zone_data.get('coordinates', {'lat': 6.5244, 'lng': 3.3792})
        
        # Default: Lagos center
        return {'lat': 6.5244, 'lng': 3.3792}
    
    def _get_marker_color(self, property_data: Dict[str, Any]) -> str:
        """Determine marker color based on risk"""
        if 'flood_risk' in property_data:
            flood_score = property_data['flood_risk'].get('score', 0)
            
            if flood_score < 30:
                return "#00AA00"  # Green
            elif flood_score < 60:
                return "#FFAA00"  # Orange
            else:
                return "#FF0000"  # Red
        
        return "#0066CC"  # Blue (default)
    
    def generate_route_map(
        self,
        origin: str,
        destination: str,
        properties_along_route: List[Dict[str, Any]],
        output_file: str = "route_map.html"
    ) -> Dict[str, Any]:
        """
        Generate map with route and properties along corridor
        
        Args:
            origin: Starting location
            destination: Ending location
            properties_along_route: Properties found in corridor
            output_file: Output HTML file path
        
        Returns:
            Dict with map generation results
        """
        if not self.maps_enabled:
            return {
                'status': 'error',
                'message': 'Google Maps API not configured'
            }
        
        try:
            # Get directions
            directions = self.gmaps.directions(
                origin,
                destination,
                mode="driving"
            )
            
            if not directions:
                return {
                    'status': 'error',
                    'message': f'No route found from {origin} to {destination}'
                }
            
            # Extract route polyline
            route = directions[0]
            polyline = route['overview_polyline']['points']
            
            # Generate map with route and properties
            html_content = self._generate_route_html(
                origin,
                destination,
                polyline,
                properties_along_route
            )
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                'status': 'success',
                'output_file': output_file,
                'route': f"{origin} → {destination}",
                'properties_count': len(properties_along_route),
                'message': f'Route map generated: {output_file}'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to generate route map: {str(e)}'
            }
    
    def _generate_route_html(
        self,
        origin: str,
        destination: str,
        polyline: str,
        properties: List[Dict[str, Any]]
    ) -> str:
        """Generate HTML for route map"""
        
        # Get origin/destination coordinates
        origin_coords = self._get_coordinates(origin)
        dest_coords = self._get_coordinates(destination)
        
        # Center map between origin and destination
        center_lat = (origin_coords['lat'] + dest_coords['lat']) / 2
        center_lng = (origin_coords['lng'] + dest_coords['lng']) / 2
        
        # Property markers (reuse from generate_property_map)
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Route Map: {origin} → {destination}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
        #map {{ height: 100vh; width: 100%; }}
    </style>
</head>
<body>
    <div id="map"></div>
    
    <script>
        function initMap() {{
            const map = new google.maps.Map(document.getElementById("map"), {{
                zoom: 11,
                center: {{lat: {center_lat}, lng: {center_lng}}},
                mapTypeId: "roadmap"
            }});
            
            // Route polyline
            const routePath = google.maps.geometry.encoding.decodePath("{polyline}");
            const routeLine = new google.maps.Polyline({{
                path: routePath,
                geodesic: true,
                strokeColor: "#0066CC",
                strokeOpacity: 1.0,
                strokeWeight: 4
            }});
            routeLine.setMap(map);
            
            // Origin marker
            new google.maps.Marker({{
                position: {{lat: {origin_coords['lat']}, lng: {origin_coords['lng']}}},
                map: map,
                title: "Origin: {origin}",
                label: "A"
            }});
            
            // Destination marker
            new google.maps.Marker({{
                position: {{lat: {dest_coords['lat']}, lng: {dest_coords['lng']}}},
                map: map,
                title: "Destination: {destination}",
                label: "B"
            }});
            
            // Property markers along route
            // (Add properties here - similar to generate_property_map)
        }}
        
        window.initMap = initMap;
    </script>
    
    <script src="https://maps.googleapis.com/maps/api/js?key={self.api_key or 'YOUR_API_KEY_HERE'}&libraries=geometry&callback=initMap" async defer></script>
</body>
</html>
"""
        return html
    
    def generate_zone_heatmap(
        self,
        risk_type: str = "flood",
        output_file: str = "risk_heatmap.html"
    ) -> Dict[str, Any]:
        """
        Generate heatmap of risk scores across zones
        
        Args:
            risk_type: Type of risk ('flood', 'security', 'infrastructure')
            output_file: Output HTML file path
        
        Returns:
            Dict with heatmap generation results
        """
        if not self.zones:
            return {
                'status': 'error',
                'message': 'No zones data available'
            }
        
        # Collect risk scores
        heatmap_data = []
        
        for zone_name, zone_data in self.zones.items():
            coords = zone_data.get('coordinates', {})
            
            if risk_type == 'flood':
                score = zone_data.get('flood_risk', {}).get('score', 0)
            elif risk_type == 'security':
                score = 100 - zone_data.get('security', {}).get('score', 0)  # Invert for risk
            elif risk_type == 'infrastructure':
                score = 100 - zone_data.get('infrastructure', {}).get('score', 0)  # Invert
            else:
                score = 0
            
            heatmap_data.append({
                'location': coords,
                'weight': score
            })
        
        # Generate HTML heatmap
        html_content = self._generate_heatmap_html(risk_type, heatmap_data)
        
        # Save to file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                'status': 'success',
                'output_file': output_file,
                'risk_type': risk_type,
                'zones_count': len(heatmap_data),
                'message': f'Heatmap generated: {output_file}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to save heatmap: {str(e)}'
            }
    
    def _generate_heatmap_html(self, risk_type: str, heatmap_data: List[Dict]) -> str:
        """Generate HTML for risk heatmap"""
        
        # Format heatmap data for JavaScript
        heatmap_points = []
        for point in heatmap_data:
            loc = point['location']
            weight = point['weight']
            heatmap_points.append(f"{{location: new google.maps.LatLng({loc.get('lat', 0)}, {loc.get('lng', 0)}), weight: {weight}}}")
        
        points_js = ",\n".join(heatmap_points)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{risk_type.title()} Risk Heatmap - Lagos</title>
    <style>
        #map {{ height: 100vh; width: 100%; }}
    </style>
</head>
<body>
    <div id="map"></div>
    
    <script>
        function initMap() {{
            const map = new google.maps.Map(document.getElementById("map"), {{
                zoom: 11,
                center: {{lat: 6.5244, lng: 3.3792}},
                mapTypeId: "roadmap"
            }});
            
            const heatmapData = [
                {points_js}
            ];
            
            const heatmap = new google.maps.visualization.HeatmapLayer({{
                data: heatmapData,
                radius: 50
            }});
            
            heatmap.setMap(map);
        }}
        
        window.initMap = initMap;
    </script>
    
    <script src="https://maps.googleapis.com/maps/api/js?key={self.api_key or 'YOUR_API_KEY_HERE'}&libraries=visualization&callback=initMap" async defer></script>
</body>
</html>
"""
        return html


def demo_visualizer():
    """Demo the property visualizer"""
    print("=" * 70)
    print("NAIJA-PROP-INTEL: PROPERTY VISUALIZER DEMO")
    print("=" * 70)
    
    visualizer = PropertyVisualizer()
    
    print("\n📍 Loaded Zones:", len(visualizer.zones))
    
    # Sample properties
    sample_properties = [
        {
            'title': '3-Bedroom Flat in Lekki Phase 1',
            'price': 50000000,
            'location': 'Lekki Phase 1',
            'zone': 'Lekki Phase 1',
            'bedrooms': 3,
            'coordinates': {'lat': 6.4474, 'lng': 3.4737}
        },
        {
            'title': '4-Bedroom Duplex in Ajah',
            'price': 35000000,
            'location': 'Ajah',
            'zone': 'Ajah',
            'bedrooms': 4,
            'coordinates': {'lat': 6.4698, 'lng': 3.5852}
        },
        {
            'title': '2-Bedroom Apartment in Victoria Island',
            'price': 75000000,
            'location': 'Victoria Island',
            'zone': 'Victoria Island',
            'bedrooms': 2,
            'coordinates': {'lat': 6.4281, 'lng': 3.4219}
        }
    ]
    
    # Generate property map
    print("\n🗺️  Generating property map...")
    result = visualizer.generate_property_map(
        properties=sample_properties,
        show_risk_overlay=True,
        output_file="demo_property_map.html"
    )
    
    if result['status'] == 'success':
        print(f"✅ {result['message']}")
        print(f"   Properties: {result['properties_count']}")
        print(f"   Center: {result['center']}")
    else:
        print(f"❌ {result['message']}")
    
    # Generate flood risk heatmap
    print("\n🌊 Generating flood risk heatmap...")
    heatmap_result = visualizer.generate_zone_heatmap(
        risk_type='flood',
        output_file="demo_flood_heatmap.html"
    )
    
    if heatmap_result['status'] == 'success':
        print(f"✅ {heatmap_result['message']}")
        print(f"   Zones: {heatmap_result['zones_count']}")
    else:
        print(f"❌ {heatmap_result['message']}")
    
    print("\n" + "=" * 70)
    print("Demo complete!")
    print("\n📝 Files created:")
    print("   - demo_property_map.html (Open in browser)")
    print("   - demo_flood_heatmap.html (Open in browser)")
    print("\n⚠️  Note: Maps require Google Maps API key to display")
    print("=" * 70)


if __name__ == "__main__":
    demo_visualizer()
