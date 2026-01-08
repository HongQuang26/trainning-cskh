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
# 0. CẤU HÌNH & KHỞI TẠO AI
# ==============================================================================
# API Key của bạn
GEMINI_API_KEY = "AIzaSyD5ma9Q__JMZUs6mjBppEHUcUBpsI-wjXA"

st.set_page_config(
    page_title="Service Hero: AI Gen",
    page_icon="⚡",
    layout="wide"
)

# Khởi tạo Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    AI_READY = True
except:
    AI_READY = False

# --- HÀM TẠO ẢNH BẰNG GEMINI (CORE ENGINE) ---
def generate_scenario_thumbnail(scenario_title, scenario_desc):
    """
    Hàm này dùng Gemini để sinh ra Prompt vẽ tranh, sau đó tạo URL ảnh.
    """
    if not AI_READY:
        # Fallback nếu mất kết nối AI
        return f"https://placehold.co/800x500/1e293b/FFF?text={urllib.parse.quote(scenario_title)}"

    try:
        # Bước 1: Hỏi Gemini lấy 3 từ khóa hình ảnh (English visual keywords)
        prompt = f"""
        Act as a visual prompt generator. 
        Scenario: {scenario_title} - {scenario_desc}
        Task: Extract 3 main visual keywords (nouns/adjectives) in English to describe a photo of this scene.
        Constraint: Output ONLY the keywords separated by comma. No intro.
        Example Output: angry customer, luxury hotel lobby, cinematic
        """
        response = model.generate_content(prompt, request_options={"timeout": 5})
        keywords = response.text.strip()
        
        # Bước 2: Tạo URL ảnh (Dùng Seed ngẫu nhiên để mỗi lần F5 là ảnh khác nhau)
        seed = random.randint(0, 999999)
        # Thêm style cinematic để ảnh đẹp
        final_prompt = f"{keywords}, cinematic lighting, photorealistic, 8k, detailed"
        encoded = urllib.parse.quote(final_prompt)
        
        # Pollinations API (Nhanh, miễn phí, không giới hạn rate limit nếu dùng qua URL)
        return f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=500&seed={seed}&nologo=true&model=flux"
        
    except Exception as e:
        # Fallback an toàn tuyệt đối nếu Gemini lỗi
        seed = random.randint(0, 100)
        return f"https://loremflickr.com/800/500/business,office?lock={seed}"

# --- BỘ NẠP TÀI NGUYÊN (ASSET LOADER) ---
def preload_images(all_scenarios):
    """
    Chạy ngay khi mở app: Tạo sẵn ảnh cho tất cả kịch bản và lưu vào Session State.
    """
    if 'thumbnails' not in st.session_state:
        st.session_state.thumbnails = {}

    # Kiểm tra xem có kịch bản nào chưa có ảnh không
    missing_keys = [k for k in all_scenarios.keys() if k not in st.session_state.thumbnails]
    
    if missing_keys:
        # Hiển thị thông báo đang nạp (chỉ hiện lần đầu)
        with st.status("🚀 AI is generating assets for scenarios...", expanded=True) as status:
            progress_bar = st.progress(0)
            step = 1.0 / len(missing_keys)
            current_progress = 0.0
            
            for key in missing_keys:
                data = all_scenarios[key]
                # Gọi AI tạo ảnh
                img_url = generate_scenario_thumbnail(data['title'], data['desc'])
                st.session_state.thumbnails[key] = img_url
                
                # Cập nhật tiến trình
                current_progress += step
                progress_bar.progress(min(current_progress, 1.0))
                time.sleep(0.1) # Nghỉ xíu để tránh spam API quá gắt
            
            status.update(label="✅ AI Assets Loaded!", state="complete", expanded=False)

# ==============================================================================
# 1. NEON UI CSS (GIAO DIỆN BẮT MẮT)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
    * { font-family: 'Outfit', sans-serif !important; }

    /* 1. DARK NEON BACKGROUND */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(15, 15, 30) 0%, rgb(30, 30, 50) 90.2%);
        color: #fff;
    }
    
    /* 2. CARD DESIGN (HÌNH ẢNH TO & ĐẸP) */
    .scenario-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        overflow: hidden; /* Để bo góc ảnh */
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 20px;
        backdrop-filter: blur(5px);
    }
    .scenario-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 0 20px rgba(0, 210, 255, 0.4);
        border-color: #00d2ff;
    }
    
    /* Phần chứa ảnh trong card */
    .card-img {
        width: 100%;
        height: 180px;
        background-size: cover;
        background-position: center;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    .card-content { padding: 15px; }
    
    /* 3. TYPOGRAPHY */
    h1 {
        background: linear-gradient(to right, #00c6ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    h3 { margin-top: 0 !important; font-size: 1.2rem !important; }
    p { color: #cbd5e1 !important; font-size: 0.9rem !important; }

    /* 4. BUTTONS */
    .stButton button {
        background: linear-gradient(90deg, #FDBB2D 0%, #22C1C3 100%);
        color: #000 !important;
        border: none;
        font-weight: 800 !important;
        text-transform: uppercase;
        border-radius: 8px;
        padding: 12px 24px;
        box-shadow: 0 4px 15px rgba(34, 193, 195, 0.4);
        transition: 0.3s;
    }
    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 25px rgba(34, 193, 195, 0.7);
        color: #fff !important;
    }

    /* 5. CHAT BUBBLES */
    .chat-container {
        background: rgba(0,0,0,0.4);
        border-left: 5px solid #FDBB2D;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
    }
    .dialogue { font-size: 1.3rem; font-style: italic; color: #fff; }
    
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DATASET (11 KỊCH BẢN)
# ==============================================================================
INITIAL_DATA = {
    "SC_FNB_01": {
        "title": "F&B: Foreign Object", "desc": "Hair in soup situation.", "difficulty": "Hard",
        "customer": {"name": "Jade", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Jade", "traits": ["Picky"]},
        "steps": {
            "start": { "text": "There's a hair in my soup! Disgusting!", "choices": {"A": "Deny", "B": "Apologize"}, "consequences": {"A": {"next": "lose", "change": -40, "analysis": "❌ Denial"}, "B": {"next": "step_2", "change": +10, "analysis": "✅ Action"}} },
            "step_2": { "text": "I lost my appetite.", "choices": {"A": "Force eat", "B": "Offer Dessert"}, "consequences": {"A": {"next": "lose", "change": -10, "analysis": "⚠️ Force"}, "B": {"next": "win", "change": +40, "analysis": "✅ Nice"}} },
            "win": {"type": "WIN", "title": "SAVED", "text": "She is happy.", "score": 100},
            "lose": {"type": "LOSE", "title": "FAILED", "text": "Bad review.", "score": 40}
        }
    },
    "SC_HOTEL_01": {
        "title": "Hotel: Overbooked", "desc": "Honeymoon suite missing.", "difficulty": "Very Hard",
        "customer": {"name": "Mike", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Mike", "traits": ["Tired"]},
        "steps": {
            "start": { "text": "Where is my Ocean View?!", "choices": {"A": "System Error", "B": "My Fault"}, "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Blame"}, "B": {"next": "step_2", "change": +20, "analysis": "✅ Own it"}} },
            "step_2": { "text": "Fix this now!", "choices": {"A": "Breakfast", "B": "Suite Upgrade"}, "consequences": {"A": {"next": "lose", "change": -10, "analysis": "⚠️ Small"}, "B": {"next": "win", "change": +50, "analysis": "🏆 Hero"}} },
            "win": {"type": "WIN", "title": "DREAM", "text": "Upgrade loved.", "score": 100},
            "lose": {"type": "LOSE", "title": "LEFT", "text": "Walked out.", "score": 0}
        }
    },
    "SC_TECH_01": { "title": "IT: Internet Down", "desc": "Meeting interrupted.", "difficulty": "Medium", "customer": {"name": "Ken", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Ken", "traits": ["Urgent"]}, "steps": { "start": {"text":"Net down!","choices":{"A":"Restart","B":"Check"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"FIXED", "text":"Fixed.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Lost.", "score":0} } },
    "SC_RETAIL_01": { "title": "Retail: Broken Item", "desc": "VIP vase broken.", "difficulty": "Hard", "customer": {"name": "Lan", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Lan", "traits": ["VIP"]}, "steps": { "start": {"text":"Broken!","choices":{"A":"Refund","B":"Replace"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"FIXED", "text":"Fixed.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Lost.", "score":0} } },
    "SC_ECOMM_01": { "title": "E-comm: Lost Pkg", "desc": "Delivery missing.", "difficulty": "Medium", "customer": {"name": "Tom", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Tom", "traits": ["Anxious"]}, "steps": { "start": {"text":"Missing!","choices":{"A":"Wait","B":"Check"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"FIXED", "text":"Fixed.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Lost.", "score":0} } },
    "SC_BANK_01": { "title": "Bank: Card Eaten", "desc": "ATM swallowed card.", "difficulty": "Hard", "customer": {"name": "Eve", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Eve", "traits": ["Old"]}, "steps": { "start": {"text":"My card!","choices":{"A":"Wait","B":"Help"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"FIXED", "text":"Fixed.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Lost.", "score":0} } },
    "SC_AIRLINE_01": { "title": "Airline: Cancelled", "desc": "Flight cancelled.", "difficulty": "Very Hard", "customer": {"name": "Dave", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Dave", "traits": ["Panic"]}, "steps": { "start": {"text":"Cancelled!","choices":{"A":"Sorry","B":"Rebook"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"FIXED", "text":"Fixed.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Lost.", "score":0} } },
    "SC_SPA_01": { "title": "Spa: Allergy", "desc": "Face burning.", "difficulty": "Hard", "customer": {"name": "Chloe", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Chloe", "traits": ["Pain"]}, "steps": { "start": {"text":"Ouch!","choices":{"A":"Ignore","B":"Ice"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"FIXED", "text":"Fixed.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Lost.", "score":0} } },
    "SC_SAAS_01": { "title": "SaaS: Data Loss", "desc": "Deleted data.", "difficulty": "Hard", "customer": {"name": "Sarah", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah", "traits": ["Angry"]}, "steps": { "start": {"text":"Gone!","choices":{"A":"Oops","B":"Restore"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"FIXED", "text":"Fixed.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Lost.", "score":0} } },
    "SC_REALESTATE_01": { "title": "Real Estate: Mold", "desc": "Moldy apartment.", "difficulty": "Very Hard", "customer": {"name": "Chen", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Chen", "traits": ["Rich"]}, "steps": { "start": {"text":"Mold!","choices":{"A":"Clean","B":"Move"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"FIXED", "text":"Fixed.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Lost.", "score":0} } },
    "SC_LOGISTICS_01": { "title": "Logistics: Broken", "desc": "Broken gear.", "difficulty": "Very Hard", "customer": {"name": "Rob", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Rob", "traits": ["Mad"]}, "steps": { "start": {"text":"Broken!","choices":{"A":"Claim","B":"Truck"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"FIXED", "text":"Fixed.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Lost.", "score":0} } }
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

ALL_SCENARIOS = load_data()

# --- PRELOAD AI IMAGES (THE MAGIC STEP) ---
preload_images(ALL_SCENARIOS)

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ Service Hero")
    st.caption("AI-Powered | Neon Edition")
    menu = st.radio("MENU", ["DASHBOARD", "CREATE"])
    st.divider()
    if st.button("🔄 REGENERATE IMAGES"):
        # Xóa cache để AI tạo bộ ảnh mới
        st.session_state.thumbnails = {}
        st.experimental_rerun()

# --- DASHBOARD ---
if menu == "DASHBOARD":
    if st.session_state.current_scenario is None:
        st.title("MISSION CONTROL 🚀")
        
        if 'player_name' not in st.session_state: st.session_state.player_name = ""
        if not st.session_state.player_name:
            st.info("Identify yourself:")
            st.session_state.player_name = st.text_input("CODENAME:")
            if not st.session_state.player_name: st.stop()
        else:
            c1, c2 = st.columns([3, 1])
            c1.success(f"ONLINE: **{st.session_state.player_name}**")
            if c2.button("LOGOUT"): 
                st.session_state.player_name = ""
                st.rerun()

        with st.expander("🏆 LEADERBOARD"):
            show_leaderboard()
            
        st.divider()
        st.subheader("SELECT A MISSION")
        
        cols = st.columns(2)
        idx = 0
        for key, val in ALL_SCENARIOS.items():
            with cols[idx % 2]:
                # Lấy ảnh từ cache (đã được tạo bởi AI lúc khởi động)
                img_src = st.session_state.thumbnails.get(key, "https://placehold.co/800x500")
                
                # Render Card bằng HTML để chèn ảnh Background đẹp
                st.markdown(f"""
                <div class="scenario-card">
                    <div class="card-img" style="background-image: url('{img_src}');"></div>
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
        
        # Lấy ảnh đại diện của scenario (từ cache) cho đồng bộ
        main_img = st.session_state.thumbnails.get(s_key)
        
        with st.sidebar:
            st.divider()
            if st.button("❌ ABORT", use_container_width=True):
                st.session_state.current_scenario = None
                st.rerun()
            
            cust = scenario['customer']
            st.image(cust['avatar'], width=80)
            st.markdown(f"**TARGET: {cust['name']}**")
            
            p = st.session_state.patience
            color = "#00d2ff" if p > 50 else "#ff0080"
            st.markdown(f"**PATIENCE:** <span style='color:{color}'>{p}%</span>", unsafe_allow_html=True)
            st.progress(p/100)

        if "type" in step_data: # End
            st.title(step_data['title'])
            st.image(main_img, use_container_width=True)
            
            # Kết quả
            res_color = "#00ff7f" if step_data['type'] == 'WIN' else "#ff005f"
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.1); border:2px solid {res_color}; padding:20px; border-radius:15px; color:{res_color}; text-align:center;">
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
            st.image(main_img, use_container_width=True)
            
            st.markdown(f"""
            <div class="chat-container">
                <div class="customer-label">🗣️ {cust['name'].upper()} SAYS:</div>
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
    st.header("BUILDER")
    st.info("Demo Mode")
