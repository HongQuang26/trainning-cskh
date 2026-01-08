import streamlit as st
import json
import os
import time
import pandas as pd
from datetime import datetime
import urllib.parse
import google.generativeai as genai
import random

# ==============================================================================
# 0. CẤU HÌNH & KHỞI TẠO
# ==============================================================================
GEMINI_API_KEY = "AIzaSyD5ma9Q__JMZUs6mjBppEHUcUBpsI-wjXA"

st.set_page_config(
    page_title="Service Hero Academy",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Khởi tạo Gemini
AI_READY = False
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    AI_READY = True
except:
    pass

# --- KHO ẢNH DỰ PHÒNG (BACKUP LIBRARY - CHỐNG LỖI 404) ---
# Ảnh Unsplash chất lượng cao, link cố định
BACKUP_IMAGES = {
    "F&B": [
        "https://images.unsplash.com/photo-1559339352-11d035aa65de?q=80&w=1000",
        "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=1000"
    ],
    "HOTEL": [
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1000",
        "https://images.unsplash.com/photo-1582719508461-905c673771fd?q=80&w=1000"
    ],
    "OFFICE": [
        "https://images.unsplash.com/photo-1497215728101-856f4ea42174?q=80&w=1000",
        "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?q=80&w=1000"
    ],
    "RETAIL": [
        "https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=1000",
        "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?q=80&w=1000"
    ],
    "GENERAL": [
        "https://images.unsplash.com/photo-1521791136064-7986c2920216?q=80&w=1000"
    ]
}

def get_smart_image(scenario_title, step_text, category_key="GENERAL"):
    """
    Hệ thống tạo ảnh thông minh 2 lớp:
    Lớp 1: Dùng Gemini tạo Prompt -> Pollinations (Ảnh độc nhất).
    Lớp 2: Nếu lỗi -> Dùng ảnh Backup từ Unsplash (Ảnh an toàn).
    """
    # 1. Cố gắng dùng AI tạo ảnh mới
    if AI_READY:
        try:
            prompt_req = f"Extract 3 visual keywords (english nouns) for stock photo: '{scenario_title} - {step_text}'. Comma separated. No intro."
            res = model.generate_content(prompt_req, request_options={"timeout": 3})
            keywords = res.text.strip().replace("\n", "")
            
            seed = hash(step_text) % 10000
            encoded = urllib.parse.quote(f"{keywords}, highly detailed, cinematic lighting")
            return f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=600&seed={seed}&nologo=true&model=flux"
        except:
            pass # Nếu lỗi thì xuống Lớp 2
    
    # 2. Lớp dự phòng (Backup)
    cat = category_key if category_key in BACKUP_IMAGES else "GENERAL"
    images = BACKUP_IMAGES.get(cat, BACKUP_IMAGES["GENERAL"])
    idx = len(step_text) % len(images)
    return images[idx]

# ==============================================================================
# 1. NEON UI CSS
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
    * { font-family: 'Outfit', sans-serif !important; }
    .stApp { background: radial-gradient(circle at 10% 20%, rgb(20, 20, 35) 0%, rgb(40, 40, 60) 90%); color: #fff; }
    [data-testid="stSidebar"] { background-color: rgba(15, 15, 30, 0.95); border-right: 1px solid rgba(255,255,255,0.1); }
    .scenario-card { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; margin-bottom: 20px; backdrop-filter: blur(10px); }
    .scenario-card:hover { transform: translateY(-5px); border-color: #00d2ff; box-shadow: 0 10px 30px rgba(0, 210, 255, 0.2); }
    .chat-container { background: rgba(0, 0, 0, 0.3); border-left: 5px solid #FDBB2D; padding: 25px; border-radius: 12px; margin: 20px 0; }
    .customer-label { color: #FDBB2D; font-size: 0.9rem; font-weight: bold; letter-spacing: 1px; }
    .dialogue { font-size: 1.4rem; font-style: italic; color: #fff; line-height: 1.5; margin-top: 5px;}
    .stButton button { background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%); color: #fff !important; border: 1px solid rgba(255,255,255,0.2); font-weight: 700; border-radius: 8px; padding: 12px 24px; transition: 0.3s; height: auto; min-height: 60px; white-space: normal;}
    .stButton button:hover { background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%); transform: scale(1.02); color: #000 !important; border: none; }
    h1 { background: linear-gradient(to right, #00c6ff, #0072ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. EXTENDED DATASET (NỘI DUNG MỞ RỘNG VÀ CHI TIẾT)
# ==============================================================================
INITIAL_DATA = {
    # --- F&B ---
    "SC_FNB_01": {
        "title": "F&B: Foreign Object", "desc": "Hair found in soup.", "difficulty": "Hard", "category": "F&B",
        "customer": {"name": "Ms. Jade", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Jade", "traits": ["Picky", "Food Critic"]},
        "steps": {
            "start": { 
                "text": "Manager! Get over here! Look at this! There is a disgusting long hair in my lobster soup! Is this a joke?",
                "choices": {"A": "Defensive: 'Our staff wear hairnets. Are you sure it's not yours?'", "B": "Apology: 'I am terribly sorry Ms. Jade! That is unacceptable. I'll remove this immediately.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -50, "analysis": "❌ Accusing the customer escalates it."}, "B": {"next": "step_2", "change": +20, "analysis": "✅ Immediate removal is correct."}}
            },
            "step_2": { 
                "text": "My appetite is gone. I've been waiting 30 mins and now my friend eats alone while I watch!",
                "choices": {"A": "Standard: 'Would you like to order something else?'", "B": "Empathy: 'I understand. It's awful to eat out of sync. May I offer a complimentary wine while you decide?'"},
                "consequences": {"A": {"next": "step_3_angry", "change": -10, "analysis": "⚠️ She said she lost appetite."}, "B": {"next": "step_3_calm", "change": +20, "analysis": "✅ Addressing the pain point."}}
            },
            "step_3_angry": {
                "text": "No! Just bring the bill. I'm writing a review right now.",
                "choices": {"A": "Give Up: 'Here is the bill. Sorry.'", "B": "Recover: 'Please, don't leave like this. The meal is on us, plus a voucher for next time.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Guaranteed bad review."}, "B": {"next": "game_over_save", "change": +30, "analysis": "🏆 Strong recovery attempt."}}
            },
            "step_3_calm": { 
                "text": "(Sips wine) Fine. But tonight is ruined. Just bring the check.",
                "choices": {"A": "Discount: 'I removed the soup and gave 10% off.'", "B": "Wow: 'Tonight is on the house. I also packed a dessert for you. We hope to see you again.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ 10% is insulting."}, "B": {"next": "game_over_good", "change": +40, "analysis": "🏆 Turning negative to Wow."}}
            },
            "game_over_good": {"type": "WIN", "title": "SAVED", "text": "She was impressed and left a tip.", "score": 100},
            "game_over_save": {"type": "WIN", "title": "AVERTED", "text": "She accepted the apology.", "score": 70},
            "game_over_fail": {"type": "LOSE", "title": "LOST", "text": "She left a 1-star review.", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "DISASTER", "text": "Viral bad video.", "score": 0}
        }
    },
    # --- HOTEL ---
    "SC_HOTEL_01": {
        "title": "Hotel: Honeymoon Fail", "desc": "Overbooked Ocean View.", "difficulty": "Very Hard", "category": "HOTEL",
        "customer": {"name": "Mike", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Mike", "traits": ["Tired", "High Expectation"]},
        "steps": {
            "start": { 
                "text": "System Error? I booked Ocean View 6 months ago! This is our HONEYMOON!",
                "choices": {"A": "Policy: 'Sorry, system overbooked. Garden view is nice too.'", "B": "Own it: 'This is entirely our mistake. I can't imagine how disappointing this is.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Don't sell the downgrade."}, "B": {"next": "step_2", "change": +20, "analysis": "✅ Validation."}}
            },
            "step_2": { 
                "text": "My wife is crying. We flew 12 hours! Fix this or refund us!",
                "choices": {"A": "Compensate: 'Free breakfast and massage?'", "B": "Solve: 'Give me 5 mins. I'm calling our sister property or finding a suite.'"},
                "consequences": {"A": {"next": "step_3_fail", "change": -10, "analysis": "⚠️ Breakfast doesn't fix the room."}, "B": {"next": "step_3_hero", "change": +30, "analysis": "✅ Action oriented."}}
            },
            "step_3_fail": {
                "text": "I don't want a massage! I want my room! Call the manager!",
                "choices": {"A": "Escalate: 'I'll get him, but he will say the same.'", "B": "Last Try: 'Wait! Presidential Suite is free for 2 nights. I can move you?'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Dismissive."}, "B": {"next": "game_over_good", "change": +40, "analysis": "🏆 Upgrade saves the day."}}
            },
            "step_3_hero": { 
                "text": "Well? Did you find anything?",
                "choices": {"A": "Bad News: 'Nearby hotels full. Here is $200 credit.'", "B": "Hero: 'Upgraded to Presidential Suite tonight, then Ocean Villa tomorrow.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Money doesn't buy memories."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Over-delivery."}}
            },
            "game_over_good": {"type": "WIN", "title": "DREAM SAVED", "text": "Thrilled with the upgrade.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "WALK OUT", "text": "They left to competitor.", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "SHAMING", "text": "Angry social media post.", "score": 0}
        }
    },
    # --- RETAIL ---
    "SC_RETAIL_01": {
        "title": "Retail: Broken Gift", "desc": "Broken vase before party.", "difficulty": "Hard", "category": "RETAIL",
        "customer": {"name": "Lan", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Lan", "traits": ["VIP", "Emotional"]},
        "steps": {
            "start": { "text": "My $500 vase arrived shattered! The party is TONIGHT!", "choices": {"A": "Process: 'Send photo and Order ID for claim.'", "B": "Empathy: 'Oh my god! That is heartbreaking! I am so sorry.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -20, "analysis": "⚠️ Too robotic."}, "B": {"next": "step_2", "change": +20, "analysis": "✅ Emotional connection."}} },
            "step_2": { "text": "I need a gift by 6 PM! Do you have stock?", "choices": {"A": "System: 'System says out of stock.'", "B": "Check: 'Let me check all city branches right now.'"}, "consequences": {"A": {"next": "step_3_fail", "change": -20, "analysis": "❌ Dead end."}, "B": {"next": "step_3_solution", "change": +20, "analysis": "✅ Effort."}} },
            "step_3_fail": { "text": "You ruined everything!", "choices": {"A": "Refund: 'Full refund processed.'", "B": "Alt: 'We have a blue vase?'"}, "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "😐 Problem not solved."}, "B": {"next": "game_over_save", "change": +20, "analysis": "✅ Better than nothing."}} },
            "step_3_solution": { "text": "Found one?", "choices": {"A": "Pickup: 'Yes, at downtown store. Go pick it up.'", "B": "Concierge: 'Yes! I booked Grab Express. Arriving by 5 PM.'"}, "consequences": {"A": {"next": "game_over_save", "change": 0, "analysis": "😐 Making customer work."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 VIP Service."}} },
            "game_over_good": {"type": "WIN", "title": "PARTY SAVED", "text": "Arrived in time.", "score": 100},
            "game_over_save": {"type": "WIN", "title": "OKAY", "text": "Got replacement.", "score": 70},
            "game_over_fail": {"type": "LOSE", "title": "LOST VIP", "text": "She left.", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "RANT", "text": "Furious.", "score": 0}
        }
    },
    # --- TECH ---
    "SC_TECH_01": {
        "title": "IT: Net Down", "desc": "Meeting interrupted.", "difficulty": "Medium", "category": "OFFICE",
        "customer": {"name": "Ken", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Ken", "traits": ["Urgent", "CEO"]},
        "steps": {
            "start": { "text": "Net down! 50 investors on call! Restarted twice already!", "choices": {"A": "Script: 'Restart again.'", "B": "Listen: 'I see packet loss. Checking line.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Ignored customer."}, "B": {"next": "step_2", "change": +10, "analysis": "✅ Validated."}} },
            "step_2": { "text": "Hurry! Losing money!", "choices": {"A": "Wait: 'Tech in 2 hours.'", "B": "Action: 'Resetting port (5m). Activating 50GB 4G Data NOW.'"}, "consequences": {"A": {"next": "step_3_fail", "change": -20, "analysis": "⚠️ Too slow."}, "B": {"next": "step_3_win", "change": +40, "analysis": "🏆 Instant Backup."}} },
            "step_3_fail": { "text": "2 hours? Deal is dead!", "choices": {"A": "Sorry: 'Fastest slot.'", "B": "Push: 'Trying for 30 mins.'"}, "consequences": {"A": {"next": "game_over_churn", "change": -20, "analysis": "❌ Helpless."}, "B": {"next": "game_over_churn", "change": -10, "analysis": "⚠️ Still late."}} },
            "step_3_win": { "text": "Okay 4G works. Why fiber failed?", "choices": {"A": "Tech: 'Signal degradation.'", "B": "Focus: 'We will investigate later. Good luck with the pitch!'"}, "consequences": {"A": {"next": "game_over_good", "change": +10, "analysis": "✅ Honest."}, "B": {"next": "game_over_good", "change": +30, "analysis": "🏆 Focus on goal."}} },
            "game_over_good": {"type": "WIN", "title": "DEAL SAVED", "text": "Meeting smooth.", "score": 100},
            "game_over_churn": {"type": "LOSE", "title": "CANCELLED", "text": "Lost contract.", "score": 20},
            "game_over_bad": {"type": "LOSE", "title": "FURIOUS", "text": "Hung up.", "score": 0}
        }
    },
    # --- AIRLINE ---
    "SC_AIRLINE_01": {
        "title": "Airline: Groom Late", "desc": "Flight cancelled before wedding.", "difficulty": "Extreme", "category": "TRAVEL",
        "customer": {"name": "David", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=David", "traits": ["Panic", "Groom"]},
        "steps": {
            "start": { "text": "Cancelled?! I'm the GROOM! Wedding in 6 hours!", "choices": {"A": "Reason: 'Technical fault.'", "B": "Act: 'Emergency! Finding alternative.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Don't explain."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Urgency."}} },
            "step_2": { "text": "Get me there!", "choices": {"A": "Us: 'Next flight tomorrow.'", "B": "Partner: 'Checking partners... Flight in 45 mins.'"}, "consequences": {"A": {"next": "step_3_fail", "change": -20, "analysis": "⚠️ Policy bot."}, "B": {"next": "step_3_win", "change": +30, "analysis": "✅ Above & Beyond."}} },
            "step_3_fail": { "text": "Tomorrow?! I'll miss it!", "choices": {"A": "Sorry: 'Apologies.'", "B": "Creative: 'Fly nearby + Taxi?'"}, "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "❌ Gave up."}, "B": {"next": "game_over_save", "change": +30, "analysis": "🏆 Creative."}} },
            "step_3_win": { "text": "45 mins? Tight!", "choices": {"A": "Honesty: 'Run fast.'", "B": "Support: 'Buggy waiting to take you to gate.'"}, "consequences": {"A": {"next": "game_over_save", "change": +10, "analysis": "✅ Good."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Full Support."}} },
            "game_over_good": {"type": "WIN", "title": "ARRIVED", "text": "Made it.", "score": 100},
            "game_over_save": {"type": "WIN", "title": "CLOSE", "text": "Barely made it.", "score": 70},
            "game_over_fail": {"type": "LOSE", "title": "TRAGEDY", "text": "Missed wedding.", "score": 0},
            "game_over_bad": {"type": "LOSE", "title": "SECURITY", "text": "Detained.", "score": 0}
        }
    },
    # --- BANK ---
    "SC_BANK_01": {
        "title": "Bank: Card Eaten", "desc": "Elderly lady needs medicine money.", "difficulty": "Hard", "category": "OFFICE",
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
    # --- REAL ESTATE ---
    "SC_REALESTATE_01": {
        "title": "Real Estate: Mold", "desc": "Mold in luxury apt.", "difficulty": "Very Hard", "category": "HOTEL",
        "customer": {"name": "Chen", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Chen", "traits": ["Rich"]},
        "steps": {
            "start": { "text": "$4000 for mold? My son has asthma!", "choices": {"A": "Defend: 'Did you air it?'", "B": "Alert: 'Evacuate now.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -40, "analysis": "❌ Blaming."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Safety."}} },
            "step_2": { "text": "Can't stay.", "choices": {"A": "Paint: 'Tomorrow.'", "B": "Move: 'Move now.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -30, "analysis": "⚠️ Unsafe."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Correct."}} },
            "step_3": { "text": "Where?", "choices": {"A": "Motel: 'Cheap.'", "B": "Hotel: '5-Star.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Insult."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Classy."}} },
            "game_over_good": {"type": "WIN", "title": "HAPPY", "text": "Safe.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "LEFT", "text": "Tenant left.", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "SUED", "text": "Lawsuit.", "score": 0}
        }
    },
    # --- SAAS ---
    "SC_SAAS_01": {
        "title": "SaaS: Data Deleted", "desc": "Admin deleted data.", "difficulty": "Hard", "category": "OFFICE",
        "customer": {"name": "Sarah", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah", "traits": ["Angry"]},
        "steps": {
            "start": { "text": "DATA GONE!", "choices": {"A": "Ask: 'Cleared cache?'", "B": "Alert: 'Escalating.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -20, "analysis": "❌ Silly."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Serious."}} },
            "step_2": { "text": "Restore 4 hours?", "choices": {"A": "Sorry: 'Process.'", "B": "Work: 'Manual extract?'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Passive."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Action."}} },
            "step_3": { "text": "Boss will kill me.", "choices": {"A": "Comfort: 'It's ok.'", "B": "Cover: 'I'll email boss.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "❌ Weak."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Ownership."}} },
            "game_over_good": {"type": "WIN", "title": "RENEWED", "text": "Job saved.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "LOST", "text": "Cancelled.", "score": 0}
        }
    },
    # --- SPA ---
    "SC_SPA_01": {
        "title": "Spa: Allergic", "desc": "Face burning.", "difficulty": "Hard", "category": "HOTEL",
        "customer": {"name": "Chloe", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Chloe", "traits": ["Pain"]},
        "steps": {
            "start": { "text": "Face burning!", "choices": {"A": "Waiver: 'You signed.'", "B": "Aid: 'Ice pack!'"}, "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Cruel."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ Care."}} },
            "step_2": { "text": "Still red!", "choices": {"A": "Wait: 'Will pass.'", "B": "Doctor: 'Dermatologist.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Risky."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Safe."}} },
            "step_3": { "text": "Who pays?", "choices": {"A": "Split: '50/50.'", "B": "Full: 'We pay 100%.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Cheap."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Responsible."}} },
            "game_over_good": {"type": "WIN", "title": "HEALED", "text": "All good.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "REVIEW", "text": "Bad review.", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "SUED", "text": "Lawsuit.", "score": 0}
        }
    },
    # --- LOGISTICS ---
    "SC_LOGISTICS_01": {
        "title": "Logistics: Event Fail", "desc": "Gear broken.", "difficulty": "Very Hard", "category": "RETAIL",
        "customer": {"name": "Robert", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Robert", "traits": ["Furious"]},
        "steps": {
            "start": { "text": "Gear broken! Event tomorrow!", "choices": {"A": "Form: 'File claim.'", "B": "Fix: 'Handling it.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Bureaucratic."}, "B": {"next": "step_2", "change": +40, "analysis": "✅ Leader."}} },
            "step_2": { "text": "How?", "choices": {"A": "Rent: 'Rent locally?'", "B": "Truck: 'Truck diverted.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Lazy."}, "B": {"next": "step_3", "change": +30, "analysis": "✅ Solution."}} },
            "step_3": { "text": "Will it arrive?", "choices": {"A": "Hope: 'Maybe.'", "B": "Backup: 'Sent 2 trucks.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Weak."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Guarantee."}} },
            "game_over_good": {"type": "WIN", "title": "SAVED", "text": "Success.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "FIRED", "text": "Contract lost.", "score": 0}
        }
    },
    # --- ECOMM ---
    "SC_ECOMM_01": {
        "title": "E-comm: Lost Package", "desc": "Package missing.", "difficulty": "Medium", "category": "RETAIL",
        "customer": {"name": "Tom", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Tom", "traits": ["Anxious"]},
        "steps": {
            "start": { "text": "App says delivered. I see nothing! Scam?", "choices": {"A": "Deflect: 'Check neighbors.'", "B": "Help: 'Checking now.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -20, "analysis": "❌ Lazy."}, "B": {"next": "step_2", "change": +20, "analysis": "✅ Helpful."}} },
            "step_2": { "text": "I need it tomorrow!", "choices": {"A": "Wait: 'Wait 24h.'", "B": "Urgent: 'Calling driver.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Slow."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Fast."}} },
            "step_3": { "text": "Driver hid it in a bush?", "choices": {"A": "Hope: 'Check there.'", "B": "Guarantee: 'Check. If missing, I send new pair.'"}, "consequences": {"A": {"next": "game_over_good", "change": 0, "analysis": "😐 Passive."}, "B": {"next": "game_over_good", "change": +40, "analysis": "🏆 Risk reversal."}} },
            "game_over_good": {"type": "WIN", "title": "FOUND", "text": "He got it.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "ANGRY", "text": "Refunded.", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "REPORTED", "text": "Scam report.", "score": 0}
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
            st.dataframe(df.sort_values(by="Score", ascending=False).head(10), use_container_width=True, hide_index=True)
        else: st.info("No data yet.")
    else: st.info("No history found.")

# ==============================================================================
# 4. APP LOGIC
# ==============================================================================
if 'current_scenario' not in st.session_state: st.session_state.current_scenario = None
if 'img_cache' not in st.session_state: st.session_state.img_cache = {}

ALL_SCENARIOS = load_data()

with st.sidebar:
    st.title("💎 Service Hero")
    st.markdown("### AI Academy")
    menu = st.radio("Navigation", ["Dashboard", "Create"])
    st.divider()
    if st.button("🔄 Restore Defaults"):
        load_data(True)
        st.success("Restored!")
        time.sleep(1)
        st.rerun()

if menu == "Dashboard":
    if st.session_state.current_scenario is None:
        st.title("🎓 Service Hero Academy")
        st.markdown("<p style='font-size:1.1rem; color:#4B5563;'>Master customer service skills.</p>", unsafe_allow_html=True)
        
        if 'player_name' not in st.session_state: st.session_state.player_name = ""
        if not st.session_state.player_name:
            st.info("Please enter your name.")
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
        
        cols = st.columns(2)
        idx = 0
        for key, val in ALL_SCENARIOS.items():
            with cols[idx % 2]:
                badge_class = "badge-hard" if "Hard" in val['difficulty'] else "badge-med"
                st.markdown(f"""
                <div class="scenario-card">
                    <h3>{val['title']}</h3>
                    <p style="color:#64748b;">{val['desc']}</p>
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
        s_key = st.session_state.current_scenario
        if s_key not in ALL_SCENARIOS: 
            st.session_state.current_scenario = None
            st.rerun()
            
        scenario = ALL_SCENARIOS[s_key]
        step_id = st.session_state.current_step
        step_data = scenario['steps'].get(step_id, scenario.get(step_id))
        
        cache_key = f"{s_key}_{step_id}"
        if cache_key not in st.session_state.img_cache:
            with st.spinner("🤖 AI is visualizing..."):
                cat = scenario.get('category', 'GENERAL')
                ai_url = get_smart_image(scenario['title'], step_data.get('text', ''), cat)
                st.session_state.img_cache[cache_key] = ai_url
        
        current_img = st.session_state.img_cache[cache_key]
        
        with st.sidebar:
            st.divider()
            if st.button("❌ Exit Mission", use_container_width=True):
                st.session_state.current_scenario = None
                st.rerun()
            cust = scenario['customer']
            st.image(cust.get('avatar', 'https://placehold.co/100'), width=100)
            st.markdown(f"**{cust['name']}**")
            p = st.session_state.patience
            st.markdown(f"**Patience:** {p}%")
            st.progress(p/100)

        if "type" in step_data: 
            st.title(step_data['title'])
            st.image(current_img, use_container_width=True)
            res_class = "win-box" if step_data['type'] == 'WIN' else "lose-box"
            st.markdown(f"<div class='analysis-box {res_class}'><h2>{step_data['text']}</h2></div>", unsafe_allow_html=True)
            if step_data['type'] == 'WIN': st.balloons()
            st.metric("Score", step_data['score'])
            if 'saved' not in st.session_state:
                save_score(st.session_state.player_name, scenario['title'], step_data['score'], step_data['type'])
                st.session_state.saved = True
            if st.button("Back", use_container_width=True):
                st.session_state.current_scenario = None
                if 'saved' in st.session_state: del st.session_state.saved
                st.rerun()
            st.divider()
            st.subheader("Analysis")
            for h in st.session_state.history:
                icon = "✅" if h['change'] > 0 else "❌"
                st.info(f"{icon} Choice: {h['choice']} -> {h['analysis']}")

        else:
            st.subheader(scenario['title'])
            st.image(current_img, use_container_width=True)
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
    st.header("Builder")
    st.info("Demo Mode")
