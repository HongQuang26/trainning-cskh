import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime

# --- KHỐI XỬ LÝ IMPORT AN TOÀN ---
try:
    import google.generativeai as genai
    import matplotlib.pyplot as plt
except ImportError:
    st.error("🚨 Thiếu thư viện! Chạy lệnh: `pip install pandas matplotlib google-generativeai`")
    st.stop()

# ==============================================================================
# 1. CẤU HÌNH HỆ THỐNG & GIAO DIỆN
# ==============================================================================
st.set_page_config(page_title="Service Hero AI Academy", page_icon="🛡️", layout="wide")

# CSS chuyên nghiệp (Giao diện Chat & Card)
st.markdown("""
<style>
    /* Giao diện chung */
    .main { background-color: #f0f2f6; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; color: #2c3e50; }
    
    /* Card kịch bản */
    .scenario-card {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;
        border-left: 5px solid #3498db; transition: transform 0.2s;
    }
    .scenario-card:hover { transform: translateY(-5px); border-left-color: #e74c3c; }
    
    /* Bong bóng chat */
    .stChatMessage { padding: 10px; border-radius: 10px; }
    
    /* Thanh điểm số */
    .score-container {
        padding: 10px; background: white; border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

HISTORY_FILE = "training_history.csv"

# ==============================================================================
# 2. KHO KỊCH BẢN CHUYÊN SÂU (SCENARIO DATABASE)
# ==============================================================================
# Đây là phần bạn yêu cầu "Nhiều và Chỉn chu hơn".
# Mỗi kịch bản có context rõ ràng để AI nhập vai tốt nhất.

SCENARIOS_DB = {
    "SC_RETAIL_01": {
        "title": "🛍️ Bán lẻ: Vụ án chiếc váy cưới",
        "industry": "Retail (Thời trang)",
        "difficulty": "⭐⭐⭐ (Khó)",
        "context": {
            "role_name": "Chị Lan",
            "role_desc": "Cô dâu sắp cưới vào tuần sau. Đã đặt váy thiết kế riêng nhưng nhận được váy sai kích thước và bị rách một đường nhỏ.",
            "personality": "Hoảng loạn, thất vọng tột độ, dễ xúc động, đang khóc.",
            "initial_msg": "Alo cửa hàng phải không? Các người làm ăn kiểu gì thế hả?! Tuần sau tôi cưới rồi mà gửi cái váy rách nát này cho tôi à? Tôi bắt đền!!!",
            "win_condition": "Nhân viên phải bình tĩnh, không đổ lỗi, cam kết sửa/đổi trong 24h và có đền bù tinh thần.",
            "lose_condition": "Nhân viên đổ lỗi cho bên vận chuyển, bảo khách tự sửa, hoặc tỏ thái độ thờ ơ."
        }
    },
    "SC_TECH_01": {
        "title": "💻 Công nghệ: Sự cố sập Server",
        "industry": "B2B SaaS",
        "difficulty": "⭐⭐⭐⭐ (Rất Khó)",
        "context": {
            "role_name": "Mr. David (CTO)",
            "role_desc": "Giám đốc kỹ thuật của đối tác lớn. Hệ thống bên bạn cung cấp bị sập 2 tiếng vào ngày Black Friday, khiến họ mất hàng tỷ đồng.",
            "personality": "Giận dữ, chuyên nghiệp, đòi hỏi số liệu, dọa cắt hợp đồng, không nghe lời xin lỗi suông.",
            "initial_msg": "Tôi không cần lời xin lỗi của cậu! 2 tiếng vừa qua chúng tôi mất 50.000$ doanh thu. Giải thích ngay nguyên nhân hoặc tôi gọi luật sư!",
            "win_condition": "Minh bạch nguyên nhân, đưa ra giải pháp khắc phục (RCA), cam kết SLA credit (đền bù tiền dịch vụ).",
            "lose_condition": "Vòng vo, giấu lỗi, hứa suông mà không có mốc thời gian cụ thể."
        }
    },
    "SC_HOSPITALITY_01": {
        "title": "hotel Khách sạn: Tiếng ồn đêm khuya",
        "industry": "Hospitality",
        "difficulty": "⭐⭐ (Trung bình)",
        "context": {
            "role_name": "Khách hàng VIP (Phòng 808)",
            "role_desc": "Doanh nhân đang đi công tác, cần ngủ sớm để mai họp quan trọng. Phòng bên cạnh tiệc tùng ồn ào lúc 1h sáng.",
            "personality": "Mệt mỏi, cáu kỉnh, muốn giải quyết ngay lập tức.",
            "initial_msg": "Lễ tân đâu? Bây giờ là mấy giờ rồi mà phòng bên cạnh như cái vũ trường thế? Tôi trả 500$ một đêm để nghe nhạc sàn à?",
            "win_condition": "Xử lý tiếng ồn ngay lập tức (trong 5p), đề xuất đổi phòng yên tĩnh hơn hoặc tặng bữa sáng miễn phí.",
            "lose_condition": "Bảo khách ráng chịu đựng, hứa sẽ 'nhắc nhở' nhưng không làm ngay."
        }
    },
    "SC_BANK_01": {
        "title": "💳 Ngân hàng: Khoá thẻ khi đi du lịch",
        "industry": "Finance",
        "difficulty": "⭐⭐⭐ (Khó)",
        "context": {
            "role_name": "Du khách Tuấn",
            "role_desc": "Đang đi du lịch nước ngoài, thẻ tín dụng bị khóa đột ngột khi đang thanh toán tiền khách sạn. Đang đứng ở quầy lễ tân rất quê độ.",
            "personality": "Gấp gáp, xấu hổ, lo lắng vì không có tiền mặt.",
            "initial_msg": "Trời ơi ngân hàng làm cái gì vậy? Tôi đang check-out khách sạn ở Paris, thẻ báo lỗi. Giờ tôi đứng đây như thằng ăn trộm. Mở thẻ ngay cho tôi!",
            "win_condition": "Trấn an, kiểm tra bảo mật nhanh, mở thẻ tạm thời hoặc hướng dẫn cách rút tiền khẩn cấp.",
            "lose_condition": "Yêu cầu khách ra chi nhánh (đang ở nước ngoài sao ra?), bắt đợi 24h."
        }
    },
    "SC_LOGISTICS_01": {
        "title": "📦 Vận chuyển: Shipper làm vỡ hàng",
        "industry": "E-commerce",
        "difficulty": "⭐⭐ (Trung bình)",
        "context": {
            "role_name": "Chị Mai",
            "role_desc": "Đặt bộ ấm chén tặng tân gia, shipper giao đến nơi nghe tiếng loảng xoảng bên trong. Shipper chối bay chối biến.",
            "personality": "Nghi ngờ, bực bội vì sợ lỡ việc tặng quà.",
            "initial_msg": "Em ơi, shipper vừa giao cái hộp mà lắc nghe rổn rảng. Anh ta chạy mất rồi. Giờ mở ra vỡ hết thì ai đền? Đừng có nói là do chị không kiểm hàng nhé!",
            "win_condition": "Nhận trách nhiệm ngay, cam kết đổi mới (ship hỏa tốc) để kịp giờ tặng, không đôi co quy trình.",
            "lose_condition": "Đổ lỗi khách không đồng kiểm, yêu cầu video mở hộp (khi khách đang bực), quy trình hoàn tiền quá lâu."
        }
    }
}

# ==============================================================================
# 3. HÀM XỬ LÝ AI & LOGIC GAME
# ==============================================================================
def init_gemini(api_key):
    """Khởi tạo kết nối AI"""
    try:
        genai.configure(api_key=api_key)
        # Test thử model
        model = genai.GenerativeModel('gemini-1.5-flash')
        return True
    except Exception as e:
        return False

def get_ai_response(history, user_input, context):
    """
    Core function: Gửi chat sang Gemini và nhận phản hồi nhập vai + chấm điểm.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # System Prompt cực kỹ để ép AI trả về đúng định dạng JSON
    system_instruction = f"""
    Bạn đang đóng vai: {context['role_name']} trong tình huống: {context['role_desc']}.
    Tính cách của bạn: {context['personality']}.
    
    Nhiệm vụ:
    1. Đọc câu trả lời của nhân viên CSKH (User).
    2. Phản hồi lại như một người thật, giữ đúng tính cách (đang giận thì nói giọng giận, đang gấp thì nói ngắn gọn).
    3. Đánh giá câu trả lời của nhân viên trên thang điểm 0-100 (đựa trên: sự đồng cảm, giải quyết vấn đề, thái độ).
    4. Quyết định trạng thái: "CONTINUE" (tiếp tục tranh luận), "WIN" (nếu nhân viên làm bạn hài lòng hoàn toàn), "LOSE" (nếu bạn quá tức giận và bỏ đi).
    
    YÊU CẦU BẮT BUỘC: Trả về kết quả dưới dạng JSON thuần túy (không markdown):
    {{
        "reply": "Câu nói của bạn với tư cách khách hàng",
        "score": <số nguyên 0-100>,
        "feedback": "Lời khuyên ngắn gọn cho nhân viên (tại sao bạn trừ điểm hoặc cộng điểm)",
        "status": "CONTINUE" | "WIN" | "LOSE"
    }}
    """
    
    # Xây dựng lịch sử hội thoại cho AI
    chat_session = model.start_chat(history=[
        {"role": "user", "parts": [system_instruction]},
        {"role": "model", "parts": ["OK. Tôi đã hiểu vai diễn. Tôi sẽ trả về JSON."]}
    ])
    
    # Nạp lịch sử chat cũ vào session (để AI nhớ mạch chuyện)
    for msg in history:
        role = "model" if msg["role"] == "ai" else "user"
        if msg["content"]: # Bỏ qua tin nhắn rỗng
            chat_session.history.append({"role": role, "parts": [msg["content"]]})
            
    try:
        response = chat_session.send_message(user_input)
        # Làm sạch response (đôi khi AI thêm ```json ... ```)
        clean_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean_text)
    except Exception as e:
        # Fallback nếu AI bị lỗi hoặc không trả về JSON
        return {
            "reply": "Hệ thống đang bận, nhưng tôi vẫn đang đợi câu trả lời thỏa đáng từ bạn!",
            "score": 50,
            "feedback": f"Lỗi phân tích AI: {str(e)}",
            "status": "CONTINUE"
        }

def save_history(player, scenario, score, result):
    """Lưu lịch sử vào CSV"""
    new_data = {
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Player": player,
        "Scenario": scenario,
        "Score": score,
        "Result": result
    }
    if os.path.exists(HISTORY_FILE):
        df = pd.read_csv(HISTORY_FILE)
    else:
        df = pd.DataFrame(columns=["Time", "Player", "Scenario", "Score", "Result"])
    
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv(HISTORY_FILE, index=False)

# ==============================================================================
# 4. TRANG DASHBOARD & CHAT (MAIN UI)
# ==============================================================================

def main():
    # --- SIDEBAR: Cấu hình ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
        st.title("Cài Đặt")
        
        # Nhập tên
        if 'player_name' not in st.session_state: st.session_state.player_name = ""
        st.session_state.player_name = st.text_input("Tên nhân viên:", st.session_state.player_name)
        
        # Nhập API Key
        if 'api_key' not in st.session_state: st.session_state.api_key = ""
        user_api_key = st.text_input("Gemini API Key:", value=st.session_state.api_key, type="password", help="Lấy tại aistudio.google.com")
        if user_api_key: st.session_state.api_key = user_api_key
        
        st.divider()
        mode = st.radio("Chế độ:", ["🎓 Phòng Huấn Luyện", "📊 Báo Cáo (Admin)"])
        
        if st.button("🔄 Reset Ứng dụng"):
            st.session_state.clear()
            st.rerun()

    # --- KIỂM TRA ĐẦU VÀO ---
    if not st.session_state.player_name:
        st.info("👋 Chào mừng! Vui lòng nhập tên của bạn ở cột bên trái để bắt đầu.")
        return

    # --- TRANG 1: DASHBOARD CHỌN KỊCH BẢN ---
    if mode == "🎓 Phòng Huấn Luyện":
        if 'current_scenario' not in st.session_state:
            st.header(f"Xin chào, {st.session_state.player_name}! 👋")
            st.write("Hôm nay bạn muốn rèn luyện kỹ năng xử lý tình huống nào?")
            
            # Kiểm tra API Key
            if not st.session_state.api_key:
                st.warning("⚠️ Bạn chưa nhập Gemini API Key. Vui lòng nhập ở cột bên trái để kích hoạt AI.")
                st.stop()

            # Hiển thị danh sách kịch bản dạng Grid
            cols = st.columns(2)
            idx = 0
            for key, data in SCENARIOS_DB.items():
                with cols[idx % 2]:
                    # Card UI Custom
                    st.markdown(f"""
                    <div class="scenario-card">
                        <h3>{data['title']}</h3>
                        <p><b>Ngành:</b> {data['industry']} | <b>Độ khó:</b> {data['difficulty']}</p>
                        <p style="color:#666; font-style:italic;">{data['context']['role_desc']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"🔥 Bắt đầu xử lý", key=key, use_container_width=True):
                        st.session_state.current_scenario = key
                        st.session_state.messages = [] # Reset chat
                        st.session_state.score = 50 # Điểm bắt đầu
                        st.session_state.game_active = True
                        st.rerun()
                idx += 1

        # --- TRANG 2: GIAO DIỆN CHAT (INGAME) ---
        else:
            scenario_id = st.session_state.current_scenario
            s_data = SCENARIOS_DB[scenario_id]
            ctx = s_data['context']
            
            # Header
            c1, c2 = st.columns([3, 1])
            with c1:
                st.subheader(f"Đang xử lý: {s_data['title']}")
                st.caption(f"Khách hàng: {ctx['role_name']} ({ctx['personality']})")
            with c2:
                if st.button("❌ Thoát / Chọn bài khác"):
                    del st.session_state.current_scenario
                    st.rerun()

            # Thanh điểm số
            score = st.session_state.get('score', 50)
            score_color = "green" if score >= 80 else ("orange" if score >= 50 else "red")
            st.markdown(f"""
            <div class="score-container">
                <b>Độ hài lòng khách hàng:</b> 
                <span style="color:{score_color}; font-size:1.2em; font-weight:bold;">{score}/100</span>
                <br>
                <progress value="{score}" max="100" style="width:100%"></progress>
            </div>
            """, unsafe_allow_html=True)

            # Khởi tạo tin nhắn đầu tiên của AI (nếu chưa có)
            if not st.session_state.messages:
                st.session_state.messages.append({"role": "ai", "content": ctx['initial_msg']})

            # Hiển thị lịch sử chat
            for msg in st.session_state.messages:
                avatar = "🤖" if msg["role"] == "ai" else "🧑‍💼"
                with st.chat_message(msg["role"], avatar=avatar):
                    st.write(msg["content"])

            # Logic Game Loop
            if st.session_state.get('game_active', True):
                # Input của người dùng
                user_input = st.chat_input("Nhập câu trả lời của bạn...")
                
                if user_input:
                    # 1. Hiển thị User Message
                    with st.chat_message("user", avatar="🧑‍💼"):
                        st.write(user_input)
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    
                    # 2. AI Suy nghĩ & Phản hồi
                    with st.spinner(f"{ctx['role_name']} đang nhập..."):
                        # Gọi hàm AI
                        ai_result = get_ai_response(
                            st.session_state.messages[:-1], # Lịch sử trừ câu mới nhất
                            user_input, 
                            ctx
                        )
                    
                    # 3. Xử lý kết quả trả về
                    new_score = ai_result.get('score', score)
                    st.session_state.score = new_score
                    reply = ai_result.get('reply', "...")
                    feedback = ai_result.get('feedback', "")
                    status = ai_result.get('status', "CONTINUE")
                    
                    # Hiển thị AI Message
                    with st.chat_message("ai", avatar="🤖"):
                        st.write(reply)
                        if feedback:
                            st.info(f"💡 **AI Feedback:** {feedback}")
                    
                    st.session_state.messages.append({"role": "ai", "content": reply})

                    # 4. Kiểm tra điều kiện Thắng/Thua
                    if status == "WIN":
                        st.balloons()
                        st.success("🏆 CHÚC MỪNG! Bạn đã giải quyết thành công tình huống này!")
                        save_history(st.session_state.player_name, s_data['title'], new_score, "WIN")
                        st.session_state.game_active = False
                        
                    elif status == "LOSE":
                        st.error("💀 GAME OVER! Khách hàng đã quá tức giận và rời bỏ.")
                        save_history(st.session_state.player_name, s_data['title'], new_score, "LOSE")
                        st.session_state.game_active = False

            else:
                st.info("Trò chơi đã kết thúc. Nhấn nút 'Thoát' phía trên để chọn bài mới.")

    # --- TRANG 3: BÁO CÁO ADMIN ---
    elif mode == "📊 Báo Cáo (Admin)":
        st.title("Dữ liệu Đào tạo")
        pwd = st.text_input("Mật khẩu quản trị", type="password")
        
        if pwd == "admin123":
            if os.path.exists(HISTORY_FILE):
                df = pd.read_csv(HISTORY_FILE)
                
                # Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Tổng lượt train", len(df))
                m2.metric("Điểm trung bình", f"{df['Score'].mean():.1f}")
                win_rate = (len(df[df['Result']=='WIN']) / len(df)) * 100 if len(df) > 0 else 0
                m3.metric("Tỷ lệ thành công", f"{win_rate:.1f}%")
                
                st.divider()
                st.subheader("Lịch sử chi tiết")
                st.dataframe(df, use_container_width=True)
                
                # Biểu đồ
                st.subheader("Hiệu suất nhân viên")
                if not df.empty:
                    chart_data = df.groupby("Player")["Score"].mean()
                    st.bar_chart(chart_data)
            else:
                st.info("Chưa có dữ liệu nào được ghi nhận.")
        elif pwd:
            st.error("Sai mật khẩu!")

if __name__ == "__main__":
    main()
