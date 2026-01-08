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
# 0. CẤU HÌNH & AI ENGINE
# ==============================================================================
# API Key Gemini của bạn (Đã nhúng sẵn)
GEMINI_API_KEY = "AIzaSyD5ma9Q__JMZUs6mjBppEHUcUBpsI-wjXA"

st.set_page_config(
    page_title="Service Hero: Neon Edition",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Khởi tạo Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

# --- HÀM TẠO ẢNH ĐỘNG BẰNG AI (DYNAMIC AI IMAGE GENERATOR) ---
def generate_dynamic_image(scenario_context, step_text):
    """
    1. Dùng Gemini để tóm tắt ngữ cảnh thành 1 prompt vẽ tranh ngắn gọn.
    2. Gửi prompt đó đến API vẽ tranh để tạo ảnh mới cho TỪNG BƯỚC.
    """
    if not AI_AVAILABLE:
        return "https://placehold.co/1024x576/1a1a2e/FFF?text=AI+Unavailable"

    try:
        # Bước 1: Hỏi Gemini lấy keywords (khoảng 5-7 từ tiếng Anh)
        prompt_request = f"""
        Task: Create a very short visual prompt (5-7 words, English nouns/adjectives only) for an AI image generator based on this situation.
        Context: {scenario_context}
        Current Action: {step_text}
        Output format provided specifically: keyword1, keyword2, keyword3...
        """
        response = model.generate_content(prompt_request, request_options={"timeout": 5})
        keywords = response.text.strip().replace("\n", " ")
        
        # Nếu Gemini trả về rỗng hoặc lỗi, dùng ngữ cảnh cơ bản
        if not keywords or len(keywords) < 3:
             keywords = f"{scenario_context} situation"

        # Bước 2: Tạo URL ảnh với seed ngẫu nhiên để mỗi lần là 1 ảnh khác nhau
        seed = random.randint(0, 999999)
        # Thêm các từ khóa phong cách để ảnh đẹp hơn
        full_prompt = f"{keywords}, cinematic lighting, dramatic, 8k resolution, highly detailed"
        encoded_prompt = urllib.parse.quote(full_prompt)
        
        # Sử dụng Pollinations API (mô hình Flux hoặc Turbo) để vẽ
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&seed={seed}&nologo=true&model=flux"
        return image_url
        
    except Exception as e:
        # Fallback nếu lỗi kết nối
        print(f"AI Error: {e}")
        return f"https://placehold.co/1024x576/1a1a2e/FFF?text=Image+Generation+Failed"

# ==============================================================================
# 1. GIAO DIỆN NEON/CYBERPUNK (DARK MODE CSS)
# ==============================================================================
st.markdown("""
<style>
    /* Import Font hiện đại */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&display=swap');
    * { font-family: 'Rajdhani', sans-serif !important; }

    /* 1. NỀN TỐI TOÀN MÀN HÌNH */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e) !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(15, 12, 41, 0.9) !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }

    /* 2. TEXT & HEADERS (Màu trắng sáng) */
    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: #ffffff !important;
        text-shadow: 0 0 2px rgba(0,0,0,0.5);
    }
    h1 {
        background: linear-gradient(to right, #00f260, #0575e6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        text-transform: uppercase;
    }

    /* 3. THẺ KỊCH BẢN (Glassmorphism + Neon Border) */
    .scenario-card {
        background: rgba(255, 255, 255, 0.05) !important; /* Kính mờ */
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .scenario-card:hover {
        border-color: #00d2ff; /* Viền neon xanh khi hover */
        box-shadow: 0 0 20px rgba(0, 210, 255, 0.3);
        transform: translateY(-5px);
    }
    .badge {
        padding: 5px 10px; border-radius: 4px; font-size: 0.8rem; font-weight: bold;
        text-transform: uppercase; letter-spacing: 1px;
    }
    .badge-hard { background: rgba(255, 0, 128, 0.2); color: #ff0080 !important; border: 1px solid #ff0080; }
    .badge-med { background: rgba(255, 165, 0, 0.2); color: #ffa500 !important; border: 1px solid #ffa500; }

    /* 4. KHUNG HỘI THOẠI (Chat Bubble) */
    .chat-container {
        background: rgba(0, 0, 0, 0.3) !important;
        padding: 25px;
        border-radius: 15px;
        border-left: 6px solid #00d2ff; /* Thanh neon xanh */
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        margin: 20px 0;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .customer-label {
        font-size: 1rem; font-weight: 800; text-transform: uppercase;
        color: #00d2ff !important; /* Màu neon xanh */
        margin-bottom: 10px; letter-spacing: 2px;
    }
    .dialogue-text {
        font-size: 1.4rem; font-style: italic; font-weight: 500;
        line-height: 1.5;
    }

    /* 5. NÚT BẤM (Neon Gradient) */
    .stButton button {
        /* Gradient Hồng tím -> Xanh dương */
        background: linear-gradient(45deg, #ff00cc, #333399) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 15px 25px !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 15px rgba(255, 0, 204, 0.3);
        transition: all 0.3s ease;
        text-transform: uppercase;
    }
    .stButton button:hover {
        box-shadow: 0 0 25px rgba(255, 0, 204, 0.6);
        transform: scale(1.02);
    }

    /* 6. HỘP KẾT QUẢ */
    .analysis-box { padding: 20px; border-radius: 10px; margin-top: 15px; font-weight: 600; }
    .win-box { background: rgba(0, 255, 127, 0.15) !important; border: 2px solid #00ff7f; color: #00ff7f !important; }
    .lose-box { background: rgba(255, 0, 95, 0.15) !important; border: 2px solid #ff005f; color: #ff005f !important; }
    
    /* 7. Spinner Loading */
    .stSpinner > div > div {
        border-top-color: #00d2ff !important;
    }

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DỮ LIỆU KỊCH BẢN GỐC (ENGLISH)
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
                "choices": {"A": "Discount: '10% Off.'", "B": "Compensate: 'It is free tonight.'"},
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
            "step_2": { "text": "I need these shoes for tomorrow!", "choices": {"A": "Wait: 'Wait 24h.'", "B": "Urgent: 'Calling driver.'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "⚠️ Too slow."}, "B": {"next": "step_3", "change": +20, "analysis": "✅ Urgent action."}} },
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
            "step_3": { "text": "Where to?", "choices": {"A": "Cheap: 'Motel.'", "B": "Luxury: '5-Star Hotel.'"}, "consequences": {"A": {"next": "lose", "change": -20, "analysis": "❌ Insulting."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Matching standard."}} },
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
# 3. UTILS (XỬ LÝ DỮ LIỆU)
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
# Khởi tạo Session State
if 'current_scenario' not in st.session_state: st.session_state.current_scenario = None
if 'img_cache' not in st.session_state: st.session_state.img_cache = {}

ALL_SCENARIOS = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ Service Hero")
    st.caption("Neon Edition - AI Roleplay")
    menu = st.radio("MENU", ["DASHBOARD", "CREATE"])
    st.divider()
    if st.button("🔄 RESET DATA"):
        load_data(True)
        st.toast("System Reset Successfully!", icon="✅")
        time.sleep(1)
        st.rerun()

# --- DASHBOARD ---
if menu == "DASHBOARD":
    if st.session_state.current_scenario is None:
        # Màn hình chính
        st.title("WELCOME AGENT 🕶️")
        
        if 'player_name' not in st.session_state: st.session_state.player_name = ""
        if not st.session_state.player_name:
            st.info("Please identify yourself to proceed.")
            st.session_state.player_name = st.text_input("CODENAME:")
            if not st.session_state.player_name: st.stop()
        else:
            c1, c2 = st.columns([3, 1])
            c1.success(f"ONLINE: **{st.session_state.player_name}**")
            if c2.button("LOGOUT"): 
                st.session_state.player_name = ""
                st.rerun()

        with st.expander("🏆 ELITE AGENTS (Leaderboard)"):
            show_leaderboard()
            
        st.divider()
        st.subheader("AVAILABLE MISSIONS")
        
        # Lưới hiển thị kịch bản
        cols = st.columns(2)
        idx = 0
        for key, val in ALL_SCENARIOS.items():
            with cols[idx % 2]:
                # Xác định badge độ khó
                badge_class = "badge-hard" if "Hard" in val['difficulty'] else "badge-med"
                
                # Thẻ kịch bản Neon
                st.markdown(f"""
                <div class="scenario-card">
                    <h3>{val['title']}</h3>
                    <p style="opacity: 0.8;">{val['desc']}</p>
                    <span class="badge {badge_class}">{val['difficulty']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"ENGAGE 🚀", key=key, use_container_width=True):
                    st.session_state.current_scenario = key
                    st.session_state.current_step = 'start'
                    st.session_state.patience = 50
                    st.session_state.history = []
                    st.session_state.img_cache = {} # Reset cache ảnh khi bắt đầu mới
                    st.rerun()
            idx += 1

    # --- MÀN HÌNH CHƠI GAME (GAMEPLAY) ---
    else:
        s_key = st.session_state.current_scenario
        if s_key not in ALL_SCENARIOS: 
            st.session_state.current_scenario = None
            st.rerun()
            
        scenario = ALL_SCENARIOS[s_key]
        step_id = st.session_state.current_step
        step_data = scenario['steps'].get(step_id, scenario.get(step_id))
        
        # --- XỬ LÝ ẢNH ĐỘNG (DYNAMIC IMAGE) ---
        # Tạo khóa cache dựa trên kịch bản và bước hiện tại
        cache_key = f"{s_key}_{step_id}"
        
        if cache_key not in st.session_state.img_cache:
            # Nếu chưa có trong cache, hiển thị spinner và gọi AI tạo ảnh
            with st.spinner("⚡ AI is visualizing the scene..."):
                # Ngữ cảnh: Tiêu đề + Tên khách + Câu thoại hiện tại
                context = f"{scenario['title']} with customer {scenario['customer']['name']}"
                text_content = step_data.get('text', 'Conclusion')
                # Gọi hàm tạo ảnh
                img_url = generate_dynamic_image(context, text_content)
                # Lưu vào cache
                st.session_state.img_cache[cache_key] = img_url
        
        # Lấy ảnh từ cache
        current_img_url = st.session_state.img_cache[cache_key]
        # ---------------------------------------
        
        # Sidebar thông tin
        with st.sidebar:
            st.divider()
            if st.button("❌ ABORT MISSION", use_container_width=True):
                st.session_state.current_scenario = None
                st.rerun()
            
            cust = scenario['customer']
            st.image(cust['avatar'], width=80)
            st.markdown(f"**TARGET: {cust['name']}**")
            st.caption(", ".join(cust['traits']))
            
            # Thanh kiên nhẫn Neon
            p = st.session_state.patience
            color = "#00d2ff" if p > 50 else "#ff0080"
            st.markdown(f"**PATIENCE LEVEL:** <span style='color:{color}'>{p}%</span>", unsafe_allow_html=True)
            st.progress(p/100)

        # Hiển thị nội dung chính
        if "type" in step_data: # Màn hình kết thúc (Win/Lose)
            st.title(step_data['title'])
            # Hiển thị ảnh động đã tạo
            st.image(current_img_url, use_container_width=True, caption="AI Generated Finale")
            
            # Hộp kết quả Neon
            res_class = "win-box" if step_data['type'] == 'WIN' else "lose-box"
            st.markdown(f"<div class='analysis-box {res_class}'><h2>{step_data['text']}</h2></div>", unsafe_allow_html=True)
            
            if step_data['type'] == 'WIN': st.balloons()
            
            st.metric("MISSION SCORE", step_data['score'])
            
            # Lưu điểm 1 lần
            if 'saved' not in st.session_state:
                save_score(st.session_state.player_name, scenario['title'], step_data['score'], step_data['type'])
                st.session_state.saved = True
            
            if st.button("RETURN TO BASE", use_container_width=True):
                st.session_state.current_scenario = None
                if 'saved' in st.session_state: del st.session_state.saved
                st.rerun()
                
            st.divider()
            st.subheader("MISSION DEBRIEF (Analysis)")
            # Phân tích từng bước đi
            for h in st.session_state.history:
                icon = "✅" if h['change'] > 0 else "❌"
                # Màu phân tích dựa trên kết quả (Xanh/Đỏ neon)
                color = "rgba(0, 255, 127, 0.1)" if h['change'] > 0 else "rgba(255, 0, 95, 0.1)"
                border = "#00ff7f" if h['change'] > 0 else "#ff005f"
                st.markdown(f"""
                <div style="background:{color}; border-left: 4px solid {border}; padding:15px; border-radius:8px; margin-top:10px;">
                    <b>{icon} CHOICE:</b> {h['choice']}<br>
                    <i style="opacity:0.9;">👉 {h['analysis']}</i>
                </div>
                """, unsafe_allow_html=True)

        else: # Màn hình chơi (Hội thoại & Lựa chọn)
            st.subheader(scenario['title'])
            # Hiển thị ảnh động cho bước hiện tại
            st.image(current_img_url, use_container_width=True, caption="AI Generated Scene Visualization")
            
            # Hộp thoại Neon
            st.markdown(f"""
            <div class="chat-container">
                <div class="customer-label">🗣️ {cust['name'].upper()} SAYS:</div>
                <div class="dialogue-text">"{step_data['text']}"</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Các nút lựa chọn Neon Gradient
            cols = st.columns(len(step_data['choices']))
            idx = 0
            for k, v in step_data['choices'].items():
                with cols[idx]:
                    if st.button(f"{k}. {v}", use_container_width=True):
                        # Xử lý hậu quả khi chọn
                        cons = step_data['consequences'][k]
                        st.session_state.current_step = cons['next']
                        # Cập nhật kiên nhẫn (giới hạn 0-100)
                        st.session_state.patience = max(0, min(100, st.session_state.patience + cons['change']))
                        # Lưu lịch sử
                        st.session_state.history.append({
                            "step": step_data['text'],
                            "choice": v,
                            "analysis": cons['analysis'],
                            "change": cons['change']
                        })
                        st.rerun()
                idx += 1

# --- MÀN HÌNH TẠO MỚI (DEMO) ---
elif menu == "CREATE":
    st.header("SCENARIO BUILDER")
    st.info("Build custom scenarios here. AI will automatically generate images for each step!")
    with st.form("builder"):
        title = st.text_input("MISSION TITLE")
        desc = st.text_area("BRIEFING")
        if st.form_submit_button("SAVE MISSION"):
            st.success("MISSION SAVED (Demo Mode)")
