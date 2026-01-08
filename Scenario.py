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
# 0. CẤU HÌNH & KHỞI TẠO
# ==============================================================================
GEMINI_API_KEY = "AIzaSyD5ma9Q__JMZUs6mjBppEHUcUBpsI-wjXA"

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

# --- KHO ẢNH DỰ PHÒNG (BACKUP LIBRARY) ---
BACKUP_IMAGES = {
    "F&B": [
        "https://images.unsplash.com/photo-1559339352-11d035aa65de?q=80&w=1000",
        "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=1000"
    ],
    "HOTEL": [
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1000",
        "https://images.unsplash.com/photo-1582719508461-905c673771fd?q=80&w=1000"
    ],
    "OFFICE": [
        "https://images.unsplash.com/photo-1497215728101-856f4ea42174?q=80&w=1000",
        "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?q=80&w=1000"
    ],
    "RETAIL": [
        "https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=1000",
        "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?q=80&w=1000"
    ],
    "GENERAL": [
        "https://images.unsplash.com/photo-1521791136064-7986c2920216?q=80&w=1000"
    ]
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
        except:
            pass
    images = BACKUP_IMAGES.get(category_key, BACKUP_IMAGES["GENERAL"])
    idx = len(step_text) % len(images)
    return images[idx]

# ==============================================================================
# 1. NEON UI CSS
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
    * { font-family: 'Outfit', sans-serif !important; }
    .stApp { background: radial-gradient(circle at 10% 20%, rgb(20, 20, 35) 0%, rgb(40, 40, 60) 90%); color: #fff; }
    [data-testid="stSidebar"] { background-color: rgba(15, 15, 30, 0.95); border-right: 1px solid rgba(255,255,255,0.1); }
    .scenario-card { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; margin-bottom: 20px; backdrop-filter: blur(10px); }
    .scenario-card:hover { transform: translateY(-5px); border-color: #00d2ff; box-shadow: 0 10px 30px rgba(0, 210, 255, 0.2); }
    .chat-container { background: rgba(0, 0, 0, 0.3); border-left: 5px solid #FDBB2D; padding: 25px; border-radius: 12px; margin: 20px 0; }
    .customer-label { color: #FDBB2D; font-size: 0.9rem; font-weight: bold; letter-spacing: 1px; }
    .dialogue { font-size: 1.4rem; font-style: italic; color: #fff; line-height: 1.5; margin-top: 5px;}
    .stButton button { background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%); color: #fff !important; border: 1px solid rgba(255,255,255,0.2); font-weight: 700; border-radius: 8px; padding: 12px 24px; transition: 0.3s; height: auto; min-height: 60px; white-space: normal;}
    .stButton button:hover { background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%); transform: scale(1.02); color: #000 !important; border: none; }
    h1 { background: linear-gradient(to right, #00c6ff, #0072ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. EXTENDED DATASET (NỘI DUNG MỞ RỘNG VÀ CHI TIẾT)
# ==============================================================================
INITIAL_DATA = {
    # --- F&B ---
    "SC_FNB_01": {
        "title": "F&B: Foreign Object Incident",
        "desc": "A long hair found in premium lobster soup.",
        "difficulty": "Hard",
        "category": "F&B",
        "customer": {"name": "Ms. Jade", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Jade", "traits": ["Food Critic", "High Standards"]},
        "steps": {
            "start": { 
                "text": "Manager! Get over here NOW! Look at this! There is a disgusting, long black hair tangled in my lobster soup! Is this your idea of fine dining? I feel sick just looking at it!",
                "choices": {
                    "A": "Defensive: 'Madam, our kitchen staff wear hairnets. Are you sure it's not yours?'",
                    "B": "Professional: 'I am terribly sorry, Ms. Jade! That is completely unacceptable. Please allow me to remove this dish immediately.'"
                },
                "consequences": {"A": {"next": "game_over_bad", "change": -50, "analysis": "❌ Accusing the customer instantly escalates the situation."}, "B": {"next": "step_2", "change": +20, "analysis": "✅ Immediate removal and apology is the right first step."}}
            },
            "step_2": { 
                "text": "It's too late! My appetite is completely gone. I've been waiting 30 minutes for this, and now my friend is eating alone while I sit here staring at an empty table!",
                "choices": {
                    "A": "Standard: 'Would you like to order something else? I can rush the order for you.'",
                    "B": "Empathy & Pivot: 'I completely understand your frustration. It's awful to eat out of sync. May I bring you a complimentary glass of wine and some appetizers while you decide?'"
                },
                "consequences": {"A": {"next": "step_3_angry", "change": -10, "analysis": "⚠️ She just said she lost her appetite. Offering food again is tone-deaf."}, "B": {"next": "step_3_calm", "change": +20, "analysis": "✅ Addressing the 'waiting alone' pain point with a distraction (wine)."}}
            },
            "step_3_angry": {
                "text": "I told you I don't want to eat anymore! Just bring me the bill for the water. I'm writing a review about this disaster right now.",
                "choices": {
                    "A": "Give Up: 'Okay, here is the bill. Sorry about tonight.'",
                    "B": "Last Resort: 'Please, I don't want you to leave on a bad note. The entire meal is on us, and I have a voucher for your next visit.'"
                },
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Giving up guarantees a bad review."}, "B": {"next": "game_over_save", "change": +30, "analysis": "🏆 A strong recovery attempt might save the review."}}
            },
            "step_3_calm": { 
                "text": "(Sips wine) Okay, fine. The wine is decent. But honestly, tonight is ruined. Just bring me the check, I just want to go home.",
                "choices": {
                    "A": "Discount: 'I have removed the soup from your bill and applied a 10% discount on the rest.'",
                    "B": "Wow Service: 'Ms. Jade, tonight is on the house. I've also packed our signature dessert for you to enjoy at home. We hope to see you again for a flawless experience.'"
                },
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ 10% is insulting for a ruined night."}, "B": {"next": "game_over_good", "change": +40, "analysis": "🏆 Waiving the bill and giving a gift turns a negative into a 'Wow'."}}
            },
            "game_over_good": {"type": "WIN", "title": "REPUTATION SAVED", "text": "Ms. Jade was impressed by your professionalism. She didn't post the bad review and thanked you.", "score": 100},
            "game_over_save": {"type": "WIN", "title": "CRISIS AVERTED", "text": "She accepted the apology. Not happy, but she won't destroy your reputation.", "score": 70},
            "game_over_fail": {"type": "LOSE", "title": "LOST CUSTOMER", "text": "She left a 1-star review on Google Maps with photos.", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "PR NIGHTMARE", "text": "She livestreamed the argument. The restaurant is trending for the wrong reasons.", "score": 0}
        }
    },
    
    # --- HOTEL ---
    "SC_HOTEL_01": {
        "title": "Hotel: Honeymoon Nightmare",
        "desc": "Overbooked Ocean View suite for a honeymoon couple.",
        "difficulty": "Very Hard",
        "category": "HOTEL",
        "customer": {"name": "Mr. Mike", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Mike", "traits": ["Exhausted", "High Expectations"]},
        "steps": {
            "start": { 
                "text": "What do you mean 'System Error'? I booked the Ocean View Suite six months ago! This is our HONEYMOON! I refuse to stay in a Garden View room!",
                "choices": {
                    "A": "Policy: 'Sir, I apologize, but the system overbooked. The Garden View is also very nice and has a bathtub.'",
                    "B": "Ownership: 'Mr. Mike, this is entirely our mistake. I cannot imagine how disappointing this must be for your special trip. Let me see what I can do.'"
                },
                "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Don't sell the downgrade. Acknowledge the failure."}, "B": {"next": "step_2", "change": +20, "analysis": "✅ Validating their feelings is crucial."}}
            },
            "step_2": { 
                "text": "My wife is in tears in the lobby. We flew 12 hours for that view! You have to fix this, or I want a full refund and we are leaving!",
                "choices": {
                    "A": "Compensation: 'I can offer you free breakfast for your entire stay and a couple's massage at our Spa.'",
                    "B": "Solution Seeking: 'Please give me 5 minutes. I am calling our sister property next door to see if they have a suite, or I will find a better solution here.'"
                },
                "consequences": {"A": {"next": "step_3_fail", "change": -10, "analysis": "⚠️ Breakfast doesn't fix the room issue."}, "B": {"next": "step_3_hero", "change": +30, "analysis": "✅ Showing active effort to solve the core problem."}}
            },
            "step_3_fail": {
                "text": "I don't want a massage! I want the room I paid for! This is ridiculous. Call your manager!",
                "choices": {
                    "A": "Escalate: 'I will get the manager, but he will tell you the same thing.'",
                    "B": "Last Attempt: 'Wait! The Presidential Suite is free for 2 nights. I can move you there, then back to Ocean View later?'"
                },
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Dismissive attitude."}, "B": {"next": "game_over_good", "change": +40, "analysis": "🏆 Upgrading to the best room is the only way to save this."}}
            },
            "step_3_hero": { 
                "text": "(Waiting anxiously) Well? Did you find anything? We are exhausted.",
                "choices": {
                    "A": "Bad News: 'Nearby hotels are full. But I can give you $200 credit.'",
                    "B": "Hero Moment: 'Good news. I have upgraded you to the Presidential Suite for the first night, and I've secured the best Ocean Villa for the rest of your stay.'"
                },
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Money doesn't buy memories."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Over-delivering turns a disaster into a luxury upgrade."}}
            },
            "game_over_good": {"type": "WIN", "title": "DREAM VACATION SAVED", "text": "They were thrilled with the upgrade and left a glowing review about your service.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "WALK OUT", "text": "They demanded a refund and left to a competitor hotel.", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "PUBLIC SHAMING", "text": "They posted angry photos on TripAdvisor immediately.", "score": 0}
        }
    },

    # --- TECH ---
    "SC_TECH_01": {
        "title": "IT: Critical Internet Failure",
        "desc": "Internet cuts out during a CEO's investor pitch.",
        "difficulty": "Medium",
        "category": "OFFICE",
        "customer": {"name": "Mr. Ken", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Ken", "traits": ["Urgent", "CEO"]},
        "steps": {
            "start": { 
                "text": "My internet is dead! I have 50 investors on a Zoom call right now! I restarted the modem twice already! FIX IT!",
                "choices": {
                    "A": "Script: 'Sir, can you please check if the lights on the modem are blinking green?'",
                    "B": "Acknowledge: 'I see the packet loss on your line. Since you already restarted, I am checking the line signal immediately.'"
                },
                "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ He said he restarted it! Don't follow the script blindly."}, "B": {"next": "step_2", "change": +20, "analysis": "✅ Show you listened and are acting fast."}}
            },
            "step_2": { 
                "text": "Hurry up! They are waiting! I'm losing money every second this is down!",
                "choices": {
                    "A": "Timeline: 'I found the issue. A technician can be there in 2 hours.'",
                    "B": "Workaround: 'Resetting the port will take 5 mins. In the meantime, I'm activating 50GB of high-speed data on your phone plan immediately. Tether it now!'"
                },
                "consequences": {"A": {"next": "step_3_fail", "change": -20, "analysis": "⚠️ 2 hours is too long for a live meeting."}, "B": {"next": "step_3_win", "change": +40, "analysis": "🏆 Providing an instant backup solution (4G) is the game changer."}}
            },
            "step_3_fail": {
                "text": "2 hours?! Are you insane? The meeting is over by then! You just killed my deal!",
                "choices": {
                    "A": "Apology: 'I am very sorry, that is the fastest slot.'",
                    "B": "Escalate: 'Let me try to push it to 30 mins, but I can't promise.'"
                },
                "consequences": {"A": {"next": "game_over_churn", "change": -20, "analysis": "❌ Helplessness."}, "B": {"next": "game_over_churn", "change": -10, "analysis": "⚠️ Still too late."}}
            },
            "step_3_win": { 
                "text": "(Connecting to hotspot) Okay, I'm back online via 4G. It's stable. But why did the fiber fail?",
                "choices": {
                    "A": "Technical: 'It seems to be a signal degradation in your area node.'",
                    "B": "Reassurance: 'We will investigate the root cause later. For now, good luck with your pitch! I'll monitor your connection personally.'"
                },
                "consequences": {"A": {"next": "game_over_good", "change": +10, "analysis": "✅ Honest answer."}, "B": {"next": "game_over_good", "change": +30, "analysis": "🏆 prioritizing the customer's goal (the pitch) over technical details."}}
            },
            "game_over_good": {"type": "WIN", "title": "DEAL SAVED", "text": "The meeting went smooth on 4G. Ken is impressed by your quick thinking.", "score": 100},
            "game_over_churn": {"type": "LOSE", "title": "CONTRACT CANCELLED", "text": "Ken lost the investors and cancelled his business contract.", "score": 20},
            "game_over_bad": {"type": "LOSE", "title": "FURIOUS", "text": "Ken screamed and hung up.", "score": 0}
        }
    },

    # --- RETAIL ---
    "SC_RETAIL_01": {
        "title": "Retail: Broken Anniversary Gift",
        "desc": "A crystal vase arrived shattered before a party.",
        "difficulty": "Hard",
        "category": "RETAIL",
        "customer": {"name": "Ms. Lan", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Lan", "traits": ["VIP", "Emotional"]},
        "steps": {
            "start": { 
                "text": "I can't believe this! The $500 crystal vase I bought for my parents' 50th anniversary arrived in pieces! The party is TONIGHT!",
                "choices": {
                    "A": "Process: 'Oh no. Please send me a photo of the damage and your Order ID so I can file a claim.'",
                    "B": "Empathy: 'Oh my god, Ms. Lan! That is heartbreaking! I am so sorry this happened on such an important day.'"
                },
                "consequences": {"A": {"next": "game_over_bad", "change": -20, "analysis": "⚠️ Don't ask for paperwork when she is panicking."}, "B": {"next": "step_2", "change": +20, "analysis": "✅ Emotional connection first."}}
            },
            "step_2": { 
                "text": "I don't have time for a claim! I need a gift by 6 PM! Do you have another one?",
                "choices": {
                    "A": "Check System: 'Let me check... Ah, I'm sorry, our warehouse is out of stock until next week.'",
                    "B": "Check Nearby: 'Hold on one second. I am checking stock at all our city branches right now.'"
                },
                "consequences": {"A": {"next": "step_3_fail", "change": -20, "analysis": "❌ A dead end answer."}, "B": {"next": "step_3_solution", "change": +20, "analysis": "✅ Showing effort to find a solution."}}
            },
            "step_3_fail": {
                "text": "Next week?! The party is tonight! You ruined everything!",
                "choices": {
                    "A": "Refund: 'I will process a full refund immediately.'",
                    "B": "Alternative: 'We have a similar blue vase in stock. Would that work?'"
                },
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "😐 Refund doesn't solve the 'No Gift' problem."}, "B": {"next": "game_over_save", "change": +20, "analysis": "✅ Better than nothing."}}
            },
            "step_3_solution": { 
                "text": "Please tell me you found one!",
                "choices": {
                    "A": "Self-Pickup: 'Yes! The downtown store has one. You can go pick it up.'",
                    "B": "Concierge: 'I found one! I have booked a Grab Express to deliver it directly to your venue. It will arrive by 5 PM.'"
                },
                "consequences": {"A": {"next": "game_over_save", "change": 0, "analysis": "😐 Making the customer work."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Doing the work for them is true VIP service."}}
            },
            "game_over_good": {"type": "WIN", "title": "PARTY SAVED", "text": "The vase arrived in time. Lan sent a thank you email to your boss.", "score": 100},
            "game_over_save": {"type": "WIN", "title": "ACCEPTABLE", "text": "She got a replacement, but was stressed.", "score": 70},
            "game_over_fail": {"type": "LOSE", "title": "LOST VIP", "text": "She returned everything and left.", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "BAD REVIEW", "text": "She felt unheard and angry.", "score": 0}
        }
    },

    # --- AIRLINE ---
    "SC_AIRLINE_01": {
        "title": "Airline: The Missing Groom",
        "desc": "Flight cancelled, passenger is late for his own wedding.",
        "difficulty": "Extreme",
        "category": "TRAVEL",
        "customer": {"name": "Mr. David", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=David", "traits": ["Panic", "Groom"]},
        "steps": {
            "start": { 
                "text": "You cancelled my flight?! I'm the GROOM! My wedding starts in 6 hours! You have to get me on a plane right now!",
                "choices": {
                    "A": "Explanation: 'Sir, the flight was cancelled due to a technical fault. Safety is our priority.'",
                    "B": "Action: 'I understand this is an emergency! Let me look for the fastest alternative immediately.'"
                },
                "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ He doesn't care about safety right now, he cares about the wedding."}, "B": {"next": "step_2", "change": +30, "analysis": "✅ validating the urgency."}}
            },
            "step_2": { 
                "text": "I don't care how! Just get me there! Please!",
                "choices": {
                    "A": "Our Airline: 'The next flight on our airline is tomorrow morning.'",
                    "B": "Partner Airline: 'I'm checking partner airlines... There is a flight leaving in 45 mins from Terminal 2.'"
                },
                "consequences": {"A": {"next": "step_3_fail", "change": -20, "analysis": "⚠️ Following policy too strictly."}, "B": {"next": "step_3_win", "change": +30, "analysis": "✅ Going above and beyond."}}
            },
            "step_3_fail": {
                "text": "Tomorrow?! I'll miss my own wedding! Is that it? Is that all you can do?",
                "choices": {
                    "A": "Apology: 'I am truly sorry, but I cannot create a flight.'",
                    "B": "Creative: 'Wait, if you fly to a nearby city, you can drive 2 hours and make it?'"
                },
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "❌ Giving up."}, "B": {"next": "game_over_save", "change": +30, "analysis": "🏆 Creative problem solving."}}
            },
            "step_3_win": { 
                "text": "45 minutes? That's tight! Can I make it?",
                "choices": {
                    "A": "Honesty: 'It will be close. You need to run.'",
                    "B": "Assistance: 'I have called a buggy to take you to Terminal 2 fast track. Run! Good luck!'"
                },
                "consequences": {"A": {"next": "game_over_save", "change": +10, "analysis": "✅ Good luck."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Full support to ensure success."}}
            },
            "game_over_good": {"type": "WIN", "title": "GROOM ARRIVED", "text": "David made the flight and the wedding.", "score": 100},
            "game_over_save": {"type": "WIN", "title": "CLOSE CALL", "text": "He barely made it, very stressed.", "score": 70},
            "game_over_fail": {"type": "LOSE", "title": "TRAGEDY", "text": "He missed his wedding. Unforgivable.", "score": 0},
            "game_over_bad": {"type": "LOSE", "title": "SECURITY", "text": "He got aggressive and was detained.", "score": 0}
        }
    }
}

# (Giữ nguyên các hàm load_data, save_score, show_leaderboard như phiên bản trước)
# ...
