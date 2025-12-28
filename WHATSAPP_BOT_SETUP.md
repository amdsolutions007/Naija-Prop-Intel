# WhatsApp Bot Setup Guide
## Naija-Prop-Intel - Week 4 Complete

---

## 🎯 Business Impact

### Why WhatsApp?
- **90% of Nigerians** use WhatsApp daily
- **Most accessible** platform (works on feature phones)
- **Zero app download** required
- **Natural language** - no learning curve
- **Instant responses** - real-time property intelligence

### Target Users
1. **Property Seekers**: Looking for land/houses
2. **Investors**: Checking flood risk & ROI
3. **Agents**: Getting leads from verified searches
4. **Developers**: Route-based property discovery

---

## 📊 FREE Tier Benefits

### Twilio WhatsApp Business API - FREE
- **1,000 messages/month** at $0 cost
- Perfect for **Phase 1** (testing & initial traction)
- Upgrade path: $0.005/message after FREE tier

### Phase 1 Math
- 1,000 messages = 100 conversations (avg 10 messages each)
- Target: 50 agents × 2 leads each = 100 property seekers
- Cost: **$0** (within FREE tier)
- Revenue: 50 agents × ₦5,000 = **₦250,000** ($294)

---

## 🚀 Quick Start (3 Steps)

### Step 1: Get Twilio Account
```bash
# Go to: https://www.twilio.com/try-twilio
# Sign up (FREE - no credit card for sandbox)
# Verify your phone number
```

### Step 2: Get Your Credentials
1. **Account SID**: Dashboard → Account Info → SID
2. **Auth Token**: Dashboard → Account Info → Auth Token (click to reveal)
3. **Sandbox Number**: Console → Messaging → Try it out → WhatsApp Sandbox

**Sandbox Number (FREE):**
```
whatsapp:+14155238886
```

### Step 3: Set Environment Variables
**On macOS/Linux:**
```bash
export TWILIO_ACCOUNT_SID='ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
export TWILIO_AUTH_TOKEN='your_auth_token_here'
export TWILIO_WHATSAPP_NUMBER='whatsapp:+14155238886'
```

**On Windows:**
```cmd
set TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx
set TWILIO_AUTH_TOKEN=your_auth_token_here
set TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

**Permanent (Add to ~/.zshrc or ~/.bashrc):**
```bash
echo 'export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx"' >> ~/.zshrc
echo 'export TWILIO_AUTH_TOKEN="your_auth_token_here"' >> ~/.zshrc
echo 'export TWILIO_WHATSAPP_NUMBER="whatsapp:+14155238886"' >> ~/.zshrc
source ~/.zshrc
```

---

## 🤖 Test the Bot

### Run Demo
```bash
cd /path/to/Naija-Prop-Intel
python whatsapp_bot.py
```

**Expected Output:**
```
NAIJA-PROP-INTEL: WHATSAPP BOT DEMO
====================================

1. USER: Property in Lekki ₦50M
BOT:
🏠 *PROPERTY INTEL: LEKKI PHASE 1*
💰 Your Budget: ₦50,000,000
...
```

---

## 📱 Query Examples

### 1. Property Search
```
Property in Lekki ₦50M
3 bedroom in Ajah
Property in Victoria Island under ₦100M
```

**Bot Response:**
- Avg price per sqm
- Estimated total cost
- Budget fit analysis
- Flood risk score
- Security level
- Infrastructure rating
- Market appreciation
- Rental yield

### 2. Flood Risk Analysis
```
Flood risk in Ajah
Is Lekki safe from flooding?
Flooding in Victoria Island
```

**Bot Response:**
- Risk score (0-100)
- Risk level (LOW/MODERATE/HIGH)
- Affected streets
- Drainage quality
- Last major flood date
- Recommendation

### 3. Security Check
```
Security in Victoria Island
Is Ajah safe?
Crime in Lekki
```

**Bot Response:**
- Security score (0-100)
- Security level
- Police stations count
- Robbery incidents (2024)
- Safe hours
- Safety recommendation

### 4. Agent Discovery
```
Find agent in Lagos
Verified agents in Lekki
Agent in Victoria Island
```

**Bot Response:**
- List of verified agents
- Specialization
- Rating & reviews
- Contact (phone/WhatsApp)
- Coverage zones

### 5. Route-Based Search
```
Properties from Ajah to Lekki
Ajah to Victoria Island under ₦30M
```

**Bot Response:**
- Properties along route corridor
- Distance & travel time
- Smart scores
- Budget filtering
- Top 5 recommendations

### 6. Location Info
```
Tell me about Lekki
Info on Ajah
Victoria Island details
```

**Bot Response:**
- Avg price per sqm
- Flood risk
- Security level
- Infrastructure
- Power hours/day
- 5-year appreciation
- Smart Score

---

## 🌐 Deploy with Webhook (Production)

### Option A: Flask Server (Simple)
```python
# webhook_server.py
from flask import Flask, request
from whatsapp_bot import WhatsAppBot

app = Flask(__name__)
bot = WhatsAppBot()

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '')
    from_number = request.values.get('From', '')
    
    response = bot.get_webhook_response(incoming_msg, from_number)
    return response, 200, {'Content-Type': 'text/xml'}

if __name__ == '__main__':
    app.run(port=5000)
```

**Run:**
```bash
pip install flask
python webhook_server.py
```

### Option B: DigitalOcean App Platform ($50/month)
1. Push code to GitHub
2. Create new App on DigitalOcean
3. Connect GitHub repo
4. Set environment variables (TWILIO_ACCOUNT_SID, etc.)
5. Deploy

### Configure Twilio Webhook
1. Go to Twilio Console → Messaging → WhatsApp Sandbox Settings
2. Set **"When a message comes in"** to:
   ```
   https://your-domain.com/whatsapp
   ```
3. Method: **POST**
4. Save

---

## 🧪 Testing Workflow

### 1. Join Sandbox (One-Time)
1. Send WhatsApp message to: **+1 415 523 8886**
2. Send text: **join [your-sandbox-code]**
   - Example: `join apple-banana`
   - Code is shown in Twilio Console → WhatsApp Sandbox

### 2. Test Queries
Send any query from [Query Examples](#-query-examples) section.

Example:
```
Property in Lekki ₦50M
```

Bot responds:
```
🏠 *PROPERTY INTEL: LEKKI PHASE 1*

💰 Your Budget: ₦50,000,000
💵 Avg Price: ₦350,000/sqm
🏡 Est. Total (120sqm): ₦42,000,000

✅ *WITHIN BUDGET*

🌊 Flood Risk: MODERATE (45/100)
🛡️ Security: GOOD (75/100)
🏗️ Infrastructure: 70
⚡ Power: 16 hrs/day
```

### 3. Monitor Usage
- Twilio Console → Monitor → Logs → Messaging
- Track message count (stay under 1,000/month for FREE)

---

## 💰 Cost Breakdown

### Phase 1 (Months 1-2)
| Service | Cost | Notes |
|---------|------|-------|
| **Twilio WhatsApp (FREE)** | $0 | 1,000 messages/month |
| Google Maps API | $200 | 28,000 map loads |
| DigitalOcean Droplet | $50 | 2GB RAM, 50GB SSD |
| Domain (naijapropintel.ng) | $1 | $12/year ÷ 12 |
| **TOTAL** | **$251/month** | Within $250 budget ✅ |

### Upgrade Path (Month 3+)
- **Twilio Paid**: $0.005/message after 1,000 FREE
- **10,000 messages/month**: $45/month additional
- **Total**: ~$300/month
- **Revenue (400 agents)**: ₦2M = $2,353/month
- **Profit**: $2,053/month

---

## 📈 Revenue Model Integration

### How Bot Generates Revenue

#### 1. Agent Verification Funnel
```
User Query → Bot Response → "Talk to Agent" CTA → Agent Profile → ₦5,000 Verification
```

**Example:**
```
User: "Property in Lekki ₦50M"
Bot: [Shows property intel]
     "💬 Talk to verified agent?"
User: "Yes"
Bot: "Contact Chinedu Okafor (verified ✅)
     📱 +234 803 456 7890"

Agent gets lead → More agents see value → Pay ₦5,000 to verify
```

#### 2. Lead Quality Scoring
Bot tracks:
- Property budget (₦50M = high-value lead)
- Location interest (Lekki = premium market)
- Query depth (multiple questions = serious buyer)

Agents pay for **quality leads**, not random inquiries.

#### 3. Agent Network Effects
- More agents = Better coverage
- Better coverage = More user trust
- More users = More leads
- More leads = More agent signups

**Target:** 1,000 agents × ₦5,000 = **₦5M** ($5,882)

---

## 🔧 Advanced Features

### 1. Message Tracking
```python
# Track message count to stay within FREE tier
message_count = 0

def send_tracked_message(to_number, message):
    global message_count
    if message_count >= 1000:
        return {"status": "error", "message": "FREE tier limit reached"}
    
    result = bot.send_message(to_number, message)
    if result['status'] == 'success':
        message_count += 1
    
    return result
```

### 2. User Sessions
```python
# Track user conversation history
user_sessions = {}

def process_with_context(user_phone, query):
    if user_phone not in user_sessions:
        user_sessions[user_phone] = {'queries': [], 'location': None}
    
    session = user_sessions[user_phone]
    session['queries'].append(query)
    
    # Use context for better responses
    if 'there' in query.lower() and session.get('location'):
        query = query.replace('there', session['location'])
    
    response = bot.process_query(query, user_phone)
    
    # Extract location from query for future context
    location = bot._extract_location(query)
    if location:
        session['location'] = location
    
    return response
```

### 3. Lead Capture
```python
# Capture interested users for agent follow-up
def capture_lead(query, user_phone):
    if bot._extract_price(query):  # User mentioned budget = serious buyer
        lead_data = {
            'phone': user_phone,
            'query': query,
            'budget': bot._extract_price(query),
            'location': bot._extract_location(query),
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to database or send to agents
        save_lead(lead_data)
```

---

## 🐛 Troubleshooting

### Issue 1: "Twilio not installed"
```bash
pip install twilio
```

### Issue 2: "zones.json not found"
```bash
# Ensure zones.json is in data/ folder
ls data/zones.json

# If missing, copy from backup or re-run Week 1 setup
```

### Issue 3: "Route search not available"
```bash
# Set Google Maps API key
export GOOGLE_MAPS_API_KEY='your_api_key_here'

# Or add to .env file
echo "GOOGLE_MAPS_API_KEY=your_key" >> .env
```

### Issue 4: "Agent system not available"
```bash
# Ensure agent_system_v2.py exists
ls agent_system_v2.py

# Initialize database
python agent_system_v2.py
```

### Issue 5: Twilio 401 Unauthorized
- Check TWILIO_ACCOUNT_SID is correct (starts with "AC")
- Check TWILIO_AUTH_TOKEN is correct
- Regenerate token if needed (Twilio Console → Settings)

### Issue 6: Message not received
- Ensure you joined sandbox: send "join [code]" to +1 415 523 8886
- Check Twilio Console → Monitor → Logs for errors
- Verify webhook URL is accessible (test with curl)

---

## 🎓 Integration Examples

### Flask App (Full Production)
```python
# app.py
from flask import Flask, request, jsonify
from whatsapp_bot import WhatsAppBot
import os

app = Flask(__name__)
bot = WhatsAppBot()

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages"""
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    
    # Log message
    print(f"📩 Message from {from_number}: {incoming_msg}")
    
    # Process query
    response = bot.get_webhook_response(incoming_msg, from_number)
    
    return response, 200, {'Content-Type': 'text/xml'}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'bot': 'operational',
        'zones': len(bot.zones),
        'agent_system': bot.agent_system is not None
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

### FastAPI Alternative
```python
# main.py
from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse
from whatsapp_bot import WhatsAppBot

app = FastAPI()
bot = WhatsAppBot()

@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    """Handle incoming WhatsApp messages"""
    response = bot.get_webhook_response(Body, From)
    return PlainTextResponse(content=response, media_type="text/xml")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "bot": "operational",
        "zones": len(bot.zones)
    }
```

---

## 📊 Analytics Dashboard

### Track Key Metrics
```python
# analytics.py
import json
from datetime import datetime

class BotAnalytics:
    def __init__(self):
        self.metrics = {
            'total_messages': 0,
            'unique_users': set(),
            'query_types': {},
            'locations_searched': {},
            'agents_requested': 0,
            'average_response_time': []
        }
    
    def track_query(self, user_phone, query, response_time):
        self.metrics['total_messages'] += 1
        self.metrics['unique_users'].add(user_phone)
        self.metrics['average_response_time'].append(response_time)
        
        # Categorize query
        if 'flood' in query.lower():
            self.metrics['query_types']['flood'] = \
                self.metrics['query_types'].get('flood', 0) + 1
        elif 'security' in query.lower():
            self.metrics['query_types']['security'] = \
                self.metrics['query_types'].get('security', 0) + 1
        elif 'agent' in query.lower():
            self.metrics['agents_requested'] += 1
    
    def get_report(self):
        return {
            'total_messages': self.metrics['total_messages'],
            'unique_users': len(self.metrics['unique_users']),
            'avg_response_time': sum(self.metrics['average_response_time']) / 
                                len(self.metrics['average_response_time']) 
                                if self.metrics['average_response_time'] else 0,
            'query_breakdown': self.metrics['query_types'],
            'agent_requests': self.metrics['agents_requested']
        }
```

---

## 🚀 Next Steps

### Week 4 Complete ✅
- [x] Twilio WhatsApp integration
- [x] Natural language processing
- [x] Property search queries
- [x] Flood risk analysis
- [x] Security queries
- [x] Agent discovery
- [x] Route-based search
- [x] Testing & demo

### Phase 1 Completion (Next)
1. **Deploy to Production**
   - Set up DigitalOcean Droplet
   - Configure domain (naijapropintel.ng)
   - Deploy Flask webhook server

2. **Marketing Launch**
   - Onboard first 50 agents
   - Share WhatsApp number publicly
   - Social media campaign

3. **Monitor & Optimize**
   - Track message usage (stay under 1,000)
   - Analyze query patterns
   - Improve response accuracy

### Phase 2 (Months 3-4)
- Advanced analytics dashboard
- Property listing by agents
- Lead management system
- Email notifications
- Payment integration (Paystack)

---

## 📝 Files Created

### Week 4 Deliverables
1. **whatsapp_bot.py** (770 lines)
   - WhatsAppBot class
   - Natural language processing
   - 7 query types (property, flood, security, agent, route, location, help)
   - Twilio integration
   - Demo function

2. **WHATSAPP_BOT_SETUP.md** (This file)
   - Complete setup guide
   - Query examples
   - Deployment instructions
   - Revenue model integration

3. **requirements.txt** (Updated)
   - twilio>=8.10.0

---

## 🎯 Success Metrics

### Phase 1 Goals (Month 1-2)
- [ ] 1,000 WhatsApp messages processed
- [ ] 100 unique users
- [ ] 50 agents onboarded (₦250K revenue)
- [ ] 10 properties listed
- [ ] 5 successful transactions

### Phase 2 Goals (Month 3-4)
- [ ] 10,000 WhatsApp messages/month
- [ ] 500 unique users
- [ ] 400 verified agents (₦2M revenue)
- [ ] 50 properties listed
- [ ] 20 successful transactions

---

## 📞 Support

### Questions?
- **Email**: support@naijapropintel.ng
- **WhatsApp**: +234 XXX XXX XXXX (Coming soon)
- **GitHub Issues**: https://github.com/amdsolutions007/Naija-Prop-Intel/issues

### Documentation
- [Week 1: Location Expansion](data/zones.json)
- [Week 2: Google Maps Integration](GOOGLE_MAPS_SETUP.md)
- [Week 3-4: Agent System](AGENT_SYSTEM_README.md)
- [Week 4: WhatsApp Bot](WHATSAPP_BOT_SETUP.md) ← You are here

---

## 📄 License
© 2025 AMD Solutions. All rights reserved.

---

**🎉 Week 4 Complete!**
**Phase 1 Deliverables: 4/4 ✅**

Next: Deploy to production and start generating revenue! 🚀
