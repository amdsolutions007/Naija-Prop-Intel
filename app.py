"""
Naija-Prop-Intel: Property Intelligence CLI
© 2025 AMD Solutions. All Rights Reserved.

Interactive CLI for Nigerian property analysis
"""

import sys
import os
from analyzer import PropertyAnalyzer


def print_banner():
    """Display application banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                  NAIJA-PROP-INTEL v0.1.0                 ║
║          AI Real Estate Intelligence - Nigeria           ║
║                                                           ║
║     Flood Risk • Security • ROI • Omo Onile Calculator   ║
║                                                           ║
║            © 2025 AMD Solutions - Licensed               ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_section(title: str):
    """Print section header"""
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print('─' * 60)


def format_dict_output(data: dict, indent: int = 0):
    """Pretty print nested dictionary"""
    prefix = "  " * indent
    
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{prefix}{key.replace('_', ' ').title()}:")
            format_dict_output(value, indent + 1)
        elif isinstance(value, list):
            print(f"{prefix}{key.replace('_', ' ').title()}: {', '.join(map(str, value))}")
        else:
            print(f"{prefix}{key.replace('_', ' ').title()}: {value}")


def analyze_property_interactive(analyzer: PropertyAnalyzer):
    """Interactive property analysis mode"""
    print_section("🏠 PROPERTY ANALYSIS")
    
    # Show available locations
    locations = analyzer.get_available_locations()
    print("\n📍 Available Locations:")
    for i, loc in enumerate(locations, 1):
        print(f"  {i}. {loc}")
    
    # Get user input
    print("\n" + "─" * 60)
    location = input("Enter location name (or number): ").strip()
    
    # Handle numeric input
    if location.isdigit():
        idx = int(location) - 1
        if 0 <= idx < len(locations):
            location = locations[idx]
        else:
            print("❌ Invalid location number")
            return
    
    # Get price
    try:
        price_input = input("Enter property price (₦): ").strip()
        # Remove commas and ₦ symbol
        price_input = price_input.replace(',', '').replace('₦', '')
        price = float(price_input)
    except ValueError:
        print("❌ Invalid price format")
        return
    
    property_type = input("Property type (default: 3-bedroom): ").strip() or "3-bedroom"
    
    # Perform analysis
    print("\n🔍 Analyzing property...")
    result = analyzer.analyze_property(location, price, property_type)
    
    if 'error' in result:
        print(f"\n❌ {result['error']}")
        return
    
    # Display results
    print_section("📊 ANALYSIS RESULTS")
    
    print(f"\n📍 Location: {result['location']}")
    print(f"🏘️  Property Type: {result['property_type']}")
    print(f"💰 Price Offered: {result['price_offered']}")
    
    print(f"\n🎯 SMART SCORE: {result['smart_score']}/100")
    print(f"⚠️  OVERALL RISK: {result['overall_risk']}")
    print(f"\n{result['recommendation']}")
    
    # Risk breakdown
    print_section("🔍 RISK BREAKDOWN")
    
    flood = result['risk_breakdown']['flood_risk']
    print(f"\n🌊 FLOOD RISK ({flood['weight']})")
    print(f"   Score: {flood['score']}/100 - {flood['level']}")
    print(f"   Last Major Flood: {flood['last_major_flood']}")
    print(f"   Rainy Season: {flood['rainy_season']}")
    print(f"   Drainage: {flood['drainage']}")
    
    security = result['risk_breakdown']['security']
    print(f"\n🔒 SECURITY ({security['weight']})")
    print(f"   Score: {security['score']}/100 - {security['level']}")
    print(f"   Police Stations: {security['police_stations']}")
    print(f"   Incidents (2024): {security['incidents_2024']}")
    print(f"   Safe Hours: {security['safe_hours']}")
    
    infra = result['risk_breakdown']['infrastructure']
    print(f"\n🏗️  INFRASTRUCTURE ({infra['weight']})")
    print(f"   Score: {infra['score']}/100 - {infra['level']}")
    print(f"   Road Quality: {infra['road_quality']}/100")
    print(f"   Power Hours/Day: {infra['power_hours']} hours")
    print(f"   Water Source: {infra['water_source']}")
    print(f"   Fiber Internet: {infra['internet']}")
    
    # Price analysis
    print_section("💵 PRICE ANALYSIS")
    price_analysis = result['price_analysis']
    print(f"\n{price_analysis['verdict']}")
    print(f"Status: {price_analysis['status']}")
    print(f"Market Range: {price_analysis['market_range']}")
    print(f"Market Median: {price_analysis.get('market_median', 'N/A')}")
    
    # Hidden costs
    print_section("⚠️  HIDDEN COSTS (The Omo Onile Factor)")
    hidden = result['hidden_costs']
    print(f"\n💸 Omo Onile Fees: {hidden['omo_onile']}")
    print(f"📋 Land Survey: {hidden['land_survey']}")
    print(f"🌊 Flood Insurance: {hidden['flood_insurance']}")
    print(f"⚡ Generator (Monthly): {hidden['monthly_generator']}")
    print(f"\n💰 TOTAL HIDDEN COSTS: {hidden['total_hidden']}")
    print("   (Factor this into your budget!)")
    
    # Market intelligence
    print_section("📈 MARKET INTELLIGENCE")
    market = result['market_intelligence']
    print(f"\nAvg Price/Sqm: {market['avg_price_per_sqm']}")
    print(f"Typical Range: {market['typical_range']}")
    print(f"5-Year Appreciation: {market['5yr_appreciation']}")
    print(f"Rental Yield: {market['rental_yield']}")
    print(f"Days to Sell: {market['days_to_sell']} days")
    print(f"Demand Level: {market['demand']}")
    
    # Local notes
    print_section("📝 LOCAL INTELLIGENCE")
    print(f"\n{result['local_notes']}")
    
    print("\n" + "═" * 60)


def calculate_roi_interactive(analyzer: PropertyAnalyzer):
    """Interactive ROI calculation mode"""
    print_section("💰 INVESTMENT ROI CALCULATOR")
    
    # Show available locations
    locations = analyzer.get_available_locations()
    print("\n📍 Available Locations:")
    for i, loc in enumerate(locations, 1):
        print(f"  {i}. {loc}")
    
    # Get user input
    print("\n" + "─" * 60)
    location = input("Enter location name (or number): ").strip()
    
    # Handle numeric input
    if location.isdigit():
        idx = int(location) - 1
        if 0 <= idx < len(locations):
            location = locations[idx]
        else:
            print("❌ Invalid location number")
            return
    
    # Get investment details
    try:
        price_input = input("Enter investment price (₦): ").strip()
        price_input = price_input.replace(',', '').replace('₦', '')
        price = float(price_input)
        
        holding_input = input("Holding period in years (default: 5): ").strip()
        holding_period = int(holding_input) if holding_input else 5
    except ValueError:
        print("❌ Invalid input format")
        return
    
    # Calculate ROI
    print("\n💹 Calculating ROI...")
    result = analyzer.calculate_roi(price, location, holding_period)
    
    if 'error' in result:
        print(f"\n❌ {result['error']}")
        return
    
    # Display results
    print_section("📊 ROI ANALYSIS")
    
    print(f"\n📍 Location: {result['location']}")
    print(f"💰 Investment Price: {result['investment_price']}")
    print(f"⏱️  Holding Period: {result['holding_period']}")
    
    # Returns
    print_section("📈 EXPECTED RETURNS")
    
    rental = result['returns']['rental_income']
    print(f"\n🏠 Rental Income:")
    print(f"   Annual: {rental['annual']} ({rental['yield']} yield)")
    print(f"   Total ({holding_period} years): {rental['total']}")
    
    capital = result['returns']['capital_gain']
    print(f"\n📊 Capital Appreciation:")
    print(f"   Total Gain: {capital['total']}")
    print(f"   Appreciation Rate: {capital['appreciation_rate']}")
    
    print(f"\n💵 Gross Return: {result['returns']['gross_return']}")
    
    # Costs
    print_section("💸 COSTS BREAKDOWN")
    
    one_time = result['costs']['one_time']
    print(f"\n🔴 One-Time Costs:")
    print(f"   Omo Onile: {one_time['omo_onile']}")
    print(f"   Land Survey: {one_time['land_survey']}")
    print(f"   Subtotal: {one_time['subtotal']}")
    
    recurring = result['costs']['recurring_annual']
    print(f"\n🔄 Recurring Annual Costs:")
    print(f"   Generator Fuel: {recurring['generator_fuel']}")
    print(f"   Flood Insurance: {recurring['flood_insurance']}")
    print(f"   Other: {recurring['other_annual']}")
    print(f"   Subtotal: {recurring['subtotal']}")
    
    print(f"\n💰 TOTAL HIDDEN COSTS ({holding_period} years): {result['costs']['total_hidden_costs']}")
    
    # Net analysis
    print_section("🎯 NET ANALYSIS")
    
    net = result['net_analysis']
    print(f"\n💎 Net Return: {net['net_return']}")
    print(f"📊 ROI: {net['roi_percentage']} ({net['annual_roi']} per year)")
    print(f"\n{net['verdict']}")
    
    # Market context
    print_section("📈 MARKET CONTEXT")
    market = result['market_context']
    print(f"\nDays to Sell: {market['days_to_sell']} days")
    print(f"Demand Level: {market['demand_level']}")
    print(f"Liquidity: {market['liquidity']}")
    
    print("\n" + "═" * 60)


def main():
    """Main CLI application"""
    print_banner()
    
    # Initialize analyzer
    try:
        analyzer = PropertyAnalyzer()
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPlease ensure the data/zones.json file exists.")
        sys.exit(1)
    
    while True:
        print("\n" + "═" * 60)
        print("MAIN MENU")
        print("═" * 60)
        print("1. 🏠 Analyze Property (Risk + Price)")
        print("2. 💰 Calculate ROI (Investment Returns)")
        print("3. 📍 List Available Locations")
        print("4. ❌ Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            analyze_property_interactive(analyzer)
        elif choice == "2":
            calculate_roi_interactive(analyzer)
        elif choice == "3":
            print_section("📍 AVAILABLE LOCATIONS")
            locations = analyzer.get_available_locations()
            for i, loc in enumerate(locations, 1):
                print(f"  {i}. {loc}")
        elif choice == "4":
            print("\n👋 Thank you for using Naija-Prop-Intel!")
            print("💡 Save millions on your next property deal.")
            print("\n© 2025 AMD Solutions - Licensed Software")
            break
        else:
            print("\n❌ Invalid option. Please select 1-4.")
        
        input("\n⏎ Press ENTER to continue...")


if __name__ == "__main__":
    main()
