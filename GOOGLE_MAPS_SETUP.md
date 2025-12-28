# Google Maps Setup Guide
**Naija-Prop-Intel - Week 2 Integration**

## 🗺️ Google Maps API Setup

### Step 1: Get Google Maps API Key

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create a New Project**
   - Click "Select a project" → "New Project"
   - Name: `Naija-Prop-Intel`
   - Click "Create"

3. **Enable Required APIs**
   - Go to "APIs & Services" → "Library"
   - Enable these APIs:
     * **Maps JavaScript API** (for web maps)
     * **Geocoding API** (for address conversion)
     * **Distance Matrix API** (for route calculations)
     * **Directions API** (for route planning)

4. **Create API Key**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy your API key (looks like: `AIzaSyD...`)

5. **Restrict API Key (IMPORTANT)**
   - Click on your API key to edit
   - Under "Application restrictions":
     * For development: Choose "None"
     * For production: Choose "IP addresses" and add your server IP
   - Under "API restrictions":
     * Select "Restrict key"
     * Check: Maps JavaScript API, Geocoding API, Distance Matrix API, Directions API
   - Click "Save"

### Step 2: Set Environment Variable

**macOS/Linux:**
```bash
export GOOGLE_MAPS_API_KEY='your-api-key-here'
```

To make it permanent, add to `~/.zshrc` or `~/.bash_profile`:
```bash
echo 'export GOOGLE_MAPS_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**Windows:**
```cmd
set GOOGLE_MAPS_API_KEY=your-api-key-here
```

### Step 3: Test the Integration

```bash
cd /Users/mac/Desktop/Naija-Prop-Intel
python maps_integration.py
python geocoding.py
python route_search.py
```

## 📊 API Usage & Costs

### Free Tier (Monthly)
- **$200 free credit** = 28,000 map loads
- **Geocoding:** 40,000 requests free
- **Distance Matrix:** 100 elements free, then $5 per 1,000 elements
- **Directions:** 100 requests free, then $5 per 1,000 requests

### Expected Usage (Month 1-2)
- **Development/Testing:** ~1,000 requests/month = FREE
- **Production (1,000 users):** ~5,000 requests/month = ~$50/month
- **Target:** Stay under $200/month threshold

### Cost Optimization Tips
1. **Cache results** - Store geocoded addresses in database
2. **Batch requests** - Use Distance Matrix for multiple destinations
3. **Rate limiting** - Max 50 requests per second
4. **Use static map images** - Where interactive maps not needed

## 🎯 Features Enabled

### 1. Satellite View
```python
from maps_integration import MapsIntegration

maps = MapsIntegration()
data = maps.get_property_map_data("Lekki Phase 1")
print(data['satellite_view'])  # URL to satellite view
```

### 2. Street View
```python
print(data['street_view'])  # URL to street view
```

### 3. Distance Calculations
```python
distance = maps.calculate_distance(
    origin_coords=(6.4675, 3.5687),  # Ajah
    dest_coords=(6.4378, 3.4730),    # Lekki
    mode="driving"
)
print(f"{distance['distance_km']}km, {distance['duration_minutes']} mins")
```

### 4. Route-Based Search
```python
from route_search import RouteSearcher

searcher = RouteSearcher()
results = searcher.search_route_corridor(
    origin="Ajah",
    destination="Lekki Phase 1",
    corridor_width_km=5,
    max_price_per_sqm=200000
)
print(f"Found {results['properties_found']} properties along route")
```

### 5. Geocoding
```python
from geocoding import Geocoder

geocoder = Geocoder()
result = geocoder.address_to_coordinates("Admiralty Way, Lekki, Lagos")
print(result['coordinates'])  # {'lat': 6.4378, 'lng': 3.4730}
```

## 🔧 Troubleshooting

### Error: "API key not valid"
- Check if API key is correctly set in environment
- Verify APIs are enabled in Google Cloud Console
- Check API key restrictions

### Error: "Over query limit"
- You've exceeded free tier
- Implement caching to reduce requests
- Consider upgrading to paid plan

### Error: "Request denied"
- API not enabled in Google Cloud Console
- Go enable: Geocoding, Distance Matrix, Directions APIs

## 📈 Next Steps

### Week 2-3 Milestones:
- [x] Google Maps API setup
- [x] Satellite view integration
- [x] Geocoding implementation
- [x] Route-based search
- [ ] Integrate into main app.py
- [ ] Add map views to property reports
- [ ] Cache geocoding results
- [ ] Test with real user queries

### Week 3-4: Agent Registration System
- Build agent database
- ₦5,000 verification fee collection
- Agent search by location

### Week 4: WhatsApp Bot
- Twilio WhatsApp API integration
- Natural language property search
- Automated responses

## 💡 Usage Examples

### Example 1: Find Properties Along Commute Route
```python
# User: "Show me properties from Ajah to Victoria Island under ₦50M"

searcher = RouteSearcher()
results = searcher.search_by_budget_along_route(
    origin="Ajah",
    destination="Victoria Island",
    budget=50000000,
    bedrooms=3
)

for prop in results['properties']:
    print(f"{prop['zone_name']}: {prop['price_range']}")
```

### Example 2: Validate Nigerian Address
```python
# User: "Is this address valid? 15 Admiralty Way, Lekki"

geocoder = Geocoder()
validation = geocoder.validate_nigerian_address("15 Admiralty Way, Lekki, Lagos")

if validation['valid']:
    print(f"✅ Valid address in {validation['state']}")
    print(f"Nearest zone: {validation['nearest_zone']}")
```

### Example 3: Compare Multiple Routes
```python
# User: "Compare properties from Ikeja to Lekki vs VI vs Ikoyi"

searcher = RouteSearcher()
comparisons = searcher.compare_routes(
    origin="Ikeja GRA",
    destinations=["Lekki Phase 1", "Victoria Island", "Ikoyi"]
)

for route in comparisons:
    print(f"To {route['destination']}: {route['properties_found']} properties")
    print(f"  Avg price: ₦{route['avg_price_per_sqm']:,}/sqm")
```

## 📝 Notes

- **Development:** Use test API key with no restrictions
- **Production:** Apply IP restrictions and API limits
- **Caching:** Store frequent queries to reduce costs
- **Monitoring:** Check Google Cloud Console for usage stats

---

**© 2025 AMD Solutions. All Rights Reserved.**
