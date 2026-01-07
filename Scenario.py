import streamlit as st
import json
import os
import time
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# ==============================================================================
# 1. CẤU HÌNH & GIAO DIỆN (CONFIGURATION & UI)
# ==============================================================================
st.set_page_config(
    page_title="Service Hero Pro",
    page_icon="🦸‍♂️",
    layout="wide"
)

# Custom CSS cho giao diện đẹp hơn
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
    .certificate-box {
        border: 5px double #D4AF37; padding: 20px; text-align: center;
        background: #FFF8DC; color: #5D4037; border-radius: 10px; margin-top: 20px;
    }
    .metric-card {
        background-color: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DỮ LIỆU & HÀM HỖ TRỢ
# ==============================================================================
INITIAL_DATA = {
    "SC_FNB_01": {
        "title": "F&B: Dị vật trong món ăn",
        "desc": "Tóc trong súp. Giải quyết trong 3 bước.",
        "difficulty": "Hard",
        "customer": {"name": "Ms. Jade", "avatar": "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?q=80&w=400", "traits": ["Kỹ tính", "Reviewer"], "spending": "Khách mới"},
        "steps": {
            "start": { 
                "patience": 30, "img": "https://images.unsplash.com/photo-1533777857889-4be7c70b33f7?q=80&w=800",
                "text": "Quản lý đâu! Nhìn xem! Một sợi tóc dài trong súp của tôi! Các người cho tôi ăn rác đấy à?",
                "choices": {"A": "Phủ nhận: 'Không phải tóc nhân viên chúng tôi.'", "B": "Hành động: 'Tôi vô cùng xin lỗi! Tôi sẽ xử lý ngay.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -40, "analysis": "❌ Phủ nhận làm mất niềm tin ngay lập tức."}, "B": {"next": "step_2_wait", "change": +10, "analysis": "✅ Hành động ngay lập tức là chính xác."}}
            },
            "step_2_wait": { 
                "patience": 40, "img": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=800",
                "text": "(5 phút sau) Tôi hết muốn ăn rồi. Đợi lâu quá tôi mất cả hứng.",
                "choices": {"A": "Thuyết phục: 'Mời chị thử đi ạ, bếp trưởng làm riêng đấy.'", "B": "Chuyển hướng: 'Tôi hoàn toàn hiểu ạ. Tôi xin phép dọn món này đi. Tôi mời chị món tráng miệng nhé?'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Đừng ép khách ăn khi họ đang bực."}, "B": {"next": "step_3_bill", "change": +20, "analysis": "✅ Tôn trọng cảm xúc và đưa ra giải pháp thay thế."}}
            },
            "step_3_bill": { 
                "patience": 60, "img": "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?q=80&w=800",
                "text": "Thôi được. Mang hóa đơn ra đây.",
                "choices": {"A": "Giảm giá: 'Gửi chị hóa đơn giảm 10% ạ.'", "B": "Đền bù: 'Bữa tối nay nhà hàng xin mời. Và đây là voucher cho lần sau ạ.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ 10% là quá ít cho trải nghiệm tồi tệ."}, "B": {"next": "game_over_good", "change": +40, "analysis": "🏆 Đền bù vượt mong đợi biến thảm họa thành khoảnh khắc Wow."}}
            },
            "game_over_good": {"type": "WIN", "title": "KHÔI PHỤC NIỀM TIN", "text": "Cô ấy bất ngờ và tip cho nhân viên.", "img": "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?q=80&w=800", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "MẤT KHÁCH", "text": "Cô ấy để lại đánh giá 1 sao.", "img": "https://images.unsplash.com/photo-1522029916167-9c1a97aa3c24?q=80&w=800", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "THẢM HỌA", "text": "Video cãi nhau lan truyền.", "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800", "score": 0}
        }
    }
}

DB_FILE = "scenarios.json"
HISTORY_FILE = "score_history.csv"

def load_data(force_reset=False):
    if force_reset or not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(INITIAL_DATA, f, ensure_ascii=False, indent=4)
        return INITIAL_DATA.copy()
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        try: data = json.load(f)
        except: data = INITIAL_DATA.copy()
    updated = False
    for k, v in INITIAL_DATA.items():
        if k not in data:
            data[k] = v
            updated = True
    if updated: save_data(data)
    return data

def save_data(new_data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)

def delete_scenario(key):
    data = load_data()
    if key in data:
        del data[key]
        save_data(data)
        return True
    return False

def save_score(player_name, scenario_title, score, outcome):
    new_record = {
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Player": player_name,
        "Scenario": scenario_title,
        "Score": score,
        "Outcome": outcome
    }
    if os.path.exists(HISTORY_FILE):
        df = pd.read_csv(HISTORY_FILE)
    else:
        df = pd.DataFrame(columns=["Time", "Player", "Scenario", "Score", "Outcome"])
    new_df = pd.DataFrame([new_record])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(HISTORY_FILE, index=False)

# ==============================================================================
# 3. TÍNH NĂNG CAO CẤP: ADMIN & CERTIFICATE
# ==============================================================================
def render_certificate(player_name):
    """Tạo chứng chỉ HTML đơn giản để hiển thị"""
    cert_html = f"""
    <div class="certificate-box">
        <h1>🎖️ CHỨNG NHẬN HOÀN THÀNH 🎖️</h1>
        <p>Trao tặng cho đặc vụ xuất sắc:</p>
        <h2>{player_name}</h2>
        <p>Đã hoàn thành xuất sắc khóa huấn luyện Service Hero.</p>
        <p><i>Ngày cấp: {datetime.now().strftime("%d/%m/%Y")}</i></p>
    </div>
    """
    st.markdown(cert_html, unsafe_allow_html=True)
    st.balloons()

def admin_dashboard():
    """Trang quản trị viên cao cấp"""
    st.title("🔐 Admin Dashboard")
    
    # Kiểm tra mật khẩu
    password = st.text_input("Nhập mật khẩu quản trị:", type="password")
    if password != "admin123": # Mật khẩu mặc định
        st.warning("Vui lòng nhập mật khẩu để truy cập dữ liệu nhạy cảm.")
        st.stop()
    
    st.success("Đăng nhập thành công!")
    
    if not os.path.exists(HISTORY_FILE):
        st.info("Chưa có dữ liệu lịch sử để phân tích.")
        return

    df = pd.read_csv(HISTORY_FILE)
    
    # 1. Thống kê tổng quan (Metrics)
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Tổng lượt chơi", len(df))
    with c2: st.metric("Điểm trung bình", f"{df['Score'].mean():.1f}")
    with c3: st.metric("Tỷ lệ thắng", f"{(len(df[df['Outcome']=='WIN']) / len(df) * 100):.1f}%")
    
    st.divider()
    
    # 2. Biểu đồ phân tích (Charts)
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📊 Điểm số theo Nhân viên")
        # Nhóm theo nhân viên và tính điểm trung bình
        avg_score = df.groupby("Player")["Score"].mean().sort_values()
        st.bar_chart(avg_score, color="#2E86C1")
        
    with col_chart2:
        st.subheader("🥧 Tỷ lệ Thắng/Thua")
        outcome_counts = df['Outcome'].value_counts()
        # Vẽ biểu đồ tròn bằng matplotlib
        fig, ax = plt.subplots()
        ax.pie(outcome_counts, labels=outcome_counts.index, autopct='%1.1f%%', startangle=90, colors=['#2ecc71', '#e74c3c'])
        ax.axis('equal') 
        st.pyplot(fig)

    st.divider()
    
    # 3. Dữ liệu chi tiết & Tải về
    st.subheader("📂 Dữ liệu chi tiết")
    st.dataframe(df, use_container_width=True)
    
    # Nút tải file CSV
    with open(HISTORY_FILE, "rb") as file:
        st.download_button(
            label="📥 Tải xuống báo cáo (CSV)",
            data=file,
            file_name="service_hero_report.csv",
            mime="text/csv"
        )

# ==============================================================================
# 4. MAIN APP LOGIC
# ==============================================================================
def create_new_scenario_ui():
    st.header("🛠️ Tạo Kịch Bản Mới")
    with st.form("creator_form"):
        c1, c2 = st.columns(2)
        with c1:
            title = st.text_input("Tiêu đề")
            difficulty = st.selectbox("Độ khó", ["Dễ", "Trung bình", "Khó"])
        with c2:
            cust_name = st.text_input("Tên khách")
            cust_trait = st.text_input("Tính cách")
        
        st.divider()
        start_text = st.text_area("Tình huống mở đầu")
        
        c3, c4 = st.columns(2)
        with c3:
            st.write("✅ **Phương án đúng (A)**")
            opt_a = st.text_input("Nội dung A")
            res_a = st.text_input("Kết quả thắng")
        with c4:
            st.write("❌ **Phương án sai (B)**")
            opt_b = st.text_input("Nội dung B")
            res_b = st.text_input("Kết quả thua")
            
        if st.form_submit_button("Lưu kịch bản"):
            if title and start_text:
                new_id = f"SC_{int(time.time())}"
                new_entry = {
                    "title": title, "desc": "Kịch bản tự tạo", "difficulty": difficulty,
                    "customer": {"name": cust_name, "avatar": "", "traits": [cust_trait], "spending": "N/A"},
                    "steps": {
                        "start": {
                            "patience": 50, "img": "", "text": start_text,
                            "choices": {"A": opt_a, "B": opt_b},
                            "consequences": {
                                "A": {"next": "win", "change": 50, "analysis": "✅ Tốt"},
                                "B": {"next": "lose", "change": -50, "analysis": "❌ Kém"}
                            }
                        },
                        "win": {"type": "WIN", "title": "THẮNG", "text": res_a, "img": "", "score": 100},
                        "lose": {"type": "LOSE", "title": "THUA", "text": res_b, "img": "", "score": 0}
                    }
                }
                data = load_data()
                data[new_id] = new_entry
                save_data(data)
                st.success("Đã lưu!")
                time.sleep(1)
                st.rerun()

# --- STATE MANAGEMENT ---
if 'current_scenario' not in st.session_state: st.session_state.current_scenario = None
if 'current_step' not in st.session_state: st.session_state.current_step = None
if 'patience_meter' not in st.session_state: st.session_state.patience_meter = 50
if 'history' not in st.session_state: st.session_state.history = []
if 'player_name' not in st.session_state: st.session_state.player_name = ""

def reset_game():
    st.session_state.current_scenario = None
    st.session_state.current_step = None
    st.session_state.patience_meter = 50
    st.session_state.history = []

def make_choice(choice_key, step_data):
    consequence = step_data['consequences'][choice_key]
    st.session_state.current_step = consequence['next']
    st.session_state.patience_meter = max(0, min(100, st.session_state.patience_meter + consequence['change']))
    st.session_state.history.append({
        "step": step_data['text'],
        "choice": step_data['choices'][choice_key],
        "analysis": consequence['analysis'],
        "change": consequence['change']
    })

# --- MENU & NAVIGATION ---
ALL_SCENARIOS = load_data()

with st.sidebar:
    st.title("🎛️ Menu")
    menu = st.radio("Chọn chế độ", ["Học viên", "🛠️ Tạo Kịch Bản", "🔐 Quản trị viên (Admin)"])
    st.divider()
    if st.button("⚠️ Reset Dữ liệu gốc"):
        load_data(force_reset=True)
        st.success("Đã reset!")
        time.sleep(1)
        st.rerun()

# --- LOGIC CÁC TRANG ---
if menu == "🔐 Quản trị viên (Admin)":
    reset_game()
    admin_dashboard()

elif menu == "🛠️ Tạo Kịch Bản":
    reset_game()
    create_new_scenario_ui()

elif menu == "Học viên":
    # 1. Nhập tên
    if not st.session_state.player_name:
        st.title("🎓 Chào mừng đến khóa huấn luyện")
        st.info("Vui lòng nhập tên để hệ thống ghi nhận thành tích.")
        name_input = st.text_input("Họ và tên của bạn:", placeholder="Nguyễn Văn A...")
        if name_input:
            st.session_state.player_name = name_input
            st.rerun()
        st.stop()

    # 2. Dashboard Học viên
    if st.session_state.current_scenario is None:
        c1, c2 = st.columns([3, 1])
        with c1: st.title(f"Xin chào, {st.session_state.player_name} 👋")
        with c2: 
            if st.button("Đăng xuất"): 
                st.session_state.player_name = ""
                st.rerun()
        
        # --- Logic nhận chứng chỉ ---
        if os.path.exists(HISTORY_FILE):
            df_my = pd.read_csv(HISTORY_FILE)
            df_my = df_my[df_my['Player'] == st.session_state.player_name]
            if not df_my.empty:
                avg = df_my['Score'].mean()
                played = len(df_my)
                st.info(f"📊 Thành tích hiện tại: Đã chơi {played} ván - Điểm trung bình: {avg:.1f}")
                
                if avg >= 80 and played >= 1:
                    with st.expander("🎖️ BẠN CÓ PHẦN THƯỞNG! MỞ NGAY", expanded=True):
                        render_certificate(st.session_state.player_name)
        # ----------------------------

        st.divider()
        st.subheader("Chọn tình huống luyện tập:")
        cols = st.columns(2)
        idx = 0
        for key, data in ALL_SCENARIOS.items():
            with cols[idx % 2]:
                with st.container(border=True):
                    st.subheader(data['title'])
                    st.markdown(f"*{data['desc']}*")
                    level_color = "red" if data['difficulty'] == "Hard" else "blue"
                    st.markdown(f":{level_color}[Level: {data['difficulty']}]")
                    if st.button(f"🔥 Bắt đầu", key=key, use_container_width=True):
                        st.session_state.current_scenario = key
                        st.session_state.current_step = 'start'
                        st.session_state.patience_meter = data['steps']['start']['patience']
                        st.session_state.history = []
                        if 'score_saved' in st.session_state: del st.session_state.score_saved
                        st.rerun()
            idx += 1

    # 3. Màn hình Chơi Game
    else:
        s_key = st.session_state.current_scenario
        if s_key not in ALL_SCENARIOS: reset_game(); st.rerun()
        s_data = ALL_SCENARIOS[s_key]
        step_data = s_data['steps'][st.session_state.current_step]

        # Sidebar thông tin
        with st.sidebar:
            st.divider()
            st.button("❌ Thoát", on_click=reset_game, use_container_width=True)
            cust = s_data['customer']
            if cust.get('avatar'): st.image(cust['avatar'], width=100)
            st.write(f"**{cust['name']}**")
            st.progress(st.session_state.patience_meter / 100, text=f"Kiên nhẫn: {st.session_state.patience_meter}%")

        # Xử lý nội dung
        if "type" in step_data: # Kết thúc
            st.markdown(f"# {step_data['title']}")
            
            # Lưu điểm
            if 'score_saved' not in st.session_state:
                save_score(st.session_state.player_name, s_data['title'], step_data['score'], step_data['type'])
                st.session_state.score_saved = True
            
            # Hiển thị kết quả
            c1, c2 = st.columns([1, 2])
            with c1: 
                if step_data.get('img'): st.image(step_data['img'])
            with c2:
                if step_data['type'] == 'WIN': 
                    st.success(step_data['text'])
                    st.balloons()
                else: 
                    st.error(step_data['text'])
                st.metric("ĐIỂM SỐ", step_data['score'])
                if st.button("🔄 Quay về Menu chính", use_container_width=True):
                    reset_game()
                    st.rerun()
            
            # Phân tích
            st.subheader("📝 Rút kinh nghiệm:")
            for h in st.session_state.history:
                icon = "✅" if h['change'] > 0 else "❌"
                st.info(f"{icon} **{h['choice']}**\n\n👉 {h['analysis']}")

        else: # Đang chơi
            st.subheader(s_data['title'])
            c1, c2 = st.columns([1, 2])
            with c1: 
                if step_data.get('img'): st.image(step_data['img'])
            with c2:
                st.markdown(f"<div class='chat-container'><b>{cust['name']} nói:</b><br><i>\"{step_data['text']}\"</i></div>", unsafe_allow_html=True)
                for k, v in step_data['choices'].items():
                    if st.button(f"{k}. {v}", use_container_width=True):
                        make_choice(k, step_data)
                        st.rerun()
