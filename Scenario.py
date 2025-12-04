import streamlit as st
import json
import os
import time

# ==============================================================================
# 1. CONFIGURATION & UI
# ==============================================================================
st.set_page_config(
    page_title="Training Master V4",
    page_icon="💎",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stButton button {
        border-radius: 12px; height: auto; min-height: 50px;
        font-weight: 600; border: 1px solid #e0e0e0;
    }
    .stButton button:hover {
        border-color: #2E86C1; color: #2E86C1; background-color: #f8f9fa;
    }
    .chat-container {
        background-color: #ffffff; padding: 25px; border-radius: 20px;
        border-left: 8px solid #2E86C1; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    .profile-card {
        background: #f8f9fa; padding: 20px; border-radius: 15px; border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DATA MANAGEMENT (JSON SYSTEM)
# ==============================================================================
DB_FILE = "scenarios.json"

# Default Scenarios (Seed Data)
DEFAULT_DATA = {
    "SC_DEMO_01": {
        "title": "Retail: Broken Item",
        "desc": "Customer received a broken product.",
        "difficulty": "Medium",
        "customer": {
            "name": "Ms. Sarah", "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=400",
            "traits": ["Angry", "Urgent"], "spending": "VIP Member"
        },
        "steps": {
            "start": {
                "patience": 30,
                "img": "https://images.unsplash.com/photo-1596496050844-461dc5b7263f?q=80&w=800",
                "text": "My order arrived completely broken! This is unacceptable!",
                "choices": {
                    "A": "Empathy: 'I am so sorry! I will replace it immediately.'",
                    "B": "Policy: 'Please send a photo first.'"
                },
                "consequences": {
                    "A": {"next": "win", "change": 50, "analysis": "✅ Great empathy!"},
                    "B": {"next": "lose", "change": -30, "analysis": "❌ Too rigid for an angry customer."}
                }
            },
            "win": {"type": "WIN", "title": "SUCCESS", "text": "Customer is happy with the quick replacement.", "img": "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?q=80&w=800", "score": 100},
            "lose": {"type": "LOSE", "title": "FAILED", "text": "Customer felt distrusted and left.", "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800", "score": 0}
        }
    }
}

def load_data():
    """Load scenarios from JSON. If not exist, create default."""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_DATA, f, ensure_ascii=False, indent=4)
        return DEFAULT_DATA
    
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(new_data):
    """Save scenarios to JSON"""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)

def delete_scenario(key):
    data = load_data()
    if key in data:
        del data[key]
        save_data(data)
        return True
    return False

# ==============================================================================
# 3. SCENARIO CREATOR LOGIC
# ==============================================================================
def create_new_scenario_ui():
    st.header("🛠️ Create New Scenario")
    st.info("Fill in the form below to generate a simple 1-step scenario (Start -> Win/Lose).")
    
    with st.form("creator_form"):
        c1, c2 = st.columns(2)
        with c1:
            title = st.text_input("Scenario Title", placeholder="e.g., Late Delivery")
            desc = st.text_input("Short Description", placeholder="e.g., Driver is late 2 hours")
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Very Hard"])
        with c2:
            cust_name = st.text_input("Customer Name", placeholder="e.g., Mr. John")
            cust_trait = st.text_input("Customer Traits", placeholder="e.g., Impatient, Rich")
            cust_spend = st.text_input("Customer Spending", placeholder="e.g., High Spender")

        st.divider()
        st.subheader("📍 The Situation")
        start_text = st.text_area("What does the customer shout first?", placeholder="e.g., Where is my pizza?!")
        
        st.divider()
        st.subheader("👉 The Choices")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("### ✅ Option A (Correct Choice)")
            opt_a_text = st.text_input("Button Text (A)", placeholder="Apologize & Refund")
            opt_a_analysis = st.text_input("Why is this good?", placeholder="Empathy wins trust.")
            opt_a_result = st.text_input("Ending Message (A)", placeholder="Customer accepted the refund happily.")
            
        with col_b:
            st.markdown("### ❌ Option B (Wrong Choice)")
            opt_b_text = st.text_input("Button Text (B)", placeholder="Argue with customer")
            opt_b_analysis = st.text_input("Why is this bad?", placeholder="Arguments lose customers.")
            opt_b_result = st.text_input("Ending Message (B)", placeholder="Customer posted a bad review.")

        submitted = st.form_submit_button("💾 Save Scenario")
        
        if submitted:
            if not title or not start_text:
                st.error("Please fill in at least the Title and Situation text.")
            else:
                # Construct the JSON structure
                new_id = f"SC_CUSTOM_{int(time.time())}"
                new_entry = {
                    "title": title,
                    "desc": desc,
                    "difficulty": difficulty,
                    "customer": {
                        "name": cust_name,
                        "avatar": "https://images.unsplash.com/photo-1511367461989-f85a21fda167?q=80&w=400", # Default avatar
                        "traits": [cust_trait],
                        "spending": cust_spend
                    },
                    "steps": {
                        "start": {
                            "patience": 40,
                            "img": "https://images.unsplash.com/photo-1528642474493-1df4321024e1?q=80&w=800", # Default angry img
                            "text": start_text,
                            "choices": {
                                "A": opt_a_text,
                                "B": opt_b_text
                            },
                            "consequences": {
                                "A": {"next": "win", "change": 60, "analysis": f"✅ {opt_a_analysis}"},
                                "B": {"next": "lose", "change": -40, "analysis": f"❌ {opt_b_analysis}"}
                            }
                        },
                        "win": {"type": "WIN", "title": "SUCCESS", "text": opt_a_result, "img": "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?q=80&w=800", "score": 100},
                        "lose": {"type": "LOSE", "title": "FAILED", "text": opt_b_result, "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800", "score": 0}
                    }
                }
                
                # Load, Update, Save
                data = load_data()
                data[new_id] = new_entry
                save_data(data)
                st.success("Scenario created successfully! Go to 'Dashboard' to play it.")
                time.sleep(1)
                st.rerun()

# ==============================================================================
# 4. GAME ENGINE
# ==============================================================================
if 'current_scenario' not in st.session_state: st.session_state.current_scenario = None
if 'current_step' not in st.session_state: st.session_state.current_step = None
if 'patience_meter' not in st.session_state: st.session_state.patience_meter = 50
if 'history' not in st.session_state: st.session_state.history = []
if 'menu_option' not in st.session_state: st.session_state.menu_option = "Dashboard"

def reset_game():
    st.session_state.current_scenario = None
    st.session_state.current_step = None
    st.session_state.patience_meter = 50
    st.session_state.history = []

def make_choice(choice_key, step_data):
    consequence = step_data['consequences'][choice_key]
    st.session_state.current_step = consequence['next']
    st.session_state.patience_meter += consequence['change']
    st.session_state.patience_meter = max(0, min(100, st.session_state.patience_meter))
    st.session_state.history.append({
        "step": step_data['text'],
        "choice": step_data['choices'][choice_key],
        "analysis": consequence['analysis'],
        "change": consequence['change']
    })

# ==============================================================================
# 5. MAIN NAVIGATION & INTERFACE
# ==============================================================================

# Sidebar Menu
with st.sidebar:
    st.title("🎛️ Menu")
    menu = st.radio("Navigate", ["Dashboard", "🛠️ Create New Scenario"])
    
    st.divider()
    st.caption("Training Master v4.0 | Author HQuang")

# LOAD DATA
ALL_SCENARIOS = load_data()

# --- SCENARIO CREATOR MODE ---
if menu == "🛠️ Create New Scenario":
    reset_game()
    create_new_scenario_ui()

# --- DASHBOARD / GAMEPLAY MODE ---
elif menu == "Dashboard":
    
    # DASHBOARD VIEW
    if st.session_state.current_scenario is None:
        st.title("🎓 TRAINING DASHBOARD")
        st.caption(f"Total Scenarios: {len(ALL_SCENARIOS)}")
        st.divider()
        
        cols = st.columns(2)
        count = 0
        for key, data in ALL_SCENARIOS.items():
            with cols[count % 2]:
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.subheader(data['title'])
                    with c2:
                        # Delete Button
                        if st.button("🗑️", key=f"del_{key}"):
                            delete_scenario(key)
                            st.rerun()
                            
                    st.write(f"📝 {data['desc']}")
                    st.write(f"🔥 Difficulty: **{data['difficulty']}**")
                    
                    if st.button(f"🚀 Start", key=f"btn_{key}", use_container_width=True):
                        st.session_state.current_scenario = key
                        st.session_state.current_step = 'start'
                        st.session_state.patience_meter = data['steps']['start']['patience']
                        st.session_state.history = []
                        st.rerun()
            count += 1
            
    # GAMEPLAY VIEW
    else:
        s_key = st.session_state.current_scenario
        
        # Check if scenario still exists (in case of deletion)
        if s_key not in ALL_SCENARIOS:
            reset_game()
            st.rerun()
            
        s_data = ALL_SCENARIOS[s_key]
        step_key = st.session_state.current_step
        step_data = s_data['steps'][step_key]
        
        # In-Game Sidebar
        with st.sidebar:
            st.divider()
            st.button("❌ Quit Scenario", on_click=reset_game, use_container_width=True)
            st.divider()
            
            cust = s_data['customer']
            st.markdown(f"<div style='text-align:center'><img src='{cust['avatar']}' style='width:100px;border-radius:50%;border:3px solid #2E86C1'></div>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center'>{cust['name']}</h3>", unsafe_allow_html=True)
            st.write(f"**Traits:** {', '.join(cust['traits'])}")
            
            # Patience Meter
            patience = st.session_state.patience_meter
            st.markdown(f"### 🌡️ Patience: {patience}/100")
            color_hex = "#28a745" if patience > 70 else ("#ffc107" if patience > 30 else "#dc3545")
            st.markdown(f"""
            <div style="width:100%;background-color:#e9ecef;border-radius:10px;height:20px;">
                <div style="width:{patience}%;background-color:{color_hex};height:20px;border-radius:10px;transition:width 0.5s;"></div>
            </div>""", unsafe_allow_html=True)

        # Main Content
        if "type" in step_data: # END SCREEN
            st.markdown(f"# {step_data['title']}")
            c1, c2 = st.columns([1, 1.5], gap="large")
            with c1: st.image(step_data['img'], use_container_width=True)
            with c2:
                if step_data['type'] == 'WIN':
                    st.success(f"### {step_data['text']}")
                    st.balloons()
                else:
                    st.error(f"### {step_data['text']}")
                st.metric("Score", f"{step_data['score']}/100")
                if st.button("🔄 Play Again", use_container_width=True):
                    st.session_state.current_step = 'start'
                    st.session_state.patience_meter = 50
                    st.session_state.history = []
                    st.rerun()
            
            st.divider()
            st.subheader("🕵️ ANALYSIS")
            for item in st.session_state.history:
                icon = "✅" if item['change'] > 0 else "❌"
                bg = "#d4edda" if item['change'] > 0 else "#f8d7da"
                st.markdown(f"<div style='background:{bg};padding:10px;border-radius:5px;margin-bottom:5px;'><b>{icon} Analysis:</b> {item['analysis']}</div>", unsafe_allow_html=True)

        else: # PLAYING SCREEN
            st.subheader(f"📍 {s_data['title']}")
            c1, c2 = st.columns([1.5, 2], gap="large")
            with c1: st.image(step_data['img'], use_container_width=True)
            with c2:
                st.markdown(f"""<div class="chat-container"><div class="customer-name">🗣️ {cust['name']} says:</div><div class="dialogue">"{step_data['text']}"</div></div>""", unsafe_allow_html=True)
                st.write("#### 👉 Your Response:")
                for k, v in step_data['choices'].items():
                    if st.button(f"{k}. {v}", use_container_width=True):
                        make_choice(k, step_data)
                        st.rerun()
