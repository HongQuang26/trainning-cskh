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
# 0. CẤU HÌNH & KHỞI TẠO (SETUP)
# ==============================================================================
GEMINI_API_KEY = "AIzaSyD5ma9Q__JMZUs6mjBppEHUcUBpsI-wjXA"

st.set_page_config(
    page_title="Service Hero: AI Core",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Khởi tạo Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    AI_READY = True
except:
    AI_READY = False

# ==============================================================================
# 1. BỘ XỬ LÝ HÌNH ẢNH "GEMINI DIRECTOR" (CORE ENGINE)
# ==============================================================================
def get_gemini_keywords(scenario_context):
    """
    Dùng Gemini để phân tích tình huống và trả về 3 từ khóa tiếng Anh chính xác nhất.
    """
    if not AI_READY: return "business,meeting,office"
    
    try:
        # Prompt tối ưu để Gemini chỉ trả về từ khóa
        prompt = f"""
        Analyze this scenario: "{scenario_context}"
        Extract exactly 3 simple visual English keywords (nouns) to search for a stock photo.
        Format: word1,word2,word3
        No introduction. No explanation.
        Example: restaurant,angry,soup
        """
        response = model.generate_content(prompt, request_options={"timeout": 5})
        keywords = response.text.strip().replace(" ", "")
        return keywords
    except:
        return "work,office,professional" # Fallback an toàn

def generate_stable_image(context, seed_modifier=0):
    """
    Tạo link ảnh "Bất tử" (100% không lỗi) dựa trên từ khóa của Gemini.
    Sử dụng LoremFlickr để đảm bảo tính ổn định cao nhất.
    """
    # 1. Lấy từ khóa thông minh từ Gemini
    keywords = get_gemini_keywords(context)
    
    # 2. Tạo Seed để ảnh cố định (không bị nhảy ảnh khi click chuột)
    # Dùng hash của context để seed luôn giống nhau cho cùng 1 tình huống
    seed = hash(context + str(seed_modifier)) % 10000
    
    # 3. Tạo URL (LoremFlickr cực kỳ ổn định, không rate limit)
    # Cấu trúc: loremflickr.com/{width}/{height}/{keywords}/all?lock={seed}
    return f"https://loremflickr.com/1024/600/{keywords}/all?lock={seed}"

def preload_assets(all_scenarios):
    """
    Chạy ngầm để chuẩn bị ảnh bìa cho Dashboard
    """
    if 'cover_cache' not in st.session_state:
        st.session_state.cover_cache = {}
        
    missing = [k for k in all_scenarios.keys() if k not in st.session_state.cover_cache]
    
    if missing:
        # Hiển thị tiến trình nhỏ ở sidebar
        status = st.sidebar.empty()
        bar = st.sidebar.progress(0)
        
        for i, key in enumerate(missing):
            status.text(f"⚡ AI Generating: {all_scenarios[key]['title']}...")
            # Tạo ảnh dựa trên tiêu đề + mô tả
            ctx = f"{all_scenarios[key]['title']} {all_scenarios[key]['desc']}"
            st.session_state.cover_cache[key] = generate_stable_image(ctx, seed_modifier=key)
            bar.progress((i + 1) / len(missing))
            time.sleep(0.05) # Delay cực nhỏ để mượt
            
        status.empty()
        bar.empty()

# ==============================================================================
# 2. GIAO DIỆN NEON CYBERPUNK (CSS)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;600;700&display=swap');
    
    /* 1. NỀN & FONT */
    .stApp {
        background-color: #050505;
        background-image: 
            radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
            radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
            radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
        font-family: 'Chakra Petch', sans-serif;
        color: #e0e0e0;
    }
    
    /* 2. SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 10, 20, 0.95);
        border-right: 1px solid rgba(255,255,255,0.1);
    }

    /* 3. HEADERS (Gradient Text) */
    h1, h2, h3 {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* 4. SCENARIO CARD (Neon Glow) */
    .scenario-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        overflow: hidden;
        transition: all 0.3s;
        margin-bottom: 20px;
        position: relative;
    }
    .scenario-card:hover {
        transform: translateY(-5px);
        border-color: #00C9FF;
        box-shadow: 0 0 15px rgba(0, 201, 255, 0.4);
    }
    .card-img-box {
        width: 100%; height: 180px; overflow: hidden;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .card-img-box img { width: 100%; height: 100%; object-fit: cover; }
    .card-content { padding: 15px; }

    /* 5. CHAT BUBBLES */
    .chat-container {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid #333;
        border-left: 4px solid #F4D03F; /* Vàng kim */
        padding: 20px;
        border-radius: 0 15px 15px 0;
        margin: 20px 0;
        backdrop-filter: blur(5px);
    }
    .customer-label { color: #F4D03F; font-size: 0.9rem; font-weight: bold; letter-spacing: 1.5px; margin-bottom: 5px;}
    .dialogue { font-size: 1.4rem; font-style: italic; color: #fff; line-height: 1.5; }

    /* 6. BUTTONS (Cyberpunk Style) */
    .stButton button {
        background: transparent;
        color: #00C9FF;
        border: 2px solid #00C9FF;
        font-family: 'Chakra Petch', sans-serif;
        font-weight: 700;
        text-transform: uppercase;
        border-radius: 4px;
        padding: 15px 20px;
        transition: 0.2s;
        width: 100%;
        box-shadow: 0 0 5px rgba(0, 201, 255, 0.2);
    }
    .stButton button:hover {
        background: #00C9FF;
        color: #000;
        box-shadow: 0 0 20px rgba(0, 201, 255, 0.6);
    }
    
    /* 7. PROGRESS BAR */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #F4D03F, #FF4B2B);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. DỮ LIỆU KỊCH BẢN (11 SCENARIOS)
# ==============================================================================
INITIAL_DATA = {
    "SC_FNB": {"title": "F&B: Hair in Soup", "desc": "Customer found hair.", "difficulty": "HARD", "customer": {"name": "Jade", "traits": ["Picky"]}, 
               "steps": {"start": {"text": "There's hair in my soup!", "choices": {"A":"Deny", "B":"Apologize"}, "consequences": {"A":{"next":"lose","change":-40,"analysis":"Bad"}, "B":{"next":"step2","change":10,"analysis":"Good"}}}, 
                         "step2": {"text": "I'm leaving!", "choices": {"A":"Let go", "B":"Dessert"}, "consequences": {"A":{"next":"lose","change":-10,"analysis":"Lost"}, "B":{"next":"win","change":40,"analysis":"Saved"}}},
                         "win": {"type":"WIN", "title":"SAVED", "text":"Happy.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Bad review.", "score":40}}},
    "SC_HOTEL": {"title": "Hotel: No Room", "desc": "Overbooked suite.", "difficulty": "EXTREME", "customer": {"name": "Mike", "traits": ["Tired"]}, 
                 "steps": {"start": {"text": "Where is my room?", "choices": {"A":"Error", "B":"My Fault"}, "consequences": {"A":{"next":"lose","change":-30,"analysis":"Excuses"}, "B":{"next":"step2","change":20,"analysis":"Ownership"}}}, 
                           "step2": {"text": "Fix it!", "choices": {"A":"Breakfast", "B":"Upgrade"}, "consequences": {"A":{"next":"lose","change":-10,"analysis":"Cheap"}, "B":{"next":"win","change":50,"analysis":"Hero"}}},
                           "win": {"type":"WIN", "title":"DREAM", "text":"Loved it.", "score":100}, "lose": {"type":"LOSE", "title":"LEFT", "text":"Walked out.", "score":0}}},
    "SC_TECH": {"title": "IT: Net Down", "desc": "Meeting cut off.", "difficulty": "MEDIUM", "customer": {"name": "Ken", "traits": ["Urgent"]}, 
                "steps": {"start": {"text": "Net down!", "choices": {"A":"Restart", "B":"Check"}, "consequences": {"A":{"next":"lose","change":-20,"analysis":"Bad"}, "B":{"next":"win","change":20,"analysis":"Good"}}}, 
                          "win": {"type":"WIN", "title":"FIXED", "text":"Online.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Churn.", "score":0}}},
    "SC_RETAIL": {"title": "Retail: Broken", "desc": "Vase arrived broken.", "difficulty": "HARD", "customer": {"name": "Lan", "traits": ["VIP"]}, 
                  "steps": {"start": {"text": "It's broken!", "choices": {"A":"Refund", "B":"Replace"}, "consequences": {"A":{"next":"lose","change":-20,"analysis":"Bad"}, "B":{"next":"win","change":20,"analysis":"Good"}}}, 
                            "win": {"type":"WIN", "title":"FIXED", "text":"Replaced.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Lost VIP.", "score":0}}},
    "SC_ECOMM": {"title": "E-comm: Lost", "desc": "Package missing.", "difficulty": "MEDIUM", "customer": {"name": "Tom", "traits": ["Anxious"]}, 
                 "steps": {"start": {"text": "Where is it?", "choices": {"A":"Wait", "B":"Check"}, "consequences": {"A":{"next":"lose","change":-20,"analysis":"Lazy"}, "B":{"next":"win","change":20,"analysis":"Helpful"}}}, 
                           "win": {"type":"WIN", "title":"FOUND", "text":"Got it.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Refund.", "score":0}}},
    "SC_BANK": {"title": "Bank: Card Eaten", "desc": "ATM took card.", "difficulty": "HARD", "customer": {"name": "Eve", "traits": ["Old"]}, 
                "steps": {"start": {"text": "My card!", "choices": {"A":"Wait", "B":"Help"}, "consequences": {"A":{"next":"lose","change":-20,"analysis":"Bad"}, "B":{"next":"win","change":20,"analysis":"Good"}}}, 
                          "win": {"type":"WIN", "title":"SAFE", "text":"Solved.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Left.", "score":0}}},
    "SC_AIRLINE": {"title": "Airline: Cancel", "desc": "Flight cancelled.", "difficulty": "EXTREME", "customer": {"name": "Dave", "traits": ["Panic"]}, 
                   "steps": {"start": {"text": "Cancelled?!", "choices": {"A":"Sorry", "B":"Rebook"}, "consequences": {"A":{"next":"lose","change":-20,"analysis":"Bad"}, "B":{"next":"win","change":20,"analysis":"Good"}}}, 
                             "win": {"type":"WIN", "title":"FLYING", "text":"Rebooked.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Missed.", "score":0}}},
    "SC_SPA": {"title": "Spa: Allergy", "desc": "Face burning.", "difficulty": "HARD", "customer": {"name": "Chloe", "traits": ["Pain"]}, 
               "steps": {"start": {"text": "Ouch!", "choices": {"A":"Ignore", "B":"Ice"}, "consequences": {"A":{"next":"lose","change":-20,"analysis":"Cruel"}, "B":{"next":"win","change":20,"analysis":"Care"}}}, 
                         "win": {"type":"WIN", "title":"HEALED", "text":"Ok now.", "score":100}, "lose": {"type":"LOSE", "title":"SUED", "text":"Lawsuit.", "score":0}}},
    "SC_SAAS": {"title": "SaaS: Data Loss", "desc": "Deleted data.", "difficulty": "HARD", "customer": {"name": "Sarah", "traits": ["Angry"]}, 
                "steps": {"start": {"text": "Gone!", "choices": {"A":"Oops", "B":"Restore"}, "consequences": {"A":{"next":"lose","change":-20,"analysis":"Bad"}, "B":{"next":"win","change":20,"analysis":"Good"}}}, 
                          "win": {"type":"WIN", "title":"SAVED", "text":"Restored.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Fired.", "score":0}}},
    "SC_REAL": {"title": "Real Est: Mold", "desc": "Moldy apartment.", "difficulty": "VERY HARD", "customer": {"name": "Chen", "traits": ["Rich"]}, 
                "steps": {"start": {"text": "Mold!", "choices": {"A":"Clean", "B":"Move"}, "consequences": {"A":{"next":"lose","change":-20,"analysis":"Bad"}, "B":{"next":"win","change":20,"analysis":"Good"}}}, 
                          "win": {"type":"WIN", "title":"HAPPY", "text":"Moved.", "score":100}, "lose": {"type":"LOSE", "title":"SUED", "text":"Health issue.", "score":0}}},
    "SC_LOG": {"title": "Logistics: Broken", "desc": "Gear broken.", "difficulty": "VERY HARD", "customer": {"name": "Rob", "traits": ["Mad"]}, 
               "steps": {"start": {"text": "Broken!", "choices": {"A":"Claim", "B":"Truck"}, "consequences": {"A":{"next":"lose","change":-20,"analysis":"Bad"}, "B":{"next":"win","change":20,"analysis":"Good"}}}, 
                         "win": {"type":"WIN", "title":"SAVED", "text":"Saved.", "score":100}, "lose": {"type":"LOSE", "title":"FIRED", "text":"Lost.", "score":0}}}
}

DB_FILE = "scenarios.json"
HISTORY_FILE = "score_history.csv"

# ==============================================================================
# 4. APP LOGIC
# ==============================================================================
def load_data(): return INITIAL_DATA

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
    else: st.info("No history.")

# SESSION STATE
if 'current_scenario' not in st.session_state: st.session_state.current_scenario = None
if 'step_img_cache' not in st.session_state: st.session_state.step_img_cache = {}

ALL_SCENARIOS = load_data()

# --- PRELOADER (TẠO ẢNH BÌA NGẦM) ---
preload_assets(ALL_SCENARIOS)

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ SERVICE HERO")
    st.caption("AI Core: Online")
    menu = st.radio("NAVIGATION", ["DASHBOARD", "CREATE"])
    st.divider()
    if st.button("🔄 REFRESH SYSTEM"):
        st.session_state.cover_cache = {}
        st.session_state.step_img_cache = {}
        st.rerun()

# --- DASHBOARD ---
if menu == "DASHBOARD":
    if st.session_state.current_scenario is None:
        st.markdown("# 🚀 MISSION CONTROL")
        
        if 'player_name' not in st.session_state: st.session_state.player_name = ""
        if not st.session_state.player_name:
            st.info("Identify yourself to access the system.")
            st.session_state.player_name = st.text_input("CODENAME:")
            if not st.session_state.player_name: st.stop()
        else:
            c1, c2 = st.columns([3, 1])
            c1.success(f"AGENT ONLINE: **{st.session_state.player_name}**")
            if c2.button("LOGOUT"): 
                st.session_state.player_name = ""
                st.rerun()

        with st.expander("🏆 ELITE AGENTS (Leaderboard)"):
            show_leaderboard()
            
        st.divider()
        st.subheader("ACTIVE MISSIONS")
        
        # GRID LAYOUT (Ảnh đã tải sẵn)
        cols = st.columns(2)
        idx = 0
        for key, val in ALL_SCENARIOS.items():
            with cols[idx % 2]:
                # Lấy ảnh từ cache (đã được tạo bởi hàm preload)
                img_src = st.session_state.cover_cache.get(key, "https://placehold.co/800x450/1a1a2e/FFF?text=Generating...")
                
                # HTML Card
                st.markdown(f"""
                <div class="scenario-card">
                    <div class="card-img-box"><img src="{img_src}" alt="Scene"></div>
                    <div class="card-content">
                        <h3>{val['title']}</h3>
                        <p>{val['desc']}</p>
                        <span style="background:#00d2ff; color:#000; padding:2px 8px; border-radius:4px; font-size:0.8rem; font-weight:bold;">{val['difficulty']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"ENGAGE MISSION", key=key, use_container_width=True):
                    st.session_state.current_scenario = key
                    st.session_state.current_step = 'start'
                    st.session_state.patience = 50
                    st.session_state.history = []
                    st.session_state.step_img_cache = {} # Reset cache ảnh từng bước
                    st.rerun()
            idx += 1

    # --- GAMEPLAY (LIVE GEN) ---
    else:
        s_key = st.session_state.current_scenario
        if s_key not in ALL_SCENARIOS: 
            st.session_state.current_scenario = None
            st.rerun()
            
        scenario = ALL_SCENARIOS[s_key]
        step_id = st.session_state.current_step
        step_data = scenario['steps'].get(step_id, scenario.get(step_id))
        
        # --- TẠO ẢNH TRỰC TIẾP CHO BƯỚC HIỆN TẠI (100% SUCCESS) ---
        cache_key = f"{s_key}_{step_id}"
        
        if cache_key not in st.session_state.step_img_cache:
            with st.spinner("⚡ AI is constructing visual data..."):
                # 1. Gemini trích xuất từ khóa cho tình huống này
                context = f"{scenario['title']} {step_data.get('text', '')}"
                # 2. Tạo link ảnh bất tử
                current_img = generate_stable_image(context, seed_modifier=cache_key)
                st.session_state.step_img_cache[cache_key] = current_img
        
        current_img = st.session_state.step_img_cache[cache_key]
        
        # Sidebar Info
        with st.sidebar:
            st.divider()
            if st.button("❌ ABORT", use_container_width=True):
                st.session_state.current_scenario = None
                st.rerun()
            
            cust = scenario['customer']
            st.image(cust['avatar'], width=80)
            st.markdown(f"**TARGET: {cust['name']}**")
            p = st.session_state.patience
            st.markdown(f"**PATIENCE:** {p}%")
            st.progress(p/100)

        # Game UI
        if "type" in step_data: # End
            st.title(step_data['title'])
            st.image(current_img, use_container_width=True)
            
            # Box Kết quả
            color = "#00ff7f" if step_data['type'] == 'WIN' else "#ff005f"
            st.markdown(f"""
            <div style="border:2px solid {color}; padding:20px; border-radius:15px; color:{color}; text-align:center; background:rgba(0,0,0,0.3);">
                <h2>{step_data['text']}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            if step_data['type'] == 'WIN': st.balloons()
            st.metric("SCORE", step_data['score'])
            
            if 'saved' not in st.session_state:
                save_score(st.session_state.player_name, scenario['title'], step_data['score'], step_data['type'])
                st.session_state.saved = True
            
            if st.button("RETURN TO BASE", use_container_width=True):
                st.session_state.current_scenario = None
                if 'saved' in st.session_state: del st.session_state.saved
                st.rerun()

        else: # Playing
            st.subheader(scenario['title'])
            st.image(current_img, use_container_width=True)
            
            st.markdown(f"""
            <div class="chat-container">
                <div class="customer-label">{cust['name'].upper()} SAYS:</div>
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

elif menu == "CREATE":
    st.header("SCENARIO BUILDER")
    st.info("Demo Mode")
