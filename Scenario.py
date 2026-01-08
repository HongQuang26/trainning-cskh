import streamlit as st
import json
import os
import time
import pandas as pd
from datetime import datetime

# ==============================================================================
# 0. CẤU HÌNH & HÌNH ẢNH CỐ ĐỊNH (FIXED ASSETS)
# ==============================================================================
st.set_page_config(
    page_title="Service Hero Academy",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- BỘ ẢNH CỐ ĐỊNH THEO KỊCH BẢN (CHỌN LỌC & KHÔNG BAO GIỜ CHẾT) ---
# Sử dụng ảnh chất lượng cao từ Unsplash với ID cụ thể để đảm bảo nội dung khớp 100%
SCENARIO_IMAGES = {
    "SC_FNB_01": "https://images.unsplash.com/photo-1559339352-11d035aa65de?q=80&w=1000&auto=format&fit=crop", # Restaurant context
    "SC_HOTEL_01": "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1000&auto=format&fit=crop", # Hotel Lobby/Resort
    "SC_ECOMM_01": "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?q=80&w=1000&auto=format&fit=crop", # Delivery/Payment
    "SC_TECH_01": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?q=80&w=1000&auto=format&fit=crop", # Office work
    "SC_RETAIL_01": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=1000&auto=format&fit=crop", # Retail Store
    "SC_BANK_01": "https://images.unsplash.com/photo-1601597111158-2fceff292cdc?q=80&w=1000&auto=format&fit=crop", # ATM/Bank
    "SC_REALESTATE_01": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=1000&auto=format&fit=crop", # Apartment
    "SC_SAAS_01": "https://images.unsplash.com/photo-1551434678-e076c223a692?q=80&w=1000&auto=format&fit=crop", # Software/Dashboard
    "SC_SPA_01": "https://images.unsplash.com/photo-1600334089648-b0d9d3028eb2?q=80&w=1000&auto=format&fit=crop", # Spa
    "SC_LOGISTICS_01": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=1000&auto=format&fit=crop", # Warehouse/Truck
    "SC_AIRLINE_01": "https://images.unsplash.com/photo-1436491865332-7a61a14527c5?q=80&w=1000&auto=format&fit=crop" # Airport
}

FALLBACK_IMG = "https://images.unsplash.com/photo-1557426272-fc759fdf7a8d?q=80&w=1000&auto=format&fit=crop" # Generic Meeting

def get_image(scenario_key):
    return SCENARIO_IMAGES.get(scenario_key, FALLBACK_IMG)

# ==============================================================================
# 1. GIAO DIỆN TƯƠNG PHẢN CAO (HIGH CONTRAST CSS)
# ==============================================================================
st.markdown("""
<style>
    /* 1. FORCE LIGHT MODE (Ép nền sáng để chữ không bị chìm) */
    [data-testid="stAppViewContainer"] {
        background-color: #F3F4F6 !important; /* Xám rất nhạt */
    }
    [data-testid="stHeader"] {
        background-color: #F3F4F6 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E5E7EB;
    }

    /* 2. TEXT VISIBILITY (Màu chữ đen đậm) */
    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: #111827 !important; /* Đen than (Charcoal) */
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* 3. CARD STYLE (Khung trắng nổi bật trên nền xám) */
    .scenario-card {
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        color: #000000 !important; /* Chữ đen tuyệt đối trong card */
    }
    
    /* 4. CHAT BUBBLES (Đoạn hội thoại) */
    .chat-container {
        background-color: #FFFFFF !important;
        padding: 25px;
        border-radius: 15px;
        border-left: 6px solid #2563EB; /* Xanh dương đậm */
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin: 20px 0;
        color: #000000 !important;
    }
    
    .customer-label {
        font-size: 0.9rem;
        font-weight: 800;
        text-transform: uppercase;
        color: #4B5563 !important; /* Xám đậm */
        margin-bottom: 5px;
    }
    
    .dialogue-text {
        font-size: 1.3rem;
        font-style: italic;
        font-weight: 600;
        color: #1F2937 !important; /* Đen đậm */
        line-height: 1.5;
    }

    /* 5. BUTTONS (Nút bấm tương phản cao) */
    .stButton button {
        background-color: #1E40AF !important; /* Xanh Navy đậm */
        color: #FFFFFF !important; /* Chữ trắng tinh */
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 12px 20px !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton button:hover {
        background-color: #1e3a8a !important; /* Xanh đậm hơn khi hover */
        transform: translateY(-2px);
    }

    /* 6. ANALYSIS BOXES (Kết quả) */
    .analysis-box {
        padding: 20px;
        border-radius: 10px;
        margin-top: 15px;
        font-weight: 600;
    }
    .win-box { 
        background-color: #D1FAE5 !important; /* Xanh lá nhạt */
        border: 2px solid #10B981;
        color: #065F46 !important; /* Chữ xanh lá đậm */
    }
    .lose-box { 
        background-color: #FEE2E2 !important; /* Đỏ nhạt */
        border: 2px solid #EF4444;
        color: #991B1B !important; /* Chữ đỏ đậm */
    }
    
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DATASET (11 SCENARIOS) - FULL ENGLISH
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
                "consequences": {"A": {"next": "lose", "change": -40, "analysis": "❌ Denial destroys trust."}, "B": {"next": "step_2", "change": +10, "analysis": "✅ Immediate action is correct."}}
            },
            "step_2": { 
                "text": "I lost my appetite. I'll just leave.",
                "choices": {"A": "Wait: 'Please eat something.'", "B": "Offer: 'Allow me to pack a dessert for you?'"},
                "consequences": {"A": {"next": "lose", "change": -10, "analysis": "⚠️ Don't force them."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Offering alternatives."}}
            },
            "step_3": { 
                "text": "Okay, fine. Can I get the bill?",
                "choices": {"A": "Discount: '10% Off.'", "B": "Compensate: 'Tonight is free. Plus a voucher.'"},
                "consequences": {"A": {"next": "lose", "change": -20, "analysis": "❌ 10% is insulting here."}, "B": {"next": "win", "change": +40, "analysis": "🏆 Wow moment created."}}
            },
            "win": {"type": "WIN", "title": "SUCCESS", "text": "She left happy.", "score": 100},
            "lose": {"type": "LOSE", "title": "FAILED", "text": "Bad Review.", "score": 40}
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
                "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Don't blame the system."}, "B": {"next": "step_2", "change": +20, "analysis": "✅ Sincere apology first."}}
            },
            "step_2": { 
                "text": "We flew 12 hours for this view!",
                "choices": {"A": "Small Gift: 'Free breakfast?'", "B": "Solution: 'Let me find an upgrade.'"},
                "consequences": {"A": {"next": "lose", "change": -10, "analysis": "⚠️ Not enough."}, "B": {"next": "step_3", "change": +10, "analysis": "✅ Effort matters."}}
            },
            "step_3": { 
                "text": "Well? My wife is waiting.",
                "choices": {"A": "Wait: 'Room available tomorrow.'", "B": "Hero: 'Upgrading you to Presidential Suite.'"},
                "consequences": {"A": {"next": "lose", "change": -20, "analysis": "❌ Disappointing."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Over-delivery wins."}}
            },
            "win": {"type": "WIN", "title": "DREAM TRIP", "text": "They loved the suite.", "score": 100},
            "lose": {"type": "LOSE", "title": "WALK OUT", "text": "They left the hotel.", "score": 0}
        }
    },
    "SC_RETAIL_01": {
        "title": "Retail: Broken Item",
        "desc": "VIP received broken vase.",
        "difficulty": "Hard",
        "customer": {"name": "Ms. Lan", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Lan", "traits": ["VIP", "Urgent"]},
        "steps": {
            "start": { "text": "My $500 vase arrived shattered! How do you do business?", "choices": {"A": "Empathy: 'Oh no! I am so sorry.'", "B": "Check: 'Order ID?'"}, "consequences": {"A": {"next": "step_2", "change": 20, "analysis": "✅ Empathy first."}, "B": {"next": "lose", "change": -20, "analysis": "⚠️ Too robotic."}} },
            "step_2": { "text": "I need it for a gift tonight!", "choices": {"A": "Stock: 'We are out of stock.'", "B": "Check: 'Let me check other stores.'"}, "consequences": {"A": {"next": "step_3", "change": 0, "analysis": "✅ Honest but bad news."}, "B": {"next": "lose", "change": -10, "analysis": "❌ Wasting time if you don't look."}} },
            "step_3": { "text": "Out of stock?! I'm dead! What do I give my boss?", "choices": {"A": "Refund: 'I'll refund you.'", "B": "Rescue: 'I'll express ship from warehouse by 5pm.'"}, "consequences": {"A": {"next": "lose", "change": -10, "analysis": "😐 Problem not solved."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Solving the need."}} },
            "win": {"type": "WIN", "title": "SAVED", "text": "Arrived in time.", "score": 100},
            "lose": {"type": "LOSE", "title": "LOST VIP", "text": "She left disappointed.", "score": 40}
        }
    },
    "SC_ECOMM_01": {
        "title": "E-comm: Lost Package",
        "desc": "App says delivered, but nothing there.",
        "difficulty": "Medium",
        "customer": {"name": "Tom", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Tom", "traits": ["Anxious"]},
        "steps": {
            "start": { "text": "App says delivered. I see nothing! Scam?", "choices": {"A": "Deflect: 'Check neighbors.'", "B": "Help: 'Checking now.'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "❌ Lazy."}, "B": {"next": "step_2", "change": +20, "analysis": "✅ Helpful."}} },
            "step_2": { "text": "I need it tomorrow!", "choices": {"A": "Wait: 'Wait 24h.'", "B": "Urgent: 'Calling driver.'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "⚠️ Too slow."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Urgent action."}} },
            "step_3": { "text": "Driver hid it in a bush?", "choices": {"A": "Hope: 'Check there.'", "B": "Guarantee: 'Check. If missing, I send new pair.'"}, "consequences": {"A": {"next": "lose", "change": 0, "analysis": "😐 Passive."}, "B": {"next": "win", "change": +40, "analysis": "🏆 Risk reversal."}} },
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
            "start": { "text": "Net down! In a meeting! I restarted already!", "choices": {"A": "Script: 'Restart again.'", "B": "Listen: 'I see packet loss.'"}, "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Listening failure."}, "B": {"next": "step_2", "change": +10, "analysis": "✅ Validated."}} },
            "step_2": { "text": "Fix it now!", "choices": {"A": "Wait: 'Tech in 4h.'", "B": "Remote: 'Resetting... 30s.'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "⚠️ Too slow."}, "B": {"next": "step_3", "change": +10, "analysis": "✅ Speed."}} },
            "step_3": { "text": "Still red!", "choices": {"A": "Sorry: 'Wait.'", "B": "Data: 'Free 50GB 4G Data.'"}, "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Stranded."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Saved meeting."}} },
            "win": {"type": "WIN", "title": "SAVED", "text": "Meeting worked.", "score": 100},
            "lose": {"type": "LOSE", "title": "CHURN", "text": "Switched provider.", "score": 0}
        }
    },
     "SC_AIRLINE_01": {
        "title": "Airline: Cancelled",
        "desc": "Missing a wedding.",
        "difficulty": "Very Hard",
        "customer": {"name": "David", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=David", "traits": ["Panic"]},
        "steps": {
            "start": { "text": "Cancelled?! I'm the best man! Wedding is in 6 hours!", "choices": {"A": "Reason: 'Weather.'", "B": "Action: 'Let me find a seat.'"}, "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Don't explain."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Act."}} },
            "step_2": { "text": "Hurry!", "choices": {"A": "Us: 'Next flight tomorrow.'", "B": "Partner: 'Checking partners...'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "⚠️ Too late."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Flexible."}} },
            "step_3": { "text": "No flights?", "choices": {"A": "Sorry: 'Apologies.'", "B": "Creative: 'Fly nearby + Taxi (On us).'"}, "consequences": {"A": {"next": "lose", "change": -10, "analysis": "❌ Giving up."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Heroic solve."}} },
            "win": {"type": "WIN", "title": "ARRIVED", "text": "Made it just in time.", "score": 100},
            "lose": {"type": "LOSE", "title": "MISSED", "text": "Missed wedding.", "score": 30}
        }
    },
    "SC_BANK_01": {
        "title": "Bank: Card Swallowed",
        "desc": "Elderly lady needs medicine money.",
        "difficulty": "Hard",
        "customer": {"name": "Evelyn", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Evelyn", "traits": ["Elderly"]},
        "steps": {
            "start": { "text": "Machine took my card! I need medicine money!", "choices": {"A": "Wait: 'Come Monday.'", "B": "Help: 'Card is safe. Let's withdraw.'"}, "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Dangerous."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Safety first."}} },
            "step_2": { "text": "Forgot ID.", "choices": {"A": "Rule: 'Can't help.'", "B": "Verify: 'Security questions?'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "⚠️ Rigid."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Adaptable."}} },
            "step_3": { "text": "Verified. How to get cash?", "choices": {"A": "Guide: 'Use the App.'", "B": "Do it: 'I will do it.'"}, "consequences": {"A": {"next": "win", "change": +40, "analysis": "🏆 Empowering."}, "B": {"next": "lose", "change": -10, "analysis": "❌ Security breach."}} },
            "win": {"type": "WIN", "title": "SAFE", "text": "Got medicine.", "score": 100},
            "lose": {"type": "LOSE", "title": "NO CASH", "text": "Went home empty.", "score": 30}
        }
    },
    "SC_REALESTATE_01": {
        "title": "Real Estate: Mold",
        "desc": "Luxury apartment has mold.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. Chen", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Chen", "traits": ["Rich"]},
        "steps": {
            "start": { "text": "$4000 for mold? My son has asthma!", "choices": {"A": "Defend: 'Did you air it out?'", "B": "Alert: 'Evacuate now.'"}, "consequences": {"A": {"next": "lose", "change": -40, "analysis": "❌ Blaming customer."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Safety."}} },
            "step_2": { "text": "Black mold! We can't stay.", "choices": {"A": "Paint: 'Painter coming tomorrow.'", "B": "Move: 'You must move.'"}, "consequences": {"A": {"next": "lose", "change": -30, "analysis": "⚠️ Not safe yet."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Correct."}} },
            "step_3": { "text": "Where to?", "choices": {"A": "Motel: 'Cheap.'", "B": "Luxury: '5-Star Hotel.'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "❌ Insulting."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Matching standard."}} },
            "win": {"type": "WIN", "title": "HAPPY", "text": "Family safe.", "score": 100},
            "lose": {"type": "LOSE", "title": "SUED", "text": "Health lawsuit.", "score": 0}
        }
    },
    "SC_SAAS_01": {
        "title": "SaaS: Data Deleted",
        "desc": "Admin deleted data by mistake.",
        "difficulty": "Hard",
        "customer": {"name": "Sarah", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah", "traits": ["Angry"]},
        "steps": {
            "start": { "text": "DATA GONE! Presentation in 2 hours!", "choices": {"A": "Ask: 'Cleared cache?'", "B": "Alert: 'Escalating SEV1.'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "❌ Silly question."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Serious."}} },
            "step_2": { "text": "Restore takes 4 hours?", "choices": {"A": "Process: 'Sorry.'", "B": "Work: 'Manual extract?'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "⚠️ Helpful."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Manual save."}} },
            "step_3": { "text": "My boss will kill me.", "choices": {"A": "Comfort: 'It's ok.'", "B": "Cover: 'I'll email explaining it's our bug.'"}, "consequences": {"A": {"next": "lose", "change": -10, "analysis": "❌ Weak."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Taking blame."}} },
            "win": {"type": "WIN", "title": "RENEWED", "text": "She kept her job.", "score": 100},
            "lose": {"type": "LOSE", "title": "LOST", "text": "Contract cancelled.", "score": 30}
        }
    },
    "SC_SPA_01": {
        "title": "Spa: Allergic",
        "desc": "Face burning after facial.",
        "difficulty": "Hard",
        "customer": {"name": "Chloe", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Chloe", "traits": ["Pain"]},
        "steps": {
            "start": { "text": "Face burning!", "choices": {"A": "Waiver: 'You signed.'", "B": "Aid: 'Ice pack!'"}, "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Cruel."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Care."}} },
            "step_2": { "text": "Still red. Casting tomorrow!", "choices": {"A": "Wait: 'It will pass.'", "B": "Doctor: 'Dermatologist now.'"}, "consequences": {"A": {"next": "lose", "change": -10, "analysis": "⚠️ Risky."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Proactive."}} },
            "step_3": { "text": "Who pays?", "choices": {"A": "Split: '50/50.'", "B": "Full: 'We pay 100%.'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "❌ Cheap."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Responsibility."}} },
            "win": {"type": "WIN", "title": "CALM", "text": "Face healed.", "score": 100},
            "lose": {"type": "LOSE", "title": "SUED", "text": "Legal action.", "score": 0}
        }
    },
    "SC_LOGISTICS_01": {
        "title": "Logistics: Event Fail",
        "desc": "Gear broken before event.",
        "difficulty": "Very Hard",
        "customer": {"name": "Robert", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Robert", "traits": ["Furious"]},
        "steps": {
            "start": { "text": "Gear broken! Event tomorrow!", "choices": {"A": "Form: 'File claim.'", "B": "Fix: 'Handling it.'"}, "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Bureaucratic."}, "B": {"next": "step_2", "change": +40, "analysis": "✅ Leader."}} },
            "step_2": { "text": "How?", "choices": {"A": "Rent: 'You rent locally?'", "B": "Truck: 'Truck diverted. 4 hours.'"}, "consequences": {"A": {"next": "lose", "change": -10, "analysis": "⚠️ Don't ask them."}, "B": {"next": "step_3", "change": +30, "analysis": "✅ Solution."}} },
            "step_3": { "text": "What if it breaks?", "choices": {"A": "Hope: 'It won't.'", "B": "Backup: 'Sent 2 trucks.'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "⚠️ Weak."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Guarantee."}} },
            "win": {"type": "WIN", "title": "SAVED", "text": "Event succeeded.", "score": 100},
            "lose": {"type": "LOSE", "title": "FIRED", "text": "Contract lost.", "score": 0}
        }
    }
}

DB_FILE = "scenarios.json"
HISTORY_FILE = "score_history.csv"

# ==============================================================================
# 3. UTILS
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
            st.dataframe(df.sort_values(by="Score", ascending=False).head(5), use_container_width=True, hide_index=True)
        else: st.info("No data yet.")
    else: st.info("No history found.")

# ==============================================================================
# 4. APP LOGIC
# ==============================================================================
if 'current_scenario' not in st.session_state: st.session_state.current_scenario = None

ALL_SCENARIOS = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=70)
    st.markdown("### Service Hero Academy")
    menu = st.radio("Navigation", ["Dashboard", "Create"])
    st.divider()
    if st.button("🔄 Restore Defaults"):
        load_data(True)
        st.success("Restored!")
        time.sleep(1)
        st.rerun()

# --- DASHBOARD ---
if menu == "Dashboard":
    if st.session_state.current_scenario is None:
        st.title("🎓 Service Hero Academy")
        st.markdown("<p style='font-size:1.1rem; color:#4B5563;'>Select a mission to begin your training.</p>", unsafe_allow_html=True)
        
        # Player Input
        if 'player_name' not in st.session_state: st.session_state.player_name = ""
        if not st.session_state.player_name:
            st.info("Enter your name to start.")
            st.session_state.player_name = st.text_input("Name:")
            if not st.session_state.player_name: st.stop()
        else:
            c1, c2 = st.columns([3, 1])
            c1.success(f"Agent: **{st.session_state.player_name}**")
            if c2.button("Log out"): 
                st.session_state.player_name = ""
                st.rerun()

        with st.expander("🏆 Top Agents"):
            show_leaderboard()
            
        st.divider()
        st.subheader("Available Scenarios")
        
        # Grid
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
        step_data = scenario['steps'].get(step_id, scenario.get(step_id))
        
        # Get Stable Image
        img_url = get_image(s_key)
        
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
            st.markdown(f"**Patience:** :{color}[{p}%]")
            st.progress(p/100)

        # Game Area
        if "type" in step_data: # End
            st.title(step_data['title'])
            st.image(img_url, use_container_width=True)
            
            result_class = "win-box" if step_data['type'] == 'WIN' else "lose-box"
            st.markdown(f"<div class='analysis-box {result_class}'><h2>{step_data['text']}</h2></div>", unsafe_allow_html=True)
            
            if step_data['type'] == 'WIN': st.balloons()
            
            st.metric("Score", step_data['score'])
            
            if 'saved' not in st.session_state:
                save_score(st.session_state.player_name, scenario['title'], step_data['score'], step_data['type'])
                st.session_state.saved = True
            
            if st.button("Return to Dashboard", use_container_width=True):
                st.session_state.current_scenario = None
                if 'saved' in st.session_state: del st.session_state.saved
                st.rerun()
                
            st.divider()
            st.subheader("Analysis")
            for h in st.session_state.history:
                icon = "✅" if h['change'] > 0 else "❌"
                color = "#D1FAE5" if h['change'] > 0 else "#FEE2E2"
                text_col = "#065F46" if h['change'] > 0 else "#991B1B"
                st.markdown(f"""
                <div style="background:{color}; padding:15px; border-radius:10px; margin-top:10px; color:{text_col};">
                    <b>{icon} You chose:</b> {h['choice']}<br>
                    <i>{h['analysis']}</i>
                </div>
                """, unsafe_allow_html=True)

        else: # Playing
            st.subheader(scenario['title'])
            st.image(img_url, use_container_width=True)
            
            st.markdown(f"""
            <div class="chat-container">
                <div class="customer-label">CUSTOMER SAYS:</div>
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
                        st.session_state.history.append({"step": step_data['text'], "choice": v, "analysis": cons['analysis'], "change": cons['change']})
                        st.rerun()
                idx += 1

elif menu == "Create":
    st.header("Scenario Builder")
    st.info("Demo Mode")
