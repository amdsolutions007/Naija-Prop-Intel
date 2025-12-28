"""
Naija-Prop-Intel: Agent Registration System (Week 3-4)
SQLite-based implementation per MASTER_PLAN.md

Business Model:
- ₦5,000 verification badge per agent
- Target: 1,000 agents = ₦5M revenue
- Agents get verified listing + property leads

Database: SQLite (data/agents.db)
Tables:
- agents: Core agent information
- verifications: Payment & verification tracking
- agent_zones: Agent coverage areas
"""

import sqlite3
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any


class AgentSystem:
    """Manages real estate agent registration, verification, and discovery"""
    
    def __init__(self, db_path: str = "data/agents.db"):
        """
        Initialize the Agent Registration System
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_database()
    
    def _ensure_database(self):
        """Create database and tables if they don't exist"""
        # Create data directory if needed
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Agents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL,
                state TEXT NOT NULL,
                lga TEXT,
                specialization TEXT,
                years_experience INTEGER,
                whatsapp TEXT,
                profile_photo TEXT,
                bio TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                rating REAL DEFAULT 0.0,
                total_reviews INTEGER DEFAULT 0
            )
        """)
        
        # Verifications table (payment tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verifications (
                verification_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                payment_amount INTEGER NOT NULL,
                payment_reference TEXT,
                payment_method TEXT,
                payment_proof TEXT,
                verification_status TEXT DEFAULT 'pending',
                verified_at TEXT,
                verified_by TEXT,
                expires_at TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
            )
        """)
        
        # Agent zones (coverage areas)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_zones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                zone_name TEXT NOT NULL,
                is_primary BOOLEAN DEFAULT 0,
                added_at TEXT NOT NULL,
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id),
                UNIQUE(agent_id, zone_name)
            )
        """)
        
        # Agent statistics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_stats (
                agent_id TEXT PRIMARY KEY,
                properties_listed INTEGER DEFAULT 0,
                properties_sold INTEGER DEFAULT 0,
                total_leads INTEGER DEFAULT 0,
                active_leads INTEGER DEFAULT 0,
                response_time_hours REAL DEFAULT 0.0,
                last_active TEXT,
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agents_state ON agents(state)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agents_rating ON agents(rating)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_verifications_agent ON verifications(agent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_zones_zone ON agent_zones(zone_name)")
        
        conn.commit()
        conn.close()
    
    def register_agent(
        self,
        name: str,
        email: str,
        phone: str,
        state: str,
        lga: Optional[str] = None,
        specialization: Optional[str] = None,
        years_experience: Optional[int] = None,
        whatsapp: Optional[str] = None,
        bio: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new real estate agent
        
        Args:
            name: Full name of the agent
            email: Email address (must be unique)
            phone: Phone number
            state: Nigerian state (e.g., "Lagos", "Abuja")
            lga: Local Government Area (optional)
            specialization: e.g., "Residential", "Commercial", "Land"
            years_experience: Years in real estate
            whatsapp: WhatsApp number (defaults to phone if not provided)
            bio: Short biography/description
        
        Returns:
            Dict with agent_id, status, and next steps
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Generate unique agent ID
            agent_id = self._generate_agent_id(email)
            
            # Use phone as WhatsApp if not provided
            if not whatsapp:
                whatsapp = phone
            
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO agents (
                    agent_id, name, email, phone, state, lga,
                    specialization, years_experience, whatsapp, bio,
                    created_at, updated_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent_id, name, email, phone, state, lga,
                specialization, years_experience, whatsapp, bio,
                now, now, 'pending'
            ))
            
            # Initialize stats
            cursor.execute("""
                INSERT INTO agent_stats (agent_id, last_active)
                VALUES (?, ?)
            """, (agent_id, now))
            
            conn.commit()
            
            return {
                "status": "success",
                "agent_id": agent_id,
                "message": "Agent registered successfully",
                "next_steps": {
                    "verification_fee": "₦5,000",
                    "payment_methods": ["Bank Transfer", "Card Payment", "USSD"],
                    "benefits": [
                        "Verified badge on profile",
                        "Priority listing in search results",
                        "Access to property leads",
                        "WhatsApp integration",
                        "Analytics dashboard"
                    ],
                    "action": f"Pay ₦5,000 to verify your account and activate your profile"
                }
            }
            
        except sqlite3.IntegrityError as e:
            conn.rollback()
            if "email" in str(e).lower():
                return {
                    "status": "error",
                    "message": "Email already registered. Please use a different email or login."
                }
            return {
                "status": "error",
                "message": f"Registration failed: {str(e)}"
            }
        
        finally:
            conn.close()
    
    def verify_agent(
        self,
        agent_id: str,
        payment_amount: int,
        payment_reference: str,
        payment_method: str = "Bank Transfer",
        payment_proof: Optional[str] = None,
        verified_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Verify an agent after payment of ₦5,000 verification fee
        
        Args:
            agent_id: Unique agent identifier
            payment_amount: Amount paid (should be 5000)
            payment_reference: Transaction reference/receipt number
            payment_method: How payment was made
            payment_proof: Path to receipt/screenshot (optional)
            verified_by: Who verified (default: "system", or admin name)
        
        Returns:
            Dict with verification status and details
        """
        VERIFICATION_FEE = 5000
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if agent exists
            cursor.execute("SELECT name, email FROM agents WHERE agent_id = ?", (agent_id,))
            agent = cursor.fetchone()
            
            if not agent:
                return {
                    "status": "error",
                    "message": f"Agent ID {agent_id} not found"
                }
            
            agent_name, agent_email = agent
            
            # Validate payment amount
            if payment_amount < VERIFICATION_FEE:
                return {
                    "status": "error",
                    "message": f"Payment amount ₦{payment_amount:,} is less than required ₦{VERIFICATION_FEE:,}"
                }
            
            # Create verification record
            verification_id = self._generate_verification_id(agent_id, payment_reference)
            now = datetime.now().isoformat()
            
            # Calculate expiry (1 year from verification)
            expires_at = (datetime.now() + timedelta(days=365)).isoformat()
            
            cursor.execute("""
                INSERT INTO verifications (
                    verification_id, agent_id, payment_amount, payment_reference,
                    payment_method, payment_proof, verification_status,
                    verified_at, verified_by, expires_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                verification_id, agent_id, payment_amount, payment_reference,
                payment_method, payment_proof, 'verified',
                now, verified_by, expires_at, now
            ))
            
            # Update agent status
            cursor.execute("""
                UPDATE agents
                SET status = 'verified', updated_at = ?
                WHERE agent_id = ?
            """, (now, agent_id))
            
            conn.commit()
            
            return {
                "status": "success",
                "agent_id": agent_id,
                "agent_name": agent_name,
                "verification_id": verification_id,
                "message": "Agent verified successfully",
                "payment_amount": f"₦{payment_amount:,}",
                "verified_at": now,
                "expires_at": expires_at,
                "benefits_activated": [
                    "✅ Verified badge displayed on profile",
                    "✅ Priority listing in search results",
                    "✅ Access to property leads system",
                    "✅ WhatsApp integration enabled",
                    "✅ Analytics dashboard activated"
                ]
            }
            
        except Exception as e:
            conn.rollback()
            return {
                "status": "error",
                "message": f"Verification failed: {str(e)}"
            }
        
        finally:
            conn.close()
    
    def search_agents(
        self,
        state: Optional[str] = None,
        lga: Optional[str] = None,
        zone_name: Optional[str] = None,
        specialization: Optional[str] = None,
        min_rating: float = 0.0,
        verified_only: bool = True,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search for agents by location, specialization, or rating
        
        Args:
            state: Filter by Nigerian state
            lga: Filter by Local Government Area
            zone_name: Filter by specific zone coverage
            specialization: Filter by specialization
            min_rating: Minimum rating (0.0-5.0)
            verified_only: Only show verified agents
            limit: Maximum number of results
        
        Returns:
            Dict with list of matching agents
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build query
        query = """
            SELECT 
                a.agent_id, a.name, a.email, a.phone, a.whatsapp,
                a.state, a.lga, a.specialization, a.years_experience,
                a.bio, a.status, a.rating, a.total_reviews,
                a.created_at,
                s.properties_listed, s.properties_sold, s.total_leads,
                s.response_time_hours,
                GROUP_CONCAT(DISTINCT az.zone_name) as zones_covered
            FROM agents a
            LEFT JOIN agent_stats s ON a.agent_id = s.agent_id
            LEFT JOIN agent_zones az ON a.agent_id = az.agent_id
            WHERE 1=1
        """
        
        params = []
        
        if verified_only:
            query += " AND a.status = 'verified'"
        
        if state:
            query += " AND a.state = ?"
            params.append(state)
        
        if lga:
            query += " AND a.lga = ?"
            params.append(lga)
        
        if zone_name:
            query += " AND az.zone_name = ?"
            params.append(zone_name)
        
        if specialization:
            query += " AND a.specialization = ?"
            params.append(specialization)
        
        if min_rating > 0:
            query += " AND a.rating >= ?"
            params.append(min_rating)
        
        query += """
            GROUP BY a.agent_id
            ORDER BY a.rating DESC, a.total_reviews DESC, s.properties_sold DESC
            LIMIT ?
        """
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        agents = []
        for row in rows:
            agent = dict(row)
            
            # Parse zones_covered from comma-separated string
            if agent['zones_covered']:
                agent['zones_covered'] = agent['zones_covered'].split(',')
            else:
                agent['zones_covered'] = []
            
            # Format display
            agent['rating_display'] = f"{agent['rating']:.1f}/5.0 ({agent['total_reviews']} reviews)"
            agent['contact'] = {
                "phone": agent['phone'],
                "whatsapp": agent['whatsapp'],
                "email": agent['email']
            }
            
            agents.append(agent)
        
        conn.close()
        
        return {
            "status": "success",
            "total_found": len(agents),
            "filters_applied": {
                "state": state,
                "lga": lga,
                "zone_name": zone_name,
                "specialization": specialization,
                "min_rating": min_rating,
                "verified_only": verified_only
            },
            "agents": agents
        }
    
    def add_agent_zone(self, agent_id: str, zone_name: str, is_primary: bool = False) -> Dict[str, Any]:
        """
        Add a zone to an agent's coverage area
        
        Args:
            agent_id: Agent identifier
            zone_name: Zone name from zones.json
            is_primary: Whether this is the agent's primary zone
        
        Returns:
            Dict with status
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO agent_zones (agent_id, zone_name, is_primary, added_at)
                VALUES (?, ?, ?, ?)
            """, (agent_id, zone_name, is_primary, now))
            
            conn.commit()
            
            return {
                "status": "success",
                "message": f"Zone '{zone_name}' added to agent's coverage"
            }
            
        except sqlite3.IntegrityError:
            return {
                "status": "error",
                "message": f"Agent already covers zone '{zone_name}'"
            }
        
        finally:
            conn.close()
    
    def get_agent_profile(self, agent_id: str) -> Dict[str, Any]:
        """
        Get complete agent profile with stats
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Dict with full agent profile
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get agent info
        cursor.execute("""
            SELECT 
                a.*,
                s.properties_listed, s.properties_sold, s.total_leads,
                s.active_leads, s.response_time_hours, s.last_active
            FROM agents a
            LEFT JOIN agent_stats s ON a.agent_id = s.agent_id
            WHERE a.agent_id = ?
        """, (agent_id,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {
                "status": "error",
                "message": f"Agent {agent_id} not found"
            }
        
        profile = dict(row)
        
        # Get zones covered
        cursor.execute("""
            SELECT zone_name, is_primary, added_at
            FROM agent_zones
            WHERE agent_id = ?
            ORDER BY is_primary DESC, zone_name
        """, (agent_id,))
        
        profile['zones_covered'] = [dict(row) for row in cursor.fetchall()]
        
        # Get verification status
        cursor.execute("""
            SELECT verification_id, verified_at, expires_at, payment_amount
            FROM verifications
            WHERE agent_id = ? AND verification_status = 'verified'
            ORDER BY verified_at DESC
            LIMIT 1
        """, (agent_id,))
        
        verification = cursor.fetchone()
        if verification:
            profile['verification'] = dict(verification)
        else:
            profile['verification'] = None
        
        conn.close()
        
        profile['status'] = "success"
        return profile
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """
        Get system-wide agent statistics
        
        Returns:
            Dict with agent statistics and revenue
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total agents
        cursor.execute("SELECT COUNT(*) FROM agents")
        total_agents = cursor.fetchone()[0]
        
        # Verified agents
        cursor.execute("SELECT COUNT(*) FROM agents WHERE status = 'verified'")
        verified_agents = cursor.fetchone()[0]
        
        # Pending verifications
        cursor.execute("SELECT COUNT(*) FROM agents WHERE status = 'pending'")
        pending_agents = cursor.fetchone()[0]
        
        # Total revenue (verified agents × ₦5,000)
        VERIFICATION_FEE = 5000
        total_revenue_naira = verified_agents * VERIFICATION_FEE
        
        # Agent breakdown by state
        cursor.execute("""
            SELECT state, COUNT(*) as count
            FROM agents
            WHERE status = 'verified'
            GROUP BY state
            ORDER BY count DESC
            LIMIT 10
        """)
        
        top_states = [{"state": row[0], "agents": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "status": "success",
            "total_agents": total_agents,
            "verified_agents": verified_agents,
            "pending_agents": pending_agents,
            "verification_rate": f"{(verified_agents / max(total_agents, 1) * 100):.1f}%",
            "revenue": {
                "total_naira": f"₦{total_revenue_naira:,}",
                "total_usd": f"${total_revenue_naira / 850:,.2f}",
                "per_agent": f"₦{VERIFICATION_FEE:,}",
                "target": "₦5,000,000 (1,000 agents)",
                "progress": f"{(verified_agents / 1000 * 100):.1f}%"
            },
            "top_states": top_states
        }
    
    def _generate_agent_id(self, email: str) -> str:
        """Generate unique agent ID from email"""
        hash_obj = hashlib.sha256(email.encode())
        return f"AGT-{hash_obj.hexdigest()[:12].upper()}"
    
    def _generate_verification_id(self, agent_id: str, payment_ref: str) -> str:
        """Generate unique verification ID"""
        combined = f"{agent_id}{payment_ref}{datetime.now().isoformat()}"
        hash_obj = hashlib.sha256(combined.encode())
        return f"VER-{hash_obj.hexdigest()[:12].upper()}"


# Demo functions
def demo_agent_system():
    """Demonstration of the Agent Registration System"""
    print("=" * 70)
    print("NAIJA-PROP-INTEL: AGENT REGISTRATION SYSTEM DEMO")
    print("=" * 70)
    
    system = AgentSystem()
    
    # 1. Register an agent
    print("\n1. REGISTERING NEW AGENT...")
    print("-" * 70)
    
    result = system.register_agent(
        name="Chinedu Okafor",
        email="chinedu.okafor@example.com",
        phone="+234 803 456 7890",
        state="Lagos",
        lga="Eti-Osa",
        specialization="Residential",
        years_experience=5,
        bio="Experienced real estate agent specializing in Lekki and Victoria Island properties"
    )
    
    print(f"Status: {result['status']}")
    print(f"Agent ID: {result.get('agent_id', 'N/A')}")
    print(f"Message: {result['message']}")
    
    if result['status'] == 'success':
        agent_id = result['agent_id']
        print(f"\nNext Steps:")
        print(f"  Verification Fee: {result['next_steps']['verification_fee']}")
        print(f"  Benefits: {', '.join(result['next_steps']['benefits'][:3])}...")
        
        # 2. Add coverage zones
        print("\n2. ADDING COVERAGE ZONES...")
        print("-" * 70)
        
        for zone in ["Lekki Phase 1", "Victoria Island", "Ajah"]:
            zone_result = system.add_agent_zone(agent_id, zone, is_primary=(zone == "Lekki Phase 1"))
            print(f"  {zone}: {zone_result['message']}")
        
        # 3. Verify agent (payment received)
        print("\n3. VERIFYING AGENT (Payment ₦5,000)...")
        print("-" * 70)
        
        verify_result = system.verify_agent(
            agent_id=agent_id,
            payment_amount=5000,
            payment_reference="TRX123456789",
            payment_method="Bank Transfer"
        )
        
        print(f"Status: {verify_result['status']}")
        print(f"Verification ID: {verify_result.get('verification_id', 'N/A')}")
        print(f"Message: {verify_result['message']}")
        
        if verify_result['status'] == 'success':
            print("\nBenefits Activated:")
            for benefit in verify_result['benefits_activated']:
                print(f"  {benefit}")
    
    # 4. Search for agents
    print("\n4. SEARCHING FOR AGENTS IN LAGOS...")
    print("-" * 70)
    
    search_result = system.search_agents(state="Lagos", verified_only=True)
    
    print(f"Total Found: {search_result['total_found']}")
    
    for agent in search_result['agents']:
        print(f"\n  Agent: {agent['name']}")
        print(f"  Specialization: {agent['specialization']}")
        print(f"  Rating: {agent['rating_display']}")
        print(f"  Zones: {', '.join(agent['zones_covered'])}")
        print(f"  Contact: {agent['contact']['phone']}")
    
    # 5. System statistics
    print("\n5. SYSTEM STATISTICS...")
    print("-" * 70)
    
    stats = system.get_agent_stats()
    
    print(f"Total Agents: {stats['total_agents']}")
    print(f"Verified Agents: {stats['verified_agents']}")
    print(f"Pending Agents: {stats['pending_agents']}")
    print(f"Verification Rate: {stats['verification_rate']}")
    print(f"\nRevenue Generated: {stats['revenue']['total_naira']} ({stats['revenue']['total_usd']})")
    print(f"Target Progress: {stats['revenue']['progress']} to ₦5M goal")
    
    print("\n" + "=" * 70)
    print("Demo complete! Agent registration system is operational.")
    print("=" * 70)


if __name__ == "__main__":
    demo_agent_system()
