"""
Naija-Prop-Intel: AI Real Estate Intelligence Engine
© 2025 AMD Solutions. All Rights Reserved.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  EDUCATIONAL USE ONLY - Commercial use REQUIRES LICENSE
📧 Contact: ceo@amdsolutions007.com for commercial licensing
💼 Licenses: $500 (Startup) | $2,500 (Business) | $5,000 (Enterprise)
🚨 Unauthorized commercial use = Copyright infringement
See USAGE_NOTICE.md for full terms
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Property analysis engine with Nigerian-specific intelligence:
- Flood risk detection (40% weight)
- Security analysis (30% weight)
- Infrastructure scoring (30% weight)
- Investment ROI calculator with hidden costs
- Omo Onile fee intelligence
"""

import json
import os
from typing import Dict, Any, Tuple


class PropertyAnalyzer:
    """Core intelligence engine for Nigerian property analysis"""
    
    def __init__(self, zones_file: str = "data/zones.json"):
        """Initialize analyzer with zones database"""
        self.zones_file = zones_file
        self.zones_data = self._load_zones()
    
    def _load_zones(self) -> Dict:
        """Load property zones database"""
        if not os.path.exists(self.zones_file):
            raise FileNotFoundError(
                f"Zones database not found: {self.zones_file}\n"
                f"Please ensure data/zones.json exists."
            )
        
        with open(self.zones_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get('zones', {})
    
    def get_available_locations(self) -> list:
        """Get list of available locations"""
        return sorted(self.zones_data.keys())
    
    def analyze_property(
        self, 
        location: str, 
        price: float, 
        property_type: str = "3-bedroom"
    ) -> Dict[str, Any]:
        """
        Analyze property with weighted risk scoring
        
        Scoring Formula:
        Smart Score = (100 - flood_risk) * 0.4 + security_score * 0.3 + infrastructure_score * 0.3
        
        Args:
            location: Property location (e.g., "Ajah", "Lekki Phase 1")
            price: Property price in Naira
            property_type: Type of property (default: "3-bedroom")
        
        Returns:
            Comprehensive analysis with smart score, risks, and recommendations
        """
        # Normalize location name
        location_key = self._normalize_location(location)
        
        if location_key not in self.zones_data:
            return {
                "error": f"Location '{location}' not found in database",
                "available_locations": self.get_available_locations()
            }
        
        zone = self.zones_data[location_key]
        
        # Extract risk components
        flood_risk = zone['flood_risk']['score']
        security_score = zone['security']['score']
        infrastructure_score = zone['infrastructure']['score']
        
        # Calculate weighted Smart Score (0-100%)
        # Invert flood risk (lower is better)
        flood_safety = 100 - flood_risk
        smart_score = (
            flood_safety * 0.4 + 
            security_score * 0.3 + 
            infrastructure_score * 0.3
        )
        
        # Price analysis
        avg_price_sqm = zone['market_data']['avg_price_per_sqm']
        price_verdict = self._evaluate_price(price, avg_price_sqm, location_key)
        
        # Risk level determination
        if smart_score >= 80:
            overall_risk = "LOW"
            recommendation = "✅ EXCELLENT INVESTMENT - Low risk, strong fundamentals"
        elif smart_score >= 65:
            overall_risk = "MODERATE"
            recommendation = "⚠️ PROCEED WITH CAUTION - Good potential, some risks"
        else:
            overall_risk = "HIGH"
            recommendation = "🚨 HIGH RISK - Significant concerns, reconsider"
        
        # Build comprehensive analysis
        analysis = {
            "location": zone['location'],
            "property_type": property_type,
            "price_offered": f"₦{price:,.0f}",
            "smart_score": round(smart_score, 1),
            "overall_risk": overall_risk,
            "recommendation": recommendation,
            
            "risk_breakdown": {
                "flood_risk": {
                    "score": flood_risk,
                    "level": zone['flood_risk']['level'],
                    "weight": "40%",
                    "last_major_flood": zone['flood_risk']['last_major_flood'],
                    "rainy_season": zone['flood_risk']['rainy_season_danger'],
                    "drainage": zone['flood_risk']['drainage_quality']
                },
                "security": {
                    "score": security_score,
                    "level": zone['security']['level'],
                    "weight": "30%",
                    "police_stations": zone['security']['police_stations'],
                    "incidents_2024": zone['security']['robbery_incidents_2024'],
                    "safe_hours": zone['security']['safe_hours']
                },
                "infrastructure": {
                    "score": infrastructure_score,
                    "level": self._score_to_level(infrastructure_score),
                    "weight": "30%",
                    "road_quality": zone['infrastructure']['road_quality'],
                    "power_hours": zone['infrastructure']['power_hours_per_day'],
                    "water_source": zone['infrastructure']['water_source'],
                    "internet": "Yes" if zone['infrastructure']['fiber_internet'] else "No"
                }
            },
            
            "price_analysis": price_verdict,
            
            "hidden_costs": {
                "omo_onile": f"₦{zone['hidden_costs']['omo_onile']:,.0f}",
                "land_survey": f"₦{zone['hidden_costs']['land_survey']:,.0f}",
                "flood_insurance": f"₦{zone['hidden_costs']['flood_insurance']:,.0f}",
                "monthly_generator": f"₦{zone['hidden_costs']['generator_diesel_monthly']:,.0f}",
                "total_hidden": f"₦{self._calculate_total_hidden(zone['hidden_costs']):,.0f}"
            },
            
            "market_intelligence": {
                "avg_price_per_sqm": f"₦{avg_price_sqm:,.0f}",
                "typical_range": zone['market_data']['price_range'],
                "5yr_appreciation": f"{zone['market_data']['5yr_appreciation'] * 100}%",
                "rental_yield": f"{zone['market_data']['rental_yield'] * 100}%",
                "days_to_sell": zone['market_data']['days_to_sell_avg'],
                "demand": zone['market_data']['demand_level']
            },
            
            "local_notes": zone['notes']
        }
        
        return analysis
    
    def calculate_roi(
        self, 
        price: float, 
        location: str, 
        holding_period: int = 5
    ) -> Dict[str, Any]:
        """
        Calculate Investment ROI with Nigerian hidden costs
        
        Formula:
        ROI = ((Price × Rental_Yield × Years) + (Price × Appreciation) - Hidden_Costs) / Price × 100
        
        Args:
            price: Property purchase price
            location: Property location
            holding_period: Investment period in years (default: 5)
        
        Returns:
            ROI analysis with income breakdown and hidden costs
        """
        location_key = self._normalize_location(location)
        
        if location_key not in self.zones_data:
            return {
                "error": f"Location '{location}' not found in database",
                "available_locations": self.get_available_locations()
            }
        
        zone = self.zones_data[location_key]
        
        # Extract market data
        rental_yield = zone['market_data']['rental_yield']
        appreciation_rate = zone['market_data']['5yr_appreciation']
        
        # Calculate income streams
        annual_rental_income = price * rental_yield
        total_rental_income = annual_rental_income * holding_period
        
        # Calculate capital appreciation
        appreciation_total = appreciation_rate * holding_period
        capital_gain = price * appreciation_total
        
        # Calculate hidden costs (one-time + recurring)
        hidden = zone['hidden_costs']
        one_time_costs = (
            hidden['omo_onile'] + 
            hidden['land_survey']
        )
        
        # Recurring costs (generator, insurance, maintenance)
        monthly_costs = hidden['generator_diesel_monthly']
        annual_costs = monthly_costs * 12 + hidden['flood_insurance']
        
        # Add borehole maintenance if applicable
        if 'borehole_maintenance' in hidden:
            annual_costs += hidden['borehole_maintenance']
        
        # Add estate service charge if applicable
        if 'estate_service_charge' in hidden:
            annual_costs += hidden['estate_service_charge']
        
        total_recurring_costs = annual_costs * holding_period
        total_hidden_costs = one_time_costs + total_recurring_costs
        
        # Calculate net ROI
        gross_return = total_rental_income + capital_gain
        net_return = gross_return - total_hidden_costs
        roi_percentage = (net_return / price) * 100
        
        # Determine verdict
        if roi_percentage >= 80:
            verdict = "🎯 EXCELLENT - Strong returns expected"
        elif roi_percentage >= 50:
            verdict = "✅ GOOD - Solid investment potential"
        elif roi_percentage >= 30:
            verdict = "⚠️ FAIR - Modest returns, consider alternatives"
        else:
            verdict = "❌ POOR - Low returns, high risk"
        
        return {
            "location": zone['location'],
            "investment_price": f"₦{price:,.0f}",
            "holding_period": f"{holding_period} years",
            
            "returns": {
                "rental_income": {
                    "annual": f"₦{annual_rental_income:,.0f}",
                    "total": f"₦{total_rental_income:,.0f}",
                    "yield": f"{rental_yield * 100}%"
                },
                "capital_gain": {
                    "total": f"₦{capital_gain:,.0f}",
                    "appreciation_rate": f"{appreciation_total * 100}%"
                },
                "gross_return": f"₦{gross_return:,.0f}"
            },
            
            "costs": {
                "one_time": {
                    "omo_onile": f"₦{hidden['omo_onile']:,.0f}",
                    "land_survey": f"₦{hidden['land_survey']:,.0f}",
                    "subtotal": f"₦{one_time_costs:,.0f}"
                },
                "recurring_annual": {
                    "generator_fuel": f"₦{monthly_costs * 12:,.0f}",
                    "flood_insurance": f"₦{hidden['flood_insurance']:,.0f}",
                    "other_annual": f"₦{annual_costs - monthly_costs * 12 - hidden['flood_insurance']:,.0f}",
                    "subtotal": f"₦{annual_costs:,.0f}"
                },
                "total_hidden_costs": f"₦{total_hidden_costs:,.0f}"
            },
            
            "net_analysis": {
                "net_return": f"₦{net_return:,.0f}",
                "roi_percentage": f"{roi_percentage:.1f}%",
                "verdict": verdict,
                "annual_roi": f"{roi_percentage / holding_period:.1f}%"
            },
            
            "market_context": {
                "days_to_sell": zone['market_data']['days_to_sell_avg'],
                "demand_level": zone['market_data']['demand_level'],
                "liquidity": "High" if zone['market_data']['days_to_sell_avg'] < 90 else "Moderate" if zone['market_data']['days_to_sell_avg'] < 150 else "Low"
            }
        }
    
    def _normalize_location(self, location: str) -> str:
        """Normalize location name for database lookup"""
        # Try exact match first
        if location in self.zones_data:
            return location
        
        # Try case-insensitive match
        location_lower = location.lower()
        for key in self.zones_data.keys():
            if key.lower() == location_lower:
                return key
        
        # Try partial match
        for key in self.zones_data.keys():
            if location_lower in key.lower():
                return key
        
        return location
    
    def _evaluate_price(
        self, 
        offered_price: float, 
        avg_price_sqm: float, 
        location: str
    ) -> Dict[str, str]:
        """Evaluate if price is fair, overpriced, or underpriced"""
        zone = self.zones_data[location]
        price_range = zone['market_data']['price_range']
        
        # Extract typical range for 3-bedroom
        # Format: "₦25M - ₦60M (3-bedroom)"
        import re
        match = re.search(r'₦(\d+)M\s*-\s*₦(\d+)M', price_range)
        
        if match:
            low_range = float(match.group(1)) * 1_000_000
            high_range = float(match.group(2)) * 1_000_000
            mid_range = (low_range + high_range) / 2
            
            # Determine verdict
            if offered_price < low_range * 0.9:
                verdict = "🎉 BARGAIN - Below market, investigate why"
                status = "UNDERPRICED"
            elif offered_price <= mid_range:
                verdict = "✅ FAIR PRICE - Within typical range"
                status = "FAIR"
            elif offered_price <= high_range:
                verdict = "⚠️ HIGH - Upper range, negotiate down"
                status = "ELEVATED"
            else:
                verdict = "🚨 OVERPRICED - Above market, avoid"
                status = "OVERPRICED"
            
            return {
                "verdict": verdict,
                "status": status,
                "market_range": price_range,
                "offered_price": f"₦{offered_price:,.0f}",
                "market_median": f"₦{mid_range:,.0f}"
            }
        
        return {
            "verdict": "⚠️ UNABLE TO DETERMINE - Verify market research",
            "status": "UNKNOWN",
            "market_range": price_range,
            "offered_price": f"₦{offered_price:,.0f}"
        }
    
    def _calculate_total_hidden(self, hidden_costs: Dict) -> float:
        """Calculate total one-time hidden costs"""
        total = (
            hidden_costs['omo_onile'] +
            hidden_costs['land_survey'] +
            hidden_costs['flood_insurance']
        )
        return total
    
    def _score_to_level(self, score: int) -> str:
        """Convert numeric score to risk level"""
        if score >= 80:
            return "EXCELLENT"
        elif score >= 65:
            return "GOOD"
        elif score >= 50:
            return "MODERATE"
        else:
            return "POOR"


# Quick test function
def test_analyzer():
    """Test the analyzer with sample data"""
    analyzer = PropertyAnalyzer()
    
    print("🏠 NAIJA-PROP-INTEL TEST")
    print("=" * 50)
    
    # Test 1: High-risk location (Ajah)
    print("\n📍 TEST 1: AJAH (High Flood Risk)")
    result = analyzer.analyze_property("Ajah", 45_000_000)
    print(f"Smart Score: {result['smart_score']}/100")
    print(f"Risk Level: {result['overall_risk']}")
    print(f"Recommendation: {result['recommendation']}")
    
    # Test 2: Premium location (Ikoyi)
    print("\n📍 TEST 2: IKOYI (Premium)")
    result = analyzer.analyze_property("Ikoyi", 400_000_000)
    print(f"Smart Score: {result['smart_score']}/100")
    print(f"Risk Level: {result['overall_risk']}")
    print(f"Price Verdict: {result['price_analysis']['verdict']}")
    
    # Test 3: ROI Calculation
    print("\n💰 TEST 3: ROI ANALYSIS - LEKKI PHASE 1")
    roi = analyzer.calculate_roi(120_000_000, "Lekki Phase 1", holding_period=5)
    print(f"5-Year ROI: {roi['net_analysis']['roi_percentage']}")
    print(f"Verdict: {roi['net_analysis']['verdict']}")
    print(f"Total Hidden Costs: {roi['costs']['total_hidden_costs']}")
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    test_analyzer()
