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
# 0. CẤU HÌNH HỆ THỐNG
# ==============================================================================
GEMINI_API_KEY = "AIzaSyD5ma9Q__JMZUs6mjBppEHUcUBpsI-wjXA"

st.set_page_config(
    page_title="Service Hero AI",
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
# 1. BỘ MÁY TẠO ẢNH AI (AI IMAGE ENGINE)
# ==============================================================================
def get_gemini_prompt(context_text):
    """
    Dùng Gemini để tóm tắt tình huống thành Prompt vẽ tranh tiếng Anh ngắn gọn.
    """
    if not AI_READY: return context_text
    try:
        # Yêu cầu Gemini chỉ trả về keyword để tránh lỗi URL quá dài
        response = model.generate_content(
            f"Generate 5 english visual keywords for this scene: '{context_text}'. Output format: word1, word2, word3...",
            request_options={"timeout": 5}
        )
        return response.text.strip()
    except:
        return context_text

def generate_image_url(prompt_text, seed=None):
    """
    Tạo link ảnh từ Prompt. Sử dụng model FLUX để ảnh đẹp và nhanh.
    """
    if seed is None:
        seed = random.randint(0, 999999)
    
    # Làm sạch prompt để tránh lỗi URL
    clean_prompt = urllib.parse.quote(prompt_text[:100]) # Giới hạn 100 ký tự
    
    # URL Pollinations với tham số nologo và private để tránh cache lỗi cũ
    return f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1024&height=576&seed={seed}&nologo=true&model=flux"

def preload_scenario_covers(all_scenarios):
    """
    Hàm chạy ngầm: Tự động Gen ảnh cho tất cả scenario chưa có ảnh.
    """
    if 'cover_cache' not in st.session_state:
        st.session_state.cover_cache = {}
        
    # Tìm các scenario chưa có ảnh trong cache
    missing = [k for k in all_scenarios.keys() if k not in st.session_state.cover_cache]
    
    if missing:
        # Hiển thị thanh loading ở sidebar để báo hiệu đang gen ngầm
        status_text = st.sidebar.empty()
        progress_bar = st.sidebar.progress(0)
        
        for i, key in enumerate(missing):
            status_text.caption(f"🎨 AI Generating: {all_scenarios[key]['title']}...")
            
            # 1. Gọi Gemini lấy prompt
            raw_prompt = f"{all_scenarios[key]['title']} {all_scenarios[key]['desc']}"
            ai_prompt = get_gemini_prompt(raw_prompt)
            
            # 2. Tạo URL ảnh
            img_url = generate_image_url(ai_prompt, seed=i)
            st.session_state.cover_cache[key] = img_url
            
            # Cập nhật thanh tiến trình
            progress_bar.progress((i + 1) / len(missing))
            time.sleep(0.1) # Delay nhẹ để tránh overload
            
        status_text.empty()
        progress_bar.empty()
        st.sidebar.success("✅ AI Assets Ready!", icon="✨")

# ==============================================================================
# 2. GIAO DIỆN NEON (CSS)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    
    /* GLOBAL THEME */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(at 50% 0%, #1a1a2e 0%, #000000 100%);
        color: #e0e0e0;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #0a0a12;
        border-right: 1px solid #333;
    }

    /* HEADERS */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(90deg, #00f260, #0575e6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
    }

    /* SCENARIO CARD */
    .scenario-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        overflow: hidden;
        transition: transform 0.3s, border-color 0.3s;
        margin-bottom: 20px;
    }
    .scenario-card:hover {
        transform: translateY(-5px);
        border-color: #00d2ff;
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.3);
    }
    .card-img {
        width: 100%; height: 160px; object-fit: cover;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        background-color: #1a1a1a;
    }
    .card-content { padding: 15px; }
    
    /* CHAT BUBBLES */
    .chat-container {
        background: rgba(20, 20, 30, 0.8);
        border-left: 4px solid #facc15;
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .customer-label { color: #facc15; font-size: 0.9rem; font-weight: bold; letter-spacing: 1px; }
    .dialogue { font-size: 1.3rem; font-style: italic; color: #fff; line-height: 1.5; }

    /* BUTTONS */
    .stButton button {
        background: linear-gradient(45deg, #2b5876 0%, #4e4376 100%);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 1px;
        transition: 0.3s;
        width: 100%;
        padding: 15px 0;
    }
    .stButton button:hover {
        background: linear-gradient(45deg, #00d2ff 0%, #3a7bd5 100%);
        border-color: #00d2ff;
        box-shadow: 0 0 10px #00d2ff;
        color: #000;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. DỮ LIỆU KỊCH BẢN (11 SCENARIOS)
# ==============================================================================
INITIAL_DATA = {
    "SC_FNB": {"title": "F&B: Hair in Soup", "desc": "Customer found hair in food.", "difficulty": "Hard", "customer": {"name": "Jade", "traits": ["Picky"]}, 
               "steps": {"start": {"text": "There's hair in my soup!", "choices": {"A":"Deny", "B":"Apologize"}, "consequences": {"A":{"next":"lose","change":-40,"analysis":"Bad"}, "B":{"next":"step2","change":10,"analysis":"Good"}}}, 
                         "step2": {"text": "I'm leaving!", "choices": {"A":"Let go", "B":"Free Dessert"}, "consequences": {"A":{"next":"lose","change":-10,"analysis":"Lost"}, "B":{"next":"win","change":40,"analysis":"Saved"}}},
                         "win": {"type":"WIN", "title":"SAVED", "text":"Customer is happy.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Bad review.", "score":40}}},
    
    "SC_HOTEL": {"title": "Hotel: Overbooked", "desc": "No room for honeymoon.", "difficulty": "Very Hard", "customer": {"name": "Mike", "traits": ["Tired"]}, 
                 "steps": {"start": {"text": "Where is my Ocean View?", "choices": {"A":"System Error", "B":"My Fault"}, "consequences": {"A":{"next":"lose","change":-30,"analysis":"Excuses"}, "B":{"next":"step2","change":20,"analysis":"Ownership"}}}, 
                           "step2": {"text": "Fix it!", "choices": {"A":"Breakfast", "B":"Suite Upgrade"}, "consequences": {"A":{"next":"lose","change":-10,"analysis":"Cheap"}, "B":{"next":"win","change":50,"analysis":"Hero"}}},
                           "win": {"type":"WIN", "title":"DREAM", "text":"Loved the suite.", "score":100}, "lose": {"type":"LOSE", "title":"LEFT", "text":"Walked out.", "score":0}}},
    
    "SC_TECH": {"title": "IT: Net Down", "desc": "Meeting interrupted.", "difficulty": "Medium", "customer": {"name": "Ken", "traits": ["Urgent"]}, 
                "steps": {"start": {"text": "Internet is dead!", "choices": {"A":"Restart", "B":"Check"}, "consequences": {"A":{"next":"lose","change":-20,"analysis":"Bad"}, "B":{"next":"win","change":20,"analysis":"Good"}}}, 
                          "win": {"type":"WIN", "title":"FIXED", "text":"Online again.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Churned.", "score":0}}},
    
    "SC_RETAIL": {"title": "Retail: Broken", "desc": "Vase arrived broken.", "difficulty": "Hard", "customer": {"name": "Lan", "traits": ["VIP"]}, 
                  "steps": {"start": {"text": "It's shattered!", "choices": {"A":"Refund", "B":"Replace"}, "consequences": {"A":{"next":"lose","change":-20,"analysis":"Bad"}, "B":{"next":"win","change":20,"analysis":"Good"}}}, 
                            "win": {"type":"WIN", "title":"FIXED", "text":"Replaced.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Lost VIP.", "score":0}}},
    
    "SC_ECOMM": {"title": "E-comm: Lost", "desc": "Package missing.", "difficulty": "Medium", "customer": {"name": "Tom", "traits": ["Anxious"]}, 
                 "steps": {"start": {"text": "Where is it?", "choices": {"A":"Wait", "B":"Check"}, "consequences": {"A":{"next":"lose","change":-20,"analysis":"Lazy"}, "B":{"next":"win","change":20,"analysis":"Helpful"}}}, 
                           "win": {"type":"WIN", "title":"FOUND", "text":"Got it.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Refund.", "score":0}}},
    
    "SC_BANK": {"title": "Bank: Card Eaten", "desc": "ATM took card.", "difficulty": "Hard", "customer": {"name": "Eve", "traits": ["Old"]}, 
                "steps": {"start": {"text": "My card!", "choices": {"A":"Wait", "B":"Help"}, "consequences": {"A":{"next":"lose","change":-20,"analysis":"Bad"}, "B":{"next":"win","change":20,"analysis":"Good"}}}, 
                          "win": {"type":"WIN", "title":"SAFE", "text":"Solved.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Left.", "score":0}}},
    
    "SC_AIRLINE": {"title": "Airline: Cancelled", "desc": "Flight cancelled.", "difficulty": "Extreme", "customer": {"name": "Dave", "traits": ["Panic"]}, 
                   "steps": {"start": {"text": "Cancelled?!", "choices": {"A":"Sorry", "B":"Rebook"}, "consequences": {"A":{"next":"lose","change":-20,"analysis":"Bad"}, "B":{"next":"win","change":20,"analysis":"Good"}}}, 
                             "win": {"type":"WIN", "title":"FLYING", "text":"Rebooked.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Missed.", "score":0}}},
    
    "SC_SPA": {"title": "Spa: Allergy", "desc": "Face burning.", "difficulty": "Hard", "customer": {"name": "Chloe", "traits": ["Pain"]}, 
               "steps": {"start": {"text": "It burns!", "choices": {"A":"Ignore", "B":"Ice"}, "consequences": {"A":{"next":"lose","change":-20,"analysis":"Cruel"}, "B":{"next":"win","change":20,"analysis":"Care"}}}, 
                         "win": {"type":"WIN", "title":"HEALED", "text":"Ok now.", "score":100}, "lose": {"type":"LOSE", "title":"SUED", "text":"Lawsuit.", "score":0}}},
    
    "SC_SAAS": {"title": "SaaS: Data Loss", "desc": "Deleted data.", "difficulty": "Hard", "customer": {"name": "Sarah", "traits": ["Angry"]}, 
                "steps": {"start": {"text": "Data gone!", "choices": {"A":"Oops", "B":"Restore"}, "consequences": {"A":{"next":"lose","change":-20,"analysis":"Bad"}, "B":{"next":"win","change":20,"analysis":"Good"}}}, 
                          "win": {"type":"WIN", "title":"SAVED", "text":"Restored.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Fired.", "score":0}}},
    
    "SC_REAL": {"title": "Real Estate: Mold", "desc": "Moldy apartment.", "difficulty": "Very Hard", "customer": {"name": "Chen", "traits": ["Rich"]}, 
                "steps": {"start": {"text": "Mold!", "choices": {"A":"Clean", "B":"Move"}, "consequences": {"A":{"next":"lose","change":-20,"analysis":"Unsafe"}, "B":{"next":"win","change":20,"analysis":"Safe"}}}, 
                          "win": {"type":"WIN", "title":"HAPPY", "text":"Moved.", "score":100}, "lose": {"type":"LOSE", "title":"SUED", "text":"Health issue.", "score":0}}},
    
    "SC_LOG": {"title": "Logistics: Broken", "desc": "Gear broken.", "difficulty": "Very Hard", "customer": {"name": "Rob", "traits": ["Mad"]}, 
               "steps": {"start": {"text": "Broken!", "choices": {"A":"Claim", "B":"Truck"}, "consequences": {"A":{"next":"lose","change":-20,"analysis":"Slow"}, "B":{"next":"win","change":20,"analysis":"Fast"}}}, 
                         "win": {"type":"WIN", "title":"SAVED", "text":"Event saved.", "score":100}, "lose": {"type":"LOSE", "title":"FIRED", "text":"Contract lost.", "score":0}}}
}

DB_FILE = "scenarios.json"
HISTORY_FILE = "score_history.csv"

# ==============================================================================
# 4. APP LOGIC
# ==============================================================================
def load_data():
    return INITIAL_DATA # Dùng data cứng để ổn định, có thể mở rộng load json sau

def save_score(player, scenario, score, outcome):
    new_row = {"Time": datetime.now().strftime("%Y-%m-%d %H:%M"), "Player": player, "Scenario": scenario, "Score": score, "Outcome": outcome}
    if os.path.exists(HISTORY_FILE):
        df = pd.read_csv(HISTORY_FILE)
    else:
        df = pd.DataFrame(columns=["Time", "Player", "Scenario", "Score", "Outcome"])
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(HISTORY_FILE, index=False)

# INIT SESSION
if 'current_scenario' not in st.session_state: st.session_state.current_scenario = None
if 'step_img_cache' not in st.session_state: st.session_state.step_img_cache = {}

ALL_SCENARIOS = load_data()

# --- PRELOADER (CHẠY NGẦM TẠO ẢNH BÌA) ---
preload_scenario_covers(ALL_SCENARIOS)

# --- SIDEBAR MENU ---
with st.sidebar:
    st.title("⚡ SERVICE HERO")
    st.caption("AI-Generated Assets")
    menu = st.radio("NAVIGATION", ["DASHBOARD", "CREATE"])
    
    st.divider()
    if st.button("🔄 REFRESH ASSETS"):
        st.session_state.cover_cache = {}
        st.session_state.step_img_cache = {}
        st.rerun()

# --- DASHBOARD ---
if menu == "DASHBOARD":
    if st.session_state.current_scenario is None:
        st.markdown("# 🚀 MISSION CONTROL")
        
        # Player Input
        if 'player_name' not in st.session_state: st.session_state.player_name = ""
        if not st.session_state.player_name:
            st.info("Identify yourself:")
            st.session_state.player_name = st.text_input("CODENAME:")
            if not st.session_state.player_name: st.stop()
        else:
            c1, c2 = st.columns([3, 1])
            c1.success(f"AGENT ONLINE: **{st.session_state.player_name}**")
            if c2.button("LOGOUT"): 
                st.session_state.player_name = ""
                st.rerun()

        st.divider()
        
        # GRID LAYOUT (HIỂN THỊ ẢNH ĐÃ PRELOAD)
        cols = st.columns(2)
        idx = 0
        for key, val in ALL_SCENARIOS.items():
            with cols[idx % 2]:
                # Lấy ảnh từ cache (đã được tạo bởi hàm preload)
                # Nếu chưa kịp tạo xong thì hiện placeholder
                img_src = st.session_state.cover_cache.get(key, "https://placehold.co/800x450/1a1a2e/FFF?text=AI+Generating...")
                
                # Render Card
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
                
                if st.button(f"START MISSION", key=key, use_container_width=True):
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
        
        # --- TẠO ẢNH TRỰC TIẾP CHO BƯỚC HIỆN TẠI ---
        cache_key = f"{s_key}_{step_id}"
        
        if cache_key not in st.session_state.step_img_cache:
            with st.spinner("⚡ AI is painting the scene..."):
                # 1. Gemini tạo prompt mới dựa trên hội thoại hiện tại
                context = f"{scenario['title']}. Scene: {step_data.get('text', '')}"
                ai_prompt = get_gemini_prompt(context)
                
                # 2. Gen ảnh
                current_img = generate_image_url(ai_prompt)
                st.session_state.step_img_cache[cache_key] = current_img
        
        current_img = st.session_state.step_img_cache[cache_key]
        
        # Sidebar Info
        with st.sidebar:
            st.divider()
            if st.button("❌ ABORT", use_container_width=True):
                st.session_state.current_scenario = None
                st.rerun()
            
            cust = scenario['customer']
            st.markdown(f"**TARGET: {cust['name']}**")
            p = st.session_state.patience
            st.markdown(f"**PATIENCE:** {p}%")
            st.progress(p/100)

        # Game UI
        if "type" in step_data: # End
            st.title(step_data['title'])
            st.image(current_img, use_container_width=True)
            st.info(step_data['text'])
            
            if step_data['type'] == 'WIN': st.balloons()
            st.metric("SCORE", step_data['score'])
            
            if 'saved' not in st.session_state:
                save_score(st.session_state.player_name, scenario['title'], step_data['score'], step_data['type'])
                st.session_state.saved = True
            
            if st.button("RETURN", use_container_width=True):
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
