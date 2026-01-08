import streamlit as st
import json
import os
import time
import pandas as pd
from datetime import datetime
import urllib.parse
import google.generativeai as genai

# ==============================================================================
# 0. CONFIGURATION & AI ENGINE
# ==============================================================================
# Your API Key (Embedded)
GEMINI_API_KEY = "AIzaSyD5ma9Q__JMZUs6mjBppEHUcUBpsI-wjXA"

st.set_page_config(
    page_title="Service Hero Global",
    page_icon="🌍",
    layout="wide"
)

def init_ai():
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        return True
    except:
        return False

def generate_ai_image_url(scenario_context, default_img_url):
    """
    Generates an image URL using Gemini for prompting and Pollinations for rendering.
    Optimized to prevent broken images.
    """
    try:
        # 1. Use Gemini to get a short, clear visual description
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt_request = f"""
        Describe the following scene in 10 words for an AI image generator. 
        Focus on the main subject and emotion. 
        Scene: "{scenario_context}"
        Output ONLY the 10 words in English. No intro.
        """
        response = model.generate_content(prompt_request)
        clean_prompt = response.text.strip().replace("\n", " ").replace('"', '')
        
        # 2. Construct a Safe URL
        # We simplify the prompt to avoid URL encoding errors
        encoded_prompt = urllib.parse.quote(clean_prompt)
        seed = int(time.time())
        # Use a high-speed model 'flux' or 'turbo'
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=500&seed={seed}&nologo=true&model=flux"
        return image_url
    except Exception as e:
        # Fallback to Unsplash if AI fails
        return default_img_url

init_ai()

# ==============================================================================
# 1. MODERN UI STYLING (CSS)
# ==============================================================================
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
    }
    
    /* Custom Card Style */
    .scenario-card {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 5px solid #3b82f6;
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .scenario-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    /* Headers */
    h1 { color: #1e293b; font-weight: 800; }
    h2 { color: #334155; font-weight: 700; }
    h3 { color: #0f172a; }

    /* Custom Buttons */
    .stButton button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
    }
    .stButton button:hover {
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
        transform: scale(1.02);
        box-shadow: 0 6px 12px rgba(59, 130, 246, 0.4);
        color: white;
    }
    
    /* Chat Bubbles */
    .chat-container {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 20px;
        border-top-left-radius: 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin: 15px 0;
        border-left: 4px solid #6366f1;
    }
    .customer-label {
        font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px;
        color: #64748b; margin-bottom: 5px; font-weight: bold;
    }
    .dialogue-text {
        font-size: 1.2em; color: #1e293b; font-style: italic; line-height: 1.5;
    }
    
    /* Analysis Boxes */
    .analysis-box { padding: 15px; border-radius: 10px; margin-top: 10px; border: 1px solid transparent; }
    .good { background-color: #dcfce7; color: #166534; border-color: #bbf7d0; }
    .bad { background-color: #fee2e2; color: #991b1b; border-color: #fecaca; }
    
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. FULL ENGLISH DATASET (11 SCENARIOS)
# ==============================================================================
INITIAL_DATA = {
    # --- 1. F&B ---
    "SC_FNB_01": {
        "title": "F&B: Foreign Object in Food",
        "desc": "Hair found in soup. Handle the angry customer.",
        "difficulty": "Hard",
        "customer": {"name": "Ms. Jade", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Jade", "traits": ["Picky", "Famous Reviewer"], "spending": "New Customer"},
        "steps": {
            "start": { 
                "patience": 30, "img": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=800",
                "text": "Where is the manager?! Look at this! A long hair in my soup! Are you feeding me garbage?",
                "choices": {"A": "Deny: 'That is not our staff's hair.'", "B": "Act: 'I am terribly sorry! I will handle this immediately.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -40, "analysis": "❌ Denial destroys trust immediately."}, "B": {"next": "step_2_wait", "change": +10, "analysis": "✅ Immediate action is the correct first step."}}
            },
            "step_2_wait": { 
                "patience": 40, "img": "https://images.unsplash.com/photo-1512485800893-e082253cd558?q=80&w=800",
                "text": "(5 mins later) I lost my appetite. I've been waiting too long. My friend is almost done eating.",
                "choices": {"A": "Persuade: 'Please try it, the chef made it specially.'", "B": "Pivot: 'I completely understand. I will remove this item. May I offer you a dessert instead?'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Never force an angry customer to eat."}, "B": {"next": "step_3_bill", "change": +20, "analysis": "✅ Respecting emotions and offering alternatives."}}
            },
            "step_3_bill": { 
                "patience": 60, "img": "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?q=80&w=800",
                "text": "Fine, get me a glass of wine. But tonight is ruined. Bring me the bill.",
                "choices": {"A": "Discount: 'Here is the bill with 10% off.'", "B": "Compensate: 'Tonight is on the house. And here is a voucher for your next visit.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ 10% is an insult for a ruined night."}, "B": {"next": "game_over_good", "change": +40, "analysis": "🏆 Over-delivering turns a disaster into a Wow moment."}}
            },
            "game_over_good": {"type": "WIN", "title": "TRUST RESTORED", "text": "She was surprised by your generosity and left a tip.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "LOST CUSTOMER", "text": "She paid but left a 1-star review.", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "PR DISASTER", "text": "A video of the argument went viral.", "score": 0}
        }
    },
    # --- 2. HOTEL ---
    "SC_HOTEL_01": {
        "title": "Hotel: Overbooked Room",
        "desc": "Honeymoon couple, but the hotel is full.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. Mike", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Mike", "traits": ["Tired", "High Expectations"], "spending": "Honeymoon"},
        "steps": {
            "start": { 
                "patience": 20, "img": "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=800",
                "text": "I booked an Ocean View 3 months ago! I will NOT accept a Garden View!",
                "choices": {"A": "Policy: 'It's a system error. Please understand.'", "B": "Empathy: 'This is entirely our fault. I sincerely apologize.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Blaming the system doesn't help."}, "B": {"next": "step_2_alt", "change": +20, "analysis": "✅ Owning the mistake is crucial."}}
            },
            "step_2_alt": { 
                "patience": 40, "img": "https://images.unsplash.com/photo-1582719508461-905c673771fd?q=80&w=800",
                "text": "Sorry doesn't give me an ocean view! We flew 12 hours for this!",
                "choices": {"A": "Standard: 'I can give you free breakfast and spa.'", "B": "Check: 'Please give me a moment to find the best upgrade option.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Small gifts don't fix the main issue."}, "B": {"next": "step_3_upgrade", "change": +10, "analysis": "✅ Showing effort to find a real solution."}}
            },
            "step_3_upgrade": { 
                "patience": 50, "img": "https://images.unsplash.com/photo-1618773928121-c32242e63f39?q=80&w=800",
                "text": "(Waiting anxiously) Well? My wife is crying over there.",
                "choices": {"A": "Partial: 'We have a partial ocean view available tomorrow.'", "B": "Hero: 'I found the Presidential Suite vacant. I'm upgrading you for free.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Still disappointing."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Over-delivering saves the vacation."}}
            },
            "game_over_good": {"type": "WIN", "title": "DREAM VACATION", "text": "They were thrilled with the Suite.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "SAD TRIP", "text": "They stayed but won't return.", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "WALK OUT", "text": "They demanded a refund and left.", "score": 0}
        }
    },
    # --- 3. E-COMMERCE ---
    "SC_ECOMM_01": {
        "title": "Online: Lost Package",
        "desc": "App says delivered, customer received nothing.",
        "difficulty": "Medium",
        "customer": {"name": "Tom", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Tom", "traits": ["Anxious", "Skeptical"], "spending": "Low"},
        "steps": {
            "start": {
                "patience": 40, "img": "https://images.unsplash.com/photo-1566576912321-d58ba2188273?q=80&w=800",
                "text": "App says delivered but I see nothing! Are you scamming me?",
                "choices": {"A": "Deflect: 'Check with your neighbors.'", "B": "Reassure: 'I will take responsibility to check this right now.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -20, "analysis": "❌ Don't make the customer do your work."}, "B": {"next": "step_2_check", "change": +20, "analysis": "✅ Siding with the customer."}}
            },
            "step_2_check": {
                "patience": 50, "img": "https://images.unsplash.com/photo-1556741533-6e6a62bd8b49?q=80&w=800",
                "text": "I checked everywhere! I need these shoes for a contest tomorrow!",
                "choices": {"A": "Wait: 'Please wait 24h for shipper response.'", "B": "Urgent: 'I am calling the local courier directly right now.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ 24h is too late for his deadline."}, "B": {"next": "step_3_result", "change": +20, "analysis": "✅ Urgency matches customer needs."}}
            },
            "step_3_result": {
                "patience": 60, "img": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?q=80&w=800",
                "text": "(Shipper hid it in a bush) Shipper said it's in the bush? What if it's stolen?",
                "choices": {"A": "Trust: 'It's probably still there.'", "B": "Commit: 'Please check. If it's gone, I will express ship a new pair immediately.'"},
                "consequences": {"A": {"next": "game_over_normal", "change": 0, "analysis": "😐 Too passive."}, "B": {"next": "game_over_good", "change": +40, "analysis": "🏆 Risk-free commitment builds absolute trust."}}
            },
            "game_over_good": {"type": "WIN", "title": "LOYAL FAN", "text": "Tom found the shoes and rated 5 stars.", "score": 100},
            "game_over_normal": {"type": "WIN", "title": "FOUND IT", "text": "Item found but customer is annoyed.", "score": 70},
            "game_over_fail": {"type": "LOSE", "title": "TOO LATE", "text": "He bought shoes elsewhere.", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "SCAM REPORT", "text": "He reported the shop as a scam.", "score": 0}
        }
    },
    # --- 4. RETAIL ---
    "SC_RETAIL_01": {
        "title": "Retail: Broken Vase",
        "desc": "VIP customer received a broken item.",
        "difficulty": "Hard",
        "customer": {"name": "Ms. Lan", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Lan", "traits": ["VIP", "Urgent"], "spending": "High"},
        "steps": {
            "start": { 
                "patience": 40, "img": "https://images.unsplash.com/photo-1596496050844-461dc5b7263f?q=80&w=800",
                "text": "My $500 vase arrived shattered! How do you do business?",
                "choices": {"A": "Empathy: 'Oh my god! I am so sorry Ms. Lan. I'll handle it.'", "B": "Process: 'Can I have your order ID?'"},
                "consequences": {"A": {"next": "step_2_stock", "change": 20, "analysis": "✅ Using name and showing empathy first."}, "B": {"next": "game_over_bad", "change": -20, "analysis": "⚠️ VIPs hate being treated like a number."}}
            },
            "step_2_stock": { 
                "patience": 60, "img": "https://images.unsplash.com/photo-1616486338812-3a4772eb77f9?q=80&w=800",
                "text": "I need to gift this to my boss at 6 PM tonight! Do you have stock?",
                "choices": {"A": "Check: 'Sorry, we are out of stock at this store.'", "B": "Check: 'Out of stock here, but I can order one for next week.'"},
                "consequences": {"A": {"next": "step_3_sol", "change": 0, "analysis": "✅ Honest."}, "B": {"next": "game_over_fail", "change": -30, "analysis": "❌ Next week is too late."}}
            },
            "step_3_sol": { 
                "patience": 50, "img": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?q=80&w=800",
                "text": "Out of stock?! I'm dead! What do I give my boss?",
                "choices": {"A": "Refund: 'I will refund you immediately.'", "B": "Rescue: 'I will pull stock from the warehouse and Grab-Express it to you before 5:30.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "😐 Refund doesn't solve the 'Gift' problem."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Solving the 'Job to be done'."}}
            },
            "game_over_good": {"type": "WIN", "title": "EXCELLENT", "text": "She got the vase in time.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "LOST VIP", "text": "She was disappointed and left.", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "CRISIS", "text": "Social media rant about your shop.", "score": 0}
        }
    },
    # --- 5. TECH ---
    "SC_TECH_01": {
        "title": "IT: Internet Outage",
        "desc": "Internet down during important meeting.",
        "difficulty": "Medium",
        "customer": {"name": "Mr. Ken", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Ken", "traits": ["Tech-savvy", "Urgent"], "spending": "Business"},
        "steps": {
            "start": { 
                "patience": 30, "img": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?q=80&w=800",
                "text": "Net is down! I'm in a meeting! I restarted the modem, still red light!",
                "choices": {"A": "Basic: 'Try unplugging it and plugging it back in.'", "B": "Expert: 'I see packet loss from your end. I'm investigating.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ He just said he restarted it!"}, "B": {"next": "step_2_fix", "change": +10, "analysis": "✅ Acknowledge technical detail."}}
            },
            "step_2_fix": { 
                "patience": 40, "img": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=800",
                "text": "Fix it! I have 5 minutes!",
                "choices": {"A": "Tech: 'Technician will arrive in 4 hours.'", "B": "Remote: 'I'm resetting the port remotely... Give me 30s.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Too slow."}, "B": {"next": "step_3_fail", "change": +10, "analysis": "✅ Try immediate solution."}}
            },
            "step_3_fail": { 
                "patience": 20, "img": "https://images.unsplash.com/photo-1531403009284-440f080d1e12?q=80&w=800",
                "text": "Still not working! My meeting is ruined!",
                "choices": {"A": "Give up: 'Sorry, we need to send a technician.'", "B": "Lifeline: 'Turn on your 4G. I just added 50GB high-speed data to your number FOR FREE.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -30, "analysis": "❌ Leaving customer stranded."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Workaround saved the meeting."}}
            },
            "game_over_good": {"type": "WIN", "title": "SMART SAVE", "text": "Meeting went smoothly via 4G.", "score": 90},
            "game_over_fail": {"type": "LOSE", "title": "FAILED", "text": "He missed the meeting.", "score": 50},
            "game_over_bad": {"type": "LOSE", "title": "CANCELLED", "text": "He switched to another provider.", "score": 0}
        }
    },
    # --- 6. AIRLINE ---
    "SC_AIRLINE_01": {
        "title": "Airline: Flight Cancelled",
        "desc": "Passenger missing a wedding.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. David", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=David", "traits": ["Stressed", "Urgent"], "spending": "Gold Flyer"},
        "steps": {
            "start": { 
                "patience": 20, "img": "https://images.unsplash.com/photo-1569154941061-e231b4725ef1?q=80&w=800",
                "text": "Cancelled?! I'm the best man! Wedding is in 6 hours! Get me on a plane NOW!",
                "choices": {"A": "Reason: 'It's due to bad weather.'", "B": "Empathy: 'Oh no! Let me find another flight immediately.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Don't explain, just act."}, "B": {"next": "step_2_alt", "change": +30, "analysis": "✅ Validate urgency."}}
            },
            "step_2_alt": { 
                "patience": 50, "img": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?q=80&w=800", "text": "Hurry! The party starts at 7 PM!", "choices": {"A": "Us: 'Next flight is tomorrow morning.'", "B": "Partner: 'I am checking partner airlines too...'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Tomorrow is too late."}, "B": {"next": "step_3_mix", "change": +20, "analysis": "✅ Flexible solution."}}
            },
            "step_3_mix": { 
                "patience": 40, "img": "https://images.unsplash.com/photo-1517400508447-f8dd518b86db?q=80&w=800", "text": "No direct flights? I'm doomed!", "choices": {"A": "Sorry: 'I apologize.'", "B": "Creative: 'Fly to nearby city + Taxi (We pay).'"}, "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "❌ Giving up too soon."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Creative problem solving."}}
            },
            "game_over_good": {"type": "WIN", "title": "JUST IN TIME", "text": "David made it to the wedding.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "MISSED IT", "text": "David missed his best friend's wedding.", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "SECURITY", "text": "Security was called.", "score": 0}
        }
    },
     # --- 7. BANK ---
    "SC_BANK_01": {
        "title": "Bank: ATM Swallowed Card",
        "desc": "Elderly needing cash for medicine.",
        "difficulty": "Hard",
        "customer": {"name": "Mrs. Evelyn", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Evelyn", "traits": ["Elderly", "Panicked"], "spending": "Loyal"},
        "steps": {
            "start": { "patience": 30, "img": "https://images.unsplash.com/photo-1563986768609-322da13575f3?q=80&w=800", "text": "Help! The machine took my card! I need money for heart medicine now!", "choices": {"A": "Process: 'Come back on Monday.'", "B": "Reassure: 'Your card is safe. Let me help you withdraw cash.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Health risk."}, "B": {"next": "step_2_verify", "change": +30, "analysis": "✅ Prioritize health."}} },
            "step_2_verify": { "patience": 50, "img": "https://images.unsplash.com/photo-1556742031-c6961e8560b0?q=80&w=800", "text": "But I forgot my ID at home.", "choices": {"A": "Rigid: 'Then I can't help you.'", "B": "Flexible: 'I will verify via security questions and recent transactions.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Dead end."}, "B": {"next": "step_3_tech", "change": +20, "analysis": "✅ Flexible for emergency."}} },
            "step_3_tech": { "patience": 60, "img": "https://images.unsplash.com/photo-1601597111158-2fceff292cdc?q=80&w=800", "text": "Okay, verified. But how do I get cash?", "choices": {"A": "Guide: 'I will guide you to use Cardless Withdrawal on the App.'", "B": "Do it: 'Let me do it for you.'"}, "consequences": {"A": {"next": "game_over_good", "change": +40, "analysis": "🏆 Patient guidance."}, "B": {"next": "game_over_fail", "change": -10, "analysis": "❌ Never touch customer's phone/app (Security breach)."}} },
            "game_over_good": {"type": "WIN", "title": "SAFE", "text": "She got her medicine.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "NO CASH", "text": "She had to go home.", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "LOST TRUST", "text": "She switched banks.", "score": 0}
        }
    },
    # --- 8. REAL ESTATE ---
    "SC_REALESTATE_01": {
        "title": "Real Estate: Moldy Apt",
        "desc": "Luxury tenant found mold.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. Chen", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Chen", "traits": ["Wealthy", "Clean freak"], "spending": "Luxury"},
        "steps": {
            "start": { "patience": 20, "img": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?q=80&w=800", "text": "I pay $4000/month for this moldy hole? My son has asthma!", "choices": {"A": "Defensive: 'Did you open the windows?'", "B": "Alarmed: 'That is dangerous. Please evacuate, I am coming.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -40, "analysis": "❌ Victim blaming."}, "B": {"next": "step_2_inspect", "change": +30, "analysis": "✅ Safety first."}} },
            "step_2_inspect": { "patience": 40, "img": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?q=80&w=800", "text": "(You arrive) Look! Black mold! We are not sleeping here.", "choices": {"A": "Clean: 'I will send painters tomorrow.'", "B": "Relocate: 'Agreed. You need to move now.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -30, "analysis": "⚠️ Painting doesn't kill mold instantly."}, "B": {"next": "step_3_hotel", "change": +20, "analysis": "✅ Immediate solution."}} },
            "step_3_hotel": { "patience": 50, "img": "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=800", "text": "Where to? A motel?", "choices": {"A": "Budget: 'I have a $50/night budget.'", "B": "Luxury: 'I booked a 5-star hotel nearby for your family.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Insulting a Luxury client."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Matching the lifestyle."}} },
            "game_over_good": {"type": "WIN", "title": "SMOOTH", "text": "Family is happy with the hotel.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "LEASE BROKEN", "text": "Tenant moved out.", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "LAWSUIT", "text": "Sued for health damages.", "score": 0}
        }
    },
    # --- 9. SAAS ---
    "SC_SAAS_01": {
        "title": "SaaS: Data Loss",
        "desc": "Accidentally deleted important data before meeting.",
        "difficulty": "Very Hard",
        "customer": {"name": "Sarah", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah", "traits": ["Angry", "Executive"], "spending": "Enterprise"},
        "steps": {
            "start": { "patience": 10, "img": "https://images.unsplash.com/photo-1531297461136-82lw9z3w9z?q=80&w=800", "text": "WHERE IS MY DATA?! I have a presentation in 2 hours!", "choices": {"A": "Tip: 'Did you clear cache?'", "B": "Emergency: 'I am alerting engineering for immediate recovery (SEV1).'"}, "consequences": {"A": {"next": "game_over_bad", "change": -20, "analysis": "❌ Don't ask silly questions."}, "B": {"next": "step_2_status", "change": +30, "analysis": "✅ Correct severity level."}} },
            "step_2_status": { "patience": 30, "img": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?q=80&w=800", "text": "Restore takes 4 hours? I am dead!", "choices": {"A": "Sorry: 'It is the process.'", "B": "Manual: 'Can I manually extract key metrics to Excel for you first?'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Passive."}, "B": {"next": "step_3_ceo", "change": +20, "analysis": "✅ Saving the situation manually."}} },
            "step_3_ceo": { "patience": 40, "img": "https://images.unsplash.com/photo-1573164713988-8665fc963095?q=80&w=800", "text": "Still risky. If my boss finds out, I'm fired.", "choices": {"A": "Comfort: 'It will be fine.'", "B": "Protect: 'I will write an official email taking full blame for the system glitch.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "❌ Empty words."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Taking the bullet for the customer."}} },
            "game_over_good": {"type": "WIN", "title": "SAVED", "text": "Contract renewed.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "CHURNED", "text": "Customer cancelled.", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "SUED", "text": "SLA Breach.", "score": 0}
        }
    },
    # --- 10. SPA ---
    "SC_SPA_01": {
        "title": "Spa: Bad Reaction",
        "desc": "Customer's face is itchy after facial.",
        "difficulty": "Hard",
        "customer": {"name": "Ms. Chloe", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Chloe", "traits": ["Scared", "In Pain"], "spending": "New"},
        "steps": {
            "start": { "patience": 30, "img": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?q=80&w=800", "text": "My face is burning! What did you put on me?!", "choices": {"A": "Waiver: 'You signed the waiver.'", "B": "Care: 'Ice pack! Call the manager!'"}, "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Cold hearted."}, "B": {"next": "step_2_future", "change": +30, "analysis": "✅ Safety first."}} },
            "step_2_future": { "patience": 40, "img": "https://images.unsplash.com/photo-1616394584738-fc6e612e71b9?q=80&w=800", "text": "It's better but still red. I have a casting tomorrow!", "choices": {"A": "Hope: 'It should be fine by tomorrow.'", "B": "Support: 'I am taking you to a dermatologist right now to be sure.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Uncertainty."}, "B": {"next": "step_3_bill", "change": +20, "analysis": "✅ Proactive aftermath handling."}} },
            "step_3_bill": { "patience": 50, "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?q=80&w=800", "text": "Who pays the doctor? I won't.", "choices": {"A": "Split: 'You pay 50%.'", "B": "Full: 'We cover 100% of medical bills and treatments.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Nickel and diming."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Full responsibility."}} },
            "game_over_good": {"type": "WIN", "title": "HANDLED", "text": "No lawsuit filed.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "BAD REVIEW", "text": "1-star review with photos.", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "LAWSUIT", "text": "Sued for damages.", "score": 0}
        }
    },
    # --- 11. LOGISTICS ---
    "SC_LOGISTICS_01": {
        "title": "Logistics: Damaged Equipment",
        "desc": "Late and broken delivery for an event.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. Robert", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Robert", "traits": ["High Pressure", "Furious"], "spending": "VIP Account"},
        "steps": {
            "start": { "patience": 10, "img": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=800", "text": "Late AND broken! My $500k event is tomorrow! You ruined it!", "choices": {"A": "Insurance: 'File a claim form.'", "B": "Crisis: 'I am personally handling this. Solution in 10 mins.'"}, "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Bureaucracy."}, "B": {"next": "step_2_options", "change": +40, "analysis": "✅ Immediate action."}} },
            "step_2_options": { "patience": 30, "img": "https://images.unsplash.com/photo-1493934558415-9d19f0b2b4d2?q=80&w=800", "text": "How? Imported gear takes weeks!", "choices": {"A": "Rent: 'Try renting locally?'", "B": "Dispatch: 'I diverted a truck from the next state. Arriving in 4 hours.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Don't make customer work."}, "B": {"next": "step_3_confirm", "change": +30, "analysis": "✅ Concrete solution."}} },
            "step_3_confirm": { "patience": 50, "img": "https://images.unsplash.com/photo-1505373877841-8d25f7d46678?q=80&w=800", "text": "4 hours is tight. What if the truck breaks down?", "choices": {"A": "Hope: 'It will be fine.'", "B": "Guarantee: 'I sent 2 trucks (1 backup). Plus a tech team to help install.'"}, "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Still risky."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Overwhelming support."}} },
            "game_over_good": {"type": "WIN", "title": "EVENT SAVED", "text": "Event was a success.", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "FAILED", "text": "Event cancelled.", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "FIRED", "text": "Contract terminated.", "score": 0}
        }
    }
}

DB_FILE = "scenarios.json"
HISTORY_FILE = "score_history.csv"

# ==============================================================================
# 3. DATA UTILS
# ==============================================================================
def load_data(force_reset=False):
    if force_reset or not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(INITIAL_DATA, f, indent=4)
        return INITIAL_DATA.copy()
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for k, v in INITIAL_DATA.items():
            if k not in data: data[k] = v
        return data
    except: return load_data(True)

def save_data(new_data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=4)

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
        else: st.info("No data yet.")
    else: st.info("No history found.")

# ==============================================================================
# 4. MAIN APPLICATION
# ==============================================================================
if 'current_scenario' not in st.session_state: st.session_state.current_scenario = None
if 'img_cache' not in st.session_state: st.session_state.img_cache = {}

ALL_SCENARIOS = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.title("Service Hero")
    st.caption("AI Training Hub")
    
    menu = st.radio("Navigation", ["Dashboard", "Create Scenario"])
    
    st.divider()
    if st.button("⚠️ Reset to Default"):
        load_data(True)
        st.success("Restored 11 Original Scenarios!")
        time.sleep(1)
        st.rerun()

# --- MAIN CONTENT ---
if menu == "Dashboard":
    if st.session_state.current_scenario is None:
        st.title("Welcome to Service Hero Academy 🎓")
        st.markdown("Master customer service skills with **AI-powered roleplay**.")
        
        # Player Name Input
        if 'player_name' not in st.session_state: st.session_state.player_name = ""
        if not st.session_state.player_name:
            st.info("Please enter your name to start training.")
            st.session_state.player_name = st.text_input("Your Name:")
            if not st.session_state.player_name: st.stop()
        else:
            c1, c2 = st.columns([3, 1])
            c1.success(f"Agent: **{st.session_state.player_name}**")
            if c2.button("Log out"): 
                st.session_state.player_name = ""
                st.rerun()

        with st.expander("🏆 Leaderboard & History"):
            show_leaderboard()
            
        st.divider()
        st.subheader(f"Available Scenarios ({len(ALL_SCENARIOS)})")
        
        # Grid Layout for Scenarios
        cols = st.columns(2)
        idx = 0
        for key, val in ALL_SCENARIOS.items():
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="scenario-card">
                    <h3>{val['title']}</h3>
                    <p style='color:#64748b; font-size:0.9em;'>{val['desc']}</p>
                    <span style='background:#e0f2fe; color:#0369a1; padding:2px 8px; border-radius:4px; font-size:0.8em;'>{val['difficulty']}</span>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Start Mission 🚀", key=key, use_container_width=True):
                    st.session_state.current_scenario = key
                    st.session_state.current_step = 'start'
                    st.session_state.patience = 50
                    st.session_state.history = []
                    st.rerun()
            idx += 1

    else:
        # --- GAMEPLAY SCREEN ---
        s_key = st.session_state.current_scenario
        if s_key not in ALL_SCENARIOS: 
            st.session_state.current_scenario = None
            st.rerun()
            
        scenario = ALL_SCENARIOS[s_key]
        step_id = st.session_state.current_step
        step_data = scenario['steps'][step_id]
        
        # --- AI IMAGE GENERATION (FIXED) ---
        cache_key = f"{s_key}_{step_id}"
        # Fallback image from data or placeholder
        default_img = step_data.get('img', 'https://placehold.co/800x500?text=Scenario+Scene')
        
        if cache_key not in st.session_state.img_cache:
            with st.spinner("🤖 AI is visualizing the scene..."):
                context = f"Scene: {scenario['title']}. Character {scenario['customer']['name']} says: {step_data.get('text', '')}"
                ai_url = generate_ai_image_url(context, default_img)
                st.session_state.img_cache[cache_key] = ai_url
        
        current_img = st.session_state.img_cache[cache_key]
        
        # --- SIDEBAR INFO ---
        with st.sidebar:
            st.divider()
            if st.button("❌ Exit Mission", use_container_width=True):
                st.session_state.current_scenario = None
                st.rerun()
            
            cust = scenario['customer']
            st.image(cust['avatar'], width=100)
            st.markdown(f"**{cust['name']}**")
            st.caption(", ".join(cust['traits']))
            
            # Patience Meter
            p = st.session_state.patience
            color = "green" if p > 50 else "red"
            st.markdown(f"**Customer Patience:** :{color}[{p}%]")
            st.progress(p/100)

        # --- MAIN DISPLAY ---
        if "type" in step_data: # Game Over Screen
            st.title(step_data['title'])
            st.image(current_img, use_container_width=True)
            
            if step_data['type'] == 'WIN':
                st.balloons()
                st.markdown(f"<div class='analysis-box good'><h3>🎉 SUCCESS</h3>{step_data['text']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='analysis-box bad'><h3>💀 FAILED</h3>{step_data['text']}</div>", unsafe_allow_html=True)
                
            st.metric("Final Score", step_data['score'])
            
            # Save Score Logic
            if 'saved' not in st.session_state:
                save_score(st.session_state.player_name, scenario['title'], step_data['score'], step_data['type'])
                st.session_state.saved = True
                
            if st.button("🔄 Return to Dashboard", use_container_width=True):
                st.session_state.current_scenario = None
                if 'saved' in st.session_state: del st.session_state.saved
                st.rerun()
                
            st.divider()
            st.subheader("📝 Mission Analysis")
            for h in st.session_state.history:
                icon = "✅" if h['change'] > 0 else "❌"
                color_class = "good" if h['change'] > 0 else "bad"
                st.markdown(f"""
                <div class='analysis-box {color_class}'>
                    <b>{icon} You chose:</b> {h['choice']}<br>
                    <i>👉 {h['analysis']}</i>
                </div>
                """, unsafe_allow_html=True)

        else: # Gameplay Screen
            st.header(scenario['title'])
            st.image(current_img, use_container_width=True, caption="AI Generated Scene")
            
            st.markdown(f"""
            <div class="chat-container">
                <div class="customer-label">🗣️ {cust['name']} says:</div>
                <div class="dialogue-text">"{step_data['text']}"</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Choice Buttons
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

elif menu == "Create Scenario":
    st.header("🛠️ Scenario Creator")
    st.info("Create custom scenarios here. AI will handle the images automatically!")
    
    with st.form("new_scen"):
        title = st.text_input("Title")
        desc = st.text_input("Description")
        start_txt = st.text_area("Opening Line")
        if st.form_submit_button("Save Scenario"):
            st.success("Scenario saved! (Demo Mode)")
