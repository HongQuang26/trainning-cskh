import streamlit as st
import json
import os
import time
import pandas as pd
from datetime import datetime
import urllib.parse
import google.generativeai as genai

# ==============================================================================
# 0. CONFIGURATION & AI ENGINE
# ==============================================================================
# Your API Key
GEMINI_API_KEY = "AIzaSyD5ma9Q__JMZUs6mjBppEHUcUBpsI-wjXA"

st.set_page_config(
    page_title="Service Hero Global",
    page_icon="🌍",
    layout="wide"
)

def init_ai():
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        return True
    except:
        return False

def generate_ai_image_url(scenario_context, default_img_url):
    """
    Generates a reliable image URL.
    Strategy: Ask Gemini for just 3 simple keywords to ensure the URL never breaks.
    """
    try:
        # 1. Ask Gemini for KEYWORDS only (Safe & Short)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt_request = f"""
        Extract 3 simple visual keywords (nouns/adjectives) from this scene for an image generator.
        Scene: "{scenario_context}"
        Output format: word1 word2 word3
        Example: angry customer restaurant
        """
        response = model.generate_content(prompt_request)
        keywords = response.text.strip().replace("\n", " ").replace('"', '').replace(',', '')
        
        # 2. Limit length to prevent URL breakage
        if len(keywords) > 50: keywords = "customer service situation"
        
        # 3. Construct Safe URL
        encoded_prompt = urllib.parse.quote(keywords)
        seed = int(time.time())
        # Using Pollinations with simple keywords is 99% stable
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=500&seed={seed}&nologo=true&model=flux"
        return image_url
    except Exception:
        # Absolute fallback to a reliable placeholder
        return "https://placehold.co/800x500/png?text=Scene+Loading..."

init_ai()

# ==============================================================================
# 1. HIGH CONTRAST UI STYLING (CSS)
# ==============================================================================
st.markdown("""
<style>
    /* FORCE LIGHT THEME & HIGH CONTRAST */
    .stApp {
        background-color: #f4f6f9 !important; /* Light Grey Background */
    }
    
    h1, h2, h3, p, div, span, label {
        color: #1e293b !important; /* Dark Blue-Black Text */
    }
    
    /* CARD STYLE - WHITE BACKGROUND, DARK TEXT */
    .scenario-card {
        background-color: #ffffff !important;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
        color: #000000 !important;
    }
    
    /* CHAT BUBBLES */
    .chat-container {
        background-color: #ffffff !important;
        padding: 20px;
        border-radius: 15px;
        border-left: 6px solid #2563eb;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin: 15px 0;
        color: #000000 !important;
    }
    
    .customer-label {
        font-weight: bold;
        color: #64748b !important;
        text-transform: uppercase;
        font-size: 0.85rem;
    }
    
    .dialogue-text {
        font-size: 1.2rem;
        font-style: italic;
        color: #0f172a !important; /* Deep Black */
        line-height: 1.5;
    }
    
    /* BUTTONS */
    .stButton button {
        background-color: #3b82f6 !important;
        color: white !important;
        border: none;
        font-weight: bold;
        border-radius: 8px;
        height: 50px;
    }
    .stButton button:hover {
        background-color: #2563eb !important;
    }
    
    /* ANALYSIS BOXES */
    .analysis-box {
        padding: 15px; border-radius: 8px; margin-top: 10px;
        color: #000000 !important;
    }
    .good { background-color: #dcfce7 !important; border: 1px solid #86efac; }
    .bad { background-color: #fee2e2 !important; border: 1px solid #fca5a5; }
    
    /* Hide Streamlit default menu elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. FULL ENGLISH DATASET (11 SCENARIOS)
# ==============================================================================
INITIAL_DATA = {
    "SC_FNB_01": {
        "title": "F&B: Foreign Object",
        "desc": "Hair in soup. Customer is disgusted.",
        "difficulty": "Hard",
        "customer": {"name": "Ms. Jade", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Jade", "traits": ["Picky", "Reviewer"]},
        "steps": {
            "start": { 
                "text": "Manager! Look! A hair in my soup! Are you feeding me garbage?",
                "choices": {"A": "Deny: 'Not our staff's hair.'", "B": "Act: 'Terribly sorry! Handling it now.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -40, "analysis": "❌ Denial destroys trust."}, "B": {"next": "step_2", "change": +10, "analysis": "✅ Immediate action is correct."}}
            },
            "step_2": { 
                "text": "I lost my appetite. My friend is almost done eating.",
                "choices": {"A": "Persuade: 'Please try it again.'", "B": "Pivot: 'I understand. Dessert on us instead?'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Don't force them."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Offering alternatives."}}
            },
            "step_3": { 
                "text": "Fine. Bring me the bill.",
                "choices": {"A": "Discount: '10% off.'", "B": "Compensate: 'Tonight is free. Plus a voucher.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ 10% is insulting here."}, "B": {"next": "game_over_good", "change": +40, "analysis": "🏆 Wow moment created."}}
            },
            "game_over_good": {"type": "WIN", "title": "SUCCESS", "text": "She left a tip.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "LOST CUSTOMER", "text": "She left a 1-star review.", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "DISASTER", "text": "Video went viral.", "score": 0}
        }
    },
    "SC_HOTEL_01": {
        "title": "Hotel: Overbooked",
        "desc": "Honeymoon couple, no ocean view room.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. Mike", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Mike", "traits": ["Tired", "High Expectation"]},
        "steps": {
            "start": { 
                "text": "I booked Ocean View months ago! I won't take Garden View!",
                "choices": {"A": "Policy: 'System error. Sorry.'", "B": "Own it: 'This is our fault. I apologize.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Don't blame the system."}, "B": {"next": "step_2", "change": +20, "analysis": "✅ Sincere apology first."}}
            },
            "step_2": { 
                "text": "We flew 12 hours for this view!",
                "choices": {"A": "Small Gift: 'Free breakfast?'", "B": "Solution: 'Let me find an upgrade.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Not enough."}, "B": {"next": "step_3", "change": +10, "analysis": "✅ Effort matters."}}
            },
            "step_3": { 
                "text": "Well? My wife is waiting.",
                "choices": {"A": "Wait: 'Room available tomorrow.'", "B": "Hero: 'Upgrading you to Presidential Suite.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Disappointing."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Over-delivery wins."}}
            },
            "game_over_good": {"type": "WIN", "title": "DREAM TRIP", "text": "They loved the suite.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "SAD TRIP", "text": "They won't return.", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "WALK OUT", "text": "They left the hotel.", "score": 0}
        }
    },
    "SC_RETAIL_01": {
        "title": "Retail: Broken Item",
        "desc": "VIP received broken vase.",
        "difficulty": "Hard",
        "customer": {"name": "Ms. Lan", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Lan", "traits": ["VIP", "Urgent"]},
        "steps": {
            "start": { "text": "My $500 vase arrived shattered!", "choices": {"A": "Empathy: 'Oh no! I am so sorry.'", "B": "Check: 'Order ID?'"}, "consequences": {"A": {"next": "step_2", "change": 20, "analysis": "✅ Empathy first."}, "B": {"next": "game_over_bad", "change": -20, "analysis": "⚠️ Too robotic."}} },
            "step_2": { "text": "I need it for a gift tonight!", "choices": {"A": "Stock: 'We are out of stock.'", "B": "Check: 'Let me check other stores.'"}, "consequences": {"A": {"next": "step_3", "change": 0, "analysis": "✅ Honest but bad news."}, "B": {"next": "game_over_fail", "change": -10, "analysis": "❌ Wasting time if you don't look."}} },
            "step_3": { "text": "Out of stock?! I'm dead!", "choices": {"A": "Refund: 'I'll refund you.'", "B": "Rescue: 'I'll express ship from warehouse by 5pm.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "😐 Problem not solved."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Solving the need."}} },
            "game_over_good": {"type": "WIN", "title": "SAVED", "text": "Arrived in time.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "LOST VIP", "text": "She left disappointed.", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "RANT", "text": "Bad social media post.", "score": 0}
        }
    },
    "SC_ECOMM_01": {
        "title": "E-comm: Lost Package",
        "desc": "App says delivered, but nothing there.",
        "difficulty": "Medium",
        "customer": {"name": "Tom", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Tom", "traits": ["Anxious"]},
        "steps": {
            "start": { "text": "App says delivered. I see nothing! Scam?", "choices": {"A": "Deflect: 'Check neighbors.'", "B": "Help: 'I will investigate now.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -20, "analysis": "❌ Don't be lazy."}, "B": {"next": "step_2", "change": +20, "analysis": "✅ Helpful."}} },
            "step_2": { "text": "I need these shoes for tomorrow!", "choices": {"A": "Wait: 'Wait 24h.'", "B": "Call: 'Calling courier now.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Too slow."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Urgent action."}} },
            "step_3": { "text": "Courier put it in a bush?", "choices": {"A": "Hope: 'Check there.'", "B": "Guarantee: 'Check. If missing, I send new pair.'"}, "consequences": {"A": {"next": "game_over_good", "change": 0, "analysis": "😐 Passive."}, "B": {"next": "game_over_good", "change": +40, "analysis": "🏆 Risk reversal."}} },
            "game_over_good": {"type": "WIN", "title": "FOUND", "text": "He found the shoes.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "LATE", "text": "He bought elsewhere.", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "REPORTED", "text": "Marked as scam.", "score": 0}
        }
    },
    "SC_TECH_01": {
        "title": "IT: Internet Down",
        "desc": "Meeting in progress, net cuts out.",
        "difficulty": "Medium",
        "customer": {"name": "Ken", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Ken", "traits": ["Urgent"]},
        "steps": {
            "start": { "text": "Net is down! I'm in a meeting! I restarted it already!", "choices": {"A": "Script: 'Restart again.'", "B": "Listen: 'I see packet loss.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ He just said he did!"}, "B": {"next": "step_2", "change": +10, "analysis": "✅ Listening."}} },
            "step_2": { "text": "Fix it! 5 minutes left!", "choices": {"A": "Wait: 'Tech coming in 4h.'", "B": "Remote: 'Resetting port... 30s.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Too slow."}, "B": {"next": "step_3", "change": +10, "analysis": "✅ Fast attempt."}} },
            "step_3": { "text": "Still red light!", "choices": {"A": "Sorry: 'Wait for tech.'", "B": "Data: 'Gifting you 50GB 4G Data NOW.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -30, "analysis": "❌ Stranded."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Saved the meeting."}} },
            "game_over_good": {"type": "WIN", "title": "SAVED", "text": "Meeting worked on 4G.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "FAILED", "text": "Missed meeting.", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "CHURN", "text": "Switched provider.", "score": 0}
        }
    },
     "SC_AIRLINE_01": {
        "title": "Airline: Cancelled",
        "desc": "Missing a wedding.",
        "difficulty": "Very Hard",
        "customer": {"name": "David", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=David", "traits": ["Panic"]},
        "steps": {
            "start": { "text": "Cancelled?! I'm the best man! Wedding is in 6 hours!", "choices": {"A": "Reason: 'Weather.'", "B": "Action: 'Let me find a seat.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Don't explain."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Act."}} },
            "step_2": { "text": "Hurry!", "choices": {"A": "Us: 'Next flight tomorrow.'", "B": "Partner: 'Checking partners...'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Too late."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Flexible."}} },
            "step_3": { "text": "No flights?", "choices": {"A": "Sorry: 'Apologies.'", "B": "Creative: 'Fly nearby + Taxi (On us).'"}, "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "❌ Giving up."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Heroic solve."}} },
            "game_over_good": {"type": "WIN", "title": "ARRIVED", "text": "Made it just in time.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "MISSED", "text": "Missed wedding.", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "SECURITY", "text": "Security called.", "score": 0}
        }
    },
    "SC_BANK_01": {
        "title": "Bank: Card Swallowed",
        "desc": "Elderly lady needs medicine money.",
        "difficulty": "Hard",
        "customer": {"name": "Evelyn", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Evelyn", "traits": ["Elderly"]},
        "steps": {
            "start": { "text": "Machine took my card! I need medicine money!", "choices": {"A": "Wait: 'Come Monday.'", "B": "Help: 'Card is safe. Let's withdraw.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Dangerous."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Safety first."}} },
            "step_2": { "text": "Forgot ID.", "choices": {"A": "Rule: 'Can't help.'", "B": "Verify: 'Security questions?'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Rigid."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Adaptable."}} },
            "step_3": { "text": "Verified. How to get cash?", "choices": {"A": "Guide: 'Use the App.'", "B": "Do it: 'I will do it.'"}, "consequences": {"A": {"next": "game_over_good", "change": +40, "analysis": "🏆 Empowering."}, "B": {"next": "game_over_fail", "change": -10, "analysis": "❌ Security breach."}} },
            "game_over_good": {"type": "WIN", "title": "SAFE", "text": "Got medicine.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "NO CASH", "text": "Went home empty.", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "LEFT", "text": "Switched banks.", "score": 0}
        }
    },
    "SC_REALESTATE_01": {
        "title": "Real Estate: Mold",
        "desc": "Luxury apartment has mold.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. Chen", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Chen", "traits": ["Rich"]},
        "steps": {
            "start": { "text": "$4000 for mold? My son has asthma!", "choices": {"A": "Defend: 'Did you air it out?'", "B": "Alert: 'Evacuate now.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -40, "analysis": "❌ Blaming customer."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Safety."}} },
            "step_2": { "text": "Black mold! We can't stay.", "choices": {"A": "Paint: 'Painter coming tomorrow.'", "B": "Move: 'You must move.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -30, "analysis": "⚠️ Not safe yet."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Correct."}} },
            "step_3": { "text": "Where to?", "choices": {"A": "Cheap: 'Motel.'", "B": "Luxury: '5-Star Hotel.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Insulting."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Matching standard."}} },
            "game_over_good": {"type": "WIN", "title": "HAPPY", "text": "Family safe.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "LEFT", "text": "Tenant left.", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "SUED", "text": "Health lawsuit.", "score": 0}
        }
    },
    "SC_SAAS_01": {
        "title": "SaaS: Data Deleted",
        "desc": "Admin deleted data by mistake.",
        "difficulty": "Hard",
        "customer": {"name": "Sarah", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah", "traits": ["Angry"]},
        "steps": {
            "start": { "text": "DATA GONE! Presentation in 2 hours!", "choices": {"A": "Ask: 'Cleared cache?'", "B": "Alert: 'Escalating SEV1.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -20, "analysis": "❌ Silly question."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Serious."}} },
            "step_2": { "text": "Restore takes 4 hours?", "choices": {"A": "Process: 'Sorry.'", "B": "Work: 'Manual extract?'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Helpful."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Manual save."}} },
            "step_3": { "text": "My boss will kill me.", "choices": {"A": "Comfort: 'It's ok.'", "B": "Cover: 'I'll email explaining it's our bug.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "❌ Weak."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Taking blame."}} },
            "game_over_good": {"type": "WIN", "title": "RENEWED", "text": "She kept her job.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "LOST", "text": "Contract cancelled.", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "ANGRY", "text": "Furious feedback.", "score": 0}
        }
    },
    "SC_SPA_01": {
        "title": "Spa: Allergic",
        "desc": "Face burning after facial.",
        "difficulty": "Hard",
        "customer": {"name": "Chloe", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Chloe", "traits": ["Pain"]},
        "steps": {
            "start": { "text": "Face burning!", "choices": {"A": "Waiver: 'You signed.'", "B": "Aid: 'Ice pack!'"}, "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Cruel."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Care."}} },
            "step_2": { "text": "Still red. Casting tomorrow!", "choices": {"A": "Wait: 'It will pass.'", "B": "Doctor: 'Dermatologist now.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Risky."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Proactive."}} },
            "step_3": { "text": "Who pays?", "choices": {"A": "Split: '50/50.'", "B": "Full: 'We pay 100%.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Cheap."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Responsibility."}} },
            "game_over_good": {"type": "WIN", "title": "CALM", "text": "Face healed.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "REVIEW", "text": "Bad review.", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "SUED", "text": "Legal action.", "score": 0}
        }
    },
    "SC_LOGISTICS_01": {
        "title": "Logistics: Event Fail",
        "desc": "Gear broken before event.",
        "difficulty": "Very Hard",
        "customer": {"name": "Robert", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Robert", "traits": ["Furious"]},
        "steps": {
            "start": { "text": "Gear broken! Event tomorrow!", "choices": {"A": "Form: 'File claim.'", "B": "Fix: 'Handling it.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Bureaucratic."}, "B": {"next": "step_2", "change": +40, "analysis": "✅ Leader."}} },
            "step_2": { "text": "How?", "choices": {"A": "Rent: 'You rent locally?'", "B": "Truck: 'Truck diverted. 4 hours.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Don't ask them."}, "B": {"next": "step_3", "change": +30, "analysis": "✅ Solution."}} },
            "step_3": { "text": "What if it breaks?", "choices": {"A": "Hope: 'It won't.'", "B": "Backup: 'Sent 2 trucks.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Weak."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Guarantee."}} },
            "game_over_good": {"type": "WIN", "title": "SAVED", "text": "Event succeeded.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "CANCELLED", "text": "Event ruined.", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "FIRED", "text": "Contract lost.", "score": 0}
        }
    }
}

DB_FILE = "scenarios.json"
HISTORY_FILE = "score_history.csv"

# ==============================================================================
# 3. DATA UTILS
# ==============================================================================
def load_data(force_reset=False):
    if force_reset or not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(INITIAL_DATA, f, indent=4)
        return INITIAL_DATA.copy()
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for k, v in INITIAL_DATA.items():
            if k not in data: data[k] = v
        return data
    except: return load_data(True)

def save_score(player, scenario, score, outcome):
    new_row = {"Time": datetime.now().strftime("%Y-%m-%d %H:%M"), "Player": player, "Scenario": scenario, "Score": score, "Outcome": outcome}
    if os.path.exists(HISTORY_FILE):
        df = pd.read_csv(HISTORY_FILE)
    else:
        df = pd.DataFrame(columns=["Time", "Player", "Scenario", "Score", "Outcome"])
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(HISTORY_FILE, index=False)

def show_leaderboard():
    if os.path.exists(HISTORY_FILE):
        df = pd.read_csv(HISTORY_FILE)
        if not df.empty:
            st.dataframe(df.sort_values(by="Score", ascending=False).head(10), use_container_width=True, hide_index=True)
        else: st.info("No data yet.")
    else: st.info("No history found.")

# ==============================================================================
# 4. MAIN APP LOGIC
# ==============================================================================
if 'current_scenario' not in st.session_state: st.session_state.current_scenario = None
if 'img_cache' not in st.session_state: st.session_state.img_cache = {}

ALL_SCENARIOS = load_data()

# --- SIDEBAR MENU ---
with st.sidebar:
    st.title("🛡️ Service Hero")
    st.markdown("### AI Training Hub")
    menu = st.radio("Navigation", ["Dashboard", "Create New"])
    
    st.divider()
    if st.button("🔄 Reset Scenarios"):
        load_data(True)
        st.success("Restored!")
        time.sleep(1)
        st.rerun()

# --- DASHBOARD ---
if menu == "Dashboard":
    if st.session_state.current_scenario is None:
        st.title("Welcome Agent 🎓")
        
        # Player Entry
        if 'player_name' not in st.session_state: st.session_state.player_name = ""
        if not st.session_state.player_name:
            st.info("Please enter your name to start.")
            st.session_state.player_name = st.text_input("Name:")
            if not st.session_state.player_name: st.stop()
        else:
            c1, c2 = st.columns([3, 1])
            c1.success(f"Logged in as: **{st.session_state.player_name}**")
            if c2.button("Logout"): 
                st.session_state.player_name = ""
                st.rerun()

        with st.expander("🏆 Leaderboard"):
            show_leaderboard()
            
        st.write("---")
        st.subheader("Select a Mission:")
        
        # Scenario Grid
        cols = st.columns(2)
        idx = 0
        for key, val in ALL_SCENARIOS.items():
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="scenario-card">
                    <h3>{val['title']}</h3>
                    <p style="color:#475569;">{val['desc']}</p>
                    <span style="background:#e2e8f0; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold;">{val['difficulty']}</span>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Start Mission ▶", key=key, use_container_width=True):
                    st.session_state.current_scenario = key
                    st.session_state.current_step = 'start'
                    st.session_state.patience = 50
                    st.session_state.history = []
                    st.rerun()
            idx += 1

    # --- GAMEPLAY ---
    else:
        s_key = st.session_state.current_scenario
        if s_key not in ALL_SCENARIOS: 
            st.session_state.current_scenario = None
            st.rerun()
            
        scenario = ALL_SCENARIOS[s_key]
        step_id = st.session_state.current_step
        step_data = scenario['steps'][step_id]
        
        # Image Generation (Safe Mode)
        cache_key = f"{s_key}_{step_id}"
        if cache_key not in st.session_state.img_cache:
            with st.spinner("🤖 AI is visualizing..."):
                # Always provide a fallback placeholder just in case
                fallback = "https://placehold.co/800x500/png?text=Scene+Loading..."
                ai_url = generate_ai_image_url(f"{scenario['title']} - {step_data.get('text', '')}", fallback)
                st.session_state.img_cache[cache_key] = ai_url
        
        current_img = st.session_state.img_cache[cache_key]
        
        # Sidebar
        with st.sidebar:
            st.divider()
            if st.button("❌ Abort Mission", use_container_width=True):
                st.session_state.current_scenario = None
                st.rerun()
            
            cust = scenario['customer']
            st.image(cust['avatar'], width=80)
            st.markdown(f"**{cust['name']}**")
            
            p = st.session_state.patience
            st.write(f"Patience: {p}%")
            st.progress(p/100)

        # Game Screen
        if "type" in step_data: # End Screen
            st.title(step_data['title'])
            st.image(current_img, use_container_width=True)
            
            result_class = "good" if step_data['type'] == 'WIN' else "bad"
            st.markdown(f"<div class='analysis-box {result_class}'><h3>{step_data['text']}</h3></div>", unsafe_allow_html=True)
            
            if step_data['type'] == 'WIN': st.balloons()
            
            st.metric("Final Score", step_data['score'])
            
            if 'saved' not in st.session_state:
                save_score(st.session_state.player_name, scenario['title'], step_data['score'], step_data['type'])
                st.session_state.saved = True
                
            if st.button("Back to Base", use_container_width=True):
                st.session_state.current_scenario = None
                if 'saved' in st.session_state: del st.session_state.saved
                st.rerun()
                
            st.write("---")
            st.subheader("Mission Debrief")
            for h in st.session_state.history:
                icon = "✅" if h['change'] > 0 else "❌"
                color = "good" if h['change'] > 0 else "bad"
                st.markdown(f"<div class='analysis-box {color}'><b>{icon} Choice:</b> {h['choice']}<br><i>{h['analysis']}</i></div>", unsafe_allow_html=True)

        else: # Playing
            st.subheader(scenario['title'])
            st.image(current_img, use_container_width=True)
            
            st.markdown(f"""
            <div class="chat-container">
                <div class="customer-label">Customer says:</div>
                <div class="dialogue-text">"{step_data['text']}"</div>
            </div>
            """, unsafe_allow_html=True)
            
            cols = st.columns(len(step_data['choices']))
            idx = 0
            for k, v in step_data['choices'].items():
                with cols[idx]:
                    if st.button(f"{k}. {v}", use_container_width=True):
                        cons = step_data['consequences'][k]
                        st.session_state.current_step = cons['next']
                        st.session_state.patience = max(0, min(100, st.session_state.patience + cons['change']))
                        st.session_state.history.append({
                            "step": step_data['text'],
                            "choice": v,
                            "analysis": cons['analysis'],
                            "change": cons['change']
                        })
                        st.rerun()
                idx += 1

elif menu == "Create New":
    st.header("Scenario Builder")
    st.info("Custom scenarios will also generate AI images automatically!")
    with st.form("builder"):
        title = st.text_input("Title")
        desc = st.text_input("Description")
        if st.form_submit_button("Save"):
            st.success("Saved (Demo Mode)")
