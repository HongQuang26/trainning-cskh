import streamlit as st
import json
import os
import time
from datetime import datetime

# --- KHỐI XỬ LÝ IMPORT ---
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import google.generativeai as genai
except ImportError:
    st.error("❌ Thiếu thư viện! Chạy lệnh: `pip install pandas matplotlib google-generativeai`")
    st.stop()

# ==============================================================================
# 1. CẤU HÌNH & HÀM TIỆN ÍCH
# ==============================================================================
st.set_page_config(page_title="Service Hero AI Pro", page_icon="🤖", layout="wide")

# Hàm Rerun an toàn
def safe_rerun():
    time.sleep(0.1)
    st.rerun()

# CSS chuyên nghiệp
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stButton button {
        border-radius: 8px; font-weight: 600; border: 1px solid #ddd;
        transition: all 0.3s;
    }
    .stButton button:hover {
        border-color: #4CAF50; color: #4CAF50; background-color: #fff;
        transform: translateY(-2px);
    }
    .chat-bubble-user {
        background-color: #e3f2fd; padding: 15px; border-radius: 15px 15px 0 15px;
        margin: 10px 0; text-align: right; border: 1px solid #bbdefb;
    }
    .chat-bubble-ai {
        background-color: #ffffff; padding: 15px; border-radius: 15px 15px 15px 0;
        margin: 10px 0; text-align: left; border: 1px solid #e0e0e0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .feedback-box {
        font-size: 0.9em; color: #666; font-style: italic; margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

DB_FILE = "scenarios_pro.json"
HISTORY_FILE = "score_history_pro.csv"

# ==============================================================================
# 2. DỮ LIỆU KỊCH BẢN (NÂNG CẤP DÀI & LOGIC HƠN)
# ==============================================================================
INITIAL_DATA = {
    "SC_COMPLEX_01": {
        "title": "B2B: Khủng hoảng Hợp đồng SaaS",
        "desc": "Giám đốc IT dọa cắt hợp đồng vì lỗi bảo mật.",
        "difficulty": "Hard",
        "mode": "Classic", # Chế độ kịch bản tĩnh
        "customer": {"name": "Mr. David (CTO)", "role": "Giám đốc Kỹ thuật"},
        "steps": {
            "start": {
                "text": "Tôi vừa nhận báo cáo hệ thống của các anh làm rò rỉ dữ liệu nhân viên của tôi! Đây là vi phạm nghiêm trọng SLA. Tôi sẽ báo pháp chế hủy hợp đồng ngay lập tức!",
                "patience": 10,
                "choices": {
                    "A": "Phủ nhận: 'Không thể nào, hệ thống bên tôi bảo mật chuẩn ISO.'",
                    "B": "Xoa dịu: 'Tôi hiểu sự nghiêm trọng. Anh cho tôi 30 phút để kiểm tra log được không?'",
                    "C": "Thừa nhận & Cam kết: 'Thưa anh David, đây là ưu tiên số 1. Tôi đang kích hoạt quy trình SEV-1 và sẽ cập nhật anh mỗi 15 phút.'"
                },
                "consequences": {
                    "A": {"next": "game_over_bad", "change": -50, "analysis": "❌ Cãi lý với khách hàng đang giận dữ là tự sát."},
                    "B": {"next": "step_2_wait", "change": +10, "analysis": "⚠️ Tạm ổn, nhưng chưa đủ khẩn cấp với một lỗi bảo mật."},
                    "C": {"next": "step_2_investigate", "change": +30, "analysis": "✅ Chuyên nghiệp. Kích hoạt quy trình khẩn cấp (SEV-1) tạo sự tin tưởng."}
                }
            },
            "step_2_investigate": {
                "text": "(15 phút sau) Đội của anh vẫn chưa tìm ra nguyên nhân à? Ban giám đốc đang ép tôi chuyển sang đối thủ của các anh đấy!",
                "patience": 30,
                "choices": {
                    "A": "Xin thêm giờ: 'Xin anh bình tĩnh, kỹ thuật đang cố hết sức.'",
                    "B": "Minh bạch: 'Chúng tôi đã khoanh vùng được lỗ hổng API. Đang vá nóng (hotfix). Cam kết xong trong 20 phút nữa.'"
                },
                "consequences": {
                    "A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Lời nói suông không có giá trị lúc này."},
                    "B": {"next": "step_3_solution", "change": +20, "analysis": "✅ Cung cấp tiến độ cụ thể và giải pháp kỹ thuật."}
                }
            },
            "step_3_solution": {
                "text": "Được, vá xong rồi. Nhưng lòng tin thì mất rồi. Tại sao tôi phải tiếp tục gia hạn năm sau?",
                "patience": 50,
                "choices": {
                    "A": "Khuyến mãi: 'Chúng tôi giảm giá 20% cho năm sau.'",
                    "B": "Cam kết tương lai: 'Chúng tôi sẽ gửi báo cáo RCA (Nguyên nhân gốc rễ) và thuê đơn vị thứ 3 audit lại toàn bộ hệ thống miễn phí cho bên anh.'"
                },
                "consequences": {
                    "A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Giảm giá lúc này giống như hối lộ để bịt miệng."},
                    "B": {"next": "game_over_win", "change": +40, "analysis": "🏆 Giải quyết đúng nỗi đau (sợ lặp lại lỗi) bằng Audit bên thứ 3."}
                }
            },
            # Các kết thúc
            "game_over_win": {"type": "WIN", "text": "Hợp đồng được giữ lại. David đánh giá cao sự chuyên nghiệp.", "score": 100},
            "game_over_fail": {"type": "LOSE", "text": "Khách hàng không hài lòng và không gia hạn.", "score": 40},
            "game_over_bad": {"type": "LOSE", "text": "Khách hàng kiện ra tòa và bêu xấu trên LinkedIn.", "score": 0},
            "step_2_wait": {"type": "LOSE", "text": "Bạn phản ứng quá chậm chạp. Khách đã cúp máy.", "score": 20} # Đường nhánh cụt
        }
    }
}

# --- QUẢN LÝ DỮ LIỆU ---
def load_data(force_reset=False):
    if force_reset or not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(INITIAL_DATA, f, ensure_ascii=False, indent=4)
        return INITIAL_DATA.copy()
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return load_data(True)

def save_score(player, scenario, score, outcome, mode="Classic"):
    if not os.path.exists(HISTORY_FILE):
        df = pd.DataFrame(columns=["Time", "Player", "Scenario", "Score", "Outcome", "Mode"])
        df.to_csv(HISTORY_FILE, index=False)
    
    new_row = pd.DataFrame([{
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Player": player,
        "Scenario": scenario,
        "Score": score,
        "Outcome": outcome,
        "Mode": mode
    }])
    new_row.to_csv(HISTORY_FILE, mode='a', header=False, index=False)

# ==============================================================================
# 3. GEMINI AI ENGINE (TRÁI TIM CỦA APP)
# ==============================================================================
def init_gemini(api_key):
    if not api_key: return False
    try:
        genai.configure(api_key=api_key)
        return True
    except: return False

def get_gemini_response(history, user_input, context):
    """
    Hàm này gửi lịch sử chat cho Gemini và nhận lại phản hồi đóng vai khách hàng.
    """
    # Prompt kỹ thuật (System Prompt)
    system_prompt = f"""
    Bạn là một khách hàng đang gặp vấn đề: {context['desc']}.
    Tính cách của bạn: {context['trait']}.
    Tên của bạn: {context['name']}.
    
    Nhiệm vụ của bạn:
    1. Đóng vai khách hàng, phản hồi lại câu nói của nhân viên CSKH (người dùng).
    2. Đánh giá câu trả lời của nhân viên trên thang điểm 0-100 (độ hài lòng hiện tại).
    3. Nếu nhân viên giải quyết xuất sắc, hãy nói [WIN]. Nếu quá tệ hoặc bạn hết kiên nhẫn, nói [LOSE]. Còn lại cứ tiếp tục hội thoại.
    
    Định dạng trả về JSON:
    {{
        "customer_reply": "Câu trả lời của bạn với tư cách khách hàng",
        "patience_score": 50, (Số nguyên từ 0-100)
        "feedback": "Nhận xét ngắn gọn về câu trả lời của nhân viên (tại sao tốt/xấu)",
        "status": "CONTINUE" (hoặc "WIN" hoặc "LOSE")
    }}
    Chỉ trả về JSON thuần túy, không có markdown.
    """
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Xây dựng lịch sử chat để AI nhớ ngữ cảnh
    chat_history = [{"role": "user", "parts": [system_prompt]}]
    for msg in history:
        role = "model" if msg['role'] == "ai" else "user"
        chat_history.append({"role": role, "parts": [msg['content']]})
    
    chat_history.append({"role": "user", "parts": [f"Nhân viên nói: {user_input}"]})
    
    try:
        response = model.generate_content(chat_history)
        # Xử lý chuỗi JSON trả về (đôi khi Gemini thêm ```json)
        txt = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(txt)
    except Exception as e:
        return {"customer_reply": "Lỗi kết nối AI...", "patience_score": 0, "feedback": str(e), "status": "LOSE"}

# ==============================================================================
# 4. GIAO DIỆN ADMIN PRO
# ==============================================================================
def admin_page():
    st.header("🔐 Trung Tâm Chỉ Huy (Admin)")
    pwd = st.text_input("Mật khẩu truy cập", type="password")
    if pwd != "admin123": st.stop()
    
    # SỬA LỖI ADMIN: Kiểm tra file trước khi đọc
    if not os.path.exists(HISTORY_FILE):
        st.warning("📭 Chưa có dữ liệu đào tạo nào được ghi nhận.")
        return

    try:
        df = pd.read_csv(HISTORY_FILE)
        if df.empty:
            st.warning("Dữ liệu trống.")
            return

        # Dashboard chuyên nghiệp
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Tổng lượt train", len(df))
        c2.metric("Điểm trung bình", f"{df['Score'].mean():.1f}")
        c3.metric("Số nhân viên", df['Player'].nunique())
        
        win_count = len(df[df['Outcome'] == 'WIN'])
        c4.metric("Tỷ lệ thành công", f"{(win_count/len(df)*100):.1f}%")
        
        st.divider()
        col_L, col_R = st.columns([2, 1])
        with col_L:
            st.subheader("📈 Hiệu suất nhân viên")
            st.bar_chart(df.groupby("Player")["Score"].mean())
        with col_R:
            st.subheader("🥧 Phân loại kết quả")
            # Xử lý biểu đồ an toàn
            outcome_counts = df['Outcome'].value_counts()
            fig, ax = plt.subplots()
            ax.pie(outcome_counts, labels=outcome_counts.index, autopct='%1.1f%%', colors=['#66bb6a', '#ef5350'])
            st.pyplot(fig)
            
        with st.expander("Xem chi tiết Log (Raw Data)"):
            st.dataframe(df, use_container_width=True)
            
    except Exception as e:
        st.error(f"Lỗi đọc dữ liệu: {e}")

# ==============================================================================
# 5. GIAO DIỆN CHƠI GAME (TRAINING)
# ==============================================================================
def training_page():
    # Sidebar: Cài đặt & Thông tin
    with st.sidebar:
        st.title("⚙️ Cấu hình")
        
        # Nhập tên
        if 'player_name' not in st.session_state: st.session_state.player_name = ""
        st.session_state.player_name = st.text_input("Tên nhân viên:", st.session_state.player_name)
        
        if not st.session_state.player_name:
            st.warning("Vui lòng nhập tên để bắt đầu.")
            st.stop()
            
        st.divider()
        st.markdown("### 🧠 Trí tuệ nhân tạo (AI)")
        api_key = st.text_input("Gemini API Key", type="password", help="Nhập key để mở khóa chế độ AI Roleplay")
        ai_ready = init_gemini(api_key)
        if ai_ready: st.success("AI đã sẵn sàng!")
        else: st.info("Chưa có Key. Chỉ dùng chế độ cơ bản.")
        
        st.divider()
        if st.button("Trở về màn hình chính"):
            st.session_state.current_scenario = None
            st.session_state.ai_history = []
            safe_rerun()

    # Chọn kịch bản
    data = load_data()
    
    if 'current_scenario' not in st.session_state or st.session_state.current_scenario is None:
        st.title(f"Xin chào, {st.session_state.player_name} 👋")
        st.write("Chọn tình huống đào tạo hôm nay:")
        
        tabs = st.tabs(["📚 Kịch bản Cố định (Classic)", "🤖 Giả lập AI (Pro)"])
        
        with tabs[0]: # CLASSIC
            for key, val in data.items():
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.subheader(val['title'])
                        st.write(val['desc'])
                    with c2:
                        if st.button("Bắt đầu", key=key):
                            st.session_state.current_scenario = key
                            st.session_state.mode = "Classic"
                            st.session_state.step = 'start'
                            st.session_state.score = 50 # Điểm khởi đầu
                            safe_rerun()
                            
        with tabs[1]: # AI MODE
            if not ai_ready:
                st.warning("⚠️ Vui lòng nhập Gemini API Key ở cột bên trái để dùng tính năng này.")
            else:
                st.info("Chế độ này cho phép bạn chat tự do. AI sẽ đóng vai khách hàng.")
                # Tạo nhanh ngữ cảnh AI
                with st.form("ai_setup"):
                    st.write("Thiết lập tình huống giả lập:")
                    ai_name = st.text_input("Tên khách hàng", "Ms. Anna")
                    ai_trait = st.text_input("Tính cách", "Khó tính, đang vội, hay bắt bẻ")
                    ai_desc = st.text_input("Vấn đề", "Mua hàng online nhưng nhận được hàng giả")
                    if st.form_submit_button("🔥 Bắt đầu giả lập"):
                        st.session_state.current_scenario = "AI_GEN"
                        st.session_state.mode = "AI"
                        st.session_state.ai_context = {"name": ai_name, "trait": ai_trait, "desc": ai_desc}
                        st.session_state.ai_history = []
                        st.session_state.score = 50
                        safe_rerun()

    else:
        # --- MÀN HÌNH CHƠI GAME ---
        scenario_id = st.session_state.current_scenario
        
        # SỬA LỖI ẢNH: Dùng Placeholder tự động
        def show_header(title):
            # Tạo ảnh placeholder màu sắc dựa trên tên
            st.image(f"[https://placehold.co/800x200/2E86C1/FFFFFF/png?text=](https://placehold.co/800x200/2E86C1/FFFFFF/png?text=){title.replace(' ', '+')}", use_container_width=True)

        # === LOGIC CHẾ ĐỘ CLASSIC ===
        if st.session_state.mode == "Classic":
            scen_data = data[scenario_id]
            step_id = st.session_state.step
            
            # Kiểm tra kết thúc
            if step_id not in scen_data['steps']: # Win/Lose steps
                 # Logic xử lý hiển thị kết quả cuối (vì trong JSON tôi lưu chung vào steps)
                 pass 

            step_data = scen_data['steps'][step_id]
            
            show_header(scen_data['title'])
            
            # Thanh trạng thái
            st.progress(st.session_state.score / 100, text=f"Độ hài lòng khách hàng: {st.session_state.score}%")
            
            # Hiển thị hội thoại
            if "type" in step_data: # Màn hình kết thúc (WIN/LOSE)
                msg_type = step_data['type']
                if msg_type == "WIN":
                    st.success(f"🎉 {step_data['text']}")
                    st.balloons()
                else:
                    st.error(f"💀 {step_data['text']}")
                
                # Lưu điểm (ngăn lưu trùng)
                if 'saved' not in st.session_state:
                    save_score(st.session_state.player_name, scen_data['title'], step_data['score'], msg_type, "Classic")
                    st.session_state.saved = True
                
                if st.button("Chơi lại"):
                    st.session_state.current_scenario = None
                    if 'saved' in st.session_state: del st.session_state.saved
                    safe_rerun()
            else:
                # Màn hình chọn lựa
                st.markdown(f"""
                <div class="chat-bubble-ai">
                    <b>👤 {scen_data['customer']['name']}:</b><br>{step_data['text']}
                </div>
                """, unsafe_allow_html=True)
                
                st.write("👉 **Bạn sẽ trả lời thế nào?**")
                cols = st.columns(len(step_data['choices']))
                idx = 0
                for key, val in step_data['choices'].items():
                    with cols[idx]:
                        if st.button(val, use_container_width=True):
                            cons = step_data['consequences'][key]
                            st.session_state.step = cons['next']
                            st.session_state.score = max(0, min(100, st.session_state.score + cons['change']))
                            st.toast(cons['analysis'], icon="💡") # Feedback nhanh
                            time.sleep(1)
                            safe_rerun()
                    idx += 1

        # === LOGIC CHẾ ĐỘ AI (GEMINI) ===
        elif st.session_state.mode == "AI":
            ctx = st.session_state.ai_context
            show_header(f"Sim: {ctx['desc']}")
            
            # Thanh điểm số
            color = "green" if st.session_state.score > 50 else "red"
            st.markdown(f"**Cảm xúc khách hàng:** :{color}[{st.session_state.score}/100]")
            st.progress(st.session_state.score / 100)
            
            # Khởi tạo tin nhắn đầu tiên của AI nếu chưa có
            if not st.session_state.ai_history:
                with st.spinner("Khách hàng đang bước vào..."):
                    initial_prompt = [{"role": "user", "content": "Xin chào, tôi là nhân viên hỗ trợ."}] # Mồi nhẹ
                    resp = get_gemini_response([], "Tôi vừa bắt đầu cuộc hội thoại, hãy phàn nàn về vấn đề của bạn ngay lập tức.", ctx)
                    st.session_state.ai_history.append({"role": "ai", "content": resp['customer_reply']})
            
            # Hiển thị lịch sử chat
            for msg in st.session_state.ai_history:
                if msg['role'] == "ai":
                    st.markdown(f'<div class="chat-bubble-ai"><b>👤 {ctx["name"]}:</b> {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-bubble-user"><b>🎧 Bạn:</b> {msg["content"]}</div>', unsafe_allow_html=True)
            
            # Ô nhập liệu người dùng
            user_input = st.chat_input("Nhập câu trả lời của bạn...")
            
            if user_input:
                # 1. Hiện câu của user ngay lập tức
                st.session_state.ai_history.append({"role": "user", "content": user_input})
                
                # 2. Gọi Gemini xử lý
                with st.spinner(f"{ctx['name']} đang suy nghĩ..."):
                    ai_resp = get_gemini_response(st.session_state.ai_history, user_input, ctx)
                
                # 3. Cập nhật trạng thái
                st.session_state.score = ai_resp['patience_score']
                st.session_state.ai_history.append({"role": "ai", "content": ai_resp['customer_reply']})
                
                # 4. Feedback ngay lập tức
                if ai_resp.get('feedback'):
                    st.toast(f"Đánh giá AI: {ai_resp['feedback']}")
                
                # 5. Kiểm tra Win/Lose
                if ai_resp['status'] == "WIN":
                    save_score(st.session_state.player_name, ctx['desc'], st.session_state.score, "WIN", "AI-Gemini")
                    st.success("🏆 BẠN ĐÃ THẮNG! Khách hàng đã hài lòng.")
                    st.balloons()
                    if st.button("Kết thúc"): 
                        st.session_state.current_scenario = None
                        safe_rerun()
                elif ai_resp['status'] == "LOSE":
                    save_score(st.session_state.player_name, ctx['desc'], st.session_state.score, "LOSE", "AI-Gemini")
                    st.error("💀 GAME OVER! Khách hàng đã rời bỏ.")
                    if st.button("Kết thúc"): 
                        st.session_state.current_scenario = None
                        safe_rerun()
                else:
                    safe_rerun()

# ==============================================================================
# 6. APP MAIN
# ==============================================================================
# Điều hướng Menu
if 'page' not in st.session_state: st.session_state.page = "training"

with st.sidebar:
    st.divider()
    page = st.radio("Menu chính", ["🎓 Huấn Luyện", "🔐 Quản Trị (Admin)"])

if page == "🎓 Huấn Luyện":
    training_page()
elif page == "🔐 Quản Trị (Admin)":
    admin_page()
