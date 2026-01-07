import streamlit as st
import json
import os
import time
from datetime import datetime

# --- KHỐI XỬ LÝ LỖI IMPORT THƯ VIỆN ---
try:
    import pandas as pd
    import matplotlib.pyplot as plt
except ImportError as e:
    st.error(f"❌ Lỗi: Thiếu thư viện cần thiết. Vui lòng chạy lệnh sau trong terminal:\n\n`pip install pandas matplotlib`")
    st.stop()

# ==============================================================================
# 1. CẤU HÌNH & HÀM HỖ TRỢ (CORE UTILS)
# ==============================================================================
st.set_page_config(
    page_title="Service Hero Pro",
    page_icon="🦸‍♂️",
    layout="wide"
)

# Hàm Rerun tương thích mọi phiên bản Streamlit
def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

# CSS Custom
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
        border: 5px double #D4AF37; padding: 30px; text-align: center;
        background: #FFF8DC; color: #5D4037; border-radius: 15px; margin-top: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DỮ LIỆU MẪU (INITIAL DATA)
# ==============================================================================
INITIAL_DATA = {
    "SC_FNB_01": {
        "title": "F&B: Dị vật trong món ăn",
        "desc": "Khách phát hiện tóc trong súp.",
        "difficulty": "Hard",
        "customer": {"name": "Ms. Jade", "avatar": "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?q=80&w=400", "traits": ["Kỹ tính", "Reviewer"], "spending": "Khách mới"},
        "steps": {
            "start": { 
                "patience": 30, "img": "https://images.unsplash.com/photo-1533777857889-4be7c70b33f7?q=80&w=800",
                "text": "Quản lý đâu! Nhìn xem! Một sợi tóc dài trong súp của tôi! Các người làm ăn kiểu gì vậy?",
                "choices": {"A": "Phủ nhận: 'Không phải tóc nhân viên chúng tôi.'", "B": "Hành động: 'Tôi vô cùng xin lỗi! Tôi sẽ xử lý ngay.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -40, "analysis": "❌ Phủ nhận làm mất niềm tin ngay lập tức."}, "B": {"next": "step_2_wait", "change": +10, "analysis": "✅ Hành động ngay lập tức là chính xác."}}
            },
            "step_2_wait": { 
                "patience": 40, "img": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=800",
                "text": "(5 phút sau) Tôi hết muốn ăn rồi. Đợi lâu quá tôi mất cả hứng.",
                "choices": {"A": "Thuyết phục: 'Mời chị thử đi ạ, bếp trưởng làm riêng đấy.'", "B": "Chuyển hướng: 'Tôi hiểu ạ. Tôi xin phép dọn món này đi. Tôi mời chị món tráng miệng nhé?'"},
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

# ==============================================================================
# 3. HÀM QUẢN LÝ DỮ LIỆU (DATA MANAGER)
# ==============================================================================
def load_data(force_reset=False):
    """Tải dữ liệu an toàn với xử lý lỗi."""
    if force_reset or not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(INITIAL_DATA, f, ensure_ascii=False, indent=4)
        return INITIAL_DATA.copy()
    
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Merge dữ liệu cũ nếu thiếu
            updated = False
            for k, v in INITIAL_DATA.items():
                if k not in data:
                    data[k] = v
                    updated = True
            if updated:
                save_data(data)
            return data
    except Exception as e:
        st.error(f"Lỗi đọc file dữ liệu: {e}. Đã reset về mặc định.")
        return load_data(force_reset=True)

def save_data(new_data):
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Không thể lưu dữ liệu: {e}")

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
    try:
        if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
            df = pd.read_csv(HISTORY_FILE)
        else:
            df = pd.DataFrame(columns=["Time", "Player", "Scenario", "Score", "Outcome"])
        
        new_df = pd.DataFrame([new_record])
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_csv(HISTORY_FILE, index=False)
    except Exception as e:
        st.warning(f"Không thể lưu điểm số: {e}")

# ==============================================================================
# 4. LOGIC TÍNH NĂNG (FEATURES)
# ==============================================================================
def render_certificate(player_name):
    st.balloons()
    cert_html = f"""
    <div class="certificate-box">
        <h1>🎖️ CHỨNG CHỈ HOÀN THÀNH 🎖️</h1>
        <p>Chứng nhận đặc vụ xuất sắc:</p>
        <h2 style="color:#2E86C1; text-transform:uppercase;">{player_name}</h2>
        <p>Đã vượt qua khóa huấn luyện Service Hero với thành tích ấn tượng.</p>
        <hr style="border-top: 1px dashed #8c8b8b; width: 50%; margin: auto;">
        <p><i>Ngày cấp: {datetime.now().strftime("%d/%m/%Y")}</i></p>
    </div>
    """
    st.markdown(cert_html, unsafe_allow_html=True)

def admin_dashboard():
    st.title("🔐 Admin Dashboard")
    
    pwd = st.text_input("Mật khẩu quản trị", type="password")
    if pwd != "admin123":
        st.warning("Vui lòng nhập mật khẩu (Mặc định: admin123)")
        st.stop()
    
    if not os.path.exists(HISTORY_FILE) or os.path.getsize(HISTORY_FILE) == 0:
        st.info("Chưa có dữ liệu lịch sử.")
        return

    try:
        df = pd.read_csv(HISTORY_FILE)
        
        # Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Tổng lượt chơi", len(df))
        c2.metric("Điểm trung bình", f"{df['Score'].mean():.1f}")
        
        win_rate = 0
        if len(df) > 0:
            win_rate = (len(df[df['Outcome']=='WIN']) / len(df)) * 100
        c3.metric("Tỷ lệ thắng", f"{win_rate:.1f}%")
        
        st.divider()
        
        # Charts
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            st.subheader("📊 Điểm số nhân viên")
            if not df.empty:
                avg_score = df.groupby("Player")["Score"].mean().sort_values(ascending=False)
                st.bar_chart(avg_score, color="#2E86C1")
        
        with c_chart2:
            st.subheader("🥧 Tỷ lệ kết quả")
            if not df.empty:
                outcome_counts = df['Outcome'].value_counts()
                fig, ax = plt.subplots()
                ax.pie(outcome_counts, labels=outcome_counts.index, autopct='%1.1f%%', startangle=90, colors=['#2ecc71', '#e74c3c'])
                ax.axis('equal')
                st.pyplot(fig)
                plt.close(fig) # Giải phóng bộ nhớ

        st.divider()
        st.subheader("📂 Dữ liệu chi tiết")
        st.dataframe(df, use_container_width=True)
        
        # Download
        with open(HISTORY_FILE, "rb") as f:
            st.download_button("📥 Tải báo cáo (CSV)", f, "report.csv", "text/csv")
            
    except Exception as e:
        st.error(f"Lỗi khi tải báo cáo: {e}")

# ==============================================================================
# 5. UI TẠO KỊCH BẢN (CREATOR UI)
# ==============================================================================
def create_new_scenario_ui():
    st.header("🛠️ Tạo Kịch Bản Mới")
    with st.form("creator"):
        c1, c2 = st.columns(2)
        title = c1.text_input("Tên tình huống")
        diff = c1.selectbox("Độ khó", ["Dễ", "Trung bình", "Khó"])
        cust_name = c2.text_input("Tên khách hàng")
        cust_trait = c2.text_input("Tính cách")
        
        st.divider()
        start_text = st.text_area("Câu thoại mở đầu của khách")
        
        c3, c4 = st.columns(2)
        with c3:
            st.write("✅ **Phương án ĐÚNG (A)**")
            opt_a = st.text_input("Nội dung A")
            res_a = st.text_input("Kết quả thắng (A)")
        with c4:
            st.write("❌ **Phương án SAI (B)**")
            opt_b = st.text_input("Nội dung B")
            res_b = st.text_input("Kết quả thua (B)")
            
        if st.form_submit_button("Lưu Kịch Bản"):
            if title and start_text:
                new_id = f"SC_{int(time.time())}"
                new_entry = {
                    "title": title, "desc": "Kịch bản tự tạo", "difficulty": diff,
                    "customer": {"name": cust_name, "avatar": "", "traits": [cust_trait], "spending": "N/A"},
                    "steps": {
                        "start": {
                            "patience": 50, "img": "", "text": start_text,
                            "choices": {"A": opt_a, "B": opt_b},
                            "consequences": {
                                "A": {"next": "win", "change": 50, "analysis": "✅ Giải quyết tốt."},
                                "B": {"next": "lose", "change": -50, "analysis": "❌ Giải quyết kém."}
                            }
                        },
                        "win": {"type": "WIN", "title": "THẮNG", "text": res_a, "img": "", "score": 100},
                        "lose": {"type": "LOSE", "title": "THUA", "text": res_b, "img": "", "score": 0}
                    }
                }
                data = load_data()
                data[new_id] = new_entry
                save_data(data)
                st.success("Đã lưu thành công!")
                time.sleep(1)
                safe_rerun()
            else:
                st.warning("Vui lòng nhập đủ thông tin.")

# ==============================================================================
# 6. MAIN APP LOOP
# ==============================================================================
# Khởi tạo Session State
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

# --- GIAO DIỆN CHÍNH ---
ALL_SCENARIOS = load_data()

with st.sidebar:
    st.title("🎛️ Menu")
    menu = st.radio("Chế độ", ["Học viên", "🛠️ Tạo Kịch Bản", "🔐 Admin"])
    st.divider()
    if st.button("⚠️ Reset Dữ liệu"):
        load_data(force_reset=True)
        st.success("Đã reset!")
        time.sleep(1)
        safe_rerun()

if menu == "🔐 Admin":
    reset_game()
    admin_dashboard()

elif menu == "🛠️ Tạo Kịch Bản":
    reset_game()
    create_new_scenario_ui()

elif menu == "Học viên":
    # 1. Màn hình nhập tên
    if not st.session_state.player_name:
        st.title("🎓 Chào mừng đặc vụ mới")
        st.info("Nhập tên để bắt đầu hồ sơ huấn luyện.")
        name_in = st.text_input("Tên của bạn:")
        if name_in:
            st.session_state.player_name = name_in
            safe_rerun()
        st.stop()

    # 2. Dashboard chọn bài
    if st.session_state.current_scenario is None:
        c1, c2 = st.columns([3, 1])
        c1.title(f"Xin chào, {st.session_state.player_name} 👋")
        if c2.button("Đăng xuất"):
            st.session_state.player_name = ""
            safe_rerun()
            
        # Kiểm tra chứng chỉ
        if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
            try:
                df = pd.read_csv(HISTORY_FILE)
                df_me = df[df['Player'] == st.session_state.player_name]
                if not df_me.empty:
                    avg = df_me['Score'].mean()
                    played = len(df_me)
                    st.success(f"📊 Thành tích: Đã chơi {played} ván - Điểm TB: {avg:.1f}")
                    if avg >= 80 and played >= 1:
                        with st.expander("🎖️ BẠN CÓ PHẦN THƯỞNG!", expanded=True):
                            render_certificate(st.session_state.player_name)
            except: pass

        st.divider()
        st.subheader("Chọn tình huống:")
        
        cols = st.columns(2)
        idx = 0
        for key, data in ALL_SCENARIOS.items():
            with cols[idx % 2]:
                with st.container(border=True):
                    st.subheader(data['title'])
                    st.write(f"_{data['desc']}_")
                    st.caption(f"Độ khó: {data['difficulty']}")
                    if st.button("🔥 Bắt đầu", key=f"btn_{key}", use_container_width=True):
                        st.session_state.current_scenario = key
                        st.session_state.current_step = 'start'
                        st.session_state.patience_meter = data['steps']['start']['patience']
                        st.session_state.history = []
                        if 'score_saved' in st.session_state: del st.session_state.score_saved
                        safe_rerun()
            idx += 1

    # 3. Màn hình chơi (Game Loop)
    else:
        s_key = st.session_state.current_scenario
        if s_key not in ALL_SCENARIOS:
            reset_game()
            safe_rerun()
        
        s_data = ALL_SCENARIOS[s_key]
        
        # Kiểm tra step hợp lệ
        if st.session_state.current_step not in s_data['steps']:
            st.error("Lỗi: Bước không tồn tại!")
            if st.button("Về menu"): reset_game(); safe_rerun()
            st.stop()
            
        step_data = s_data['steps'][st.session_state.current_step]

        # Sidebar thông tin
        with st.sidebar:
            st.divider()
            if st.button("❌ Thoát về Menu"):
                reset_game()
                safe_rerun()
            st.divider()
            
            cust = s_data['customer']
            if cust.get('avatar'): st.image(cust['avatar'], width=100)
            st.write(f"**{cust['name']}**")
            st.write(f"Đặc điểm: {', '.join(cust['traits'])}")
            
            p_val = st.session_state.patience_meter
            st.write(f"Kiên nhẫn: {p_val}%")
            st.progress(p_val / 100)

        # Xử lý nội dung
        if "type" in step_data: # Kết thúc Game
            st.markdown(f"# {step_data['title']}")
            
            # Lưu điểm (chỉ lưu 1 lần)
            if 'score_saved' not in st.session_state:
                save_score(st.session_state.player_name, s_data['title'], step_data['score'], step_data['type'])
                st.session_state.score_saved = True
            
            c1, c2 = st.columns([1, 2])
            with c1:
                if step_data.get('img'): st.image(step_data['img'])
            with c2:
                if step_data['type'] == 'WIN':
                    st.success(step_data['text'])
                    st.balloons()
                else:
                    st.error(step_data['text'])
                
                st.metric("KẾT QUẢ", f"{step_data['score']} điểm")
                if st.button("🔄 Chơi lại / Về Menu", use_container_width=True):
                    reset_game()
                    safe_rerun()
            
            st.subheader("🔍 Phân tích chi tiết:")
            for h in st.session_state.history:
                icon = "✅" if h['change'] > 0 else "❌"
                st.info(f"{icon} Bạn chọn: **{h['choice']}**\n\n👉 {h['analysis']}")

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
                        safe_rerun()
