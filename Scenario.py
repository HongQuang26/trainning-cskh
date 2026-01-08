import streamlit as st
import json
import os
import time
import pandas as pd
from datetime import datetime
import random

# ==============================================================================
# 0. CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Service Hero Academy",
    page_icon="💎",
    layout="wide"
)

# --- ROBUST IMAGE ENGINE (LOREMFLICKR) ---
# Dùng LoremFlickr để lấy ảnh theo từ khóa. Luôn đảm bảo có ảnh.
def get_scene_image(category, step_index):
    """
    Generates a stable image URL based on category keywords.
    Uses 'lock' parameter to ensure the image doesn't change randomly on re-renders.
    """
    # Map categories to reliable keywords
    keywords_map = {
        "F&B": "restaurant,dining,food",
        "HOTEL": "luxury hotel,resort,room",
        "TECH": "office,computer,meeting",
        "RETAIL": "shopping,store,boutique",
        "TRAVEL": "airport,airplane,travel",
        "BANK": "bank,atm,finance",
        "SPA": "spa,massage,skincare",
        "REAL ESTATE": "apartment,living room,house",
        "LOGISTICS": "delivery,warehouse,shipping",
        "GENERAL": "business,meeting,office"
    }
    
    # Determine keywords based on scenario title/category
    keywords = "business"
    for key, val in keywords_map.items():
        if key in category.upper():
            keywords = val
            break
            
    # Construct URL (LoremFlickr is very stable)
    # width=800, height=500
    # lock={step_index} ensures different steps get different images, but consistent ones.
    return f"https://loremflickr.com/800/500/{keywords}?lock={step_index + 100}"

# ==============================================================================
# 1. VIBRANT UI CSS
# ==============================================================================
st.markdown("""
<style>
    /* 1. GLOBAL FONTS & THEME */
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;800&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #f6f8fd 0%, #eef2f3 100%);
        font-family: 'Manrope', sans-serif;
        color: #1e293b;
    }
    
    /* 2. HEADERS */
    h1 {
        background: linear-gradient(90deg, #2563eb, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    /* 3. CARD STYLING */
    .scenario-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid rgba(255,255,255,0.8);
        transition: transform 0.2s, box-shadow 0.2s;
        margin-bottom: 20px;
    }
    .scenario-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(37, 99, 235, 0.15);
        border-left: 6px solid #2563eb;
    }
    .card-title { font-size: 1.25rem; font-weight: 800; color: #0f172a; margin-bottom: 8px; }
    .card-desc { font-size: 0.95rem; color: #64748b; margin-bottom: 16px; line-height: 1.5; }
    
    /* 4. CHAT INTERFACE */
    .chat-container {
        background: white;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.06);
        margin: 20px 0;
        border-left: 8px solid #f59e0b; /* Amber for attention */
    }
    .dialogue {
        font-size: 1.35rem;
        font-weight: 600;
        color: #1e293b;
        font-style: italic;
        margin-top: 10px;
        line-height: 1.6;
    }
    .customer-label {
        font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1.5px;
        font-weight: 800; color: #94a3b8;
    }

    /* 5. ACTION BUTTONS (HIGH CONTRAST) */
    .stButton button {
        background: linear-gradient(to bottom, #1e293b, #0f172a) !important; /* Dark Blue/Black */
        color: #fcd34d !important; /* Amber/Gold Text */
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 18px 24px !important;
        border-radius: 12px !important;
        border: 1px solid #334155 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
        width: 100%;
    }
    .stButton button:hover {
        background: linear-gradient(to bottom, #334155, #1e293b) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        color: #fff !important;
    }

    /* 6. BADGES & METRICS */
    .badge {
        padding: 6px 12px; border-radius: 50px; font-size: 0.75rem; font-weight: 800;
        text-transform: uppercase; letter-spacing: 0.5px;
    }
    .badge-hard { background: #fee2e2; color: #991b1b; }
    .badge-med { background: #fef3c7; color: #92400e; }
    
    .analysis-box {
        padding: 20px; border-radius: 12px; margin-top: 15px; color: white;
    }
    .win-bg { background: linear-gradient(135deg, #10b981, #059669); }
    .lose-bg { background: linear-gradient(135deg, #ef4444, #dc2626); }

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
        "customer": {"name": "Ms. Jade", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Jade", "traits": ["Picky"]},
        "steps": {
            "start": { "text": "Manager! Look! A hair in my soup! Are you feeding me garbage?", "choices": {"A": "Deny: 'Not our staff's hair.'", "B": "Act: 'Terribly sorry! Handling it now.'"}, "consequences": {"A": {"next": "lose", "change": -40, "analysis": "❌ Denial destroys trust."}, "B": {"next": "step_2", "change": +10, "analysis": "✅ Immediate action."}} },
            "step_2": { "text": "I lost my appetite. I'll just leave.", "choices": {"A": "Wait: 'Please eat something.'", "B": "Offer: 'Allow me to pack a dessert for you?'"}, "consequences": {"A": {"next": "lose", "change": -10, "analysis": "⚠️ Don't force."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Nice gesture."}} },
            "step_3": { "text": "Okay, fine. Can I get the bill?", "choices": {"A": "Discount: '10% Off.'", "B": "Compensate: 'It is free tonight.'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "❌ Insulting."}, "B": {"next": "win", "change": +40, "analysis": "🏆 Wow moment."}} },
            "win": {"type": "WIN", "title": "SUCCESS", "text": "She left happy.", "score": 100},
            "lose": {"type": "LOSE", "title": "FAILED", "text": "Bad Review.", "score": 40}
        }
    },
    "SC_HOTEL_01": {
        "title": "Hotel: Overbooked",
        "desc": "No room for honeymoon couple.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mike", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Mike", "traits": ["Tired"]},
        "steps": {
            "start": { "text": "I booked Ocean View! Why Garden View?", "choices": {"A": "Policy: 'System error.'", "B": "Apology: 'Our fault entirely.'"}, "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Excuses."}, "B": {"next": "step_2", "change": +20, "analysis": "✅ Ownership."}} },
            "step_2": { "text": "This ruins our trip!", "choices": {"A": "Gift: 'Free breakfast.'", "B": "Upgrade: 'Finding better room.'"}, "consequences": {"A": {"next": "lose", "change": -10, "analysis": "⚠️ Too small."}, "B": {"next": "step_3", "change": +10, "analysis": "✅ Effort."}} },
            "step_3": { "text": "Well?", "choices": {"A": "Wait: 'Tomorrow.'", "B": "Hero: 'Presidential Suite (Free).'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "❌ Sad."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Heroic."}} },
            "win": {"type": "WIN", "title": "DREAM TRIP", "text": "They loved it.", "score": 100},
            "lose": {"type": "LOSE", "title": "WALK OUT", "text": "They left.", "score": 0}
        }
    },
    "SC_ECOMM_01": {
        "title": "E-comm: Lost Package",
        "desc": "Package marked delivered but missing.",
        "difficulty": "Medium",
        "customer": {"name": "Tom", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Tom", "traits": ["Anxious"]},
        "steps": {
            "start": { "text": "App says delivered. I see nothing!", "choices": {"A": "Deflect: 'Check neighbors.'", "B": "Help: 'Checking now.'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "❌ Lazy."}, "B": {"next": "step_2", "change": +20, "analysis": "✅ Helpful."}} },
            "step_2": { "text": "I need it tomorrow!", "choices": {"A": "Wait: 'Wait 24h.'", "B": "Urgent: 'Calling driver.'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "⚠️ Slow."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Fast."}} },
            "step_3": { "text": "Driver hid it in a bush?", "choices": {"A": "Hope: 'Look there.'", "B": "Safety: 'Check. If lost, I resend.'"}, "consequences": {"A": {"next": "lose", "change": 0, "analysis": "😐 Passive."}, "B": {"next": "win", "change": +40, "analysis": "🏆 Trust."}} },
            "win": {"type": "WIN", "title": "FOUND", "text": "He got it.", "score": 100},
            "lose": {"type": "LOSE", "title": "ANGRY", "text": "Refunded.", "score": 30}
        }
    },
    "SC_TECH_01": {
        "title": "IT: Internet Down",
        "desc": "Meeting in progress, net cuts out.",
        "difficulty": "Medium",
        "customer": {"name": "Ken", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Ken", "traits": ["Urgent"]},
        "steps": {
            "start": { "text": "Net down! In a meeting! I restarted already!", "choices": {"A": "Script: 'Restart again.'", "B": "Listen: 'I see the error.'"}, "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Listening failure."}, "B": {"next": "step_2", "change": +10, "analysis": "✅ Validated."}} },
            "step_2": { "text": "Fix it now!", "choices": {"A": "Wait: 'Tech in 4h.'", "B": "Remote: 'Resetting... 30s.'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "⚠️ Too slow."}, "B": {"next": "step_3", "change": +10, "analysis": "✅ Speed."}} },
            "step_3": { "text": "Still red!", "choices": {"A": "Sorry: 'Wait.'", "B": "Data: 'Free 50GB 4G Data.'"}, "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Stranded."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Saved meeting."}} },
            "win": {"type": "WIN", "title": "SAVED", "text": "Meeting worked.", "score": 100},
            "lose": {"type": "LOSE", "title": "CHURN", "text": "Switched provider.", "score": 0}
        }
    },
    "SC_RETAIL_01": {
        "title": "Retail: Broken Item",
        "desc": "VIP received broken vase.",
        "difficulty": "Hard",
        "customer": {"name": "Lan", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Lan", "traits": ["VIP"]},
        "steps": {
            "start": { "text": "My $500 vase is broken!", "choices": {"A": "Empathy: 'Oh no! Sorry.'", "B": "Check: 'Order ID?'"}, "consequences": {"A": {"next": "step_2", "change": 20, "analysis": "✅ Good start."}, "B": {"next": "lose", "change": -20, "analysis": "⚠️ Robotic."}} },
            "step_2": { "text": "Need it tonight!", "choices": {"A": "Stock: 'No stock.'", "B": "Look: 'Checking stores.'"}, "consequences": {"A": {"next": "step_3", "change": 0, "analysis": "✅ Honest."}, "B": {"next": "lose", "change": -10, "analysis": "❌ Lazy."}} },
            "step_3": { "text": "Out of stock?!", "choices": {"A": "Refund: 'Refund.'", "B": "Rescue: 'Express ship warehouse.'"}, "consequences": {"A": {"next": "lose", "change": -10, "analysis": "😐 Not solved."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Solved."}} },
            "win": {"type": "WIN", "title": "SAVED", "text": "Arrived in time.", "score": 100},
            "lose": {"type": "LOSE", "title": "LOST VIP", "text": "She left.", "score": 40}
        }
    },
    "SC_BANK_01": {
        "title": "Bank: Card Swallowed",
        "desc": "Elderly lady needs medicine money.",
        "difficulty": "Hard",
        "customer": {"name": "Evelyn", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Evelyn", "traits": ["Elderly"]},
        "steps": {
            "start": { "text": "Card gone! Need medicine!", "choices": {"A": "Wait: 'Come Monday.'", "B": "Help: 'Card is safe.'"}, "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Dangerous."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Safety first."}} },
            "step_2": { "text": "Forgot ID.", "choices": {"A": "Rule: 'Can't help.'", "B": "Verify: 'Security Qs?'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "⚠️ Rigid."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Adaptable."}} },
            "step_3": { "text": "Verified.", "choices": {"A": "App: 'Use App cash.'", "B": "Do it: 'I do it.'"}, "consequences": {"A": {"next": "win", "change": +40, "analysis": "🏆 Empowering."}, "B": {"next": "lose", "change": -10, "analysis": "❌ Security risk."}} },
            "win": {"type": "WIN", "title": "SAFE", "text": "Got medicine.", "score": 100},
            "lose": {"type": "LOSE", "title": "LEFT", "text": "Switched banks.", "score": 0}
        }
    },
    "SC_LOGISTICS_01": {
        "title": "Logistics: Event Fail",
        "desc": "Gear broken before event.",
        "difficulty": "Very Hard",
        "customer": {"name": "Robert", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Robert", "traits": ["Furious"]},
        "steps": {
            "start": { "text": "Gear broken! Event tomorrow!", "choices": {"A": "Form: 'File claim.'", "B": "Fix: 'Handling it.'"}, "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Bureaucratic."}, "B": {"next": "step_2", "change": +40, "analysis": "✅ Leader."}} },
            "step_2": { "text": "How?", "choices": {"A": "Rent: 'Rent locally?'", "B": "Truck: 'Truck diverted.'"}, "consequences": {"A": {"next": "lose", "change": -10, "analysis": "⚠️ Lazy."}, "B": {"next": "step_3", "change": +30, "analysis": "✅ Solution."}} },
            "step_3": { "text": "Will it arrive?", "choices": {"A": "Hope: 'Maybe.'", "B": "Backup: 'Sent 2 trucks.'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "⚠️ Weak."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Guarantee."}} },
            "win": {"type": "WIN", "title": "SAVED", "text": "Success.", "score": 100},
            "lose": {"type": "LOSE", "title": "FIRED", "text": "Contract lost.", "score": 0}
        }
    },
    "SC_SAAS_01": {
        "title": "SaaS: Data Deleted",
        "desc": "Admin deleted data.",
        "difficulty": "Hard",
        "customer": {"name": "Sarah", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah", "traits": ["Angry"]},
        "steps": {
            "start": { "text": "DATA GONE!", "choices": {"A": "Ask: 'Cleared cache?'", "B": "Alert: 'Escalating.'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "❌ Silly."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Serious."}} },
            "step_2": { "text": "Restore 4 hours?", "choices": {"A": "Sorry: 'Process.'", "B": "Work: 'Manual extract?'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "⚠️ Passive."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Action."}} },
            "step_3": { "text": "Boss will kill me.", "choices": {"A": "Comfort: 'It's ok.'", "B": "Cover: 'I'll email boss.'"}, "consequences": {"A": {"next": "lose", "change": -10, "analysis": "❌ Weak."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Ownership."}} },
            "win": {"type": "WIN", "title": "RENEWED", "text": "Job saved.", "score": 100},
            "lose": {"type": "LOSE", "title": "LOST", "text": "Cancelled.", "score": 0}
        }
    },
    "SC_SPA_01": {
        "title": "Spa: Allergic",
        "desc": "Face burning.",
        "difficulty": "Hard",
        "customer": {"name": "Chloe", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Chloe", "traits": ["Pain"]},
        "steps": {
            "start": { "text": "Face burning!", "choices": {"A": "Waiver: 'You signed.'", "B": "Aid: 'Ice pack!'"}, "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Cruel."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Care."}} },
            "step_2": { "text": "Still red!", "choices": {"A": "Wait: 'Will pass.'", "B": "Doctor: 'Dermatologist.'"}, "consequences": {"A": {"next": "lose", "change": -10, "analysis": "⚠️ Risky."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Safe."}} },
            "step_3": { "text": "Who pays?", "choices": {"A": "Split: '50/50.'", "B": "Full: 'We pay 100%.'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "❌ Cheap."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Responsible."}} },
            "win": {"type": "WIN", "title": "HEALED", "text": "All good.", "score": 100},
            "lose": {"type": "LOSE", "title": "SUED", "text": "Lawsuit.", "score": 0}
        }
    },
    "SC_REALESTATE_01": {
        "title": "Real Estate: Mold",
        "desc": "Mold in luxury apt.",
        "difficulty": "Very Hard",
        "customer": {"name": "Chen", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Chen", "traits": ["Rich"]},
        "steps": {
            "start": { "text": "Mold?! My son has asthma!", "choices": {"A": "Defend: 'Air it?'", "B": "Alert: 'Evacuate.'"}, "consequences": {"A": {"next": "lose", "change": -40, "analysis": "❌ Blaming."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Safety."}} },
            "step_2": { "text": "Can't stay.", "choices": {"A": "Paint: 'Tomorrow.'", "B": "Move: 'Move now.'"}, "consequences": {"A": {"next": "lose", "change": -30, "analysis": "⚠️ Unsafe."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Correct."}} },
            "step_3": { "text": "Where?", "choices": {"A": "Motel: 'Cheap.'", "B": "Hotel: '5-Star.'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "❌ Insult."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Classy."}} },
            "win": {"type": "WIN", "title": "HAPPY", "text": "Safe.", "score": 100},
            "lose": {"type": "LOSE", "title": "SUED", "text": "Lawsuit.", "score": 0}
        }
    },
    "SC_AIRLINE_01": {
        "title": "Airline: Cancelled",
        "desc": "Missing wedding.",
        "difficulty": "Very Hard",
        "customer": {"name": "David", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=David", "traits": ["Panic"]},
        "steps": {
            "start": { "text": "Cancelled?! Wedding in 6h!", "choices": {"A": "Reason: 'Weather.'", "B": "Act: 'Finding seat.'"}, "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Don't explain."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Act."}} },
            "step_2": { "text": "Hurry!", "choices": {"A": "Us: 'Tomorrow.'", "B": "Partner: 'Checking partners.'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "⚠️ Too late."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Flexible."}} },
            "step_3": { "text": "No flights?", "choices": {"A": "Sorry: 'Apologies.'", "B": "Creative: 'Fly + Taxi.'"}, "consequences": {"A": {"next": "lose", "change": -10, "analysis": "❌ Giving up."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Hero."}} },
            "win": {"type": "WIN", "title": "ARRIVED", "text": "In time.", "score": 100},
            "lose": {"type": "LOSE", "title": "MISSED", "text": "Missed it.", "score": 0}
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

ALL_SCENARIOS = load_data()

# --- SIDEBAR MENU ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.markdown("### Service Hero Academy")
    menu = st.radio("Navigation", ["Dashboard", "Create New"])
    
    st.divider()
    if st.button("🔄 Restore Original Scenarios"):
        load_data(True)
        st.success("Restored!")
        time.sleep(1)
        st.rerun()

# --- DASHBOARD ---
if menu == "Dashboard":
    if st.session_state.current_scenario is None:
        st.title("🎓 Service Hero Academy")
        st.write("Master your skills with interactive roleplay scenarios.")
        
        # Player Entry
        if 'player_name' not in st.session_state: st.session_state.player_name = ""
        if not st.session_state.player_name:
            st.info("Please enter your name to start.")
            st.session_state.player_name = st.text_input("Name:")
            if not st.session_state.player_name: st.stop()
        else:
            c1, c2 = st.columns([3, 1])
            c1.success(f"Agent: **{st.session_state.player_name}**")
            if c2.button("Logout"): 
                st.session_state.player_name = ""
                st.rerun()

        with st.expander("🏆 Leaderboard"):
            show_leaderboard()
            
        st.divider()
        st.subheader(f"Available Missions ({len(ALL_SCENARIOS)})")
        
        # Grid Layout for Scenarios
        cols = st.columns(2)
        idx = 0
        for key, val in ALL_SCENARIOS.items():
            with cols[idx % 2]:
                badge_class = "badge-hard" if "Hard" in val['difficulty'] else "badge-med"
                st.markdown(f"""
                <div class="scenario-card">
                    <div class="card-title">{val['title']}</div>
                    <div class="card-desc">{val['desc']}</div>
                    <span class="badge {badge_class}">{val['difficulty']}</span>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Start Mission 🚀", key=key, use_container_width=True):
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
        step_data = scenario['steps'].get(step_id, scenario.get(step_id)) # Handle win/lose keys
        
        # Robust Image Loading
        # Step index for locking image: start=0, step_2=1, step_3=2...
        step_idx = 0
        if step_id == 'step_2': step_idx = 1
        elif step_id == 'step_3': step_idx = 2
        elif step_id in ['win', 'lose']: step_idx = 3
        
        img_url = get_scene_image(scenario['title'], step_idx)
        
        # Sidebar
        with st.sidebar:
            st.divider()
            if st.button("❌ Exit Mission", use_container_width=True):
                st.session_state.current_scenario = None
                st.rerun()
            
            cust = scenario['customer']
            st.image(cust['avatar'], width=100)
            st.markdown(f"**{cust['name']}**")
            
            p = st.session_state.patience
            color = "green" if p > 50 else "red"
            st.markdown(f"**Customer Patience:** :{color}[{p}%]")
            st.progress(p/100)

        # Game Screen
        if "type" in step_data: # End Screen
            st.title(step_data['title'])
            st.image(img_url, use_container_width=True)
            
            result_class = "win-bg" if step_data['type'] == 'WIN' else "lose-bg"
            st.markdown(f"<div class='analysis-box {result_class}'><h2>{step_data['text']}</h2></div>", unsafe_allow_html=True)
            
            if step_data['type'] == 'WIN': st.balloons()
            
            st.metric("Final Score", step_data['score'])
            
            if 'saved' not in st.session_state:
                save_score(st.session_state.player_name, scenario['title'], step_data['score'], step_data['type'])
                st.session_state.saved = True
                
            if st.button("Return to Dashboard", use_container_width=True):
                st.session_state.current_scenario = None
                if 'saved' in st.session_state: del st.session_state.saved
                st.rerun()
                
            st.divider()
            st.subheader("Mission Analysis")
            for h in st.session_state.history:
                icon = "✅" if h['change'] > 0 else "❌"
                color = "#dcfce7" if h['change'] > 0 else "#fee2e2"
                text_col = "#166534" if h['change'] > 0 else "#991b1b"
                st.markdown(f"""
                <div style="background:{color}; padding:15px; border-radius:10px; margin-top:10px; color:{text_col}; font-weight:600;">
                    {icon} You chose: {h['choice']}<br>
                    <span style="font-weight:400; font-style:italic;">👉 {h['analysis']}</span>
                </div>
                """, unsafe_allow_html=True)

        else: # Playing
            st.subheader(scenario['title'])
            st.image(img_url, use_container_width=True)
            
            st.markdown(f"""
            <div class="chat-container">
                <div class="customer-label">CUSTOMER SAYS:</div>
                <div class="dialogue">"{step_data['text']}"</div>
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
    st.info("Custom scenarios are supported in Demo mode.")
    with st.form("builder"):
        title = st.text_input("Title")
        desc = st.text_input("Description")
        if st.form_submit_button("Save"):
            st.success("Saved (Demo Mode)")
