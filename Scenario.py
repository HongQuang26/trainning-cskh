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

# --- KHO ẢNH DỰ PHÒNG (BACKUP LIBRARY) ---
BACKUP_IMAGES = {
    "F&B": [
        "https://images.unsplash.com/photo-1572802419224-296b0aeee0d9?q=80&w=1000",
        "https://images.unsplash.com/photo-1559339352-11d035aa65de?q=80&w=1000",
        "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=1000"
    ],
    "HOTEL": [
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1000",
        "https://images.unsplash.com/photo-1582719508461-905c673771fd?q=80&w=1000",
        "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?q=80&w=1000"
    ],
    "OFFICE": [
        "https://images.unsplash.com/photo-1497215728101-856f4ea42174?q=80&w=1000",
        "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?q=80&w=1000",
        "https://images.unsplash.com/photo-1531403009284-440f080d1e12?q=80&w=1000"
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
    if AI_READY:
        try:
            prompt_req = f"Extract 3 visual keywords (english nouns) for stock photo: '{scenario_title} - {step_text}'. Comma separated. No intro."
            res = model.generate_content(prompt_req, request_options={"timeout": 3})
            keywords = res.text.strip().replace("\n", "")
            seed = hash(step_text) % 10000
            encoded = urllib.parse.quote(f"{keywords}, highly detailed, cinematic lighting")
            return f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=600&seed={seed}&nologo=true&model=flux"
        except:
            pass
    images = BACKUP_IMAGES.get(category_key, BACKUP_IMAGES["GENERAL"])
    idx = len(step_text) % len(images)
    return images[idx]

# ==============================================================================
# 1. NEON UI CSS (GIAO DIỆN BẮT MẮT)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
    * { font-family: 'Outfit', sans-serif !important; }

    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(20, 20, 35) 0%, rgb(40, 40, 60) 90%);
        color: #fff;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(15, 15, 30, 0.95);
        border-right: 1px solid rgba(255,255,255,0.1);
    }

    .scenario-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        overflow: hidden;
        transition: transform 0.3s;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    .scenario-card:hover {
        transform: translateY(-5px);
        border-color: #00d2ff;
        box-shadow: 0 10px 30px rgba(0, 210, 255, 0.2);
    }
    .card-img {
        width: 100%; height: 180px; object-fit: cover;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    .chat-container {
        background: rgba(0, 0, 0, 0.3);
        border-left: 5px solid #FDBB2D;
        padding: 25px;
        border-radius: 12px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .customer-label { color: #FDBB2D; font-size: 0.9rem; font-weight: bold; letter-spacing: 1px; }
    .dialogue { font-size: 1.4rem; font-style: italic; color: #fff; line-height: 1.5; margin-top: 5px;}

    .stButton button {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: #fff !important;
        border: 1px solid rgba(255,255,255,0.2);
        font-weight: 700;
        border-radius: 8px;
        padding: 12px 24px;
        transition: 0.3s;
    }
    .stButton button:hover {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        transform: scale(1.02);
        color: #000 !important;
        border: none;
    }
    
    h1 {
        background: linear-gradient(to right, #00c6ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900; letter-spacing: 1px;
    }
    
    /* FIX LAYOUT SPACING */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }
    
    /* LOGIN BOX */
    .login-box {
        background: rgba(255,255,255,0.1);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DỮ LIỆU KỊCH BẢN (11 SCENARIOS)
# ==============================================================================
INITIAL_DATA = {
    "SC_FNB": {
        "title": "F&B: Hair in Soup", "desc": "Customer found hair in food.", "difficulty": "HARD", "category": "F&B",
        "cover": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=800&auto=format&fit=crop",
        "customer": {"name": "Jade", "traits": ["Picky"], "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Jade"}, 
        "steps": {
            "start": {"text": "There's hair in my soup! Disgusting!", "choices": {"A":"Deny", "B":"Apologize"}, "consequences": {"A":{"next":"lose","change":-40,"analysis":"Bad"}, "B":{"next":"step2","change":10,"analysis":"Good"}}}, 
            "step2": {"text": "I'm leaving!", "choices": {"A":"Let go", "B":"Free Dessert"}, "consequences": {"A":{"next":"lose","change":-10,"analysis":"Lost"}, "B":{"next":"win","change":40,"analysis":"Saved"}}},
            "win": {"type":"WIN", "title":"SAVED", "text":"Customer is happy.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Bad review.", "score":40}}
    },
    "SC_HOTEL": {
        "title": "Hotel: Overbooked", "desc": "No room for honeymoon.", "difficulty": "EXTREME", "category": "HOTEL",
        "cover": "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=800&auto=format&fit=crop",
        "customer": {"name": "Mike", "traits": ["Tired"], "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Mike"}, 
        "steps": {
            "start": {"text": "Where is my Ocean View?", "choices": {"A":"System Error", "B":"My Fault"}, "consequences": {"A":{"next":"lose","change":-30,"analysis":"Excuses"}, "B":{"next":"step2","change":20,"analysis":"Ownership"}}}, 
            "step2": {"text": "Fix it!", "choices": {"A":"Breakfast", "B":"Upgrade"}, "consequences": {"A":{"next":"lose","change":-10,"analysis":"Cheap"}, "B":{"next":"win","change":50,"analysis":"Hero"}}},
            "win": {"type":"WIN", "title":"DREAM", "text":"Loved the suite.", "score":100}, "lose": {"type":"LOSE", "title":"LEFT", "text":"Walked out.", "score":0}}
    },
    "SC_TECH": { "title": "IT: Net Down", "desc": "Meeting interrupted.", "difficulty": "MEDIUM", "category": "OFFICE", "cover": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=800",
        "customer": {"name": "Ken", "traits": ["Urgent"], "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Ken"}, 
        "steps": { "start": {"text":"Net down!","choices":{"A":"Restart","B":"Check"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"FIXED", "text":"Online again.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Churn.", "score":0} } },
    
    "SC_RETAIL": { "title": "Retail: Broken", "desc": "Vase arrived broken.", "difficulty": "HARD", "category": "RETAIL", "cover": "https://images.unsplash.com/photo-1596496050844-461dc5b7263f?q=80&w=800",
        "customer": {"name": "Lan", "traits": ["VIP"], "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Lan"}, 
        "steps": { "start": {"text":"Broken!","choices":{"A":"Refund","B":"Replace"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"FIXED", "text":"Replaced.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Lost.", "score":0} } },
    
    "SC_ECOMM": { "title": "E-comm: Lost", "desc": "Package missing.", "difficulty": "MEDIUM", "category": "RETAIL", "cover": "https://images.unsplash.com/photo-1566576912321-d58ba2188273?q=80&w=800",
        "customer": {"name": "Tom", "traits": ["Anxious"], "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Tom"}, 
        "steps": { "start": {"text":"Missing!","choices":{"A":"Wait","B":"Check"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"FOUND", "text":"Got it.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Refund.", "score":0} } },
    
    "SC_BANK": { "title": "Bank: Card Eaten", "desc": "ATM took card.", "difficulty": "HARD", "category": "OFFICE", "cover": "https://images.unsplash.com/photo-1601597111158-2fceff292cdc?q=80&w=800",
        "customer": {"name": "Eve", "traits": ["Old"], "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Eve"}, 
        "steps": { "start": {"text":"My card!","choices":{"A":"Wait","B":"Help"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"SAFE", "text":"Solved.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Left.", "score":0} } },
    
    "SC_AIRLINE": { "title": "Airline: Cancel", "desc": "Flight cancelled.", "difficulty": "EXTREME", "category": "HOTEL", "cover": "https://images.unsplash.com/photo-1436491865332-7a61a14527c5?q=80&w=800",
        "customer": {"name": "Dave", "traits": ["Panic"], "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Dave"}, 
        "steps": { "start": {"text":"Cancelled?!","choices":{"A":"Sorry","B":"Rebook"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"FLYING", "text":"Rebooked.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Missed.", "score":0} } },
    
    "SC_SPA": { "title": "Spa: Allergy", "desc": "Face burning.", "difficulty": "HARD", "category": "HOTEL", "cover": "https://images.unsplash.com/photo-1600334089648-b0d9d3028eb2?q=80&w=800",
        "customer": {"name": "Chloe", "traits": ["Pain"], "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Chloe"}, 
        "steps": { "start": {"text":"Ouch!","choices":{"A":"Ignore","B":"Ice"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Cruel"},"B":{"next":"win","change":20,"analysis":"Care"}}}, "win": {"type":"WIN", "title":"HEALED", "text":"Ok now.", "score":100}, "lose": {"type":"LOSE", "title":"SUED", "text":"Lawsuit.", "score":0} } },
    
    "SC_SAAS": { "title": "SaaS: Data Loss", "desc": "Deleted data.", "difficulty": "HARD", "category": "OFFICE", "cover": "https://images.unsplash.com/photo-1551434678-e076c223a692?q=80&w=800",
        "customer": {"name": "Sarah", "traits": ["Angry"], "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah"}, 
        "steps": { "start": {"text":"Gone!","choices":{"A":"Oops","B":"Restore"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"SAVED", "text":"Restored.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Fired.", "score":0} } },
    
    "SC_REAL": { "title": "Real Est: Mold", "desc": "Moldy apartment.", "difficulty": "VERY HARD", "category": "HOTEL", "cover": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=800",
        "customer": {"name": "Chen", "traits": ["Rich"], "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Chen"}, 
        "steps": { "start": {"text":"Mold!","choices":{"A":"Clean","B":"Move"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"HAPPY", "text":"Moved.", "score":100}, "lose": {"type":"LOSE", "title":"SUED", "text":"Health issue.", "score":0} } },
    
    "SC_LOG": { "title": "Logistics: Broken", "desc": "Gear broken.", "difficulty": "VERY HARD", "category": "RETAIL", "cover": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=800",
        "customer": {"name": "Rob", "traits": ["Mad"], "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Rob"}, 
        "steps": { "start": {"text":"Broken!","choices":{"A":"Claim","B":"Truck"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"SAVED", "text":"Saved.", "score":100}, "lose": {"type":"LOSE", "title":"FIRED", "text":"Lost.", "score":0} } }
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
        
        # Merge Missing Fields
        for k, v in INITIAL_DATA.items():
            if k not in data:
                data[k] = v
            else:
                if 'cover' not in data[k]: data[k]['cover'] = v['cover']
                if 'category' not in data[k]: data[k]['category'] = v.get('category', 'GENERAL')
                if 'customer' in data[k] and 'avatar' not in data[k]['customer']:
                    data[k]['customer']['avatar'] = v['customer']['avatar']
        return data
    except: return load_data(True)

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

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

# AI CHATBOT FUNCTION
def get_ai_chat_response(messages, context):
    """
    Hàm xử lý chat tự do với AI đóng vai khách hàng.
    """
    if not AI_READY: return "AI System Offline."
    
    system_prompt = f"""
    You are roleplaying as a customer named {context['name']} in a {context['title']} scenario.
    Description: {context['desc']}
    Your traits: {', '.join(context['traits'])}.
    
    Be concise, act like a real person (emotional, maybe angry or happy depending on user input).
    Do NOT act like an AI assistant. ACT LIKE THE CUSTOMER.
    """
    
    try:
        # Convert history to Gemini format
        history = [{"role": "user", "parts": [system_prompt]}]
        for msg in messages:
            role = "model" if msg["role"] == "assistant" else "user"
            history.append({"role": role, "parts": [msg["content"]]})
            
        model_chat = genai.GenerativeModel('gemini-1.5-flash')
        response = model_chat.generate_content(history)
        return response.text
    except Exception as e:
        return f"Connection error: {e}"

# SESSION STATE
if 'current_scenario' not in st.session_state: st.session_state.current_scenario = None
if 'step_img_cache' not in st.session_state: st.session_state.step_img_cache = {}
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'chat_context' not in st.session_state: st.session_state.chat_context = None

ALL_SCENARIOS = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ SERVICE HERO")
    st.caption("AI Core: Online")
    menu = st.radio("NAVIGATION", ["DASHBOARD", "CREATE", "AI ROLEPLAY"])
    st.divider()
    if st.button("🔄 REFRESH SYSTEM"):
        st.session_state.step_img_cache = {}
        st.rerun()

# --- 1. DASHBOARD ---
if menu == "DASHBOARD":
    if st.session_state.current_scenario is None:
        st.markdown("# 🚀 MISSION CONTROL")
        
        # --- FIX: LOGIN SECTION IN SEPARATE CONTAINER ---
        with st.container(border=True):
            st.markdown("### 👤 AGENT IDENTIFICATION")
            if 'player_name' not in st.session_state: st.session_state.player_name = ""
            
            if not st.session_state.player_name:
                st.info("Please enter your name to unlock the system.")
                st.session_state.player_name = st.text_input("CODENAME:", key="login_input")
                if not st.session_state.player_name: st.stop()
            else:
                c1, c2 = st.columns([3, 1])
                c1.success(f"ONLINE: **{st.session_state.player_name}**")
                if c2.button("LOGOUT"): 
                    st.session_state.player_name = ""
                    st.rerun()

        st.write("") # Spacer

        # --- LEADERBOARD ---
        with st.expander("🏆 ELITE AGENTS (LEADERBOARD)"):
            show_leaderboard()
            
        st.divider()
        st.subheader("ACTIVE MISSIONS")
        
        # --- SCENARIO GRID ---
        cols = st.columns(2)
        idx = 0
        for key, val in ALL_SCENARIOS.items():
            with cols[idx % 2]:
                img_src = val.get('cover', 'https://images.unsplash.com/photo-1557426272-fc759fdf7a8d?q=80&w=800')
                
                st.markdown(f"""
                <div class="scenario-card">
                    <img src="{img_src}" class="card-img">
                    <div class="card-content">
                        <h3>{val['title']}</h3>
                        <p>{val['desc']}</p>
                        <span style="background:#00d2ff; color:#000; padding:2px 8px; border-radius:4px; font-size:0.8rem; font-weight:bold;">{val['difficulty']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"ENGAGE", key=key, use_container_width=True):
                    st.session_state.current_scenario = key
                    st.session_state.current_step = 'start'
                    st.session_state.patience = 50
                    st.session_state.history = []
                    st.session_state.step_img_cache = {}
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
        
        cache_key = f"{s_key}_{step_id}"
        if cache_key not in st.session_state.step_img_cache:
            cat = scenario.get('category', 'GENERAL')
            st.session_state.step_img_cache[cache_key] = get_smart_image(scenario['title'], step_data.get('text', ''), cat)
        
        current_img = st.session_state.step_img_cache[cache_key]
        
        with st.sidebar:
            st.divider()
            if st.button("❌ ABORT", use_container_width=True):
                st.session_state.current_scenario = None
                st.rerun()
            
            cust = scenario['customer']
            avatar = cust.get('avatar', f"https://api.dicebear.com/7.x/avataaars/svg?seed={cust['name']}")
            st.image(avatar, width=80)
            st.markdown(f"**TARGET: {cust['name']}**")
            p = st.session_state.patience
            st.markdown(f"**PATIENCE:** {p}%")
            st.progress(p/100)

        if "type" in step_data: 
            st.title(step_data['title'])
            st.image(current_img, use_container_width=True)
            color = "#00ff7f" if step_data['type'] == 'WIN' else "#ff005f"
            st.markdown(f"<div style='border:2px solid {color}; padding:20px; border-radius:15px; color:{color}; text-align:center;'><h2>{step_data['text']}</h2></div>", unsafe_allow_html=True)
            
            if step_data['type'] == 'WIN': st.balloons()
            st.metric("SCORE", step_data['score'])
            
            if 'saved' not in st.session_state:
                save_score(st.session_state.player_name, scenario['title'], step_data['score'], step_data['type'])
                st.session_state.saved = True
            
            if st.button("RETURN TO BASE", use_container_width=True):
                st.session_state.current_scenario = None
                if 'saved' in st.session_state: del st.session_state.saved
                st.rerun()

        else:
            st.subheader(scenario['title'])
            st.image(current_img, use_container_width=True)
            st.markdown(f"<div class='chat-container'><div class='customer-label'>{cust['name'].upper()} SAYS:</div><div class='dialogue'>\"{step_data['text']}\"</div></div>", unsafe_allow_html=True)
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

# --- 2. CREATE SCENARIO (FIXED) ---
elif menu == "CREATE":
    st.header("🛠️ BUILDER")
    st.info("Design your own training scenario.")
    
    with st.form("create_form"):
        c1, c2 = st.columns(2)
        title = c1.text_input("Title", placeholder="e.g., Angry Boss")
        category = c2.selectbox("Category", ["OFFICE", "RETAIL", "F&B", "HOTEL", "TECH"])
        desc = st.text_area("Description", placeholder="Brief context...")
        cust_name = st.text_input("Customer Name", placeholder="Mr. John")
        start_text = st.text_area("Opening Line (What does customer say?)", placeholder="Where is my report?!")
        
        st.markdown("### Choices")
        c3, c4 = st.columns(2)
        opt_a = c3.text_input("Choice A (Bad)", placeholder="It's not done.")
        opt_b = c4.text_input("Choice B (Good)", placeholder="I am finishing it now.")
        
        if st.form_submit_button("SAVE SCENARIO"):
            if title and start_text:
                new_id = f"SC_CUSTOM_{int(time.time())}"
                new_scen = {
                    "title": title, "desc": desc, "difficulty": "CUSTOM", "category": category,
                    "cover": "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?q=80&w=800",
                    "customer": {"name": cust_name, "traits": ["Custom"], "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={cust_name}"},
                    "steps": {
                        "start": {
                            "text": start_text,
                            "choices": {"A": opt_a, "B": opt_b},
                            "consequences": {
                                "A": {"next": "lose", "change": -20, "analysis": "Poor choice."},
                                "B": {"next": "win", "change": 20, "analysis": "Good choice."}
                            }
                        },
                        "win": {"type": "WIN", "title": "SUCCESS", "text": "Customer is satisfied.", "score": 100},
                        "lose": {"type": "LOSE", "title": "FAIL", "text": "Customer left.", "score": 0}
                    }
                }
                ALL_SCENARIOS[new_id] = new_scen
                save_data(ALL_SCENARIOS)
                st.success("Scenario Created Successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Please fill in Title and Opening Line.")

# --- 3. AI ROLEPLAY (NEW FEATURE) ---
elif menu == "AI ROLEPLAY":
    st.header("🤖 FREE ROLEPLAY MODE")
    st.info("Chat freely with an AI Customer. Test your soft skills without predefined choices.")
    
    # Select Context
    scenario_list = {k: v['title'] for k, v in ALL_SCENARIOS.items()}
    selected_scen_key = st.selectbox("Choose a Scenario Context:", list(scenario_list.keys()), format_func=lambda x: scenario_list[x])
    
    if st.button("START NEW CHAT"):
        st.session_state.chat_context = ALL_SCENARIOS[selected_scen_key]
        st.session_state.chat_history = []
        # Initial greeting from customer
        init_msg = ALL_SCENARIOS[selected_scen_key]['steps']['start']['text']
        st.session_state.chat_history.append({"role": "assistant", "content": init_msg})
        st.rerun()
        
    st.divider()
    
    # Display Chat
    if st.session_state.chat_context:
        ctx = st.session_state.chat_context
        st.markdown(f"**Interacting with:** {ctx['customer']['name']} ({ctx['title']})")
        
        for msg in st.session_state.chat_history:
            avatar = "🧑‍💻" if msg["role"] == "user" else "👤"
            with st.chat_message(msg["role"], avatar=avatar):
                st.write(msg["content"])
                
        # Input
        if prompt := st.chat_input("Type your response..."):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧑‍💻"):
                st.write(prompt)
                
            # Get AI response
            with st.spinner("Customer is typing..."):
                ai_reply = get_ai_chat_response(st.session_state.chat_history, ctx)
                
            # Add AI message
            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
            with st.chat_message("assistant", avatar="👤"):
                st.write(ai_reply)
