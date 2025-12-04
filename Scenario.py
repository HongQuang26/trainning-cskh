import streamlit as st
import time

# ==============================================================================
# 1. CẤU HÌNH & GIAO DIỆN (UI/UX)
# ==============================================================================
st.set_page_config(
    page_title="Training Master Pro",
    page_icon="💎",
    layout="wide"
)

# CSS tùy chỉnh để giao diện trông "Đắt tiền" hơn
st.markdown("""
<style>
    /* Tùy chỉnh nút bấm */
    .stButton button {
        border-radius: 12px;
        height: auto;
        min-height: 60px;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 1px solid #e0e0e0;
        white-space: pre-wrap; /* Để text dài tự xuống dòng */
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        border-color: #2E86C1;
        color: #2E86C1;
        background-color: #f8f9fa;
    }
    
    /* Khung hội thoại */
    .chat-container {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 20px;
        border-left: 8px solid #2E86C1;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .customer-name {
        font-size: 18px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 8px;
    }
    .dialogue {
        font-size: 18px;
        line-height: 1.6;
        color: #34495e;
        font-style: italic;
    }
    
    /* Thẻ thông tin bên trái */
    .profile-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #dee2e6;
    }
    
    /* Phân tích */
    .analysis-box-good {
        background: #d4edda;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #28a745;
        color: #155724;
        margin-bottom: 10px;
    }
    .analysis-box-bad {
        background: #f8d7da;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #dc3545;
        color: #721c24;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. KHO DỮ LIỆU KỊCH BẢN CHI TIẾT
# ==============================================================================

ALL_SCENARIOS = {
    "SC_FNB_01": {
        "title": "F&B: Sự Cố Vật Thể Lạ",
        "desc": "Khách hàng phát hiện có tóc trong món súp tại nhà hàng 5 sao.",
        "difficulty": "Hard",
        "customer": {
            "name": "Chị Ngọc (Food Reviewer)",
            "avatar": "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?q=80&w=400",
            "traits": ["Khó tính", "Reviewer nổi tiếng", "Thích sự hoàn hảo"],
            "spending": "Khách mới (Rủi ro cao)"
        },
        "steps": {
            "start": {
                "patience": 30, 
                "img": "https://images.unsplash.com/photo-1533777857889-4be7c70b33f7?q=80&w=800",
                "text": "(Giọng đanh lại, chỉ vào bát súp) Quản lý đâu? Ra đây tôi bảo. Nhà hàng 5 sao kiểu gì mà trong súp lại có sợi tóc dài ngoằng thế này? Các người định cho khách ăn đồ bẩn à? Thật kinh tởm!",
                "choices": {
                    "A": "Chối bỏ: 'Dạ chị ơi, bếp bên em toàn tóc đen và đội mũ kỹ lắm, tóc này màu vàng lạ quá. Chị xem lại có phải tóc của chị rơi xuống không?'",
                    "B": "Tiếp nhận & Hành động: 'Dạ em thành thật xin lỗi chị Ngọc về trải nghiệm tồi tệ này! Em nhìn thấy rồi ạ. Em xin phép thu hồi món này ngay lập tức.'"
                },
                "consequences": {
                    "A": {"next": "game_over_bad_fnb", "change": -40, "analysis": "❌ SAI LẦM CHẾT NGƯỜI: Tuyệt đối không được đổ lỗi ngược lại cho khách hàng về vấn đề vệ sinh. Tranh cãi lúc này là tự sát."},
                    "B": {"next": "step_compensate", "change": +20, "analysis": "✅ CHUẨN XÁC: Công nhận vấn đề ngay lập tức và hành động (thu hồi món) để giảm bớt sự ghê tẩm của khách."}
                }
            },
            "step_compensate": {
                "patience": 50,
                "img": "https://images.unsplash.com/photo-1552581234-26160f608093?q=80&w=800",
                "text": "(Vẫn còn khó chịu) Tôi hết hứng ăn uống rồi. Bữa tối kỷ niệm của vợ chồng tôi bị phá hỏng hoàn toàn. Giờ các bạn tính sao?",
                "choices": {
                    "A": "Giải pháp tiêu chuẩn: 'Dạ em xin phép đổi cho chị bát súp mới và giảm giá 10% tổng hóa đơn bữa nay để xin lỗi ạ.'",
                    "B": "Giải pháp WOW: 'Dạ em rất hiểu sự thất vọng của chị. Em xin phép MIỄN PHÍ toàn bộ bữa tối nay. Ngoài ra, bếp trưởng xin gửi tặng anh chị món tráng miệng đặc biệt thay lời xin lỗi ạ.'"
                },
                "consequences": {
                    "A": {"next": "game_over_fail_fnb", "change": -10, "analysis": "⚠️ TRUNG BÌNH: Với lỗi vệ sinh nghiêm trọng ở nhà hàng 5 sao, giảm 10% là không đủ. Khách vẫn cảm thấy thiệt thòi."},
                    "B": {"next": "game_over_good_fnb", "change": +50, "analysis": "🏆 XUẤT SẮC: 'Over-compensate' (Đền bù vượt mong đợi) là cách duy nhất để cứu vãn uy tín trong tình huống này."}
                }
            },
            "game_over_good_fnb": {
                "type": "WIN",
                "title": "⭐ LẤY LẠI NIỀM TIN",
                "img": "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?q=80&w=800",
                "text": "Chị Ngọc bất ngờ trước cách xử lý hào phóng. Chị ấy viết bài review khen ngợi cách xử lý khủng hoảng chuyên nghiệp thay vì bóc phốt.",
                "score": 100
            },
            "game_over_fail_fnb": {
                "type": "LOSE",
                "title": "😐 KHÁCH HÀNG KHÔNG QUAY LẠI",
                "img": "https://images.unsplash.com/photo-1522029916167-9c1a97aa3c24?q=80&w=800",
                "text": "Khách chấp nhận giảm 10% nhưng ăn qua loa rồi về. Họ đánh giá 2 sao trên Google Maps về vấn đề vệ sinh.",
                "score": 40
            },
            "game_over_bad_fnb": {
                "type": "LOSE",
                "title": "☠️ THẢM HỌA TRUYỀN THÔNG",
                "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800",
                "text": "Chị Ngọc quay video cảnh tranh cãi đăng lên TikTok: 'Nhà hàng 5 sao đổ oan cho khách bỏ tóc vào đồ ăn'. Video lên xu hướng ngay lập tức.",
                "score": 0
            }
        }
    },

    "SC_HOTEL_01": {
        "title": "Hotel: Hết Phòng (Overbooked)",
        "desc": "Khách đi trăng mật đến nơi thì lễ tân báo hết phòng View Biển đã đặt.",
        "difficulty": "Very Hard",
        "customer": {
            "name": "Anh Minh & Chị Hoa",
            "avatar": "https://images.unsplash.com/photo-1542909168-82c3e7fdca5c?q=80&w=400",
            "traits": ["Mệt mỏi sau chuyến bay", "Kỳ vọng cao (Trăng mật)", "Dễ xúc động"],
            "spending": "Gói Trăng mật (10tr/đêm)"
        },
        "steps": {
            "start": {
                "patience": 20,
                "img": "https://images.unsplash.com/photo-1542596594-6eb9880fb7a6?q=80&w=800",
                "text": "(Anh Minh lớn tiếng) Cái gì? Hết phòng là sao? Tôi đã đặt và thanh toán trước cả tháng nay rồi! Đây là kỳ nghỉ trăng mật, tôi không chấp nhận phòng hướng vườn đâu!",
                "choices": {
                    "A": "Đổ lỗi hệ thống: 'Dạ em rất xin lỗi. Do hệ thống đặt phòng bị lỗi overbook nên bên em không giữ được phòng View Biển ạ. Mong anh chị thông cảm.'",
                    "B": "Đồng cảm & Nhận lỗi: 'Dạ em thành thật xin lỗi anh Minh, chị Hoa! Đây hoàn toàn là lỗi của bên em khi không đảm bảo được phòng cho kỳ nghỉ quan trọng này.'"
                },
                "consequences": {
                    "A": {"next": "game_over_bad_hotel", "change": -30, "analysis": "❌ TỆ: Khách hàng không quan tâm lý do hệ thống. Câu 'Mong anh chị thông cảm' nghe rất sáo rỗng."},
                    "B": {"next": "step_upgrade", "change": +20, "analysis": "✅ TỐT: Nhận lỗi trực diện, gọi đúng tên khách, thể hiện sự thấu hiểu tầm quan trọng của chuyến đi."}
                }
            },
            "step_upgrade": {
                "patience": 40,
                "img": "https://images.unsplash.com/photo-1618773928121-c32242e63f39?q=80&w=800",
                "text": "(Chị Hoa rơm rớm nước mắt) Nhưng bọn mình đã mơ về căn phòng view biển đó... Giờ ở phòng hướng vườn thì còn gì là trăng mật nữa.",
                "choices": {
                    "A": "Giải pháp Nâng cấp: 'Dạ View Biển đã hết, nhưng để chuộc lỗi, em xin NÂNG CẤP miễn phí anh chị lên hạng SUITE Tổng Thống (đắt gấp đôi) trong 2 đêm đầu ạ.'",
                    "B": "Giải pháp Hoàn tiền: 'Dạ nếu ở phòng Hướng Vườn, bên em sẽ hoàn lại tiền chênh lệch và giảm thêm 20% giá phòng cho anh chị ạ.'"
                },
                "consequences": {
                    "A": {"next": "game_over_good_hotel", "change": +60, "analysis": "🏆 TUYỆT VỜI: Khi không có cái khách muốn, hãy đưa cái tốt hơn hẳn. Suite Tổng Thống là trải nghiệm 'Wow' bù đắp nỗi thất vọng."},
                    "B": {"next": "game_over_fail_hotel", "change": -20, "analysis": "⚠️ KÉM: Với khách trăng mật, TRẢI NGHIỆM quan trọng hơn TIỀN. Hoàn tiền không cứu vãn được cảm xúc."}
                }
            },
            "game_over_good_hotel": {
                "type": "WIN",
                "title": "🥂 KỲ NGHỈ TRONG MƠ",
                "img": "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?q=80&w=800",
                "text": "Anh chị choáng ngợp trước căn Suite sang trọng. Họ cảm thấy được đối xử như VIP và sự cố trở thành kỷ niệm đẹp.",
                "score": 100
            },
            "game_over_fail_hotel": {
                "type": "LOSE",
                "title": "😢 KỲ TRĂNG MẬT BUỒN",
                "img": "https://images.unsplash.com/photo-1583323731095-d7c9bd2690f6?q=80&w=800",
                "text": "Họ miễn cưỡng nhận phòng và tiền hoàn lại, nhưng tâm trạng bị ảnh hưởng nặng nề. Họ sẽ không quay lại.",
                "score": 40
            },
            "game_over_bad_hotel": {
                "type": "LOSE",
                "title": "🤬 CƠN THỊNH NỘ",
                "img": "https://images.unsplash.com/photo-1574790502501-701452c15414?q=80&w=800",
                "text": "Anh Minh đòi gặp Giám đốc và yêu cầu hoàn tiền 100% để chuyển khách sạn khác. Cả sảnh náo loạn.",
                "score": 0
            }
        }
    },

    "SC_ECOMM_01": {
        "title": "Online: Hàng Lạc Trôi",
        "desc": "App báo giao thành công nhưng khách chưa nhận được hàng (giày đi thi).",
        "difficulty": "Medium",
        "customer": {
            "name": "Bạn Tuấn (Sinh viên)",
            "avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?q=80&w=400",
            "traits": ["Lo lắng mất tiền", "Nghi ngờ shipper", "Cần gấp"],
            "spending": "Thấp"
        },
        "steps": {
            "start": {
                "patience": 40,
                "img": "https://images.unsplash.com/photo-1566576912321-d58ba2188273?q=80&w=800",
                "text": "Alo shop ơi, app báo giao thành công rồi mà mình chưa nhận được? Mình hỏi lễ tân cũng không có. Có khi nào shipper lấy luôn rồi không? Mình cần giày gấp!",
                "choices": {
                    "A": "Đẩy trách nhiệm: 'Chào bạn, hệ thống báo giao rồi ạ. Bạn thử hỏi lại người nhà hoặc hàng xóm xem.'",
                    "B": "Trấn an: 'Chào Tuấn, shop đã ghi nhận. Bạn đừng lo, shop sẽ chịu trách nhiệm làm việc với bên vận chuyển để tìm hàng cho bạn ngay.'"
                },
                "consequences": {
                    "A": {"next": "step_panic", "change": -20, "analysis": "⚠️ KÉM: Đẩy trách nhiệm lại cho khách đang hoang mang gây ức chế. Khách đã nói hỏi lễ tân rồi."},
                    "B": {"next": "step_investigate", "change": +20, "analysis": "✅ TỐT: Câu 'shop sẽ chịu trách nhiệm' là liều thuốc an thần, khẳng định bạn đứng về phía khách."}
                }
            },
            "step_panic": {
                "patience": 20,
                "img": "https://images.unsplash.com/photo-1633934542430-0905ccb5f050?q=80&w=800",
                "text": "Mình ở trọ một mình! Mình hỏi hết rồi không ai nhận cả. Rõ ràng là lừa đảo! Trả tiền lại cho tôi!",
                "choices": {
                    "A": "Cứng rắn: 'Bạn bình tĩnh lại, bên mình làm ăn uy tín. Bạn cứ chờ để check đã.'",
                    "B": "Cam kết mạnh: 'Mình rất hiểu bạn đang lo. Mình cam kết nếu đến 6h chiều nay không tìm thấy, shop sẽ SHIP HỎA TỐC đôi mới cho bạn kịp đi thi.'",
                },
                "consequences": {
                    "A": {"next": "game_over_bad_ecomm", "change": -20, "analysis": "❌ TỆ: Bảo khách đang hoảng loạn 'bình tĩnh' là vô dụng."},
                    "B": {"next": "game_over_good_ecomm_rescue", "change": +50, "analysis": "✅ XUẤT SẮC: Đưa ra cam kết cho tình huống xấu nhất. Khách yên tâm vì đằng nào cũng có giày."}
                }
            },
             "step_investigate": {
                "patience": 60,
                "img": "https://images.unsplash.com/photo-1528736047006-d320da8a2437?q=80&w=800",
                "text": "(15p sau) Alo Tuấn ơi, shipper báo gửi tạm ở chốt bảo vệ cổng sau, không phải lễ tân ạ. Ảnh xin lỗi vì chưa kịp báo. Bạn xuống xem giúp shop nhé.",
                "choices": {
                    "A": "Kết thúc đơn giản: 'Dạ vâng lỗi do shipper ạ. Bạn xuống lấy giúp mình nha.'",
                    "B": "Kết thúc chu đáo: 'Thật xin lỗi Tuấn vì làm bạn lo lắng. Bạn xuống cổng sau lấy giúp shop nhé. Shop tặng bạn mã freeship lần sau tạ lỗi nha.'"
                },
                "consequences": {
                    "A": {"next": "game_over_normal_ecomm", "change": +10, "analysis": "🙂 TẠM ỔN: Vấn đề được giải quyết, nhưng trải nghiệm chỉ ở mức trung bình."},
                    "B": {"next": "game_over_good_ecomm", "change": +30, "analysis": "✅ TỐT: Nhận lỗi thay shipper và có quà nhỏ (freeship) xoa dịu sự khó chịu."}
                }
            },
            "game_over_good_ecomm": {
                "type": "WIN",
                "title": "👍 TÌM THẤY HÀNG",
                "img": "https://images.unsplash.com/photo-1556740758-90de374c12ad?q=80&w=800",
                "text": "Tuấn nhận được giày. Tuy hơi phiền nhưng cậu ấy đánh giá cao sự nhiệt tình hỗ trợ.",
                "score": 90
            },
            "game_over_good_ecomm_rescue": {
                "type": "WIN",
                "title": "🦸‍♂️ GIẢI CỨU THÀNH CÔNG",
                "img": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=800",
                "text": "Hàng thất lạc thật. Shop giữ đúng lời hứa ship hỏa tốc đôi mới. Tuấn trở thành khách trung thành.",
                "score": 100
            },
             "game_over_normal_ecomm": {
                "type": "WIN",
                "title": "📦 ĐÃ NHẬN HÀNG",
                "img": "https://images.unsplash.com/photo-1598942610451-9573a059795c?q=80&w=800",
                "text": "Tuấn đi lấy hàng với chút bực bội. Không đánh giá 5 sao nhưng cũng không khiếu nại.",
                "score": 70
            },
            "game_over_bad_ecomm": {
                "type": "LOSE",
                "title": "🤬 KHÁCH HÀNG MẤT NIỀM TIN",
                "img": "https://images.unsplash.com/photo-1586866016892-117e620d5520?q=80&w=800",
                "text": "Tuấn cho rằng shop bao che lừa đảo. Cậu ấy đánh giá 1 sao và báo cáo lên sàn.",
                "score": 10
            }
        }
    },

    "SC_RETAIL_01": {
        "title": "Bán Lẻ: Bình Gốm Vỡ",
        "desc": "Khách VIP nhận được bình gốm vỡ nát trước giờ tặng sếp.",
        "difficulty": "Hard",
        "customer": {
            "name": "Chị Lan (Gold Member)",
            "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=400",
            "traits": ["Nóng tính", "Quyền lực", "Đang rất gấp"],
            "spending": "50tr/năm"
        },
        "steps": {
            "start": {
                "patience": 40,
                "img": "https://images.unsplash.com/photo-1596496050844-461dc5b7263f?q=80&w=800",
                "text": "Alo! Làm ăn kiểu gì thế? Cái bình 5 triệu tặng sếp tối nay, mở ra vỡ tan tành rồi! Các người lừa đảo à?",
                "choices": {
                    "A": "Trấn an: 'Dạ em nghe đây ạ. Em rất xin lỗi chị. Chị bình tĩnh giúp em, em sẽ xử lý ngay ạ.'",
                    "B": "Đòi mã đơn: 'Dạ chị cho em xin Mã Đơn Hàng để em kiểm tra xem có đúng hàng bên em không ạ.'",
                },
                "consequences": {
                    "A": {"next": "step_solution", "change": +20, "analysis": "✅ TỐT: Ưu tiên hạ hỏa (Empathy) trước, xử lý logic sau."},
                    "B": {"next": "step_rage", "change": -20, "analysis": "⚠️ KÉM: Đòi mã đơn lúc khách điên tiết là đổ thêm dầu vào lửa."}
                }
            },
            "step_solution": {
                "patience": 60,
                "img": "https://images.unsplash.com/photo-1556740738-b6a63e27c4df?q=80&w=800",
                "text": "(Giọng dịu hơn) Chị cần gấp 6h tối nay. Giờ vỡ thế này chị lấy gì tặng? Em đền ngay cái khác được không?",
                "choices": {
                    "A": "Linh hoạt: 'Dạ trường hợp gấp, em sẽ xin sếp ship hỏa tốc cái mới cho chị ngay trong 1 tiếng nữa ạ.'",
                    "B": "Cứng nhắc: 'Dạ quy định là chị phải gửi hàng vỡ về, bên em nhận được rồi mới gửi cái mới (mất 3 ngày).'"
                },
                "consequences": {
                    "A": {"next": "game_over_good_retail", "change": +30, "analysis": "✅ XUẤT SẮC: Với khách VIP và gấp, cần linh hoạt phá bỏ quy trình."},
                    "B": {"next": "game_over_fail_retail", "change": -50, "analysis": "❌ THẤT BẠI: Đúng quy trình nhưng sai thời điểm. Mất khách vĩnh viễn."}
                }
            },
            "step_rage": {
                "patience": 20,
                "img": "https://images.unsplash.com/photo-1555861496-0666c8981751?q=80&w=800",
                "text": "Mã cái gì mà mã! Hàng nát bét rồi! Tao không rảnh lục tin nhắn. Giải quyết luôn đi!",
                "choices": {
                    "A": "Mềm mỏng: 'Dạ em xin lỗi, em sẽ tra theo số điện thoại ngay ạ. Chị chờ em 30 giây nhé.'",
                    "B": "Giáo điều: 'Không có mã thì hệ thống không cho phép em truy cập đâu ạ.'"
                },
                "consequences": {
                    "A": {"next": "step_solution", "change": +10, "analysis": "✅ KHÁ: Biết sửa sai và chủ động tìm giải pháp."},
                    "B": {"next": "game_over_bad_retail", "change": -20, "analysis": "❌ THẢM HỌA: Đôi co với khách hàng là điều tối kỵ."}
                }
            },
            "game_over_good_retail": {
                "type": "WIN",
                "title": "🏆 XỬ LÝ XUẤT SẮC",
                "img": "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?q=80&w=800",
                "text": "Khách nhận bình mới lúc 5h chiều. Chị ấy rất cảm kích và giới thiệu công ty đặt quà tết bên bạn.",
                "score": 100
            },
            "game_over_fail_retail": {
                "type": "LOSE",
                "title": "😐 MẤT KHÁCH VIP",
                "img": "https://images.unsplash.com/photo-1444312645910-ffa973656eba?q=80&w=800",
                "text": "Khách cúp máy đi mua chỗ khác. Bạn đúng quy trình nhưng công ty mất doanh thu lớn.",
                "score": 40
            },
            "game_over_bad_retail": {
                "type": "LOSE",
                "title": "☠️ KHỦNG HOẢNG",
                "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800",
                "text": "Bài bóc phốt nhận 10k share. Sếp gọi bạn lên phòng họp.",
                "score": 0
            }
        }
    },

    "SC_TECH_01": {
        "title": "IT: Sự Cố Mất Mạng",
        "desc": "Doanh nghiệp bị mất Internet giữa cuộc họp với đối tác nước ngoài.",
        "difficulty": "Medium",
        "customer": {
            "name": "Anh Tuấn (Giám đốc IT)",
            "avatar": "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=400",
            "traits": ["Logic", "Gấp gáp", "Chuyên môn cao"],
            "spending": "Gói Enterprise"
        },
        "steps": {
            "start": {
                "patience": 30,
                "img": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?q=80&w=800",
                "text": "Bên em làm ăn thế à? Đang họp với đối tác nước ngoài thì rớt mạng! Anh khởi động lại modem 3 lần rồi vẫn không được!",
                "choices": {
                    "A": "Hỏi kỹ thuật: 'Anh ơi đèn PON trên modem đang sáng màu gì ạ?'",
                    "B": "Xin lỗi chung chung: 'Dạ em xin lỗi anh ạ, chắc do đường truyền cá mập cắn cáp...'"
                },
                "consequences": {
                    "A": {"next": "step_check", "change": +10, "analysis": "✅ TỐT: Với dân IT, đi thẳng vào vấn đề kỹ thuật là cách nhanh nhất."},
                    "B": {"next": "game_over_bad_tech", "change": -30, "analysis": "❌ TỆ: Đừng đổ lỗi khách quan khi chưa kiểm tra. Khách IT ghét nhất nghe văn mẫu."}
                }
            },
            "step_check": {
                "patience": 40,
                "img": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=800",
                "text": "Đèn nháy đỏ liên tục. Anh cần mạng trong 5 phút nữa. Có cho kỹ thuật qua ngay được không?",
                "choices": {
                    "A": "Điều phối: 'Em thấy tín hiệu quang bị đứt. Em điều kỹ thuật qua ngay, nhưng nhanh nhất mất 30 phút ạ.'",
                    "B": "Giải pháp tạm thời: 'Dạ 30p kỹ thuật mới tới được. Anh dùng 4G backup tạm thời nhé? Em tặng anh gói data MAX SPEED ngay lập tức để chữa cháy.'"
                },
                "consequences": {
                    "A": {"next": "game_over_fail_tech", "change": -10, "analysis": "⚠️ TRUNG BÌNH: Trung thực là tốt, nhưng không giải quyết được vấn đề '5 phút' của khách."},
                    "B": {"next": "game_over_good_tech", "change": +40, "analysis": "✅ XUẤT SẮC: Cung cấp giải pháp thay thế (Workaround) để cứu vãn cuộc họp là ưu tiên hàng đầu."}
                }
            },
            "game_over_good_tech": {
                "type": "WIN",
                "title": "💡 GIẢI QUYẾT THÔNG MINH",
                "img": "https://images.unsplash.com/photo-1552581234-26160f608093?q=80&w=800",
                "text": "Anh Tuấn dùng 4G hoàn thành cuộc họp. Sau đó kỹ thuật tới sửa xong. Anh đánh giá cao sự linh hoạt.",
                "score": 90
            },
            "game_over_fail_tech": {
                "type": "LOSE",
                "title": "🕒 TRỄ GIỜ HỌP",
                "img": "https://images.unsplash.com/photo-1506784983877-45594efa4cbe?q=80&w=800",
                "text": "30 phút sau kỹ thuật mới tới thì cuộc họp đã tan vỡ. Khách hàng rất thất vọng.",
                "score": 50
            },
            "game_over_bad_tech": {
                "type": "LOSE",
                "title": "🤬 CẮT HỢP ĐỒNG",
                "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800",
                "text": "Anh Tuấn yêu cầu cắt hợp đồng ngay lập tức vì thái độ thiếu chuyên nghiệp.",
                "score": 0
            }
        }
    }
}

# ==============================================================================
# 3. LOGIC HỆ THỐNG (GAME ENGINE)
# ==============================================================================

if 'current_scenario' not in st.session_state: st.session_state.current_scenario = None
if 'current_step' not in st.session_state: st.session_state.current_step = None
if 'patience_meter' not in st.session_state: st.session_state.patience_meter = 50
if 'history' not in st.session_state: st.session_state.history = []

def reset_game():
    st.session_state.current_scenario = None
    st.session_state.current_step = None
    st.session_state.patience_meter = 50
    st.session_state.history = []

def start_scenario(key):
    st.session_state.current_scenario = key
    st.session_state.current_step = 'start'
    st.session_state.patience_meter = ALL_SCENARIOS[key]['steps']['start']['patience']
    st.session_state.history = []

def make_choice(choice_key, step_data):
    consequence = step_data['consequences'][choice_key]
    
    # Cập nhật trạng thái
    st.session_state.current_step = consequence['next']
    st.session_state.patience_meter += consequence['change']
    
    # Giới hạn 0-100
    st.session_state.patience_meter = max(0, min(100, st.session_state.patience_meter))
    
    # Lưu lịch sử
    st.session_state.history.append({
        "step": step_data['text'],
        "choice": step_data['choices'][choice_key],
        "analysis": consequence['analysis'],
        "change": consequence['change']
    })

# ==============================================================================
# 4. GIAO DIỆN CHÍNH
# ==============================================================================

# --- DASHBOARD ---
if st.session_state.current_scenario is None:
    st.title("🎓 TRAINING MASTER PRO")
    st.caption("Hệ thống đào tạo thực chiến (Version 3.0)")
    st.divider()
    
    # Hiển thị dạng lưới
    cols = st.columns(2)
    count = 0
    for key, data in ALL_SCENARIOS.items():
        with cols[count % 2]:
            with st.container(border=True):
                st.subheader(f"{data['title']}")
                st.write(f"📝 {data['desc']}")
                
                # Badge độ khó
                if data['difficulty'] == 'Very Hard':
                    st.markdown(":fire: Độ khó: **Rất Khó**")
                elif data['difficulty'] == 'Hard':
                    st.markdown(":warning: Độ khó: **Khó**")
                else:
                    st.markdown(":star: Độ khó: **Trung bình**")
                    
                if st.button(f"🚀 Bắt đầu ngay", key=f"btn_{key}", use_container_width=True):
                    start_scenario(key)
                    st.rerun()
        count += 1

# --- GAMEPLAY ---
else:
    s_key = st.session_state.current_scenario
    s_data = ALL_SCENARIOS[s_key]
    step_key = st.session_state.current_step
    step_data = s_data['steps'][step_key]
    
    # SIDEBAR
    with st.sidebar:
        st.button("❌ Thoát kịch bản", on_click=reset_game, use_container_width=True)
        st.divider()
        
        # Profile
        cust = s_data['customer']
        st.markdown(f"<div style='text-align:center'><img src='{cust['avatar']}' style='width:100px;border-radius:50%;border:3px solid #2E86C1'></div>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center'>{cust['name']}</h3>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="profile-card">
            <p><b>Tính cách:</b> {', '.join(cust['traits'])}</p>
            <p><b>Nhóm:</b> {cust['spending']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Thanh Kiên Nhẫn
        patience = st.session_state.patience_meter
        st.markdown(f"### 🌡️ Độ Kiên Nhẫn: {patience}/100")
        
        # Logic màu sắc thanh máu
        color_hex = "#28a745" # Green
        if patience < 30: color_hex = "#dc3545" # Red
        elif patience < 70: color_hex = "#ffc107" # Orange
            
        st.markdown(f"""
        <div style="width:100%;background-color:#e9ecef;border-radius:10px;height:20px;">
            <div style="width:{patience}%;background-color:{color_hex};height:20px;border-radius:10px;transition:width 0.5s;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        if patience <= 20 and patience > 0:
             st.error("CẢNH BÁO: KHÁCH HÀNG SẮP BỎ ĐI!")

    # MAIN AREA
    if "type" in step_data: # Màn hình kết thúc
        st.markdown(f"# {step_data['title']}")
        
        c1, c2 = st.columns([1, 1.5], gap="large")
        with c1:
            st.image(step_data['img'], use_container_width=True)
        with c2:
            if step_data['type'] == 'WIN':
                st.success(f"### {step_data['text']}")
                st.balloons()
            else:
                st.error(f"### {step_data['text']}")
            
            st.metric("Điểm số của bạn", f"{step_data['score']}/100")
            
            if st.button("🔄 Thử lại", use_container_width=True):
                start_scenario(s_key)
                st.rerun()
        
        st.divider()
        st.subheader("🕵️ PHÂN TÍCH CHUYÊN GIA")
        for idx, item in enumerate(st.session_state.history):
            with st.expander(f"Bước {idx+1}: {item['choice'][:50]}...", expanded=True):
                st.write(f"💬 **Tình huống:** {item['step']}")
                st.write(f"👉 **Bạn chọn:** {item['choice']}")
                
                # Hiển thị phân tích đẹp hơn
                style_class = "analysis-box-good" if item['change'] > 0 else "analysis-box-bad"
                icon = "✅" if item['change'] > 0 else "❌"
                sign = "+" if item['change'] > 0 else ""
                
                st.markdown(f"""
                <div class="{style_class}">
                    <b>{icon} Phân tích:</b> {item['analysis']} <br>
                    (Độ kiên nhẫn: {sign}{item['change']})
                </div>
                """, unsafe_allow_html=True)

    else: # Màn hình chơi
        st.subheader(f"📍 {s_data['title']}")
        
        col_img, col_text = st.columns([1.5, 2], gap="large")
        
        with col_img:
            st.image(step_data['img'], use_container_width=True, caption="Camera giám sát")
        
        with col_text:
            st.markdown(f"""
            <div class="chat-container">
                <div class="customer-name">🗣️ {cust['name']} nói:</div>
                <div class="dialogue">"{step_data['text']}"</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("#### 👉 Bạn sẽ phản hồi thế nào?")
            
            for key, val in step_data['choices'].items():
                if st.button(f"{key}. {val}", use_container_width=True):
                    make_choice(key, step_data)
                    st.rerun()

# Footer
st.markdown("---")
st.caption("Training Master Pro v3.0 | Author HQuang")