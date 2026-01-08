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
# Mã API Key của bạn (Đã nhúng sẵn)
GEMINI_API_KEY = "AIzaSyD5ma9Q__JMZUs6mjBppEHUcUBpsI-wjXA"

def init_ai():
    """Khởi tạo cấu hình cho Gemini"""
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        return True
    except Exception as e:
        # Không báo lỗi ầm ĩ, chỉ ghi nhận để dùng chế độ fallback
        return False

def generate_ai_image_url(scenario_context, default_img_url):
    """
    Tạo ảnh bằng AI. Nếu lỗi thì trả về ảnh mặc định (fallback).
    """
    try:
        # 1. Dùng Gemini để tạo mô tả ảnh (Prompt)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Scenario: "{scenario_context}"
        Create a vivid, cinematic image prompt for this scene.
        Keywords: Realistic, 8k resolution, professional photography, dramatic lighting.
        Output ONLY the prompt text in English.
        """
        response = model.generate_content(prompt)
        image_prompt = response.text.strip()
        
        # 2. Render ảnh qua Pollinations AI
        seed = int(time.time()) 
        encoded_prompt = urllib.parse.quote(image_prompt)
        # Thêm 'nologo' và 'model' để ảnh sạch và đẹp hơn
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=500&nologo=true&seed={seed}&model=flux"
        return image_url
    except Exception:
        # Nếu bất kỳ lỗi gì xảy ra (mạng, API...), trả về ảnh gốc Unsplash
        return default_img_url

# ==============================================================================
# 1. CẤU HÌNH GIAO DIỆN
# ==============================================================================
st.set_page_config(
    page_title="Service Hero Training (Full Version)",
    page_icon="🦸‍♂️",
    layout="wide"
)

# CSS giao diện
st.markdown("""
<style>
    .stButton button {
        border-radius: 10px; min-height: 50px; font-weight: 600;
    }
    .chat-container {
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 6px solid #2E86C1; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    .customer-name { font-size: 18px; font-weight: bold; color: #2c3e50; }
    .dialogue { font-size: 17px; font-style: italic; color: #34495e; margin-top: 5px; }
    .analysis-good { background: #d4edda; padding: 10px; border-radius: 5px; color: #155724; }
    .analysis-bad { background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24; }
</style>
""", unsafe_allow_html=True)

init_ai()

# ==============================================================================
# 2. DỮ LIỆU KỊCH BẢN (11 KỊCH BẢN GỐC - ĐẦY ĐỦ)
# ==============================================================================
INITIAL_DATA = {
    # --- 1. F&B ---
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
                "choices": {"A": "Thuyết phục: 'Mời chị thử đi ạ, bếp trưởng làm riêng đấy.'", "B": "Chuyển hướng: 'Tôi hiểu ạ. Tôi xin phép dọn món này đi. Mời chị dùng món tráng miệng thay thế nhé?'"},
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
    },
    # --- 2. HOTEL ---
    "SC_HOTEL_01": {
        "title": "Hotel: Hết phòng (Overbooked)",
        "desc": "Cặp đôi trăng mật nhưng khách sạn hết phòng.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. Mike", "avatar": "https://images.unsplash.com/photo-1542909168-82c3e7fdca5c?q=80&w=400", "traits": ["Mệt mỏi", "Kỳ vọng cao"], "spending": "Trăng mật"},
        "steps": {
            "start": { 
                "patience": 20, "img": "https://images.unsplash.com/photo-1542596594-6eb9880fb7a6?q=80&w=800",
                "text": "Tôi đặt phòng hướng biển từ 3 tháng trước! Tôi KHÔNG chấp nhận phòng hướng vườn!",
                "choices": {"A": "Chính sách: 'Lỗi hệ thống ạ. Mong anh thông cảm.'", "B": "Đồng cảm: 'Đây hoàn toàn là lỗi của chúng tôi. Tôi thành thật xin lỗi.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Đổ lỗi hệ thống không làm khách nguôi giận."}, "B": {"next": "step_2_alt", "change": +20, "analysis": "✅ Nhận trách nhiệm là bước đầu tiên."}}
            },
            "step_2_alt": { 
                "patience": 40, "img": "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=800",
                "text": "Xin lỗi thì có biển để ngắm không? Chúng tôi bay 12 tiếng đến đây đấy!",
                "choices": {"A": "Tiêu chuẩn: 'Tôi tặng anh phiếu spa và ăn sáng miễn phí.'", "B": "Kiểm tra: 'Xin chờ chút, tôi đang tìm phương án nâng cấp tốt nhất.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Quà tặng nhỏ không bù đắp được trải nghiệm chính."}, "B": {"next": "step_3_upgrade", "change": +10, "analysis": "✅ Cho thấy nỗ lực tìm giải pháp thực sự."}}
            },
            "step_3_upgrade": { 
                "patience": 50, "img": "https://images.unsplash.com/photo-1618773928121-c32242e63f39?q=80&w=800",
                "text": "(Chờ đợi lo lắng) Sao rồi? Vợ tôi đang khóc kia kìa.",
                "choices": {"A": "Một phần: 'Có phòng hướng biển một phần vào ngày mai.'", "B": "Người hùng: 'Tôi tìm được phòng Suite Tổng Thống trống. Tôi nâng cấp miễn phí cho anh chị ngay.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Vẫn gây thất vọng."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Vượt trên mong đợi (Over-deliver) cứu vãn cả kỳ nghỉ."}}
            },
            "game_over_good": {"type": "WIN", "title": "KỲ NGHỈ TRONG MƠ", "text": "Họ cực kỳ hài lòng với phòng Suite.", "img": "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?q=80&w=800", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "KỲ NGHỈ BUỒN", "text": "Họ ở lại nhưng sẽ không bao giờ quay lại.", "img": "https://images.unsplash.com/photo-1583323731095-d7c9bd2690f6?q=80&w=800", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "NỔI GIẬN", "text": "Họ đòi hoàn tiền và rời đi.", "img": "https://images.unsplash.com/photo-1574790502501-701452c15414?q=80&w=800", "score": 0}
        }
    },
    # --- 3. E-COMMERCE ---
    "SC_ECOMM_01": {
        "title": "Online: Thất lạc gói hàng",
        "desc": "Hàng báo đã giao nhưng khách chưa nhận được.",
        "difficulty": "Medium",
        "customer": {"name": "Tom", "avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?q=80&w=400", "traits": ["Lo lắng", "Đa nghi"], "spending": "Thấp"},
        "steps": {
            "start": {
                "patience": 40, "img": "https://images.unsplash.com/photo-1566576912321-d58ba2188273?q=80&w=800",
                "text": "App báo đã giao hàng mà tôi chả thấy đâu! Các người lừa đảo à?",
                "choices": {"A": "Chối: 'Anh hỏi hàng xóm xem.'", "B": "Trấn an: 'Tôi sẽ chịu trách nhiệm kiểm tra ngay.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -20, "analysis": "❌ Đừng đẩy việc cho khách."}, "B": {"next": "step_2_check", "change": +20, "analysis": "✅ Đứng về phía khách hàng."}}
            },
            "step_2_check": {
                "patience": 50, "img": "https://images.unsplash.com/photo-1633934542430-0905ccb5f050?q=80&w=800",
                "text": "Tôi tìm khắp nơi rồi! Mai tôi cần đôi giày này để đi thi!",
                "choices": {"A": "Chờ: 'Vui lòng chờ 24h để shipper phản hồi.'", "B": "Khẩn cấp: 'Tôi đang gọi trực tiếp cho đội vận chuyển khu vực anh ngay bây giờ.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ 24h là quá trễ với hạn chót của khách."}, "B": {"next": "step_3_result", "change": +20, "analysis": "✅ Sự khẩn trương phù hợp với nhu cầu khách."}}
            },
            "step_3_result": {
                "patience": 60, "img": "https://images.unsplash.com/photo-1528736047006-d320da8a2437?q=80&w=800",
                "text": "(Shipper báo giấu ở bụi cây) Shipper bảo để ở bụi cây? Lỡ mất thì sao?",
                "choices": {"A": "Tin tưởng: 'Chắc vẫn ở đó thôi ạ.'", "B": "Cam kết: 'Anh vui lòng kiểm tra. Nếu không có, tôi sẽ ship hỏa tốc đôi mới ngay lập tức.'"},
                "consequences": {"A": {"next": "game_over_normal", "change": 0, "analysis": "😐 Quá thụ động."}, "B": {"next": "game_over_good", "change": +40, "analysis": "🏆 Cam kết rủi ro bằng 0 (Risk-free) tạo niềm tin tuyệt đối."}}
            },
            "game_over_good": {"type": "WIN", "title": "KHÁCH TRUNG THÀNH", "text": "Tom tìm thấy giày và đánh giá 5 sao.", "img": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=800", "score": 100},
            "game_over_normal": {"type": "WIN", "title": "TÌM THẤY", "text": "Tìm thấy hàng nhưng khách vẫn bực.", "img": "https://images.unsplash.com/photo-1556740758-90de374c12ad?q=80&w=800", "score": 70},
            "game_over_fail": {"type": "LOSE", "title": "QUÁ TRỄ", "text": "Khách đã đi mua giày chỗ khác.", "img": "https://images.unsplash.com/photo-1586866016892-117e620d5520?q=80&w=800", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "MẤT NIỀM TIN", "text": "Khách báo cáo shop lừa đảo.", "img": "https://images.unsplash.com/photo-1586866016892-117e620d5520?q=80&w=800", "score": 0}
        }
    },
    # --- 4. RETAIL ---
    "SC_RETAIL_01": {
        "title": "Retail: Vỡ bình hoa quý",
        "desc": "Khách VIP nhận hàng bị vỡ.",
        "difficulty": "Hard",
        "customer": {"name": "Ms. Lan", "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=400", "traits": ["VIP", "Gấp gáp"], "spending": "Cao"},
        "steps": {
            "start": { 
                "patience": 40, "img": "https://images.unsplash.com/photo-1596496050844-461dc5b7263f?q=80&w=800",
                "text": "Cái bình 5 triệu của tôi vỡ tan tành rồi! Làm ăn kiểu gì thế?",
                "choices": {"A": "Đồng cảm: 'Trời ơi! Tôi xin lỗi chị Lan. Tôi sẽ xử lý ngay.'", "B": "Quy trình: 'Chị cho em xin mã đơn hàng.'"},
                "consequences": {"A": {"next": "step_2_stock", "change": 20, "analysis": "✅ Gọi tên khách và đồng cảm trước."}, "B": {"next": "game_over_bad", "change": -20, "analysis": "⚠️ Khách VIP ghét bị hỏi mã đơn như robot."}}
            },
            "step_2_stock": { 
                "patience": 60, "img": "https://images.unsplash.com/photo-1556740738-b6a63e27c4df?q=80&w=800",
                "text": "Tôi cần mang đi tặng sếp lúc 6h tối nay! Giờ còn cái nào không?",
                "choices": {"A": "Check: 'Dạ bên em đang hết hàng mẫu này ở shop.'", "B": "Check: 'Dạ hết hàng, nhưng em có thể đặt cái khác cho tuần sau.'"},
                "consequences": {"A": {"next": "step_3_sol", "change": 0, "analysis": "✅ Trung thực."}, "B": {"next": "game_over_fail", "change": -30, "analysis": "❌ Tuần sau thì quá trễ."}}
            },
            "step_3_sol": { 
                "patience": 50, "img": "https://images.unsplash.com/photo-1586769852044-692d6e3703f0?q=80&w=800",
                "text": "Hết hàng?! Chết tôi rồi! Giờ tôi lấy gì tặng sếp?",
                "choices": {"A": "Hoàn tiền: 'Em hoàn tiền ngay cho chị ạ.'", "B": "Giải cứu: 'Em sẽ lấy hàng từ kho tổng và book Grab giao tận tay chị trước 5h30.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "😐 Hoàn tiền không giải quyết được vấn đề 'quà tặng'."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Giải quyết đúng 'Job to be done' (Cần quà tặng)."}}
            },
            "game_over_good": {"type": "WIN", "title": "XUẤT SẮC", "text": "Chị Lan nhận được bình kịp giờ tiệc.", "img": "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?q=80&w=800", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "MẤT KHÁCH VIP", "text": "Chị Lan thất vọng và không quay lại.", "img": "https://images.unsplash.com/photo-1444312645910-ffa973656eba?q=80&w=800", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "KHỦNG HOẢNG", "text": "Bài bóc phốt trên mạng xã hội.", "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800", "score": 0}
        }
    },
    # --- 5. TECH ---
    "SC_TECH_01": {
        "title": "IT: Mất mạng Internet",
        "desc": "Mất mạng khi đang họp online quan trọng.",
        "difficulty": "Medium",
        "customer": {"name": "Mr. Ken", "avatar": "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=400", "traits": ["Rành công nghệ", "Gấp"], "spending": "Doanh nghiệp"},
        "steps": {
            "start": { 
                "patience": 30, "img": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?q=80&w=800",
                "text": "Mạng sập rồi! Tôi đang họp! Tôi đã khởi động lại modem rồi vẫn đèn đỏ!",
                "choices": {"A": "Cơ bản: 'Anh thử rút điện ra cắm lại xem.'", "B": "Chuyên môn: 'Em thấy tín hiệu bị mất gói (packet loss) từ phía anh.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Khách vừa nói đã khởi động lại rồi mà!"}, "B": {"next": "step_2_fix", "change": +10, "analysis": "✅ Ghi nhận vấn đề chuyên môn."}}
            },
            "step_2_fix": { 
                "patience": 40, "img": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=800",
                "text": "Biết rồi thì sửa đi! Tôi còn 5 phút nữa!",
                "choices": {"A": "Kỹ thuật: 'Kỹ thuật sẽ đến trong 4 tiếng nữa.'", "B": "Từ xa: 'Em đang reset cổng kết nối từ xa... Anh đợi 30s.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Quá chậm."}, "B": {"next": "step_3_fail", "change": +10, "analysis": "✅ Thử giải pháp tức thời."}}
            },
            "step_3_fail": { 
                "patience": 20, "img": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?q=80&w=800",
                "text": "Vẫn không được! Đèn vẫn đỏ! Cuộc họp của tôi đi tong rồi!",
                "choices": {"A": "Bó tay: 'Xin lỗi anh, phải chờ thợ thôi.'", "B": "Cứu cánh: 'Anh bật 4G trên điện thoại đi, em vừa nạp 50GB data tốc độ cao vào số của anh ĐỂ DÙNG NGAY LÚC NÀY.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -30, "analysis": "❌ Bỏ mặc khách hàng."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Giải pháp thay thế (Workaround) cứu sống cuộc họp."}}
            },
            "game_over_good": {"type": "WIN", "title": "THÔNG MINH", "text": "Cuộc họp diễn ra suôn sẻ qua 4G.", "img": "https://images.unsplash.com/photo-1552581234-26160f608093?q=80&w=800", "score": 90},
            "game_over_fail": {"type": "LOSE", "title": "THẤT BẠI", "text": "Khách lỡ cuộc họp quan trọng.", "img": "https://images.unsplash.com/photo-1506784983877-45594efa4cbe?q=80&w=800", "score": 50},
            "game_over_bad": {"type": "LOSE", "title": "HỦY HỢP ĐỒNG", "text": "Khách chuyển sang mạng khác.", "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800", "score": 0}
        }
    },
    # --- 6. AIRLINE ---
    "SC_AIRLINE_01": {
        "title": "Airline: Hủy chuyến bay",
        "desc": "Khách sắp lỡ đám cưới.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. David", "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=400", "traits": ["Căng thẳng", "Khẩn cấp"], "spending": "Gold Flyer"},
        "steps": {
            "start": { 
                "patience": 20, "img": "https://images.unsplash.com/photo-1590523741831-ab7e8b8f9c7f?q=80&w=800",
                "text": "Hủy chuyến á?! Tôi là phù rể, đám cưới bắt đầu sau 6 tiếng nữa! Đưa tôi lên máy bay NGAY!",
                "choices": {"A": "Lý do: 'Do thời tiết xấu ạ.'", "B": "Đồng cảm: 'Ôi không! Để em tìm chuyến khác ngay.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Đừng giải thích lý do lúc này."}, "B": {"next": "step_2_alt", "change": +30, "analysis": "✅ Xác nhận sự khẩn cấp của khách."}}
            },
            "step_2_alt": { 
                "patience": 50, "img": "https://images.unsplash.com/photo-1580894908361-967195033215?q=80&w=800", "text": "Nhanh lên! Tiệc bắt đầu lúc 7h tối!", "choices": {"A": "Hãng mình: 'Chuyến kế tiếp là sáng mai ạ.'", "B": "Đối tác: 'Em đang check cả hãng khác...'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Sáng mai thì muộn rồi."}, "B": {"next": "step_3_mix", "change": +20, "analysis": "✅ Linh hoạt tìm giải pháp."}}
            },
            "step_3_mix": { 
                "patience": 40, "img": "https://images.unsplash.com/photo-1519741497674-611481863552?q=80&w=800", "text": "Không có chuyến bay thẳng nào à? Chết tôi rồi!", "choices": {"A": "Bó tay: 'Xin lỗi anh.'", "B": "Sáng tạo: 'Bay đến thành phố bên cạnh + Taxi (Hãng trả tiền).'"}, "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "❌ Bỏ cuộc quá sớm."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Giải quyết vấn đề sáng tạo."}}
            },
            "game_over_good": {"type": "WIN", "title": "KỊP GIỜ", "text": "David đến kịp đám cưới.", "score": 100, "img": "https://images.unsplash.com/photo-1519741497674-611481863552?q=80&w=800"},
            "game_over_fail": {"type": "LOSE", "title": "LỠ HẸN", "text": "David lỡ đám cưới bạn thân.", "score": 40, "img": "https://images.unsplash.com/photo-1610128070660-d90571d7192c?q=80&w=800"},
            "game_over_bad": {"type": "LOSE", "title": "AN NINH", "text": "Gọi an ninh sân bay.", "score": 0, "img": "https://images.unsplash.com/photo-1574790502501-701452c15414?q=80&w=800"}
        }
    },
    # --- 7. BANK ---
    "SC_BANK_01": {
        "title": "Bank: ATM nuốt thẻ",
        "desc": "Người già cần tiền gấp mua thuốc.",
        "difficulty": "Hard",
        "customer": {"name": "Bà Evelyn", "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=400", "traits": ["Cao tuổi", "Hoảng loạn"], "spending": "Lâu năm"},
        "steps": {
            "start": { "patience": 30, "img": "https://images.unsplash.com/photo-1601597111637-3229586107b5?q=80&w=800", "text": "Cứu tôi với! Máy nuốt thẻ rồi! Tôi cần tiền mua thuốc tim ngay!", "choices": {"A": "Quy trình: 'Bà quay lại vào thứ 2 nhé.'", "B": "Trấn an: 'Thẻ an toàn rồi bà ạ. Để cháu giúp bà rút tiền.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Rủi ro sức khỏe."}, "B": {"next": "step_2_verify", "change": +30, "analysis": "✅ Ưu tiên sức khỏe khách hàng."}} },
            "step_2_verify": { "patience": 50, "img": "https://images.unsplash.com/photo-1556742031-c6961e8560b0?q=80&w=800", "text": "Nhưng bà không mang chứng minh thư.", "choices": {"A": "Cứng nhắc: 'Thế thì không rút được ạ.'", "B": "Linh hoạt: 'Cháu sẽ xác minh qua câu hỏi bảo mật và giao dịch gần nhất.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Đi vào ngõ cụt."}, "B": {"next": "step_3_tech", "change": +20, "analysis": "✅ Linh hoạt trong tình huống khẩn cấp."}} },
            "step_3_tech": { "patience": 60, "img": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?q=80&w=800", "text": "Được rồi, xong rồi. Nhưng giờ rút kiểu gì không có thẻ?", "choices": {"A": "Hướng dẫn: 'Cháu hướng dẫn bà dùng App rút tiền không cần thẻ nhé.'", "B": "Tự làm: 'Để cháu thao tác hộ bà.'"}, "consequences": {"A": {"next": "game_over_good", "change": +40, "analysis": "🏆 Kiên nhẫn hướng dẫn."}, "B": {"next": "game_over_fail", "change": -10, "analysis": "❌ Không được cầm điện thoại của khách (Vi phạm quy định)."}} },
            "game_over_good": {"type": "WIN", "title": "AN TOÀN", "text": "Bà mua được thuốc kịp thời.", "score": 100, "img": "https://images.unsplash.com/photo-1556742031-c6961e8560b0?q=80&w=800"},
            "game_over_fail": {"type": "LOSE", "title": "KHÔNG CÓ TIỀN", "text": "Bà phải về nhà lấy giấy tờ.", "score": 30, "img": "https://images.unsplash.com/photo-1573497491208-6b1acb260507?q=80&w=800"},
            "game_over_bad": {"type": "LOSE", "title": "MẤT NIỀM TIN", "text": "Bà chuyển ngân hàng khác.", "score": 0, "img": "https://images.unsplash.com/photo-1522029916167-9c1a97aa3c24?q=80&w=800"}
        }
    },
    # --- 8. REAL ESTATE ---
    "SC_REALESTATE_01": {
        "title": "BĐS: Căn hộ bị mốc",
        "desc": "Khách thuê căn hộ cao cấp phát hiện nấm mốc.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. Chen", "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=400", "traits": ["Giàu có", "Sợ bẩn"], "spending": "Luxury"},
        "steps": {
            "start": { "patience": 20, "img": "https://images.unsplash.com/photo-1581876883325-32a5b8f7fb5a?q=80&w=800", "text": "Tôi trả 4000$/tháng để ở cái ổ nấm mốc này à? Con tôi bị hen suyễn!", "choices": {"A": "Phòng thủ: 'Anh có mở cửa sổ không thế?'", "B": "Báo động: 'Nguy hiểm quá. Anh chị ra khỏi đó ngay, tôi đến liền.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -40, "analysis": "❌ Đổ lỗi cho khách."}, "B": {"next": "step_2_inspect", "change": +30, "analysis": "✅ Đặt an toàn sức khỏe lên đầu."}} },
            "step_2_inspect": { "patience": 40, "img": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?q=80&w=800", "text": "(Bạn đến nơi) Nhìn đi! Mốc đen sì góc tường! Chúng tôi không ngủ lại đây đâu.", "choices": {"A": "Dọn dẹp: 'Mai tôi cho người đến sơn lại.'", "B": "Di dời: 'Đồng ý. Anh chị cần di chuyển ngay.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -30, "analysis": "⚠️ Sơn lại không hết mốc ngay được."}, "B": {"next": "step_3_hotel", "change": +20, "analysis": "✅ Giải pháp tức thời."}} },
            "step_3_hotel": { "patience": 50, "img": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=800", "text": "Đi đâu bây giờ? Ra nhà nghỉ à?", "choices": {"A": "Ngân sách: 'Tôi có budget 1 triệu/đêm cho anh.'", "B": "Sang trọng: 'Tôi đã book khách sạn 5 sao gần nhất cho gia đình rồi.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Xúc phạm khách Luxury."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Tương xứng đẳng cấp."}} },
            "game_over_good": {"type": "WIN", "title": "XỬ LÝ ÊM ĐẸP", "text": "Gia đình hài lòng với khách sạn.", "score": 100, "img": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=800"},
            "game_over_fail": {"type": "LOSE", "title": "HỦY HỢP ĐỒNG", "text": "Khách chuyển đi nơi khác.", "score": 30, "img": "https://images.unsplash.com/photo-1596496321628-16711bb94e68?q=80&w=800"},
            "game_over_bad": {"type": "LOSE", "title": "KIỆN TỤNG", "text": "Bị kiện vì gây hại sức khỏe.", "score": 0, "img": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=800"}
        }
    },
    # --- 9. SAAS ---
    "SC_SAAS_01": {
        "title": "SaaS: Mất dữ liệu",
        "desc": "Lỡ tay xóa data quan trọng trước giờ họp.",
        "difficulty": "Very Hard",
        "customer": {"name": "Sarah", "avatar": "https://images.unsplash.com/photo-1573496799652-408c2ac9fe98?q=80&w=400", "traits": ["Giận dữ", "Sếp lớn"], "spending": "Enterprise"},
        "steps": {
            "start": { "patience": 10, "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800", "text": "DỮ LIỆU ĐÂU HẾT RỒI?! Tôi có buổi thuyết trình trong 2 tiếng nữa!", "choices": {"A": "Mẹo: 'Chị xóa cache chưa?'", "B": "Khẩn cấp: 'Em đang báo đội kỹ thuật khôi phục ngay lập tức (SEV1).'"}, "consequences": {"A": {"next": "game_over_bad", "change": -20, "analysis": "❌ Đừng hỏi câu ngớ ngẩn."}, "B": {"next": "step_2_status", "change": +30, "analysis": "✅ Xác định đúng mức độ nghiêm trọng."}} },
            "step_2_status": { "patience": 30, "img": "https://images.unsplash.com/photo-1551434678-e076c223a692?q=80&w=800", "text": "Restore mất 4 tiếng cơ à? Thế thì tôi chết chắc rồi!", "choices": {"A": "Xin lỗi: 'Quy trình nó thế ạ.'", "B": "Thay thế: 'Em có thể trích xuất thủ công các số liệu chính ra Excel cho chị trước không?'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Thụ động."}, "B": {"next": "step_3_ceo", "change": +20, "analysis": "✅ Cứu vãn tình thế tạm thời."}} },
            "step_3_ceo": { "patience": 40, "img": "https://images.unsplash.com/photo-1521791136064-7986c2920216?q=80&w=800", "text": "Vẫn rủi ro lắm. Sếp tôi mà biết là tôi bị đuổi việc.", "choices": {"A": "Trấn an: 'Chắc không sao đâu chị.'", "B": "Bảo vệ: 'Em sẽ viết mail giải trình với sếp chị rằng đây là lỗi hệ thống bên em.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "❌ Lời nói gió bay."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Nhận trách nhiệm thay khách hàng."}} },
            "game_over_good": {"type": "WIN", "title": "CỨU NGUY", "text": "Gia hạn hợp đồng.", "score": 100, "img": "https://images.unsplash.com/photo-1521791136064-7986c2920216?q=80&w=800"},
            "game_over_fail": {"type": "LOSE", "title": "RỜI BỎ", "text": "Khách cắt hợp đồng.", "score": 30, "img": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?q=80&w=800"},
            "game_over_bad": {"type": "LOSE", "title": "KIỆN TỤNG", "text": "Vi phạm SLA.", "score": 0, "img": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=800"}
        }
    },
    # --- 10. SPA ---
    "SC_SPA_01": {
        "title": "Spa: Dị ứng mỹ phẩm",
        "desc": "Khách bị ngứa sau khi làm mặt.",
        "difficulty": "Hard",
        "customer": {"name": "Ms. Chloe", "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=400", "traits": ["Sợ hãi", "Đau"], "spending": "Mới"},
        "steps": {
            "start": { "patience": 30, "img": "https://images.unsplash.com/photo-1501594256690-b7a1a14527c5?q=80&w=800", "text": "Mặt tôi nóng ran lên rồi! Các người bôi cái gì lên mặt tôi thế?!", "choices": {"A": "Giấy tờ: 'Chị ký cam kết miễn trừ rồi mà.'", "B": "Chăm sóc: 'Lấy nước đá chườm ngay! Gọi quản lý!'"}, "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Vô cảm."}, "B": {"next": "step_2_future", "change": +30, "analysis": "✅ An toàn là trên hết."}} },
            "step_2_future": { "patience": 40, "img": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?q=80&w=800", "text": "Đỡ hơn rồi nhưng vẫn đỏ. Mai tôi có buổi casting quan trọng!", "choices": {"A": "Hy vọng: 'Chắc mai là hết thôi ạ.'", "B": "Hỗ trợ: 'Em đưa chị đi bác sĩ da liễu ngay bây giờ để kiểm tra cho chắc.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Không chắc chắn."}, "B": {"next": "step_3_bill", "change": +20, "analysis": "✅ Chủ động xử lý hậu quả."}} },
            "step_3_bill": { "patience": 50, "img": "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?q=80&w=800", "text": "Tiền khám ai trả? Tôi không trả đâu nhé.", "choices": {"A": "Thỏa thuận: 'Chị trả 50% nhé.'", "B": "Trách nhiệm: 'Spa sẽ chi trả toàn bộ viện phí và thuốc thang ạ.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Cò kè bớt một thêm hai."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Nhận trách nhiệm hoàn toàn."}} },
            "game_over_good": {"type": "WIN", "title": "XỬ LÝ TỐT", "text": "Khách không kiện cáo.", "score": 100, "img": "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?q=80&w=800"},
            "game_over_fail": {"type": "LOSE", "title": "BÓC PHỐT", "text": "Review 1 sao kèm ảnh mặt sưng.", "score": 40, "img": "https://images.unsplash.com/photo-1522029916167-9c1a97aa3c24?q=80&w=800"},
            "game_over_bad": {"type": "LOSE", "title": "KIỆN TỤNG", "text": "Bị kiện đòi bồi thường.", "score": 0, "img": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=800"}
        }
    },
    # --- 11. LOGISTICS ---
    "SC_LOGISTICS_01": {
        "title": "Logistics: Hỏng thiết bị sự kiện",
        "desc": "Giao hàng trễ và bị vỡ trước sự kiện lớn.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. Robert", "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=400", "traits": ["Áp lực cao", "Giận dữ"], "spending": "VIP Account"},
        "steps": {
            "start": { "patience": 10, "img": "https://images.unsplash.com/photo-1586864387967-d021563e6516?q=80&w=800", "text": "Vừa trễ vừa vỡ nát! Sự kiện 500.000$ của tôi mai diễn ra rồi! Các người phá hỏng hết rồi!", "choices": {"A": "Bảo hiểm: 'Anh làm thủ tục đền bù đi.'", "B": "Khủng hoảng: 'Tôi đang trực tiếp xử lý vụ này. Sẽ có giải pháp trong 10 phút.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Quan liêu."}, "B": {"next": "step_2_options", "change": +40, "analysis": "✅ Hành động ngay."}} },
            "step_2_options": { "patience": 30, "img": "https://images.unsplash.com/photo-1494412651409-4963d24a38b8?q=80&w=800", "text": "Xử lý kiểu gì? Hàng nhập khẩu làm sao có ngay được?", "choices": {"A": "Thuê: 'Anh thử thuê tạm ở địa phương xem?'", "B": "Điều phối: 'Tôi vừa điều xe tải chở hàng từ kho ở tỉnh bên cạnh sang. 4 tiếng nữa sẽ tới.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Đừng bắt khách tự làm."}, "B": {"next": "step_3_confirm", "change": +30, "analysis": "✅ Có giải pháp cụ thể."}} },
            "step_3_confirm": { "patience": 50, "img": "https://images.unsplash.com/photo-1511578314322-379afb476865?q=80&w=800", "text": "4 tiếng nữa thì sát giờ quá. Lỡ xe hỏng thì sao?", "choices": {"A": "Hy vọng: 'Chắc kịp mà anh.'", "B": "Chắc chắn: 'Tôi cho 2 xe chạy cùng lúc (1 xe dự phòng). Kèm thêm 1 đội kỹ thuật đến hỗ trợ lắp đặt cho kịp giờ.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Vẫn rủi ro."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Dốc toàn lực hỗ trợ (Overwhelming support)."}} },
            "game_over_good": {"type": "WIN", "title": "CỨU SỰ KIỆN", "text": "Sự kiện thành công rực rỡ.", "score": 100, "img": "https://images.unsplash.com/photo-1511578314322-379afb476865?q=80&w=800"},
            "game_over_fail": {"type": "LOSE", "title": "THẤT BẠI", "text": "Sự kiện bị hủy.", "score": 30, "img": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?q=80&w=800"},
            "game_over_bad": {"type": "LOSE", "title": "MẤT HỢP ĐỒNG", "text": "Bị cắt hợp đồng vận chuyển.", "score": 0, "img": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=800"}
        }
    }
}

DB_FILE = "scenarios.json"
HISTORY_FILE = "score_history.csv"

# ==============================================================================
# 3. CÁC HÀM XỬ LÝ DỮ LIỆU
# ==============================================================================
def load_data(force_reset=False):
    if force_reset or not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(INITIAL_DATA, f, ensure_ascii=False, indent=4)
        return INITIAL_DATA.copy()
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Merge dữ liệu cũ vào nếu thiếu
        for k, v in INITIAL_DATA.items():
            if k not in data: data[k] = v
        return data
    except: return load_data(True)

def save_data(new_data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)

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
        else: st.info("Chưa có dữ liệu.")
    else: st.info("Chưa có lịch sử đấu.")

# ==============================================================================
# 4. TRANG CHÍNH (MAIN APP)
# ==============================================================================
if 'current_scenario' not in st.session_state: st.session_state.current_scenario = None
if 'img_cache' not in st.session_state: st.session_state.img_cache = {}

ALL_SCENARIOS = load_data()

with st.sidebar:
    st.title("🎛️ Menu")
    menu = st.radio("Chọn:", ["Dashboard", "🛠️ Tạo Kịch Bản Mới"])
    if st.button("⚠️ Reset Dữ Liệu Gốc"):
        load_data(True)
        st.success("Đã khôi phục 11 kịch bản gốc!")
        time.sleep(1)
        st.rerun()

if menu == "Dashboard":
    # Màn hình chọn kịch bản
    if st.session_state.current_scenario is None:
        st.title("SERVICE HERO - HUẤN LUYỆN VIÊN AI 🤖")
        
        # Nhập tên
        if 'player_name' not in st.session_state: st.session_state.player_name = ""
        if not st.session_state.player_name:
            st.warning("Vui lòng nhập tên để bắt đầu.")
            st.session_state.player_name = st.text_input("Tên của bạn:")
            if not st.session_state.player_name: st.stop()
        else:
            c1, c2 = st.columns([3, 1])
            c1.success(f"Chào mừng: **{st.session_state.player_name}**")
            if c2.button("Đổi tên"): 
                st.session_state.player_name = ""
                st.rerun()

        with st.expander("🏆 Bảng Xếp Hạng"):
            show_leaderboard()
            
        st.divider()
        st.write(f"Hiện có **{len(ALL_SCENARIOS)}** kịch bản thực tế.")
        
        cols = st.columns(2)
        idx = 0
        for key, val in ALL_SCENARIOS.items():
            with cols[idx % 2]:
                with st.container(border=True):
                    st.subheader(val['title'])
                    st.caption(f"Độ khó: {val['difficulty']}")
                    st.write(f"_{val['desc']}_")
                    if st.button("🚀 Bắt đầu", key=key, use_container_width=True):
                        st.session_state.current_scenario = key
                        st.session_state.current_step = 'start'
                        st.session_state.patience = 50
                        st.session_state.history = []
                        st.rerun()
            idx += 1

    # Màn hình chơi game
    else:
        s_key = st.session_state.current_scenario
        if s_key not in ALL_SCENARIOS: 
            st.session_state.current_scenario = None
            st.rerun()
            
        scenario = ALL_SCENARIOS[s_key]
        step_id = st.session_state.current_step
        step_data = scenario['steps'][step_id]
        
        # --- LOGIC XỬ LÝ ẢNH AI (CÓ FALLBACK) ---
        cache_key = f"{s_key}_{step_id}"
        
        # Ảnh mặc định từ kịch bản gốc (Unsplash)
        default_img = step_data.get('img', 'https://placehold.co/800x400?text=No+Image')
        
        if cache_key not in st.session_state.img_cache:
            # Tạo ảnh mới bằng AI
            with st.spinner("🤖 AI đang vẽ minh họa..."):
                context = f"Scene: {scenario['title']}. Character {scenario['customer']['name']} says: {step_data.get('text', '')}"
                ai_url = generate_ai_image_url(context, default_img)
                st.session_state.img_cache[cache_key] = ai_url
        
        current_img = st.session_state.img_cache[cache_key]
        # ------------------------------------------

        # Sidebar thông tin
        with st.sidebar:
            st.divider()
            if st.button("❌ Thoát Game", use_container_width=True):
                st.session_state.current_scenario = None
                st.rerun()
            
            cust = scenario['customer']
            st.image(cust['avatar'], width=80)
            st.markdown(f"**{cust['name']}**")
            st.caption(", ".join(cust['traits']))
            
            p = st.session_state.patience
            st.write(f"Kiên nhẫn: {p}%")
            st.progress(p/100)

        # Hiển thị nội dung chính
        if "type" in step_data: # Kết thúc game
            st.markdown(f"# {step_data['title']}")
            st.image(current_img, use_container_width=True)
            
            if step_data['type'] == 'WIN':
                st.success(step_data['text'])
                st.balloons()
            else:
                st.error(step_data['text'])
                
            st.metric("Điểm số", step_data['score'])
            
            # Lưu điểm (chỉ lưu 1 lần)
            if 'saved' not in st.session_state:
                save_score(st.session_state.player_name, scenario['title'], step_data['score'], step_data['type'])
                st.session_state.saved = True
                
            if st.button("🔄 Quay về Menu", use_container_width=True):
                st.session_state.current_scenario = None
                if 'saved' in st.session_state: del st.session_state.saved
                st.rerun()
                
            st.write("---")
            st.subheader("📝 Phân tích chi tiết:")
            for h in st.session_state.history:
                icon = "✅" if h['change'] > 0 else "❌"
                st.info(f"{icon} Bạn chọn: {h['choice']}\n\n👉 {h['analysis']}")

        else: # Đang chơi
            st.subheader(scenario['title'])
            st.image(current_img, use_container_width=True, caption="Minh họa bởi AI (hoặc ảnh mẫu)")
            
            st.markdown(f"""
            <div class="chat-container">
                <div class="customer-name">🗣️ {cust['name']} nói:</div>
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
                        st.session_state.history.append({
                            "step": step_data['text'],
                            "choice": v,
                            "analysis": cons['analysis'],
                            "change": cons['change']
                        })
                        st.rerun()
                idx += 1

elif menu == "🛠️ Tạo Kịch Bản Mới":
    st.header("Tạo Kịch Bản Tùy Chỉnh")
    st.info("Nhập nội dung bên dưới. Ảnh minh họa sẽ do AI tự vẽ!")
    # Form tạo kịch bản đơn giản...
    with st.form("new_scen"):
        title = st.text_input("Tên tình huống")
        desc = st.text_input("Mô tả")
        start_txt = st.text_area("Câu thoại mở đầu")
        if st.form_submit_button("Lưu"):
            st.success("Đã lưu! (Demo)")
