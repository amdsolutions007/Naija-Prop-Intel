"""
Naija-Prop-Intel: Property Data Scraper
Scrapes property listings from Jiji.ng and PropertyPro.ng
© 2025 AMD Solutions. All Rights Reserved.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  EDUCATIONAL USE ONLY - Commercial use REQUIRES LICENSE
📧 Contact: ceo@amdsolutions007.com for commercial licensing
💼 Licenses: $500 (Startup) | $2,500 (Business) | $5,000 (Enterprise)
🚨 Unauthorized commercial use = Copyright infringement
See USAGE_NOTICE.md for full terms
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Features:
- Automated data ingestion from major Nigerian property sites
- Populates properties.db with real-time listings
- Extracts: Price, Location, Bedrooms, Property Type, Agent Contact
- Rate limiting and error handling for reliable scraping
"""

import sqlite3
import json
import time
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

# Web scraping imports
try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False
    print("⚠️  Web scraping libraries not installed. Run: pip install requests beautifulsoup4")


class PropertyScraper:
    """
    Scrapes property listings from Nigerian real estate websites
    """
    
    def __init__(self, db_path: str = "data/properties.db"):
        """
        Initialize Property Scraper
        
        Args:
            db_path: Path to SQLite properties database
        """
        self.db_path = db_path
        self._init_database()
        
        # Rate limiting (respectful scraping)
        self.request_delay = 2  # seconds between requests
        
        # User agent (identify ourselves)
        self.headers = {
            'User-Agent': 'Naija-Prop-Intel/1.0 (Property Analysis Bot; +https://github.com/amdsolutions007/Naija-Prop-Intel)'
        }
    
    def _init_database(self):
        """Initialize properties database with schema"""
        Path("data").mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Properties table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                property_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                price INTEGER,
                location TEXT,
                zone TEXT,
                state TEXT,
                bedrooms INTEGER,
                bathrooms INTEGER,
                property_type TEXT,
                description TEXT,
                agent_name TEXT,
                agent_phone TEXT,
                source TEXT,
                source_url TEXT,
                scraped_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Scrape history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scrape_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                properties_found INTEGER DEFAULT 0,
                properties_added INTEGER DEFAULT 0,
                properties_updated INTEGER DEFAULT 0,
                status TEXT,
                error_message TEXT,
                scraped_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_properties_location ON properties(location)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_properties_zone ON properties(zone)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_properties_source ON properties(source)")
        
        conn.commit()
        conn.close()
    
    def ingest_market_data(self, sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Main function: Ingest property data from all sources
        
        Args:
            sources: List of sources to scrape (default: ['jiji', 'propertypro'])
        
        Returns:
            Dict with scraping results
        """
        if not SCRAPING_AVAILABLE:
            return {
                'status': 'error',
                'message': 'Scraping libraries not installed. Run: pip install requests beautifulsoup4'
            }
        
        if sources is None:
            sources = ['jiji', 'propertypro']
        
        results = {
            'status': 'success',
            'sources_scraped': 0,
            'total_properties_found': 0,
            'total_properties_added': 0,
            'total_properties_updated': 0,
            'sources': {}
        }
        
        for source in sources:
            print(f"\n📡 Scraping {source.upper()}...")
            
            if source.lower() == 'jiji':
                source_result = self.scrape_jiji()
            elif source.lower() == 'propertypro':
                source_result = self.scrape_propertypro()
            else:
                source_result = {'status': 'error', 'message': f'Unknown source: {source}'}
            
            results['sources'][source] = source_result
            
            if source_result.get('status') == 'success':
                results['sources_scraped'] += 1
                results['total_properties_found'] += source_result.get('properties_found', 0)
                results['total_properties_added'] += source_result.get('properties_added', 0)
                results['total_properties_updated'] += source_result.get('properties_updated', 0)
        
        # Log to database
        self._log_scrape_history(results)
        
        return results
    
    def scrape_jiji(self) -> Dict[str, Any]:
        """
        Scrape property listings from Jiji.ng
        
        Returns:
            Dict with scraping results
        """
        try:
            properties_found = 0
            properties_added = 0
            properties_updated = 0
            
            # Jiji.ng Lagos property search URLs
            search_urls = [
                'https://jiji.ng/lagos-state/houses-apartments-for-sale',
                'https://jiji.ng/lagos-state/houses-apartments-for-rent',
            ]
            
            for url in search_urls:
                print(f"  Fetching: {url}")
                
                # Respectful rate limiting
                time.sleep(self.request_delay)
                
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Parse property listings (Jiji's structure may change)
                    listings = soup.find_all('div', class_='b-list-advert__item')
                    
                    for listing in listings[:20]:  # Limit to 20 per page
                        property_data = self._parse_jiji_listing(listing, url)
                        
                        if property_data:
                            properties_found += 1
                            result = self._save_property(property_data)
                            
                            if result == 'added':
                                properties_added += 1
                            elif result == 'updated':
                                properties_updated += 1
                    
                except requests.RequestException as e:
                    print(f"  ⚠️  Error fetching {url}: {str(e)}")
                    continue
            
            return {
                'status': 'success',
                'source': 'jiji',
                'properties_found': properties_found,
                'properties_added': properties_added,
                'properties_updated': properties_updated
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'source': 'jiji',
                'message': str(e)
            }
    
    def scrape_propertypro(self) -> Dict[str, Any]:
        """
        Scrape property listings from PropertyPro.ng
        
        Returns:
            Dict with scraping results
        """
        try:
            properties_found = 0
            properties_added = 0
            properties_updated = 0
            
            # PropertyPro.ng Lagos property search URLs
            search_urls = [
                'https://www.propertypro.ng/property-for-sale/lagos',
                'https://www.propertypro.ng/property-for-rent/lagos',
            ]
            
            for url in search_urls:
                print(f"  Fetching: {url}")
                
                # Respectful rate limiting
                time.sleep(self.request_delay)
                
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Parse property listings (PropertyPro's structure may change)
                    listings = soup.find_all('div', class_='single-room-sale')
                    
                    for listing in listings[:20]:  # Limit to 20 per page
                        property_data = self._parse_propertypro_listing(listing, url)
                        
                        if property_data:
                            properties_found += 1
                            result = self._save_property(property_data)
                            
                            if result == 'added':
                                properties_added += 1
                            elif result == 'updated':
                                properties_updated += 1
                    
                except requests.RequestException as e:
                    print(f"  ⚠️  Error fetching {url}: {str(e)}")
                    continue
            
            return {
                'status': 'success',
                'source': 'propertypro',
                'properties_found': properties_found,
                'properties_added': properties_added,
                'properties_updated': properties_updated
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'source': 'propertypro',
                'message': str(e)
            }
    
    def _parse_jiji_listing(self, listing_element, source_url: str) -> Optional[Dict[str, Any]]:
        """Parse a single Jiji listing element"""
        try:
            # Extract data (structure may vary)
            title_elem = listing_element.find('div', class_='b-list-advert__item-title')
            price_elem = listing_element.find('div', class_='b-list-advert__item-price')
            location_elem = listing_element.find('div', class_='b-list-advert__item-location')
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            price_text = price_elem.get_text(strip=True) if price_elem else '0'
            location = location_elem.get_text(strip=True) if location_elem else 'Lagos'
            
            # Parse price
            price = self._parse_price(price_text)
            
            # Extract bedrooms
            bedrooms = self._extract_bedrooms(title)
            
            # Generate property ID
            property_id = f"jiji_{hash(title + price_text)}"
            
            return {
                'property_id': property_id,
                'title': title,
                'price': price,
                'location': location,
                'zone': self._extract_zone(location),
                'state': 'Lagos',
                'bedrooms': bedrooms,
                'bathrooms': None,
                'property_type': self._extract_property_type(title),
                'description': title,
                'agent_name': None,
                'agent_phone': None,
                'source': 'jiji',
                'source_url': source_url,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"  ⚠️  Error parsing Jiji listing: {str(e)}")
            return None
    
    def _parse_propertypro_listing(self, listing_element, source_url: str) -> Optional[Dict[str, Any]]:
        """Parse a single PropertyPro listing element"""
        try:
            # Extract data (structure may vary)
            title_elem = listing_element.find('h4', class_='room-name')
            price_elem = listing_element.find('span', class_='price')
            location_elem = listing_element.find('address', class_='room-location')
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            price_text = price_elem.get_text(strip=True) if price_elem else '0'
            location = location_elem.get_text(strip=True) if location_elem else 'Lagos'
            
            # Parse price
            price = self._parse_price(price_text)
            
            # Extract bedrooms
            bedrooms = self._extract_bedrooms(title)
            
            # Generate property ID
            property_id = f"propertypro_{hash(title + price_text)}"
            
            return {
                'property_id': property_id,
                'title': title,
                'price': price,
                'location': location,
                'zone': self._extract_zone(location),
                'state': 'Lagos',
                'bedrooms': bedrooms,
                'bathrooms': None,
                'property_type': self._extract_property_type(title),
                'description': title,
                'agent_name': None,
                'agent_phone': None,
                'source': 'propertypro',
                'source_url': source_url,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"  ⚠️  Error parsing PropertyPro listing: {str(e)}")
            return None
    
    def _parse_price(self, price_text: str) -> int:
        """Parse price from text (₦50M, 50000000, etc.)"""
        try:
            # Remove ₦, commas, spaces
            clean_text = re.sub(r'[₦,\s]', '', price_text)
            
            # Handle millions (M)
            if 'M' in clean_text.upper():
                number = float(re.findall(r'[\d.]+', clean_text)[0])
                return int(number * 1_000_000)
            
            # Handle thousands (K)
            if 'K' in clean_text.upper():
                number = float(re.findall(r'[\d.]+', clean_text)[0])
                return int(number * 1_000)
            
            # Plain number
            number = re.findall(r'\d+', clean_text)
            return int(number[0]) if number else 0
            
        except:
            return 0
    
    def _extract_bedrooms(self, text: str) -> Optional[int]:
        """Extract number of bedrooms from text"""
        match = re.search(r'(\d+)\s*(?:bed|bedroom|br)', text, re.IGNORECASE)
        return int(match.group(1)) if match else None
    
    def _extract_zone(self, location: str) -> Optional[str]:
        """Extract zone from location text"""
        # Common Lagos zones
        zones = [
            'Lekki', 'Ajah', 'Victoria Island', 'Ikoyi', 'Ikeja', 'Yaba',
            'Surulere', 'Banana Island', 'Oniru', 'Magodo', 'Maryland',
            'Gbagada', 'Apapa', 'Festac', 'Isolo', 'Oshodi'
        ]
        
        location_lower = location.lower()
        for zone in zones:
            if zone.lower() in location_lower:
                return zone
        
        return None
    
    def _extract_property_type(self, text: str) -> str:
        """Extract property type from text"""
        text_lower = text.lower()
        
        if 'flat' in text_lower or 'apartment' in text_lower:
            return 'Apartment'
        elif 'duplex' in text_lower:
            return 'Duplex'
        elif 'detached' in text_lower:
            return 'Detached House'
        elif 'semi-detached' in text_lower or 'semi detached' in text_lower:
            return 'Semi-Detached'
        elif 'terraced' in text_lower or 'terrace' in text_lower:
            return 'Terraced House'
        elif 'land' in text_lower:
            return 'Land'
        else:
            return 'House'
    
    def _save_property(self, property_data: Dict[str, Any]) -> str:
        """
        Save property to database
        
        Returns:
            'added' if new property, 'updated' if existing property updated
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if property exists
        cursor.execute(
            "SELECT property_id FROM properties WHERE property_id = ?",
            (property_data['property_id'],)
        )
        
        exists = cursor.fetchone() is not None
        
        if exists:
            # Update existing property
            cursor.execute("""
                UPDATE properties SET
                    title = ?,
                    price = ?,
                    location = ?,
                    zone = ?,
                    state = ?,
                    bedrooms = ?,
                    bathrooms = ?,
                    property_type = ?,
                    description = ?,
                    agent_name = ?,
                    agent_phone = ?,
                    source = ?,
                    source_url = ?,
                    scraped_at = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE property_id = ?
            """, (
                property_data['title'],
                property_data['price'],
                property_data['location'],
                property_data['zone'],
                property_data['state'],
                property_data['bedrooms'],
                property_data['bathrooms'],
                property_data['property_type'],
                property_data['description'],
                property_data['agent_name'],
                property_data['agent_phone'],
                property_data['source'],
                property_data['source_url'],
                property_data['scraped_at'],
                property_data['property_id']
            ))
            result = 'updated'
        else:
            # Insert new property
            cursor.execute("""
                INSERT INTO properties (
                    property_id, title, price, location, zone, state,
                    bedrooms, bathrooms, property_type, description,
                    agent_name, agent_phone, source, source_url, scraped_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                property_data['property_id'],
                property_data['title'],
                property_data['price'],
                property_data['location'],
                property_data['zone'],
                property_data['state'],
                property_data['bedrooms'],
                property_data['bathrooms'],
                property_data['property_type'],
                property_data['description'],
                property_data['agent_name'],
                property_data['agent_phone'],
                property_data['source'],
                property_data['source_url'],
                property_data['scraped_at']
            ))
            result = 'added'
        
        conn.commit()
        conn.close()
        
        return result
    
    def _log_scrape_history(self, results: Dict[str, Any]):
        """Log scraping session to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for source, source_result in results.get('sources', {}).items():
            cursor.execute("""
                INSERT INTO scrape_history (
                    source, properties_found, properties_added,
                    properties_updated, status, error_message
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                source,
                source_result.get('properties_found', 0),
                source_result.get('properties_added', 0),
                source_result.get('properties_updated', 0),
                source_result.get('status', 'unknown'),
                source_result.get('message')
            ))
        
        conn.commit()
        conn.close()
    
    def search_properties(
        self,
        zone: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        bedrooms: Optional[int] = None,
        property_type: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search properties in database
        
        Returns:
            Dict with search results
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM properties WHERE 1=1"
        params = []
        
        if zone:
            query += " AND zone LIKE ?"
            params.append(f"%{zone}%")
        
        if min_price:
            query += " AND price >= ?"
            params.append(min_price)
        
        if max_price:
            query += " AND price <= ?"
            params.append(max_price)
        
        if bedrooms:
            query += " AND bedrooms = ?"
            params.append(bedrooms)
        
        if property_type:
            query += " AND property_type LIKE ?"
            params.append(f"%{property_type}%")
        
        query += " ORDER BY scraped_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        properties = [dict(row) for row in rows]
        
        conn.close()
        
        return {
            'status': 'success',
            'count': len(properties),
            'properties': properties
        }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about properties database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total properties
        cursor.execute("SELECT COUNT(*) FROM properties")
        total_properties = cursor.fetchone()[0]
        
        # By source
        cursor.execute("""
            SELECT source, COUNT(*) as count
            FROM properties
            GROUP BY source
        """)
        by_source = dict(cursor.fetchall())
        
        # By zone
        cursor.execute("""
            SELECT zone, COUNT(*) as count
            FROM properties
            WHERE zone IS NOT NULL
            GROUP BY zone
            ORDER BY count DESC
            LIMIT 10
        """)
        top_zones = dict(cursor.fetchall())
        
        # Price range
        cursor.execute("SELECT MIN(price), MAX(price), AVG(price) FROM properties WHERE price > 0")
        price_min, price_max, price_avg = cursor.fetchone()
        
        # Recent scrapes
        cursor.execute("""
            SELECT source, properties_found, scraped_at
            FROM scrape_history
            ORDER BY scraped_at DESC
            LIMIT 5
        """)
        recent_scrapes = [
            {'source': row[0], 'properties_found': row[1], 'scraped_at': row[2]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            'total_properties': total_properties,
            'by_source': by_source,
            'top_zones': top_zones,
            'price_range': {
                'min': price_min,
                'max': price_max,
                'avg': price_avg
            },
            'recent_scrapes': recent_scrapes
        }


def demo_scraper():
    """Demo the property scraper"""
    print("=" * 70)
    print("NAIJA-PROP-INTEL: PROPERTY SCRAPER DEMO")
    print("=" * 70)
    
    scraper = PropertyScraper()
    
    print("\n🎯 Mission: Ingest property data from Jiji & PropertyPro")
    print("⚠️  Note: This is a DEMO. Actual scraping requires active internet connection.")
    print("⚠️  Note: Website structures change. Scraper may need updates.\n")
    
    # Show database stats before
    stats_before = scraper.get_database_stats()
    print(f"📊 Current Database: {stats_before['total_properties']} properties\n")
    
    # Uncomment to run actual scraping (requires internet)
    # print("🚀 Starting data ingestion...")
    # results = scraper.ingest_market_data(['jiji', 'propertypro'])
    # print(f"\n✅ Scraping Complete!")
    # print(f"   Sources Scraped: {results['sources_scraped']}")
    # print(f"   Properties Found: {results['total_properties_found']}")
    # print(f"   Properties Added: {results['total_properties_added']}")
    # print(f"   Properties Updated: {results['total_properties_updated']}")
    
    print("📝 To run actual scraping:")
    print("   1. Install: pip install requests beautifulsoup4")
    print("   2. Uncomment scraping code in demo_scraper()")
    print("   3. Run: python scraper.py")
    print("\n💡 Search properties:")
    print("   scraper.search_properties(zone='Lekki', max_price=50000000)")
    
    print("\n" + "=" * 70)
    print("Demo complete! Scraper is ready.")
    print("=" * 70)


if __name__ == "__main__":
    demo_scraper()
