import streamlit as st
import json
import os
import time
import pandas as pd
from datetime import datetime
import google.generativeai as genai
import random

# ==============================================================================
# 0. CONFIGURATION & ASSETS
# ==============================================================================
GEMINI_API_KEY = "AIzaSyD5ma9Q__JMZUs6mjBppEHUcUBpsI-wjXA"

st.set_page_config(
    page_title="Service Hero Academy",
    page_icon="💎",
    layout="wide"
)

# --- THƯ VIỆN ẢNH ỔN ĐỊNH (NO RATE LIMIT) ---
# Sử dụng ảnh Unsplash chất lượng cao để đảm bảo không bao giờ bị lỗi
IMAGE_LIBRARY = {
    "F&B": [
        "https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=1000&q=80", # Restaurant
        "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1000&q=80", # Dining
        "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=1000&q=80"  # Food
    ],
    "HOTEL": [
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1000&q=80", # Resort
        "https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=1000&q=80", # Lobby
        "https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=1000&q=80"  # Bedroom
    ],
    "TECH": [
        "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1000&q=80", # Work
        "https://images.unsplash.com/photo-1531297461136-82lw9z3w9z?auto=format&fit=crop&w=1000&q=80", # Server
        "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=1000&q=80"  # Laptop
    ],
    "RETAIL": [
        "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1000&q=80", # Store
        "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?auto=format&fit=crop&w=1000&q=80", # Clothes
        "https://images.unsplash.com/photo-1472851294608-41531b6574d4?auto=format&fit=crop&w=1000&q=80"  # Shop
    ],
    "TRAVEL": [
        "https://images.unsplash.com/photo-1436491865332-7a61a14527c5?auto=format&fit=crop&w=1000&q=80", # Plane
        "https://images.unsplash.com/photo-1569154941061-e231b4725ef1?auto=format&fit=crop&w=1000&q=80", # Airport
        "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=1000&q=80"  # Travel
    ],
    "BANK": [
        "https://images.unsplash.com/photo-1601597111158-2fceff292cdc?auto=format&fit=crop&w=1000&q=80", # ATM
        "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?auto=format&fit=crop&w=1000&q=80", # Counter
        "https://images.unsplash.com/photo-1501167786227-4cba60f6d58f?auto=format&fit=crop&w=1000&q=80"  # Money
    ],
    "GENERAL": [
        "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1000&q=80", # Meeting
        "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?auto=format&fit=crop&w=1000&q=80", # Handshake
        "https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=1000&q=80"  # Office
    ]
}

def get_scene_image(category, step_index):
    """
    Selects a stable image based on category and step to ensure visual variety without errors.
    """
    cat_key = "GENERAL"
    if "F&B" in category: cat_key = "F&B"
    elif "Hotel" in category or "Spa" in category: cat_key = "HOTEL"
    elif "IT" in category or "SaaS" in category: cat_key = "TECH"
    elif "Retail" in category or "E-comm" in category: cat_key = "RETAIL"
    elif "Airline" in category or "Logistics" in category: cat_key = "TRAVEL"
    elif "Bank" in category or "Real Estate" in category: cat_key = "BANK"
    
    # Cycle through images based on step to simulate story progression
    images = IMAGE_LIBRARY.get(cat_key, IMAGE_LIBRARY["GENERAL"])
    return images[step_index % len(images)]

# ==============================================================================
# 1. VIBRANT & HIGH CONTRAST CSS
# ==============================================================================
st.markdown("""
<style>
    /* 1. GLOBAL THEME */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap');
    
    .stApp {
        background: linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%);
        font-family: 'Outfit', sans-serif;
    }
    
    h1 {
        background: linear-gradient(to right, #1A2980, #26D0CE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* 2. CARD STYLING (Glassmorphism + Pop) */
    .scenario-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }
    .scenario-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.12);
        border-bottom: 5px solid #26D0CE;
    }
    
    .card-title { font-size: 1.4rem; font-weight: 800; color: #1e293b; margin-bottom: 5px; }
    .card-desc { color: #64748b; font-size: 0.95rem; margin-bottom: 15px; }
    
    .badge {
        display: inline-block; padding: 4px 12px; border-radius: 20px;
        font-size: 0.75rem; font-weight: 800; text-transform: uppercase;
        letter-spacing: 1px;
    }
    .badge-hard { background: #fee2e2; color: #991b1b; }
    .badge-med { background: #fef3c7; color: #92400e; }
    
    /* 3. CHAT BUBBLES - High Contrast */
    .chat-box {
        background: #ffffff;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        border-left: 8px solid #4F46E5;
        margin: 20px 0;
        color: #111827;
    }
    .customer-name { 
        font-size: 1rem; font-weight: 800; color: #4F46E5; 
        text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;
    }
    .dialogue { 
        font-size: 1.4rem; font-weight: 600; color: #1f2937; 
        font-style: italic; line-height: 1.5;
    }
    
    /* 4. BUTTONS - EYE CATCHING */
    .stButton button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        padding: 16px 24px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
    }
    .stButton button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.5);
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
    }

    /* 5. ANALYSIS BOXES */
    .analysis-container {
        padding: 20px; border-radius: 12px; margin-top: 15px;
        color: white; font-weight: 600;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .win-box { background: linear-gradient(135deg, #059669, #10b981); }
    .lose-box { background: linear-gradient(135deg, #dc2626, #ef4444); }
    
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DATASET (11 SCENARIOS)
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
            "start": { "text": "Card gone! Need medicine!", "choices": {"A": "Wait: 'Come Monday.'", "B": "Help: 'Card is safe.'"}, "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Health risk."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Care."}} },
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
            st.dataframe(df.sort_values(by="Score", ascending=False).head(5), use_container_width=True, hide_index=True)
        else: st.info("No data yet.")
    else: st.info("No history found.")

# ==============================================================================
# 4. MAIN APPLICATION
# ==============================================================================
if 'current_scenario' not in st.session_state: st.session_state.current_scenario = None

ALL_SCENARIOS = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.title("💎 Service Hero")
    st.markdown("### AI Academy")
    menu = st.radio("Navigation", ["Dashboard", "Create"])
    st.divider()
    if st.button("🔄 Reset"):
        load_data(True)
        st.success("Reset!")
        time.sleep(1)
        st.rerun()

# --- DASHBOARD ---
if menu == "Dashboard":
    if st.session_state.current_scenario is None:
        st.markdown("<h1>🎓 Service Hero Academy</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:1.2rem;'>Master customer service with <b>AI-Powered Roleplay</b>.</p>", unsafe_allow_html=True)

        if 'player_name' not in st.session_state: st.session_state.player_name = ""
        if not st.session_state.player_name:
            st.info("👋 Enter your name to begin training.")
            st.session_state.player_name = st.text_input("Agent Name:")
            if not st.session_state.player_name: st.stop()
        else:
            c1, c2 = st.columns([3, 1])
            c1.success(f"Ready: **{st.session_state.player_name}**")
            if c2.button("Log out"): 
                st.session_state.player_name = ""
                st.rerun()

        with st.expander("🏆 Top Agents"):
            show_leaderboard()
        
        st.write("---")
        st.subheader("Select Mission")
        
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

    else:
        # --- GAMEPLAY ---
        s_key = st.session_state.current_scenario
        if s_key not in ALL_SCENARIOS: 
            st.session_state.current_scenario = None
            st.rerun()
            
        scenario = ALL_SCENARIOS[s_key]
        step_id = st.session_state.current_step
        step_data = scenario['steps'][step_id]
        
        # Determine Image Category for Stable Loading
        img_url = get_scene_image(scenario['title'], 0 if step_id == 'start' else 1)

        # Sidebar Stats
        with st.sidebar:
            st.divider()
            if st.button("❌ Abort", use_container_width=True):
                st.session_state.current_scenario = None
                st.rerun()
            
            cust = scenario['customer']
            st.image(cust['avatar'], width=80)
            st.markdown(f"**{cust['name']}**")
            
            p = st.session_state.patience
            st.write(f"Patience: {p}%")
            st.progress(p/100)

        # Game Screen
        if "type" in step_data: # End
            st.title(step_data['title'])
            st.image(img_url, use_container_width=True)
            
            res_class = "win-box" if step_data['type'] == 'WIN' else "lose-box"
            st.markdown(f"<div class='analysis-container {res_class}'><h2>{step_data['text']}</h2></div>", unsafe_allow_html=True)
            
            if step_data['type'] == 'WIN': st.balloons()
            
            st.metric("Score", step_data['score'])
            
            if 'saved' not in st.session_state:
                save_score(st.session_state.player_name, scenario['title'], step_data['score'], step_data['type'])
                st.session_state.saved = True
            
            if st.button("Return to Dashboard", use_container_width=True):
                st.session_state.current_scenario = None
                if 'saved' in st.session_state: del st.session_state.saved
                st.rerun()

        else: # Playing
            st.subheader(scenario['title'])
            st.image(img_url, use_container_width=True)
            
            st.markdown(f"""
            <div class="chat-box">
                <div class="customer-name">🗣️ {cust['name']} says:</div>
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
                        st.session_state.history.append({"step": step_data['text'], "choice": v, "analysis": cons['analysis']})
                        st.rerun()
                idx += 1

elif menu == "Create":
    st.header("Scenario Builder")
    st.info("Demo Mode")
