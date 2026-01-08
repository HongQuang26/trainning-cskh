import streamlit as st
import json
import os
import time
import pandas as pd
from datetime import datetime
import urllib.parse
import google.generativeai as genai

# ==============================================================================
# 0. CẤU HÌNH AI & API KEY
# ==============================================================================
# Mã API Key của bạn đã được nhúng sẵn
GEMINI_API_KEY = "AIzaSyD5ma9Q__JMZUs6mjBppEHUcUBpsI-wjXA"

def init_ai():
    """Khởi tạo cấu hình cho Gemini"""
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        return True
    except Exception as e:
        st.error(f"Lỗi cấu hình AI: {e}")
        return False

def generate_ai_image_url(scenario_context):
    """
    Hàm này dùng Gemini để 'tưởng tượng' ra khung cảnh, 
    sau đó dùng Pollinations AI để render ảnh.
    """
    try:
        # 1. Dùng Gemini Flash 1.5 để tạo mô tả ảnh (Prompt Engineering)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Based on this scenario description: "{scenario_context}"
        Write a detailed visual description (image prompt) to generate an illustration.
        - Style: Cinematic, Realistic, Professional photography, 4k.
        - Focus on the emotion of the characters and the setting.
        - Output ONLY the prompt in English. Do not add any introduction.
        """
        response = model.generate_content(prompt)
        image_prompt = response.text.strip()
        
        # 2. Tạo URL ảnh từ Pollinations AI (Miễn phí, không cần key tạo ảnh)
        # Seed giúp ảnh cố định, không bị đổi mỗi khi load lại nếu prompt giống nhau
        seed = int(time.time()) 
        encoded_prompt = urllib.parse.quote(image_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=450&nologo=true&seed={seed}&model=flux"
        return image_url
    except Exception as e:
        # Fallback nếu lỗi kết nối
        return "https://placehold.co/800x450?text=AI+Image+Generation+Error"

# ==============================================================================
# 1. CẤU HÌNH & GIAO DIỆN (CONFIGURATION & UI)
# ==============================================================================
st.set_page_config(
    page_title="Service Hero Training (AI Powered)",
    page_icon="🦸‍♂️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stButton button {
        border-radius: 12px; height: auto; min-height: 50px;
        font-weight: 600; border: 1px solid #e0e0e0; white-space: pre-wrap;
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
    .customer-name { font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 8px; }
    .dialogue { font-size: 18px; line-height: 1.6; color: #34495e; font-style: italic; }
    
    .analysis-box-good { background: #d4edda; padding: 10px; border-radius: 5px; color: #155724; margin-bottom: 5px; }
    .analysis-box-bad { background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24; margin-bottom: 5px; }
    
    /* Hiệu ứng loading cho ảnh AI */
    .stImage { transition: opacity 0.5s ease-in-out; }
</style>
""", unsafe_allow_html=True)

# Khởi tạo AI ngay khi chạy app
init_ai()

# ==============================================================================
# 2. DỮ LIỆU KỊCH BẢN (DATASET)
# ==============================================================================
INITIAL_DATA = {
    # --- F&B ---
    "SC_FNB_01": {
        "title": "F&B: Dị vật trong món ăn",
        "desc": "Tóc trong súp. Giải quyết trong 3 bước.",
        "difficulty": "Hard",
        "customer": {"name": "Ms. Jade", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Jade", "traits": ["Kỹ tính", "Reviewer nổi tiếng"], "spending": "Khách mới"},
        "steps": {
            "start": { # TURN 1
                "patience": 30, 
                "text": "Quản lý đâu! Nhìn xem! Một sợi tóc dài trong súp của tôi! Các người cho tôi ăn rác đấy à?",
                "choices": {"A": "Phủ nhận: 'Không phải tóc nhân viên chúng tôi.'", "B": "Hành động: 'Tôi vô cùng xin lỗi! Tôi sẽ xử lý ngay.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -40, "analysis": "❌ Phủ nhận làm mất niềm tin ngay lập tức."}, "B": {"next": "step_2_wait", "change": +10, "analysis": "✅ Hành động ngay lập tức là chính xác."}}
            },
            "step_2_wait": { # TURN 2
                "patience": 40, 
                "text": "(5 phút sau, bạn mang súp mới ra) Tôi hết muốn ăn rồi. Đợi lâu quá tôi mất cả hứng. Bạn tôi ăn gần xong rồi.",
                "choices": {"A": "Thuyết phục: 'Mời chị thử đi ạ, bếp trưởng làm riêng đấy.'", "B": "Chuyển hướng: 'Tôi hoàn toàn hiểu ạ. Tôi xin phép dọn món này đi. Tôi có thể mời chị đồ uống hoặc tráng miệng thay thế không?'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Đừng ép khách ăn khi họ đang bực."}, "B": {"next": "step_3_bill", "change": +20, "analysis": "✅ Tôn trọng cảm xúc và đưa ra giải pháp thay thế."}}
            },
            "step_3_bill": { # TURN 3
                "patience": 60, 
                "text": "Thôi được, cho tôi ly rượu vang. Nhưng tối nay hỏng bét rồi. Mang hóa đơn ra đây.",
                "choices": {"A": "Giảm giá: 'Gửi chị hóa đơn giảm 10% ạ.'", "B": "Đền bù: 'Bữa tối nay nhà hàng xin mời. Và đây là voucher cho lần sau ạ.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ 10% cho một buổi tối tồi tệ là sự xúc phạm."}, "B": {"next": "game_over_good", "change": +40, "analysis": "🏆 Đền bù vượt mong đợi biến thảm họa thành khoảnh khắc Wow."}}
            },
            "game_over_good": {"type": "WIN", "title": "KHÔI PHỤC NIỀM TIN", "text": "Cô ấy bất ngờ vì sự hào phóng và đã tip cho nhân viên.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "MẤT KHÁCH", "text": "Cô ấy thanh toán nhưng để lại đánh giá 1 sao.", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "THẢM HỌA TRUYỀN THÔNG", "text": "Video cãi nhau lan truyền trên mạng.", "score": 0}
        }
    }
}

DB_FILE = "scenarios.json"
HISTORY_FILE = "score_history.csv"

# --- QUẢN LÝ DỮ LIỆU KỊCH BẢN ---
def load_data(force_reset=False):
    """Load từ JSON hoặc tạo mới từ INITIAL_DATA."""
    if force_reset or not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(INITIAL_DATA, f, ensure_ascii=False, indent=4)
        return INITIAL_DATA.copy()
    
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except:
            data = INITIAL_DATA.copy()
        
    updated = False
    for k, v in INITIAL_DATA.items():
        if k not in data:
            data[k] = v
            updated = True
    
    if updated:
        save_data(data)
        
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

# --- QUẢN LÝ LỊCH SỬ ĐIỂM SỐ ---
def save_score(player_name, scenario_title, score, outcome):
    new_record = {
        "Thời gian": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Người chơi": player_name,
        "Kịch bản": scenario_title,
        "Điểm": score,
        "Kết quả": outcome
    }
    
    if os.path.exists(HISTORY_FILE):
        df = pd.read_csv(HISTORY_FILE)
    else:
        df = pd.DataFrame(columns=["Thời gian", "Người chơi", "Kịch bản", "Điểm", "Kết quả"])
    
    new_df = pd.DataFrame([new_record])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(HISTORY_FILE, index=False)

def show_leaderboard():
    if os.path.exists(HISTORY_FILE):
        df = pd.read_csv(HISTORY_FILE)
        if not df.empty:
            df_sorted = df.sort_values(by="Điểm", ascending=False).head(10)
            st.dataframe(df_sorted, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có dữ liệu.")
    else:
        st.info("Chưa có dữ liệu lịch sử. Hãy là người đầu tiên chơi!")

# ==============================================================================
# 3. LOGIC GAME & UI TẠO MỚI
# ==============================================================================
def create_new_scenario_ui():
    st.header("🛠️ Tạo Kịch Bản Mới")
    st.info("💡 Mẹo: Bạn chỉ cần nhập nội dung, Gemini sẽ tự động vẽ ảnh minh họa khi chơi!")
    
    with st.form("creator_form"):
        c1, c2 = st.columns(2)
        with c1:
            title = st.text_input("Tiêu đề", placeholder="VD: Giao hàng trễ")
            desc = st.text_input("Mô tả ngắn", placeholder="VD: Khách đợi 1 tiếng")
            difficulty = st.selectbox("Độ khó", ["Dễ", "Trung bình", "Khó"])
        with c2:
            cust_name = st.text_input("Tên khách", placeholder="VD: Anh Nam")
            cust_trait = st.text_input("Tính cách", placeholder="VD: Đang đói")
            cust_spend = st.text_input("Loại khách", placeholder="VD: Khách VIP")

        st.divider()
        start_text = st.text_area("Tình huống (Khách nói...)", placeholder="Đồ ăn của tôi đâu?!")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("### ✅ Lựa chọn đúng (A)")
            opt_a_text = st.text_input("Nội dung A", placeholder="Xin lỗi + Tặng voucher")
            opt_a_analysis = st.text_input("Tại sao A đúng?", placeholder="Xoa dịu cơn giận.")
            opt_a_result = st.text_input("Kết quả thắng", placeholder="Khách vui vẻ trở lại.")
        with col_b:
            st.markdown("### ❌ Lựa chọn sai (B)")
            opt_b_text = st.text_input("Nội dung B", placeholder="Đổ lỗi kẹt xe")
            opt_b_analysis = st.text_input("Tại sao B sai?", placeholder="Lý do không giải quyết vấn đề.")
            opt_b_result = st.text_input("Kết quả thua", placeholder="Khách bỏ về.")

        if st.form_submit_button("💾 Lưu Kịch Bản"):
            if title and start_text:
                new_id = f"SC_CUSTOM_{int(time.time())}"
                new_entry = {
                    "title": title, "desc": desc, "difficulty": difficulty,
                    "customer": {"name": cust_name, "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=" + cust_name, "traits": [cust_trait], "spending": cust_spend},
                    "steps": {
                        "start": {
                            "patience": 40,
                            # Không cần trường 'img', AI sẽ tự lo
                            "text": start_text,
                            "choices": {"A": opt_a_text, "B": opt_b_text},
                            "consequences": {
                                "A": {"next": "win", "change": 60, "analysis": f"✅ {opt_a_analysis}"},
                                "B": {"next": "lose", "change": -40, "analysis": f"❌ {opt_b_analysis}"}
                            }
                        },
                        "win": {"type": "WIN", "title": "THÀNH CÔNG", "text": opt_a_result, "score": 100},
                        "lose": {"type": "THẤT BẠI", "text": opt_b_result, "score": 0}
                    }
                }
                data = load_data()
                data[new_id] = new_entry
                save_data(data)
                st.success("Đã lưu! Kiểm tra tại Dashboard.")
                time.sleep(1)
                st.rerun()

# KHỞI TẠO SESSION STATE
if 'current_scenario' not in st.session_state: st.session_state.current_scenario = None
if 'current_step' not in st.session_state: st.session_state.current_step = None
if 'patience_meter' not in st.session_state: st.session_state.patience_meter = 50
if 'history' not in st.session_state: st.session_state.history = []
if 'player_name' not in st.session_state: st.session_state.player_name = ""
if 'img_cache' not in st.session_state: st.session_state.img_cache = {} # Cache ảnh AI

def reset_game():
    st.session_state.current_scenario = None
    st.session_state.current_step = None
    st.session_state.patience_meter = 50
    st.session_state.history = []
    # Không clear img_cache để tận dụng lại ảnh đã tạo

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
# 4. CHƯƠNG TRÌNH CHÍNH (MAIN APP)
# ==============================================================================
ALL_SCENARIOS = load_data()

with st.sidebar:
    st.title("🎛️ Menu")
    menu = st.radio("Điều hướng", ["Dashboard", "🛠️ Tạo Kịch Bản Mới"])
    st.divider()
    
    # Nút Reset dữ liệu
    if st.button("⚠️ Khôi phục Dữ liệu gốc", help="Nhấn nút này nếu code mới không cập nhật nội dung"):
        load_data(force_reset=True)
        st.success("Đã khôi phục dữ liệu gốc!")
        time.sleep(1)
        st.rerun()
        
    st.divider()
    st.caption("SERVICE HERO (AI INSIDE)")

if menu == "🛠️ Tạo Kịch Bản Mới":
    reset_game()
    create_new_scenario_ui()

elif menu == "Dashboard":
    # --- PHẦN BẢNG XẾP HẠNG ---
    with st.expander("🏆 Bảng Vàng & Lịch Sử Đấu"):
        show_leaderboard()
    st.divider()

    if st.session_state.current_scenario is None:
        st.title("SERVICE HERO – TRUNG TÂM HUẤN LUYỆN")
        
        # --- YÊU CẦU NHẬP TÊN ---
        if not st.session_state.player_name:
            st.warning("👋 Xin chào! Vui lòng nhập tên của bạn để bắt đầu huấn luyện.")
            st.session_state.player_name = st.text_input("Tên của bạn:", placeholder="Nhập tên và nhấn Enter...")
            if not st.session_state.player_name:
                st.stop()
        else:
            c_name, c_change = st.columns([3, 1])
            with c_name: st.success(f"Chào mừng đặc vụ: **{st.session_state.player_name}**")
            with c_change: 
                if st.button("Đổi tên"): 
                    st.session_state.player_name = ""
                    st.rerun()

        st.caption(f"Hiện có {len(ALL_SCENARIOS)} tình huống. Ảnh minh họa được tạo tự động bởi AI!")
        st.divider()
        
        # --- DANH SÁCH KỊCH BẢN ---
        cols = st.columns(2)
        count = 0
        for key, data in ALL_SCENARIOS.items():
            with cols[count % 2]:
                with st.container(border=True):
                    c1, c2 = st.columns([5, 1])
                    with c1: st.subheader(data['title'])
                    with c2: 
                        if st.button("🗑️", key=f"del_{key}", help="Xóa kịch bản này"):
                            delete_scenario(key)
                            st.rerun()
                    
                    diff_color = "red" if data['difficulty'] == "Hard" or data['difficulty'] == "Khó" else "blue"
                    st.markdown(f":{diff_color}[Độ khó: {data['difficulty']}]")
                    st.write(f"📝 {data['desc']}")
                    
                    if st.button(f"🚀 Bắt đầu", key=f"btn_{key}", use_container_width=True):
                        st.session_state.current_scenario = key
                        st.session_state.current_step = 'start'
                        st.session_state.patience_meter = data['steps']['start']['patience']
                        st.session_state.history = []
                        if 'score_saved' in st.session_state: del st.session_state.score_saved
                        st.rerun()
            count += 1
            
    else:
        # --- MÀN HÌNH CHƠI GAME ---
        s_key = st.session_state.current_scenario
        if s_key not in ALL_SCENARIOS: reset_game(); st.rerun()
        s_data = ALL_SCENARIOS[s_key]
        
        if st.session_state.current_step not in s_data['steps']:
            st.error("Lỗi kịch bản: Bước không tồn tại.")
            if st.button("Quay lại"): reset_game(); st.rerun()
            st.stop()
            
        step_data = s_data['steps'][st.session_state.current_step]
        
        # --- XỬ LÝ ẢNH AI (PHẦN QUAN TRỌNG NHẤT) ---
        cache_key = f"{s_key}_{st.session_state.current_step}"
        current_img_url = ""
        
        # Kiểm tra xem ảnh cho bước này đã có trong cache chưa
        if cache_key in st.session_state.img_cache:
            current_img_url = st.session_state.img_cache[cache_key]
        else:
            # Nếu chưa có, dùng AI tạo mới
            # Nếu trong JSON đã có ảnh cứng (URL Unsplash cũ) thì ưu tiên dùng
            if "img" in step_data and "unsplash" in step_data["img"]:
                 current_img_url = step_data["img"]
            else:
                with st.spinner("🤖 AI đang vẽ lại hiện trường..."):
                    # Tạo context cho AI hiểu
                    context_desc = f"Tình huống: {s_data['title']}. Khách hàng {s_data['customer']['name']} nói: '{step_data.get('text', '')}'."
                    if "type" in step_data: context_desc += f" Kết quả: {step_data['title']}"
                    
                    # Gọi hàm tạo ảnh
                    current_img_url = generate_ai_image_url(context_desc)
                    # Lưu vào cache
                    st.session_state.img_cache[cache_key] = current_img_url
        
        # Sidebar thông tin khách
        with st.sidebar:
            st.divider()
            st.button("❌ Thoát Game", on_click=reset_game, use_container_width=True)
            st.divider()
            cust = s_data['customer']
            st.image(cust['avatar'], width=80)
            st.write(f"**{cust['name']}**")
            st.write(f"Đặc điểm: {', '.join(cust['traits'])}")
            
            color_bar = "green" if st.session_state.patience_meter > 50 else "red"
            st.write(f"Độ kiên nhẫn: :{color_bar}[{st.session_state.patience_meter}%]")
            st.progress(st.session_state.patience_meter / 100)

        # Xử lý hiển thị
        if "type" in step_data:
            # --- MÀN HÌNH KẾT THÚC ---
            st.markdown(f"# {step_data['title']}")
            
            if 'score_saved' not in st.session_state:
                save_score(st.session_state.player_name, s_data['title'], step_data['score'], step_data['type'])
                st.session_state.score_saved = True

            c1, c2 = st.columns([1, 1.5])
            with c1: 
                # Hiển thị ảnh AI
                st.image(current_img_url, use_container_width=True, caption="Ảnh minh họa bởi AI")
            with c2:
                if step_data['type'] == 'WIN': st.success(step_data['text']); st.balloons()
                else: st.error(step_data['text'])
                
                st.metric("Điểm tổng kết", step_data['score'])
                
                if st.button("🔄 Quay về Dashboard", use_container_width=True): 
                    reset_game()
                    st.rerun()
            
            st.divider()
            st.subheader("🔍 Phân tích tình huống:")
            for h in st.session_state.history:
                icon = "✅" if h['change'] > 0 else "❌"
                bg = "analysis-box-good" if h['change'] > 0 else "analysis-box-bad"
                st.markdown(f"<div class='{bg}'><b>{icon} Bạn chọn:</b> {h['choice']}<br><i>👉 {h['analysis']}</i></div>", unsafe_allow_html=True)
        else:
            # --- MÀN HÌNH HỘI THOẠI ---
            st.subheader(s_data['title'])
            c1, c2 = st.columns([1, 2])
            with c1: 
                # Hiển thị ảnh AI
                st.image(current_img_url, use_container_width=True, caption="Ảnh minh họa bởi AI")
            with c2:
                st.markdown(f"<div class='chat-container'><div class='customer-name'>🗣️ {cust['name']}</div><div class='dialogue'>\"{step_data['text']}\"</div></div>", unsafe_allow_html=True)
                
                for k, v in step_data['choices'].items():
                    if st.button(f"{k}. {v}", use_container_width=True): 
                        make_choice(k, step_data)
                        st.rerun()
