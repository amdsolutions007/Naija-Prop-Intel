"""
Naija-Prop-Intel: WhatsApp Bot (Week 4)
Twilio WhatsApp Business API Integration

Business Impact:
- 90% of Nigerians use WhatsApp daily
- Natural language property queries
- Instant flood risk & security analysis
- Agent discovery via WhatsApp
- FREE tier: 1,000 messages/month

User Flow Examples:
- "Property in Lekki ₦2M" → Returns matches with flood/security scores
- "Flood risk in Ajah?" → Returns Smart Score and analysis
- "Find agent in Lagos" → Lists verified agents
- "Properties from Ajah to Lekki" → Route-based search
"""

import os
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Twilio imports
try:
    from twilio.rest import Client
    from twilio.twiml.messaging_response import MessagingResponse
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("⚠️  Twilio not installed. Run: pip install twilio")

# Import our systems
try:
    from agent_system_v2 import AgentSystem
    AGENT_SYSTEM_AVAILABLE = True
except ImportError:
    AGENT_SYSTEM_AVAILABLE = False
    print("⚠️  agent_system_v2.py not found")

try:
    from route_search import RouteSearcher
    ROUTE_SEARCH_AVAILABLE = True
except ImportError:
    ROUTE_SEARCH_AVAILABLE = False
    print("⚠️  route_search.py not found")

try:
    from geocoding import Geocoder
    GEOCODING_AVAILABLE = True
except ImportError:
    GEOCODING_AVAILABLE = False
    print("⚠️  geocoding.py not found")


class WhatsAppBot:
    """
    Naija-Prop-Intel WhatsApp Bot
    Handles natural language queries for property intelligence
    """
    
    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_whatsapp_number: Optional[str] = None,
        zones_file: str = "data/zones.json"
    ):
        """
        Initialize WhatsApp Bot
        
        Args:
            account_sid: Twilio Account SID (or from env TWILIO_ACCOUNT_SID)
            auth_token: Twilio Auth Token (or from env TWILIO_AUTH_TOKEN)
            from_whatsapp_number: WhatsApp number (or from env TWILIO_WHATSAPP_NUMBER)
            zones_file: Path to zones.json
        """
        # Load credentials from environment if not provided
        self.account_sid = account_sid or os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = auth_token or os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = from_whatsapp_number or os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        
        # Initialize Twilio client
        if TWILIO_AVAILABLE and self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            self.twilio_enabled = True
        else:
            self.client = None
            self.twilio_enabled = False
        
        # Load zones data
        self.zones = self._load_zones(zones_file)
        
        # Initialize integrated systems
        if AGENT_SYSTEM_AVAILABLE:
            self.agent_system = AgentSystem()
        else:
            self.agent_system = None
        
        if ROUTE_SEARCH_AVAILABLE:
            try:
                self.route_searcher = RouteSearcher()
            except:
                self.route_searcher = None
        else:
            self.route_searcher = None
        
        if GEOCODING_AVAILABLE:
            try:
                self.geocoder = Geocoder()
            except:
                self.geocoder = None
        else:
            self.geocoder = None
        
        # Query patterns
        self._compile_patterns()
    
    def _load_zones(self, zones_file: str) -> Dict[str, Any]:
        """Load zones data from JSON file"""
        try:
            with open(zones_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('zones', {})
        except FileNotFoundError:
            print(f"⚠️  {zones_file} not found. Bot will have limited functionality.")
            return {}
        except json.JSONDecodeError:
            print(f"⚠️  Error parsing {zones_file}")
            return {}
    
    def _compile_patterns(self):
        """Compile regex patterns for query matching"""
        # Price pattern: ₦2M, ₦50M, 2 million, etc.
        self.price_pattern = re.compile(r'₦?\s*(\d+(?:\.\d+)?)\s*(m|million|k|thousand|b|billion)', re.IGNORECASE)
        
        # Location pattern: "in Lekki", "at Ajah", "Victoria Island"
        self.location_pattern = re.compile(r'(?:in|at|near|around)\s+([A-Za-z\s]+?)(?:\s|$|,|\?)', re.IGNORECASE)
        
        # Route pattern: "from X to Y", "X to Y"
        self.route_pattern = re.compile(r'(?:from\s+)?([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+)', re.IGNORECASE)
        
        # Flood risk queries
        self.flood_pattern = re.compile(r'flood|flooding|water|drainage', re.IGNORECASE)
        
        # Security queries
        self.security_pattern = re.compile(r'security|safe|crime|robbery|police', re.IGNORECASE)
        
        # Agent queries
        self.agent_pattern = re.compile(r'agent|broker|realtor|representative', re.IGNORECASE)
        
        # Property type
        self.property_pattern = re.compile(r'(\d+)\s*(?:bed|bedroom|br)', re.IGNORECASE)
    
    def send_message(self, to_whatsapp_number: str, message: str) -> Dict[str, Any]:
        """
        Send WhatsApp message via Twilio
        
        Args:
            to_whatsapp_number: Recipient WhatsApp number (format: whatsapp:+2348012345678)
            message: Message text
        
        Returns:
            Dict with status and message SID
        """
        if not self.twilio_enabled:
            return {
                "status": "error",
                "message": "Twilio not configured. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN"
            }
        
        try:
            # Ensure proper WhatsApp format
            if not to_whatsapp_number.startswith('whatsapp:'):
                to_whatsapp_number = f"whatsapp:{to_whatsapp_number}"
            
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_whatsapp_number
            )
            
            return {
                "status": "success",
                "message_sid": message_obj.sid,
                "to": to_whatsapp_number,
                "message": "Message sent successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send message: {str(e)}"
            }
    
    def process_query(self, query: str, user_phone: Optional[str] = None) -> str:
        """
        Process natural language query and generate response
        
        Args:
            query: User's WhatsApp message
            user_phone: User's phone number (optional, for tracking)
        
        Returns:
            Response message
        """
        query = query.strip()
        
        # Check for route-based queries first
        if "to" in query.lower() and self.route_pattern.search(query):
            return self._handle_route_query(query)
        
        # Check for flood risk queries
        if self.flood_pattern.search(query):
            return self._handle_flood_query(query)
        
        # Check for security queries
        if self.security_pattern.search(query):
            return self._handle_security_query(query)
        
        # Check for agent queries
        if self.agent_pattern.search(query):
            return self._handle_agent_query(query)
        
        # Check for property search with price
        if self.price_pattern.search(query):
            return self._handle_property_search(query)
        
        # Check for location info
        location_match = self.location_pattern.search(query)
        if location_match:
            return self._handle_location_info(location_match.group(1).strip())
        
        # Default: Show help
        return self._get_help_message()
    
    def _handle_route_query(self, query: str) -> str:
        """Handle route-based property queries (Ajah to Lekki)"""
        match = self.route_pattern.search(query)
        if not match:
            return "❌ Could not parse route. Try: 'Properties from Ajah to Lekki'"
        
        origin = match.group(1).strip()
        destination = match.group(2).strip()
        
        # Extract budget if provided
        budget = self._extract_price(query)
        
        if not self.route_searcher:
            return "❌ Route search not available. Google Maps API key required."
        
        try:
            if budget:
                # Budget-based search
                result = self.route_searcher.search_by_budget_along_route(
                    origin=origin,
                    destination=destination,
                    budget=budget,
                    bedrooms=3
                )
            else:
                # General corridor search
                result = self.route_searcher.search_route_corridor(
                    origin=origin,
                    destination=destination,
                    corridor_width_km=5
                )
            
            if result['status'] != 'success':
                return f"❌ {result.get('message', 'Route search failed')}"
            
            properties = result.get('properties', [])
            
            if not properties:
                return f"❌ No properties found along {origin} to {destination} route"
            
            # Format response
            response = f"🏠 *PROPERTIES: {origin.upper()} → {destination.upper()}*\n"
            response += f"📊 Found: {len(properties)} properties\n"
            if budget:
                response += f"💰 Budget: ₦{budget:,}\n"
            response += "\n"
            
            for i, prop in enumerate(properties[:5], 1):  # Top 5
                zone_data = prop.get('zone_data', {})
                market = zone_data.get('market_data', {})
                flood = zone_data.get('flood_risk', {})
                security = zone_data.get('security', {})
                
                response += f"*{i}. {prop['zone_name']}*\n"
                response += f"💵 ₦{market.get('avg_price_per_sqm', 0):,}/sqm\n"
                response += f"🌊 Flood: {flood.get('level', 'Unknown')}\n"
                response += f"🛡️ Security: {security.get('level', 'Unknown')}\n"
                response += f"⭐ Smart Score: {prop.get('smart_score', 0):.1f}/100\n\n"
            
            return response.strip()
            
        except Exception as e:
            return f"❌ Route search error: {str(e)}"
    
    def _handle_flood_query(self, query: str) -> str:
        """Handle flood risk queries"""
        # Extract location
        location = self._extract_location(query)
        
        if not location:
            return "❌ Please specify a location. Try: 'Flood risk in Ajah'"
        
        # Find zone
        zone_name, zone_data = self._find_zone(location)
        
        if not zone_data:
            return f"❌ Location '{location}' not found. Try: 'List locations'"
        
        flood_data = zone_data.get('flood_risk', {})
        
        response = f"🌊 *FLOOD RISK: {zone_name.upper()}*\n\n"
        response += f"📊 Risk Score: {flood_data.get('score', 'N/A')}/100\n"
        response += f"⚠️ Risk Level: {flood_data.get('level', 'Unknown')}\n\n"
        
        if flood_data.get('affected_streets'):
            response += f"🚨 Affected Areas:\n{', '.join(flood_data['affected_streets'][:3])}\n\n"
        
        response += f"🏗️ Drainage: {flood_data.get('drainage_quality', 'Unknown')}\n"
        
        if flood_data.get('last_major_flood'):
            response += f"📅 Last Major Flood: {flood_data['last_major_flood']}\n"
        
        # Add recommendation
        score = flood_data.get('score', 100)
        if score < 30:
            response += "\n✅ *Low Risk* - Safe for investment"
        elif score < 60:
            response += "\n⚠️ *Medium Risk* - Check drainage systems"
        else:
            response += "\n🚨 *High Risk* - Consider alternatives"
        
        return response.strip()
    
    def _handle_security_query(self, query: str) -> str:
        """Handle security queries"""
        location = self._extract_location(query)
        
        if not location:
            return "❌ Please specify a location. Try: 'Security in Lekki'"
        
        zone_name, zone_data = self._find_zone(location)
        
        if not zone_data:
            return f"❌ Location '{location}' not found"
        
        security_data = zone_data.get('security', {})
        
        response = f"🛡️ *SECURITY: {zone_name.upper()}*\n\n"
        response += f"📊 Security Score: {security_data.get('score', 'N/A')}/100\n"
        response += f"⚠️ Security Level: {security_data.get('level', 'Unknown')}\n\n"
        response += f"👮 Police Stations: {security_data.get('police_stations', 0)}\n"
        response += f"🚨 Robbery Incidents (2024): {security_data.get('robbery_incidents_2024', 'N/A')}\n"
        response += f"🕐 Safe Hours: {security_data.get('safe_hours', 'Unknown')}\n"
        
        # Add recommendation
        score = security_data.get('score', 0)
        if score >= 70:
            response += "\n✅ *High Security* - Safe area"
        elif score >= 50:
            response += "\n⚠️ *Moderate Security* - Take precautions"
        else:
            response += "\n🚨 *Low Security* - Extra caution needed"
        
        return response.strip()
    
    def _handle_agent_query(self, query: str) -> str:
        """Handle agent search queries"""
        if not self.agent_system:
            return "❌ Agent system not available"
        
        # Extract location
        location = self._extract_location(query)
        state = None
        
        # Try to determine state from query
        nigerian_states = [
            "Lagos", "Abuja", "Kano", "Rivers", "Kaduna", "Oyo", "Edo", "Delta",
            "Ondo", "Ogun", "Kwara", "Osun", "Anambra", "Enugu", "Abia", "Imo",
            "Akwa Ibom", "Cross River", "Bayelsa", "Borno", "Adamawa", "Taraba"
        ]
        
        for state_name in nigerian_states:
            if state_name.lower() in query.lower():
                state = state_name
                break
        
        # If location found but not state, use location
        if location and not state:
            state = location
        
        if not state:
            state = "Lagos"  # Default
        
        try:
            result = self.agent_system.search_agents(
                state=state,
                verified_only=True,
                limit=5
            )
            
            if result['status'] != 'success':
                return f"❌ Agent search failed"
            
            agents = result.get('agents', [])
            
            if not agents:
                return f"❌ No verified agents found in {state}"
            
            response = f"👥 *VERIFIED AGENTS: {state.upper()}*\n"
            response += f"📊 Found: {len(agents)} agents\n\n"
            
            for i, agent in enumerate(agents[:5], 1):
                response += f"*{i}. {agent['name']}*\n"
                response += f"🏢 {agent.get('specialization', 'General')}\n"
                response += f"⭐ {agent['rating_display']}\n"
                response += f"📱 {agent['contact']['phone']}\n"
                
                if agent.get('zones_covered'):
                    zones = ', '.join(agent['zones_covered'][:3])
                    response += f"📍 Covers: {zones}\n"
                
                response += "\n"
            
            return response.strip()
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def _handle_property_search(self, query: str) -> str:
        """Handle property search with price filter"""
        price = self._extract_price(query)
        location = self._extract_location(query)
        bedrooms = self._extract_bedrooms(query)
        
        if not location:
            return "❌ Please specify a location. Try: 'Property in Lekki ₦50M'"
        
        zone_name, zone_data = self._find_zone(location)
        
        if not zone_data:
            return f"❌ Location '{location}' not found"
        
        market_data = zone_data.get('market_data', {})
        avg_price = market_data.get('avg_price_per_sqm', 0)
        
        # Estimate property size
        if bedrooms:
            sqm_map = {2: 80, 3: 120, 4: 160, 5: 200}
            estimated_sqm = sqm_map.get(bedrooms, 120)
        else:
            estimated_sqm = 120  # Default 3BR
        
        estimated_total = avg_price * estimated_sqm
        
        response = f"🏠 *PROPERTY INTEL: {zone_name.upper()}*\n\n"
        
        if price:
            response += f"💰 Your Budget: ₦{price:,}\n"
            response += f"💵 Avg Price: ₦{avg_price:,}/sqm\n"
            response += f"🏡 Est. Total ({estimated_sqm}sqm): ₦{estimated_total:,}\n\n"
            
            if price >= estimated_total:
                response += "✅ *WITHIN BUDGET*\n\n"
            else:
                response += "⚠️ *ABOVE BUDGET*\n"
                response += f"Consider {int((price / avg_price))}sqm property\n\n"
        else:
            response += f"💵 Avg Price: ₦{avg_price:,}/sqm\n\n"
        
        # Add risk scores
        flood = zone_data.get('flood_risk', {})
        security = zone_data.get('security', {})
        infrastructure = zone_data.get('infrastructure', {})
        
        response += f"🌊 Flood Risk: {flood.get('level', 'Unknown')} ({flood.get('score', 'N/A')}/100)\n"
        response += f"🛡️ Security: {security.get('level', 'Unknown')} ({security.get('score', 'N/A')}/100)\n"
        response += f"🏗️ Infrastructure: {infrastructure.get('road_quality', 'Unknown')}\n"
        response += f"⚡ Power: {infrastructure.get('power_hours_per_day', 'N/A')} hrs/day\n\n"
        
        # Market info
        response += f"📈 5-Year Appreciation: {market_data.get('5yr_appreciation', 'N/A')}\n"
        response += f"🏦 Rental Yield: {market_data.get('rental_yield', 'N/A')}\n"
        response += f"⏱️ Avg. Days to Sell: {market_data.get('days_to_sell_avg', 'N/A')}\n"
        
        return response.strip()
    
    def _handle_location_info(self, location: str) -> str:
        """Handle general location information queries"""
        zone_name, zone_data = self._find_zone(location)
        
        if not zone_data:
            return f"❌ Location '{location}' not found. Try: 'List locations'"
        
        market = zone_data.get('market_data', {})
        flood = zone_data.get('flood_risk', {})
        security = zone_data.get('security', {})
        infra = zone_data.get('infrastructure', {})
        
        response = f"📍 *{zone_name.upper()}*\n\n"
        response += f"💵 Avg Price: ₦{market.get('avg_price_per_sqm', 0):,}/sqm\n"
        response += f"🌊 Flood: {flood.get('level', 'Unknown')}\n"
        response += f"🛡️ Security: {security.get('level', 'Unknown')}\n"
        response += f"🏗️ Roads: {infra.get('road_quality', 'Unknown')}\n"
        response += f"⚡ Power: {infra.get('power_hours_per_day', 'N/A')} hrs/day\n"
        response += f"📈 5yr Growth: {market.get('5yr_appreciation', 'N/A')}\n"
        
        # Smart Score calculation
        smart_score = (
            security.get('score', 0) * 0.35 +
            infra.get('score', 0) * 0.35 +
            (100 - flood.get('score', 0)) * 0.30
        )
        
        response += f"\n⭐ *Smart Score: {smart_score:.1f}/100*"
        
        return response.strip()
    
    def _get_help_message(self) -> str:
        """Return help message with example queries"""
        return """🤖 *NAIJA-PROP-INTEL BOT*

I can help you with:

🏠 *Property Search*
"Property in Lekki ₦50M"
"3 bedroom in Ajah"

🗺️ *Route Search*
"Properties from Ajah to Lekki"
"Ajah to Victoria Island under ₦30M"

🌊 *Flood Risk*
"Flood risk in Ajah"
"Is Lekki safe from flooding?"

🛡️ *Security*
"Security in Victoria Island"
"Is Ajah safe?"

👥 *Find Agents*
"Find agent in Lagos"
"Verified agents in Lekki"

📍 *Location Info*
"Tell me about Lekki"
"Info on Victoria Island"

📋 *List Locations*
"List all locations"
"Show cities"

Type your query to get started! 🚀"""
    
    def _extract_price(self, text: str) -> Optional[int]:
        """Extract price from text (₦2M, 50million, etc.)"""
        match = self.price_pattern.search(text)
        if not match:
            return None
        
        amount = float(match.group(1))
        unit = match.group(2).lower()
        
        multiplier_map = {
            'm': 1_000_000,
            'million': 1_000_000,
            'k': 1_000,
            'thousand': 1_000,
            'b': 1_000_000_000,
            'billion': 1_000_000_000
        }
        
        return int(amount * multiplier_map.get(unit, 1))
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from text"""
        match = self.location_pattern.search(text)
        if match:
            return match.group(1).strip()
        
        # Try to find any zone name directly in text
        text_lower = text.lower()
        for zone_name in self.zones.keys():
            if zone_name.lower() in text_lower:
                return zone_name
        
        return None
    
    def _extract_bedrooms(self, text: str) -> Optional[int]:
        """Extract number of bedrooms from text"""
        match = self.property_pattern.search(text)
        if match:
            return int(match.group(1))
        return None
    
    def _find_zone(self, location: str) -> Tuple[Optional[str], Optional[Dict]]:
        """Find zone by partial name match"""
        location_lower = location.lower()
        
        # Exact match
        if location in self.zones:
            return location, self.zones[location]
        
        # Case-insensitive exact match
        for zone_name, zone_data in self.zones.items():
            if zone_name.lower() == location_lower:
                return zone_name, zone_data
        
        # Partial match
        for zone_name, zone_data in self.zones.items():
            if location_lower in zone_name.lower() or zone_name.lower() in location_lower:
                return zone_name, zone_data
        
        return None, None
    
    def get_webhook_response(self, incoming_message: str, from_number: str) -> str:
        """
        Generate TwiML response for Twilio webhook
        
        Args:
            incoming_message: Message received from user
            from_number: User's WhatsApp number
        
        Returns:
            TwiML XML response
        """
        response_text = self.process_query(incoming_message, from_number)
        
        if TWILIO_AVAILABLE:
            response = MessagingResponse()
            response.message(response_text)
            return str(response)
        else:
            return response_text


def demo_whatsapp_bot():
    """Demo the WhatsApp bot with sample queries"""
    print("=" * 70)
    print("NAIJA-PROP-INTEL: WHATSAPP BOT DEMO")
    print("=" * 70)
    
    bot = WhatsAppBot()
    
    if not bot.zones:
        print("\n❌ Error: zones.json not loaded. Cannot run demo.")
        return
    
    # Test queries
    test_queries = [
        "Property in Lekki ₦50M",
        "Flood risk in Ajah",
        "Security in Victoria Island",
        "Find agent in Lagos",
        "Properties from Ajah to Lekki",
        "Tell me about Ikoyi",
        "help"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. USER: {query}")
        print("-" * 70)
        response = bot.process_query(query)
        print(f"BOT:\n{response}")
        print()
    
    print("=" * 70)
    print("Demo complete! Bot is operational.")
    print("\nTo use with Twilio:")
    print("1. Set environment variables:")
    print("   export TWILIO_ACCOUNT_SID='your_account_sid'")
    print("   export TWILIO_AUTH_TOKEN='your_auth_token'")
    print("   export TWILIO_WHATSAPP_NUMBER='whatsapp:+14155238886'")
    print("\n2. Install Twilio: pip install twilio")
    print("\n3. Set up webhook at: https://yourserver.com/whatsapp")
    print("=" * 70)


if __name__ == "__main__":
    demo_whatsapp_bot()
