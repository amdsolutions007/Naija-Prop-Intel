"""
Naija-Prop-Intel: Agent Network & Registration System
© 2025 AMD Solutions. All Rights Reserved.

Real Estate Agent Network:
- Agent registration with email/phone verification
- ₦5,000 verification badge system
- Listing broadcast to verified agents
- Agent database management
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional


class AgentNetwork:
    """Real Estate Agent Network Management System"""
    
    def __init__(self, db_file: str = "data/agents.db.json"):
        """Initialize agent network with database"""
        self.db_file = db_file
        self.agents_db = self._load_database()
    
    def _load_database(self) -> Dict:
        """Load agents database from JSON file"""
        if not os.path.exists(self.db_file):
            # Create initial database structure
            initial_db = {
                "agents": {},
                "listings": {},
                "payments": {},
                "stats": {
                    "total_agents": 0,
                    "verified_agents": 0,
                    "pending_verification": 0,
                    "total_listings": 0
                }
            }
            self._save_database(initial_db)
            return initial_db
        
        with open(self.db_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_database(self, data: Dict = None):
        """Save database to file"""
        if data is None:
            data = self.agents_db
        
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def register_agent(
        self, 
        name: str, 
        email: str, 
        phone: str, 
        company: str = "Independent",
        specialization: str = "Residential"
    ) -> Dict[str, Any]:
        """
        Register a new real estate agent
        
        Args:
            name: Agent's full name
            email: Email address
            phone: Phone number (Nigerian format)
            company: Company name (default: Independent)
            specialization: Agent specialization (Residential/Commercial/Land)
        
        Returns:
            Agent registration details with unique ID
        """
        # Validate inputs
        if not name or len(name) < 3:
            return {"error": "Name must be at least 3 characters"}
        
        if '@' not in email or '.' not in email:
            return {"error": "Invalid email format"}
        
        if not phone or len(phone) < 10:
            return {"error": "Invalid phone number"}
        
        # Check if agent already exists
        for agent_id, agent in self.agents_db['agents'].items():
            if agent['email'] == email:
                return {
                    "error": "Email already registered",
                    "agent_id": agent_id,
                    "status": agent['status']
                }
        
        # Generate unique agent ID
        agent_id = f"AG-{uuid.uuid4().hex[:8].upper()}"
        
        # Create agent record
        agent_data = {
            "agent_id": agent_id,
            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
            "specialization": specialization,
            "status": "pending",  # pending, verified, suspended
            "verification_badge": False,
            "payment_status": "unpaid",  # unpaid, paid, expired
            "registration_date": datetime.now().isoformat(),
            "verification_date": None,
            "listings_count": 0,
            "total_revenue": 0.0,
            "rating": 0.0,
            "reviews_count": 0
        }
        
        # Save to database
        self.agents_db['agents'][agent_id] = agent_data
        self.agents_db['stats']['total_agents'] += 1
        self.agents_db['stats']['pending_verification'] += 1
        self._save_database()
        
        return {
            "success": True,
            "agent_id": agent_id,
            "message": f"✅ Agent registered successfully!\n"
                      f"📧 Verification email sent to {email}\n"
                      f"💳 Payment Required: ₦5,000 (Verification Badge)\n"
                      f"📱 Payment Instructions:\n"
                      f"   - Bank Transfer: GTBank 0123456789 (AMD Solutions)\n"
                      f"   - Paystack: pay.amdsolutions007.com/agent-badge\n"
                      f"   - After payment, send proof with Agent ID: {agent_id}",
            "agent_data": agent_data
        }
    
    def verify_agent(
        self, 
        agent_id: str, 
        payment_proof: str,
        payment_amount: float = 5000.0
    ) -> Dict[str, Any]:
        """
        Verify agent after ₦5,000 badge payment
        
        Args:
            agent_id: Agent's unique ID
            payment_proof: Payment reference/transaction ID
            payment_amount: Amount paid (must be ₦5,000)
        
        Returns:
            Verification status and badge details
        """
        if agent_id not in self.agents_db['agents']:
            return {"error": f"Agent ID {agent_id} not found"}
        
        agent = self.agents_db['agents'][agent_id]
        
        if agent['status'] == 'verified':
            return {
                "error": "Agent already verified",
                "badge_expiry": agent.get('badge_expiry', 'Lifetime')
            }
        
        # Validate payment amount
        if payment_amount < 5000.0:
            return {
                "error": f"Insufficient payment: ₦{payment_amount:,.2f}",
                "required": "₦5,000.00"
            }
        
        # Verify agent
        agent['status'] = 'verified'
        agent['verification_badge'] = True
        agent['payment_status'] = 'paid'
        agent['verification_date'] = datetime.now().isoformat()
        agent['badge_expiry'] = 'Lifetime'  # One-time payment, lifetime access
        
        # Record payment
        payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        self.agents_db['payments'][payment_id] = {
            "payment_id": payment_id,
            "agent_id": agent_id,
            "amount": payment_amount,
            "payment_proof": payment_proof,
            "payment_date": datetime.now().isoformat(),
            "status": "confirmed"
        }
        
        # Update stats
        self.agents_db['stats']['verified_agents'] += 1
        self.agents_db['stats']['pending_verification'] -= 1
        
        self._save_database()
        
        return {
            "success": True,
            "message": f"🎉 VERIFICATION SUCCESSFUL!\n"
                      f"✅ Agent {agent['name']} is now VERIFIED\n"
                      f"🏅 Verification Badge: ACTIVE (Lifetime)\n"
                      f"📢 You can now post listings and receive leads\n"
                      f"💰 Commission: 2.5% per closed deal",
            "agent_id": agent_id,
            "badge_status": "VERIFIED",
            "payment_id": payment_id
        }
    
    def post_listing(
        self, 
        agent_id: str, 
        property_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Post property listing (Verified agents only)
        
        Args:
            agent_id: Agent's unique ID (must be verified)
            property_details: Property information
                - location: Property location
                - price: Asking price
                - property_type: Type (3-bedroom, duplex, etc.)
                - bedrooms: Number of bedrooms
                - bathrooms: Number of bathrooms
                - description: Property description
                - contact: Contact information
        
        Returns:
            Listing details and broadcast status
        """
        if agent_id not in self.agents_db['agents']:
            return {"error": f"Agent ID {agent_id} not found"}
        
        agent = self.agents_db['agents'][agent_id]
        
        # Check verification status
        if not agent['verification_badge']:
            return {
                "error": "⚠️ VERIFICATION REQUIRED",
                "message": "Only verified agents can post listings\n"
                          f"Pay ₦5,000 verification fee to activate your account"
            }
        
        # Validate listing details
        required_fields = ['location', 'price', 'property_type']
        for field in required_fields:
            if field not in property_details:
                return {"error": f"Missing required field: {field}"}
        
        # Generate listing ID
        listing_id = f"LST-{uuid.uuid4().hex[:8].upper()}"
        
        # Create listing
        listing_data = {
            "listing_id": listing_id,
            "agent_id": agent_id,
            "agent_name": agent['name'],
            "agent_phone": agent['phone'],
            "agent_email": agent['email'],
            "location": property_details['location'],
            "price": property_details['price'],
            "property_type": property_details['property_type'],
            "bedrooms": property_details.get('bedrooms', 'N/A'),
            "bathrooms": property_details.get('bathrooms', 'N/A'),
            "description": property_details.get('description', ''),
            "contact": property_details.get('contact', agent['phone']),
            "posted_date": datetime.now().isoformat(),
            "status": "active",  # active, sold, expired
            "views": 0,
            "inquiries": 0
        }
        
        # Save listing
        self.agents_db['listings'][listing_id] = listing_data
        self.agents_db['agents'][agent_id]['listings_count'] += 1
        self.agents_db['stats']['total_listings'] += 1
        self._save_database()
        
        # Broadcast to network (simulated)
        broadcast_message = f"""
🏠 NEW PROPERTY LISTING - NAIJA-PROP-INTEL

📍 Location: {property_details['location']}
💰 Price: ₦{property_details['price']:,.2f}
🏘️  Type: {property_details['property_type']}
🛏️  Bedrooms: {listing_data['bedrooms']}
🚿 Bathrooms: {listing_data['bathrooms']}

📝 Description:
{listing_data['description']}

👤 Listed by: {agent['name']} (VERIFIED AGENT ✅)
📱 Contact: {listing_data['contact']}
📧 Email: {agent['email']}

Listing ID: {listing_id}
Posted: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
        """
        
        return {
            "success": True,
            "listing_id": listing_id,
            "message": "✅ Listing posted successfully!",
            "broadcast": broadcast_message,
            "reach": f"{self.agents_db['stats']['verified_agents']} verified agents notified"
        }
    
    def get_agent_info(self, agent_id: str) -> Dict[str, Any]:
        """Get agent information"""
        if agent_id not in self.agents_db['agents']:
            return {"error": f"Agent ID {agent_id} not found"}
        
        return self.agents_db['agents'][agent_id]
    
    def list_verified_agents(self) -> List[Dict]:
        """Get list of all verified agents"""
        verified = [
            agent for agent in self.agents_db['agents'].values()
            if agent['verification_badge']
        ]
        return sorted(verified, key=lambda x: x['listings_count'], reverse=True)
    
    def get_network_stats(self) -> Dict:
        """Get network statistics"""
        return self.agents_db['stats']
    
    def search_listings(
        self, 
        location: Optional[str] = None,
        max_price: Optional[float] = None,
        property_type: Optional[str] = None
    ) -> List[Dict]:
        """Search property listings"""
        results = []
        
        for listing in self.agents_db['listings'].values():
            # Skip inactive listings
            if listing['status'] != 'active':
                continue
            
            # Apply filters
            if location and location.lower() not in listing['location'].lower():
                continue
            if max_price and listing['price'] > max_price:
                continue
            if property_type and property_type.lower() not in listing['property_type'].lower():
                continue
            
            results.append(listing)
        
        return sorted(results, key=lambda x: x['posted_date'], reverse=True)


def test_agent_network():
    """Test agent network system"""
    print("🧪 Testing Naija-Prop-Intel Agent Network\n")
    
    network = AgentNetwork()
    
    # Test 1: Register agent
    print("1️⃣ Registering new agent...")
    result = network.register_agent(
        name="Chukwudi Okafor",
        email="chukwudi@realestate.ng",
        phone="08012345678",
        company="Lagos Prime Properties",
        specialization="Residential"
    )
    print(result['message'] if 'message' in result else result)
    agent_id = result.get('agent_id', '')
    
    print("\n" + "─" * 60)
    
    # Test 2: Verify agent
    print("\n2️⃣ Verifying agent with ₦5,000 payment...")
    verify_result = network.verify_agent(
        agent_id=agent_id,
        payment_proof="GTB-20251227-123456",
        payment_amount=5000.0
    )
    print(verify_result['message'] if 'message' in verify_result else verify_result)
    
    print("\n" + "─" * 60)
    
    # Test 3: Post listing
    print("\n3️⃣ Posting property listing...")
    listing_result = network.post_listing(
        agent_id=agent_id,
        property_details={
            "location": "Lekki Phase 1",
            "price": 45000000,
            "property_type": "4-bedroom Detached Duplex",
            "bedrooms": 4,
            "bathrooms": 5,
            "description": "Luxurious 4-bedroom duplex in prime Lekki location. "
                          "24hr security, swimming pool, fitted kitchen, BQ, ample parking.",
            "contact": "08012345678"
        }
    )
    print(listing_result.get('broadcast', listing_result))
    
    print("\n" + "─" * 60)
    
    # Test 4: Network stats
    print("\n4️⃣ Network Statistics:")
    stats = network.get_network_stats()
    print(f"Total Agents: {stats['total_agents']}")
    print(f"Verified Agents: {stats['verified_agents']}")
    print(f"Total Listings: {stats['total_listings']}")


if __name__ == "__main__":
    test_agent_network()
