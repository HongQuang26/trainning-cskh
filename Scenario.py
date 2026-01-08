import streamlit as st
import json
import os
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import urllib.parse
import google.generativeai as genai
import random

# ==============================================================================
# 0. CẤU HÌNH & KHỞI TẠO
# ==============================================================================
GEMINI_API_KEY = "AIzaSyBCPg9W5dvvNygm4KEM-gbn9_wPnvfUsrI"

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

# --- KHO ẢNH DỰ PHÒNG ---
BACKUP_IMAGES = {
    "F&B": ["https://images.unsplash.com/photo-1572802419224-296b0aeee0d9?q=80&w=1000", "https://images.unsplash.com/photo-1559339352-11d035aa65de?q=80&w=1000", "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=1000"],
    "HOTEL": ["https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1000", "https://images.unsplash.com/photo-1582719508461-905c673771fd?q=80&w=1000", "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?q=80&w=1000"],
    "OFFICE": ["https://images.unsplash.com/photo-1497215728101-856f4ea42174?q=80&w=1000", "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?q=80&w=1000", "https://images.unsplash.com/photo-1531403009284-440f080d1e12?q=80&w=1000"],
    "RETAIL": ["https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=1000", "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?q=80&w=1000"],
    "GENERAL": ["https://images.unsplash.com/photo-1521791136064-7986c2920216?q=80&w=1000"]
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
        except: pass
    images = BACKUP_IMAGES.get(category_key, BACKUP_IMAGES["GENERAL"])
    idx = len(step_text) % len(images)
    return images[idx]

# ==============================================================================
# 1. CSS & STYLE
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&family=Great+Vibes&display=swap');
    * { font-family: 'Outfit', sans-serif !important; }
    .stApp { background: radial-gradient(circle at 10% 20%, rgb(20, 20, 35) 0%, rgb(40, 40, 60) 90%); color: #fff; }
    [data-testid="stSidebar"] { background-color: rgba(15, 15, 30, 0.95); border-right: 1px solid rgba(255,255,255,0.1); }
    .scenario-card { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; margin-bottom: 20px; transition: 0.3s; }
    .scenario-card:hover { transform: translateY(-5px); border-color: #00d2ff; box-shadow: 0 10px 30px rgba(0, 210, 255, 0.2); }
    .card-img { width: 100%; height: 180px; object-fit: cover; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .chat-container { background: rgba(0, 0, 0, 0.3); border-left: 5px solid #FDBB2D; padding: 25px; border-radius: 12px; margin: 20px 0; }
    .customer-label { color: #FDBB2D; font-weight: bold; }
    .dialogue { font-size: 1.4rem; font-style: italic; margin-top: 5px; }
    .stButton button { background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%); color: white !important; font-weight: bold; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); }
    .stButton button:hover { background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%); color: black !important; border: none; transform: scale(1.02); }
    .leaderboard-container { background: rgba(0,0,0,0.2); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); }
    
    /* CERTIFICATE */
    .certificate-box { background: #fff; color: #111; padding: 40px; border-radius: 10px; border: 10px solid #FDBB2D; text-align: center; margin-top: 20px; box-shadow: 0 0 50px rgba(253, 187, 45, 0.5); }
    .cert-title { font-family: 'Great Vibes', cursive !important; font-size: 60px; color: #d4af37; }
    .cert-name { font-size: 40px; font-weight: 900; color: #000; border-bottom: 2px solid #d4af37; display: inline-block; padding: 0 20px; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DATA
# ==============================================================================
INITIAL_DATA = {
    "SC_FNB": { "title": "F&B: Hair in Soup", "desc": "Customer found hair in food.", "difficulty": "HARD", "category": "F&B", "skill": "Đồng Cảm", "cover": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=800", "customer": {"name": "Jade", "traits": ["Picky"], "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Jade"}, "steps": { "start": {"text": "There's hair in my soup!", "choices": {"A":"Deny", "B":"Apologize"}, "consequences": {"A":{"next":"lose","change":-40,"analysis":"Bad"}, "B":{"next":"step2","change":10,"analysis":"Good"}}}, "step2": {"text": "I'm leaving!", "choices": {"A":"Let go", "B":"Dessert"}, "consequences": {"A":{"next":"lose","change":-10,"analysis":"Lost"}, "B":{"next":"win","change":40,"analysis":"Saved"}}}, "win": {"type":"WIN", "title":"SAVED", "text":"Happy.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Bad.", "score":40}} },
    "SC_HOTEL": { "title": "Hotel: Overbooked", "desc": "No room for honeymoon.", "difficulty": "EXTREME", "category": "HOTEL", "skill": "Thương Lượng", "cover": "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=800", "customer": {"name": "Mike", "traits": ["Tired"], "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Mike"}, "steps": { "start": {"text": "No room?", "choices": {"A":"Error", "B":"My Fault"}, "consequences": {"A":{"next":"lose","change":-30,"analysis":"Excuses"}, "B":{"next":"step2","change":20,"analysis":"Ownership"}}}, "step2": {"text": "Fix it!", "choices": {"A":"Breakfast", "B":"Upgrade"}, "consequences": {"A":{"next":"lose","change":-10,"analysis":"Cheap"}, "B":{"next":"win","change":50,"analysis":"Hero"}}}, "win": {"type":"WIN", "title":"DREAM", "text":"Loved it.", "score":100}, "lose": {"type":"LOSE", "title":"LEFT", "text":"Walked out.", "score":0}} },
    "SC_TECH": { "title": "IT: Net Down", "desc": "Meeting interrupted.", "difficulty": "MEDIUM", "category": "OFFICE", "skill": "Giải Quyết VĐ", "cover": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=800", "customer": {"name": "Ken", "traits": ["Urgent"], "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Ken"}, "steps": { "start": {"text":"Net down!","choices":{"A":"Restart","B":"Check"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"FIXED", "text":"Online.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Churn.", "score":0} } },
    "SC_RETAIL": { "title": "Retail: Broken", "desc": "Vase arrived broken.", "difficulty": "HARD", "category": "RETAIL", "skill": "Kiên Nhẫn", "cover": "https://images.unsplash.com/photo-1596496050844-461dc5b7263f?q=80&w=800", "customer": {"name": "Lan", "traits": ["VIP"], "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Lan"}, "steps": { "start": {"text":"Broken!","choices":{"A":"Refund","B":"Replace"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"FIXED", "text":"Replaced.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Lost.", "score":0} } },
    "SC_ECOMM": { "title": "E-comm: Lost", "desc": "Package missing.", "difficulty": "MEDIUM", "category": "RETAIL", "skill": "Trách Nhiệm", "cover": "https://images.unsplash.com/photo-1566576912321-d58ba2188273?q=80&w=800", "customer": {"name": "Tom", "traits": ["Anxious"], "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Tom"}, "steps": { "start": {"text":"Missing!","choices":{"A":"Wait","B":"Check"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"FOUND", "text":"Got it.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Refund.", "score":0} } },
    "SC_BANK": { "title": "Bank: Card Eaten", "desc": "ATM took card.", "difficulty": "HARD", "category": "OFFICE", "skill": "Tuân Thủ", "cover": "https://images.unsplash.com/photo-1601597111158-2fceff292cdc?q=80&w=800", "customer": {"name": "Eve", "traits": ["Old"], "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Eve"}, "steps": { "start": {"text":"My card!","choices":{"A":"Wait","B":"Help"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"SAFE", "text":"Solved.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Left.", "score":0} } },
    "SC_AIRLINE": { "title": "Airline: Cancel", "desc": "Flight cancelled.", "difficulty": "EXTREME", "category": "HOTEL", "skill": "Chịu Áp Lực", "cover": "https://images.unsplash.com/photo-1436491865332-7a61a14527c5?q=80&w=800", "customer": {"name": "Dave", "traits": ["Panic"], "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Dave"}, "steps": { "start": {"text":"Cancelled?!","choices":{"A":"Sorry","B":"Rebook"},"consequences":{"A":{"next":"lose","change":-20,"analysis":"Bad"},"B":{"next":"win","change":20,"analysis":"Good"}}}, "win": {"type":"WIN", "title":"FLYING", "text":"Rebooked.", "score":100}, "lose": {"type":"LOSE", "title":"FAIL", "text":"Missed.", "score":0} } }
}

DB_FILE = "scenarios.json"
HISTORY_FILE = "score_history.csv"

# ==============================================================================
# 4. APP LOGIC
# ==============================================================================
def load_data(): return INITIAL_DATA

def save_score(player, scenario, score, outcome, skill):
    new_row = {"Time": datetime.now().strftime("%Y-%m-%d %H:%M"), "Player": player, "Scenario": scenario, "Score": score, "Outcome": outcome, "Skill": skill}
    if os.path.exists(HISTORY_FILE):
        df = pd.read_csv(HISTORY_FILE)
    else:
        df = pd.DataFrame(columns=["Time", "Player", "Scenario", "Score", "Outcome", "Skill"])
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(HISTORY_FILE, index=False)

def draw_radar_chart(player_name):
    if not os.path.exists(HISTORY_FILE): return None
    df = pd.read_csv(HISTORY_FILE)
    player_df = df[df['Player'] == player_name]
    if player_df.empty or 'Skill' not in player_df.columns: return None
    
    skill_scores = player_df.groupby('Skill')['Score'].mean()
    if skill_scores.empty: return None
    
    categories = skill_scores.index.tolist()
    values = skill_scores.values.tolist()
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='#00d2ff', alpha=0.25)
    ax.plot(angles, values, color='#00d2ff', linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10, color='white')
    
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')
    ax.spines['polar'].set_color('rgba(255,255,255,0.2)')
    ax.tick_params(axis='x', colors='white')
    return fig

# SESSION STATE
if 'current_scenario' not in st.session_state: st.session_state.current_scenario = None
if 'step_img_cache' not in st.session_state: st.session_state.step_img_cache = {}

ALL_SCENARIOS = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ SERVICE HERO")
    menu = st.radio("NAVIGATION", ["DASHBOARD", "CREATE"])
    st.divider()
    
    # --- TÍNH NĂNG RESET LEADERBOARD ---
    if st.button("🗑️ RESET LEADERBOARD"):
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
            st.success("Đã xóa dữ liệu bảng xếp hạng!")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("Chưa có dữ liệu để xóa.")
            
    if st.button("🔄 REFRESH SYSTEM"):
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
            c1, c2 = st.columns([2, 1])
            c1.success(f"AGENT ONLINE: **{st.session_state.player_name}**")
            if c2.button("LOGOUT"): 
                st.session_state.player_name = ""
                st.rerun()

            # BIỂU ĐỒ NĂNG LỰC
            st.markdown("### 📊 HỒ SƠ NĂNG LỰC")
            chart = draw_radar_chart(st.session_state.player_name)
            if chart: st.pyplot(chart, use_container_width=False)
            else: st.caption("Chưa có dữ liệu. Hãy chơi để hệ thống phân tích.")

        # Leaderboard
        st.divider()
        st.subheader("🏆 ELITE AGENTS")
        if os.path.exists(HISTORY_FILE):
            df = pd.read_csv(HISTORY_FILE)
            if not df.empty:
                st.markdown('<div class="leaderboard-container">', unsafe_allow_html=True)
                st.dataframe(df.sort_values(by="Score", ascending=False).head(10), use_container_width=True, hide_index=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else: st.info("No data yet.")
        else: st.info("No history.")
            
        st.divider()
        st.subheader("ACTIVE MISSIONS")
        
        cols = st.columns(2)
        idx = 0
        for key, val in ALL_SCENARIOS.items():
            with cols[idx % 2]:
                img_src = val['cover']
                st.markdown(f"""
                <div class="scenario-card">
                    <img src="{img_src}" class="card-img">
                    <div class="card-content">
                        <h3>{val['title']}</h3>
                        <p>{val['desc']}</p>
                        <span style="background:#00d2ff; color:#000; padding:2px 8px; border-radius:4px; font-weight:bold;">Skill: {val.get('skill', 'General')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"ENGAGE", key=key, use_container_width=True):
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
        
        cache_key = f"{s_key}_{step_id}"
        if cache_key not in st.session_state.step_img_cache:
            st.session_state.step_img_cache[cache_key] = get_smart_image(scenario['title'], step_data.get('text', ''), scenario.get('category', 'GENERAL'))
        
        current_img = st.session_state.step_img_cache[cache_key]
        
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

        if "type" in step_data: # End
            st.title(step_data['title'])
            st.image(current_img, use_container_width=True)
            
            color = "#00ff7f" if step_data['type'] == 'WIN' else "#ff005f"
            st.markdown(f"""
            <div style="border:2px solid {color}; padding:20px; border-radius:15px; color:{color}; text-align:center; background:rgba(0,0,0,0.3);">
                <h2>{step_data['text']}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            if step_data['type'] == 'WIN': 
                st.balloons()
                if 'show_cert' not in st.session_state: st.session_state.show_cert = False
                if st.button("🏅 NHẬN CHỨNG CHỈ", use_container_width=True):
                    st.session_state.show_cert = True
                
                if st.session_state.show_cert:
                    st.markdown(f"""
                    <div class="certificate-box">
                        <div class="cert-title">Certificate of Excellence</div>
                        <div class="cert-name">{st.session_state.player_name}</div>
                        <div style="color:#000;">For outstanding performance in: <b>{scenario['title']}</b></div>
                    </div>
                    """, unsafe_allow_html=True)

            st.metric("SCORE", step_data['score'])
            if 'saved' not in st.session_state:
                save_score(st.session_state.player_name, scenario['title'], step_data['score'], step_data['type'], scenario.get('skill', 'General'))
                st.session_state.saved = True
            
            if st.button("RETURN TO BASE", use_container_width=True):
                st.session_state.current_scenario = None
                if 'saved' in st.session_state: del st.session_state.saved
                if 'show_cert' in st.session_state: del st.session_state.show_cert
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
                        st.session_state.history.append({"step": step_data['text'], "choice": v})
                        st.rerun()
                idx += 1

elif menu == "CREATE":
    st.header("BUILDER")
    st.info("Demo Mode")
