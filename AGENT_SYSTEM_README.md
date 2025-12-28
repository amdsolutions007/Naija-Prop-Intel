# Agent Registration System - Week 3-4

## Overview
SQLite-based agent registration and verification system for Naija-Prop-Intel.

## Business Model
- **Verification Fee**: ₦5,000 per agent
- **Target**: 1,000 agents = ₦5M revenue
- **Benefits**: Verified badge, priority listing, property leads, WhatsApp integration, analytics

## Database Schema

### Tables

#### 1. `agents`
Core agent information
```sql
- agent_id (TEXT PRIMARY KEY) - Unique identifier (AGT-XXXXXXXXXXXX)
- name (TEXT) - Full name
- email (TEXT UNIQUE) - Email address
- phone (TEXT) - Phone number
- state (TEXT) - Nigerian state
- lga (TEXT) - Local Government Area
- specialization (TEXT) - Residential/Commercial/Land
- years_experience (INTEGER) - Years in real estate
- whatsapp (TEXT) - WhatsApp number
- profile_photo (TEXT) - Photo URL/path
- bio (TEXT) - Agent biography
- created_at (TEXT) - Registration timestamp
- updated_at (TEXT) - Last update timestamp
- status (TEXT) - pending/verified/suspended
- rating (REAL) - Average rating (0.0-5.0)
- total_reviews (INTEGER) - Number of reviews
```

#### 2. `verifications`
Payment and verification tracking
```sql
- verification_id (TEXT PRIMARY KEY) - Unique ID (VER-XXXXXXXXXXXX)
- agent_id (TEXT FK) - Reference to agents table
- payment_amount (INTEGER) - Amount paid in Naira
- payment_reference (TEXT) - Transaction reference
- payment_method (TEXT) - Bank Transfer/Card/USSD
- payment_proof (TEXT) - Receipt/screenshot path
- verification_status (TEXT) - pending/verified/rejected
- verified_at (TEXT) - Verification timestamp
- verified_by (TEXT) - Admin/system who verified
- expires_at (TEXT) - Badge expiry date (1 year)
- created_at (TEXT) - Payment record creation
```

#### 3. `agent_zones`
Agent coverage areas
```sql
- id (INTEGER PRIMARY KEY AUTOINCREMENT)
- agent_id (TEXT FK) - Reference to agents table
- zone_name (TEXT) - Zone name from zones.json
- is_primary (BOOLEAN) - Primary coverage area flag
- added_at (TEXT) - When zone was added
```

#### 4. `agent_stats`
Agent performance statistics
```sql
- agent_id (TEXT PRIMARY KEY FK) - Reference to agents table
- properties_listed (INTEGER) - Total properties listed
- properties_sold (INTEGER) - Total properties sold
- total_leads (INTEGER) - Total leads received
- active_leads (INTEGER) - Currently active leads
- response_time_hours (REAL) - Average response time
- last_active (TEXT) - Last activity timestamp
```

## API Functions

### 1. `register_agent()`
Register a new real estate agent.

**Parameters:**
- `name` (str): Full name *required*
- `email` (str): Email address *required* *unique*
- `phone` (str): Phone number *required*
- `state` (str): Nigerian state *required*
- `lga` (str): Local Government Area *optional*
- `specialization` (str): Residential/Commercial/Land *optional*
- `years_experience` (int): Years in real estate *optional*
- `whatsapp` (str): WhatsApp number *optional* (defaults to phone)
- `bio` (str): Biography/description *optional*

**Returns:**
```python
{
    "status": "success",
    "agent_id": "AGT-E545B7CFFF47",
    "message": "Agent registered successfully",
    "next_steps": {
        "verification_fee": "₦5,000",
        "payment_methods": ["Bank Transfer", "Card Payment", "USSD"],
        "benefits": [...],
        "action": "Pay ₦5,000 to verify your account..."
    }
}
```

### 2. `verify_agent()`
Verify an agent after payment of ₦5,000 verification fee.

**Parameters:**
- `agent_id` (str): Agent identifier *required*
- `payment_amount` (int): Amount paid (should be 5000) *required*
- `payment_reference` (str): Transaction reference *required*
- `payment_method` (str): Payment method *optional* (default: "Bank Transfer")
- `payment_proof` (str): Receipt path *optional*
- `verified_by` (str): Who verified *optional* (default: "system")

**Returns:**
```python
{
    "status": "success",
    "agent_id": "AGT-E545B7CFFF47",
    "agent_name": "Chinedu Okafor",
    "verification_id": "VER-1E7C4803749E",
    "message": "Agent verified successfully",
    "payment_amount": "₦5,000",
    "verified_at": "2025-12-28T...",
    "expires_at": "2026-12-28T...",
    "benefits_activated": [...]
}
```

### 3. `search_agents()`
Search for agents by location, specialization, or rating.

**Parameters:**
- `state` (str): Filter by state *optional*
- `lga` (str): Filter by LGA *optional*
- `zone_name` (str): Filter by zone coverage *optional*
- `specialization` (str): Filter by specialization *optional*
- `min_rating` (float): Minimum rating 0.0-5.0 *optional* (default: 0.0)
- `verified_only` (bool): Only verified agents *optional* (default: True)
- `limit` (int): Maximum results *optional* (default: 20)

**Returns:**
```python
{
    "status": "success",
    "total_found": 10,
    "filters_applied": {...},
    "agents": [
        {
            "agent_id": "AGT-...",
            "name": "Chinedu Okafor",
            "state": "Lagos",
            "specialization": "Residential",
            "rating": 4.5,
            "rating_display": "4.5/5.0 (23 reviews)",
            "zones_covered": ["Lekki Phase 1", "Victoria Island"],
            "contact": {
                "phone": "+234 803 456 7890",
                "whatsapp": "+234 803 456 7890",
                "email": "chinedu@example.com"
            },
            ...
        }
    ]
}
```

### 4. `add_agent_zone()`
Add a zone to an agent's coverage area.

**Parameters:**
- `agent_id` (str): Agent identifier *required*
- `zone_name` (str): Zone name from zones.json *required*
- `is_primary` (bool): Primary zone flag *optional* (default: False)

**Returns:**
```python
{
    "status": "success",
    "message": "Zone 'Lekki Phase 1' added to agent's coverage"
}
```

### 5. `get_agent_profile()`
Get complete agent profile with stats.

**Parameters:**
- `agent_id` (str): Agent identifier *required*

**Returns:**
```python
{
    "status": "success",
    "agent_id": "AGT-...",
    "name": "Chinedu Okafor",
    "email": "...",
    "phone": "...",
    "state": "Lagos",
    "zones_covered": [
        {"zone_name": "Lekki Phase 1", "is_primary": True, "added_at": "..."},
        {"zone_name": "Victoria Island", "is_primary": False, "added_at": "..."}
    ],
    "verification": {
        "verification_id": "VER-...",
        "verified_at": "...",
        "expires_at": "...",
        "payment_amount": 5000
    },
    "properties_listed": 15,
    "properties_sold": 8,
    "total_leads": 42,
    ...
}
```

### 6. `get_agent_stats()`
Get system-wide agent statistics and revenue.

**Parameters:** None

**Returns:**
```python
{
    "status": "success",
    "total_agents": 245,
    "verified_agents": 187,
    "pending_agents": 58,
    "verification_rate": "76.3%",
    "revenue": {
        "total_naira": "₦935,000",
        "total_usd": "$1,100.00",
        "per_agent": "₦5,000",
        "target": "₦5,000,000 (1,000 agents)",
        "progress": "18.7%"
    },
    "top_states": [
        {"state": "Lagos", "agents": 89},
        {"state": "Abuja", "agents": 34},
        {"state": "Rivers", "agents": 21}
    ]
}
```

## Usage Example

```python
from agent_system_v2 import AgentSystem

# Initialize system
system = AgentSystem()

# Register new agent
result = system.register_agent(
    name="Amaka Nwosu",
    email="amaka.nwosu@realestate.ng",
    phone="+234 805 123 4567",
    state="Lagos",
    lga="Lekki",
    specialization="Residential",
    years_experience=3,
    bio="Specialist in affordable housing in Lekki corridor"
)

print(result['agent_id'])  # AGT-XXXXXXXXXXXX

# Add coverage zones
system.add_agent_zone(result['agent_id'], "Ajah", is_primary=True)
system.add_agent_zone(result['agent_id'], "Lekki Phase 1")

# Verify agent (after payment)
verify = system.verify_agent(
    agent_id=result['agent_id'],
    payment_amount=5000,
    payment_reference="GTB-20251228-789012",
    payment_method="Bank Transfer"
)

# Search for agents in Lagos
agents = system.search_agents(
    state="Lagos",
    specialization="Residential",
    verified_only=True,
    limit=10
)

print(f"Found {agents['total_found']} agents")

# Get system statistics
stats = system.get_agent_stats()
print(f"Revenue: {stats['revenue']['total_naira']}")
print(f"Progress: {stats['revenue']['progress']}")
```

## Database File
- **Location**: `data/agents.db`
- **Format**: SQLite3
- **Created**: Automatically on first run
- **Size**: Grows with agent data (approx 50KB per 100 agents)

## Testing
Run the demo:
```bash
python agent_system_v2.py
```

Expected output:
- Registers a test agent
- Adds coverage zones
- Verifies the agent
- Searches for agents
- Shows system statistics

## Revenue Tracking
The system automatically calculates:
- **Total Revenue** = Verified Agents × ₦5,000
- **USD Equivalent** = Total Revenue / 850 (exchange rate)
- **Progress to Target** = (Verified Agents / 1,000) × 100%

## Next Steps (Week 4)
- WhatsApp Bot integration (whatsapp_bot.py)
- Lead generation system
- Agent analytics dashboard
- Property listing integration

## Files
- `agent_system_v2.py` - Main agent system (SQLite-based)
- `agents.py` - Legacy JSON-based system (kept for backward compatibility)
- `data/agents.db` - SQLite database (auto-created)
- `AGENT_SYSTEM_README.md` - This file

## License
© 2025 AMD Solutions. All Rights Reserved.
