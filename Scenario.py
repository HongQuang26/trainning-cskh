import streamlit as st
import json
import os
import time

# ==============================================================================
# 1. CONFIGURATION & UI
# ==============================================================================
st.set_page_config(
    page_title="Training Master V7 - Deep Dive",
    page_icon="💎",
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
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. EXTENDED DATASET (3 TURNS PER SCENARIO)
# ==============================================================================
INITIAL_DATA = {
    # --- F&B ---
    "SC_FNB_01": {
        "title": "F&B: Foreign Object Incident",
        "desc": "Hair in soup. 3-Step resolution.",
        "difficulty": "Hard",
        "customer": {"name": "Ms. Jade", "avatar": "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?q=80&w=400", "traits": ["Picky", "Famous Reviewer"], "spending": "New Customer"},
        "steps": {
            "start": { # TURN 1
                "patience": 30, "img": "https://images.unsplash.com/photo-1533777857889-4be7c70b33f7?q=80&w=800",
                "text": "Manager! Look at this! A long hair in my soup! Are you feeding me garbage?",
                "choices": {"A": "Denial: 'Not our hair.'", "B": "Action: 'I am terribly sorry! Removing it now.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -40, "analysis": "❌ Denial kills trust instantly."}, "B": {"next": "step_2_wait", "change": +10, "analysis": "✅ Immediate action is correct."}}
            },
            "step_2_wait": { # TURN 2
                "patience": 40, "img": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=800",
                "text": "(5 mins later, you bring new soup) I don't even want this anymore. I've lost my appetite waiting. My friends are already halfway through their meal.",
                "choices": {"A": "Push: 'Please try it, chef made it special.'", "B": "Pivot: 'I understand completely. Let me take this away. Can I bring you a drink or dessert instead?'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Don't force food on an upset stomach."}, "B": {"next": "step_3_bill", "change": +20, "analysis": "✅ Respecting her feeling and offering alternatives."}}
            },
            "step_3_bill": { # TURN 3
                "patience": 60, "img": "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?q=80&w=800",
                "text": "Fine, just a glass of wine. But this night is ruined. Bring me the bill.",
                "choices": {"A": "Discount: 'Here is the bill with 10% off.'", "B": "Comp: 'The bill is on the house tonight. Plus a voucher for next time.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ 10% for a ruined night is an insult."}, "B": {"next": "game_over_good", "change": +40, "analysis": "🏆 Total compensation turns a disaster into a wow moment."}}
            },
            "game_over_good": {"type": "WIN", "title": "TRUST RESTORED", "text": "She was shocked by the generosity and tipped the staff.", "img": "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?q=80&w=800", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "LOST CUSTOMER", "text": "She paid but left a 1-star review.", "img": "https://images.unsplash.com/photo-1522029916167-9c1a97aa3c24?q=80&w=800", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "PR DISASTER", "text": "Viral video of argument.", "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800", "score": 0}
        }
    },

    # --- HOTEL ---
    "SC_HOTEL_01": {
        "title": "Hotel: Overbooked",
        "desc": "Honeymoon couple vs No Room. 3-Step resolution.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. Mike", "avatar": "https://images.unsplash.com/photo-1542909168-82c3e7fdca5c?q=80&w=400", "traits": ["Tired", "High Expectations"], "spending": "Honeymoon"},
        "steps": {
            "start": { # TURN 1
                "patience": 20, "img": "https://images.unsplash.com/photo-1542596594-6eb9880fb7a6?q=80&w=800",
                "text": "I booked Ocean View months ago! I will NOT accept a Garden View!",
                "choices": {"A": "Policy: 'System error. Sorry.'", "B": "Empathy: 'This is our fault. I apologize.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Excuses don't help."}, "B": {"next": "step_2_alt", "change": +20, "analysis": "✅ Taking ownership."}}
            },
            "step_2_alt": { # TURN 2
                "patience": 40, "img": "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=800",
                "text": "Apologies don't bring back the ocean! We flew 12 hours for this view. Fix it!",
                "choices": {"A": "Standard: 'I can offer free breakfast and spa credits.'", "B": "Check: 'Let me check the system for cancellations or upgrades.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Breakfast doesn't replace the room."}, "B": {"next": "step_3_upgrade", "change": +10, "analysis": "✅ Showing effort to find a real solution."}}
            },
            "step_3_upgrade": { # TURN 3
                "patience": 50, "img": "https://images.unsplash.com/photo-1618773928121-c32242e63f39?q=80&w=800",
                "text": "(Waiting anxiously) Well? Did you find anything? My wife is crying.",
                "choices": {"A": "Partial: 'We have a partial ocean view available tomorrow.'", "B": "Hero: 'I found a Presidential Suite available. I am upgrading you for free.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Still disappointing."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Exceeding expectations saves the trip."}}
            },
            "game_over_good": {"type": "WIN", "title": "DREAM TRIP", "text": "They loved the Suite.", "img": "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?q=80&w=800", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "SAD TRIP", "text": "They stayed but won't return.", "img": "https://images.unsplash.com/photo-1583323731095-d7c9bd2690f6?q=80&w=800", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "LOBBY RAGE", "text": "Demanded full refund.", "img": "https://images.unsplash.com/photo-1574790502501-701452c15414?q=80&w=800", "score": 0}
        }
    },

    # --- E-COMMERCE ---
    "SC_ECOMM_01": {
        "title": "Online: Lost Package",
        "desc": "Delivered but missing. 3-Step resolution.",
        "difficulty": "Medium",
        "customer": {"name": "Tom", "avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?q=80&w=400", "traits": ["Worried", "Suspicious"], "spending": "Low"},
        "steps": {
            "start": { # TURN 1
                "patience": 40, "img": "https://images.unsplash.com/photo-1566576912321-d58ba2188273?q=80&w=800",
                "text": "App says delivered, I have nothing! Did you steal it?",
                "choices": {"A": "Deflect: 'Check neighbors.'", "B": "Reassure: 'We take responsibility.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -20, "analysis": "❌ Don't push back."}, "B": {"next": "step_2_check", "change": +20, "analysis": "✅ Be on their side."}}
            },
            "step_2_check": { # TURN 2
                "patience": 50, "img": "https://images.unsplash.com/photo-1633934542430-0905ccb5f050?q=80&w=800",
                "text": "I checked everywhere! I need these shoes for my exam tomorrow morning!",
                "choices": {"A": "Wait: 'Wait 24h for driver update.'", "B": "Escalate: 'I am calling the driver dispatch directly right now.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ 24h is too late for his deadline."}, "B": {"next": "step_3_result", "change": +20, "analysis": "✅ Urgency matches customer needs."}}
            },
            "step_3_result": { # TURN 3
                "patience": 60, "img": "https://images.unsplash.com/photo-1528736047006-d320da8a2437?q=80&w=800",
                "text": "(Driver says he hid it in the bush) Okay, you say it's in the bush? What if it's gone?",
                "choices": {"A": "Trust: 'It should be there.'", "B": "Guarantee: 'Please check. If not there, I will Express Ship a new one immediately.'"},
                "consequences": {"A": {"next": "game_over_normal", "change": 0, "analysis": "😐 Too passive."}, "B": {"next": "game_over_good", "change": +40, "analysis": "🏆 Risk-free guarantee wins trust."}}
            },
            "game_over_good": {"type": "WIN", "title": "LOYALTY GAINED", "text": "He found it. Loves the support.", "img": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=800", "score": 100},
            "game_over_normal": {"type": "WIN", "title": "FOUND", "text": "He found it but was annoyed.", "img": "https://images.unsplash.com/photo-1556740758-90de374c12ad?q=80&w=800", "score": 70},
            "game_over_fail": {"type": "LOSE", "title": "TOO LATE", "text": "He bought shoes elsewhere.", "img": "https://images.unsplash.com/photo-1586866016892-117e620d5520?q=80&w=800", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "TRUST LOST", "text": "Reported shop.", "img": "https://images.unsplash.com/photo-1586866016892-117e620d5520?q=80&w=800", "score": 0}
        }
    },

    # --- RETAIL ---
    "SC_RETAIL_01": {
        "title": "Retail: Broken Vase",
        "desc": "VIP customer & Broken Item. 3-Step resolution.",
        "difficulty": "Hard",
        "customer": {"name": "Ms. Lan", "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=400", "traits": ["VIP", "Urgent"], "spending": "High"},
        "steps": {
            "start": { # TURN 1
                "patience": 40, "img": "https://images.unsplash.com/photo-1596496050844-461dc5b7263f?q=80&w=800",
                "text": "My $200 vase is broken! Are you scamming me?",
                "choices": {"A": "Empathy: 'So sorry! I will handle it.'", "B": "Policy: 'Give me Order ID.'"},
                "consequences": {"A": {"next": "step_2_stock", "change": 20, "analysis": "✅ Empathy first."}, "B": {"next": "game_over_bad", "change": -20, "analysis": "⚠️ Don't ask ID yet."}}
            },
            "step_2_stock": { # TURN 2
                "patience": 60, "img": "https://images.unsplash.com/photo-1556740738-b6a63e27c4df?q=80&w=800",
                "text": "I need it by 6PM for a gift! Do you have another one?",
                "choices": {"A": "Check: 'Let me check inventory... Oh, we are out of stock here.'", "B": "Check: 'Checking... Out of stock, but I can order one for next week.'"},
                "consequences": {"A": {"next": "step_3_sol", "change": 0, "analysis": "✅ Honest."}, "B": {"next": "game_over_fail", "change": -30, "analysis": "❌ Next week is too late."}}
            },
            "step_3_sol": { # TURN 3
                "patience": 50, "img": "https://images.unsplash.com/photo-1586769852044-692d6e3703f0?q=80&w=800",
                "text": "Out of stock?! You ruined my gift! What do I do now?",
                "choices": {"A": "Refund: 'Full refund.'", "B": "Magic: 'I will grab one from HQ and Uber it to you by 5PM.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "😐 Refund doesn't solve the gift problem."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Solving the 'Job to be done' (Giving a gift)."}}
            },
            "game_over_good": {"type": "WIN", "title": "EXCELLENT", "text": "She got the vase in time.", "img": "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?q=80&w=800", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "VIP LOST", "text": "She left empty handed.", "img": "https://images.unsplash.com/photo-1444312645910-ffa973656eba?q=80&w=800", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "CRISIS", "text": "Viral bad review.", "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800", "score": 0}
        }
    },

    # --- TECH ---
    "SC_TECH_01": {
        "title": "IT: Internet Outage",
        "desc": "No internet during meeting. 3-Step resolution.",
        "difficulty": "Medium",
        "customer": {"name": "Mr. Ken", "avatar": "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=400", "traits": ["Techie", "Urgent"], "spending": "Enterprise"},
        "steps": {
            "start": { # TURN 1
                "patience": 30, "img": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?q=80&w=800",
                "text": "Net is down! Meeting in progress! I restarted modem, still red light!",
                "choices": {"A": "Basic: 'Try restarting again.'", "B": "Diagnose: 'I see packet loss on your line.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ He just said he restarted!"}, "B": {"next": "step_2_fix", "change": +10, "analysis": "✅ Acknowledge his expertise."}}
            },
            "step_2_fix": { # TURN 2
                "patience": 40, "img": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=800",
                "text": "So fix it! I have 5 minutes left!",
                "choices": {"A": "Dispatch: 'Tech is coming, ETA 4 hours.'", "B": "Remote Fix: 'Attempting remote port reset...'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Too slow."}, "B": {"next": "step_3_fail", "change": +10, "analysis": "✅ Trying immediate fix."}}
            },
            "step_3_fail": { # TURN 3
                "patience": 20, "img": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?q=80&w=800",
                "text": "Remote reset failed! Still red! My meeting is dead!",
                "choices": {"A": "Give up: 'Sorry, must wait for tech.'", "B": "Workaround: 'Activate your mobile hotspot, I am adding 50GB data to your phone NOW. Use that!'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -30, "analysis": "❌ Meeting lost."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Workaround saved the meeting."}}
            },
            "game_over_good": {"type": "WIN", "title": "SMART", "text": "Meeting saved via 4G.", "img": "https://images.unsplash.com/photo-1552581234-26160f608093?q=80&w=800", "score": 90},
            "game_over_fail": {"type": "LOSE", "title": "FAILED", "text": "Meeting missed.", "img": "https://images.unsplash.com/photo-1506784983877-45594efa4cbe?q=80&w=800", "score": 50},
            "game_over_bad": {"type": "LOSE", "title": "FIRED", "text": "Contract cancelled.", "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800", "score": 0}
        }
    },

    # --- AIRLINE ---
    "SC_AIRLINE_01": {
        "title": "Airline: Flight Cancelled",
        "desc": "Wedding at risk. 3-Step resolution.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. David", "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=400", "traits": ["Stressed", "Time-critical"], "spending": "Gold Flyer"},
        "steps": {
            "start": { # TURN 1
                "patience": 20, "img": "https://images.unsplash.com/photo-1590523741831-ab7e8b8f9c7f?q=80&w=800",
                "text": "Cancelled?! I am the best man at a wedding in 6 hours! Get me on a plane NOW!",
                "choices": {"A": "Policy: 'Weather is unsafe.'", "B": "Empathy: 'Oh no! Checking alternatives.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Don't lecture him."}, "B": {"next": "step_2_alt", "change": +30, "analysis": "✅ Validating his stress."}}
            },
            "step_2_alt": { # TURN 2
                "patience": 50, "img": "https://images.unsplash.com/photo-1580894908361-967195033215?q=80&w=800",
                "text": "Hurry! The rehearsal dinner starts at 7!",
                "choices": {"A": "Our Flights: 'Next flight is tomorrow morning.'", "B": "Partners: 'Checking partner airlines too...'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Tomorrow is too late."}, "B": {"next": "step_3_mix", "change": +20, "analysis": "✅ Going beyond duty."}}
            },
            "step_3_mix": { # TURN 3
                "patience": 40, "img": "https://images.unsplash.com/photo-1519741497674-611481863552?q=80&w=800",
                "text": "No direct flights? I'm doomed!",
                "choices": {"A": "Give up: 'Sorry sir.'", "B": "Creative: 'Flight to nearby city + Taxi (Paid by us).'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "❌ Gave up too soon."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Ultimate problem solving."}}
            },
            "game_over_good": {"type": "WIN", "title": "SAVED", "text": "He made it. Thank you email.", "img": "https://images.unsplash.com/photo-1519741497674-611481863552?q=80&w=800", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "MISSED", "text": "He missed the wedding.", "img": "https://images.unsplash.com/photo-1610128070660-d90571d7192c?q=80&w=800", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "MELTDOWN", "text": "Security called.", "img": "https://images.unsplash.com/photo-1574790502501-701452c15414?q=80&w=800", "score": 0}
        }
    },

    # --- BANK ---
    "SC_BANK_01": {
        "title": "Banking: ATM Ate Card",
        "desc": "Elderly emergency. 3-Step resolution.",
        "difficulty": "Hard",
        "customer": {"name": "Mrs. Evelyn", "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=400", "traits": ["Elderly", "Panicked"], "spending": "Loyal"},
        "steps": {
            "start": { # TURN 1
                "patience": 30, "img": "https://images.unsplash.com/photo-1601597111637-3229586107b5?q=80&w=800",
                "text": "Help! Machine stole my card! Need cash for medicine! Branch closed!",
                "choices": {"A": "Wait: 'Come Monday.'", "B": "Reassure: 'Card is safe. Lets get cash.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Health risk."}, "B": {"next": "step_2_verify", "change": +30, "analysis": "✅ Prioritizing needs."}}
            },
            "step_2_verify": { # TURN 2
                "patience": 50, "img": "https://images.unsplash.com/photo-1556742031-c6961e8560b0?q=80&w=800",
                "text": "Okay... but how? I don't have ID on me.",
                "choices": {"A": "Strict: 'Need ID for verification.'", "B": "Flexible: 'I can verify you via recent transactions.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Dead end."}, "B": {"next": "step_3_tech", "change": +20, "analysis": "✅ Flexible security."}}
            },
            "step_3_tech": { # TURN 3
                "patience": 60, "img": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?q=80&w=800",
                "text": "I verified. Now what? I can't use the app well.",
                "choices": {"A": "Guide: 'I will guide you button by button on ATM.'", "B": "Push: 'Download the app.'"},
                "consequences": {"A": {"next": "game_over_good", "change": +40, "analysis": "🏆 Patience wins."}, "B": {"next": "game_over_fail", "change": -20, "analysis": "❌ Too complex for her."}}
            },
            "game_over_good": {"type": "WIN", "title": "SECURED", "text": "Got medicine.", "img": "https://images.unsplash.com/photo-1556742031-c6961e8560b0?q=80&w=800", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "GAVE UP", "text": "Left without cash.", "img": "https://images.unsplash.com/photo-1573497491208-6b1acb260507?q=80&w=800", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "LOST TRUST", "text": "Left bank.", "img": "https://images.unsplash.com/photo-1522029916167-9c1a97aa3c24?q=80&w=800", "score": 0}
        }
    },

    # --- REAL ESTATE ---
    "SC_REALESTATE_01": {
        "title": "Real Estate: Moldy Apartment",
        "desc": "Mold in luxury flat. 3-Step resolution.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. Chen", "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=400", "traits": ["Rich", "Health-conscious"], "spending": "Luxury"},
        "steps": {
            "start": { # TURN 1
                "patience": 20, "img": "https://images.unsplash.com/photo-1581876883325-32a5b8f7fb5a?q=80&w=800",
                "text": "I pay $4000/month and found toxic mold! My son has asthma!",
                "choices": {"A": "Defend: 'Did you open windows?'", "B": "Alarm: 'Get out now. I am coming.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -40, "analysis": "❌ Blaming tenant."}, "B": {"next": "step_2_inspect", "change": +30, "analysis": "✅ Health safety first."}}
            },
            "step_2_inspect": { # TURN 2
                "patience": 40, "img": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?q=80&w=800",
                "text": "(You arrive) Look at this! It's everywhere! We can't sleep here.",
                "choices": {"A": "Clean: 'I'll call cleaners tomorrow.'", "B": "Relocate: 'Agreed. You need to move.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -30, "analysis": "⚠️ Tomorrow is too late."}, "B": {"next": "step_3_hotel", "change": +20, "analysis": "✅ Immediate solution."}}
            },
            "step_3_hotel": { # TURN 3
                "patience": 50, "img": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=800",
                "text": "Where do we go? A cheap motel?",
                "choices": {"A": "Budget: 'I have a budget of $100/night.'", "B": "Luxury: 'Booked 5-star hotel nearby.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Insulting for luxury client."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Matches status."}}
            },
            "game_over_good": {"type": "WIN", "title": "AVERTED", "text": "Happy with hotel.", "img": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=800", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "LEASE BROKEN", "text": "Moved out.", "img": "https://images.unsplash.com/photo-1596496321628-16711bb94e68?q=80&w=800", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "LAWSUIT", "text": "Sued for health damages.", "img": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=800", "score": 0}
        }
    },

    # --- SAAS ---
    "SC_SAAS_01": {
        "title": "SaaS: Data Loss",
        "desc": "Deleted data. 3-Step resolution.",
        "difficulty": "Very Hard",
        "customer": {"name": "Sarah", "avatar": "https://images.unsplash.com/photo-1573496799652-408c2ac9fe98?q=80&w=400", "traits": ["Furious", "High stakes"], "spending": "Enterprise"},
        "steps": {
            "start": { # TURN 1
                "patience": 10, "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800",
                "text": "WHERE IS OUR DATA?! Presentation in 2 hours!",
                "choices": {"A": "Tips: 'Clear cache?'", "B": "Escalate: 'This is SEV1. On it.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -20, "analysis": "❌ Insulting."}, "B": {"next": "step_2_status", "change": +30, "analysis": "✅ Correct severity."}}
            },
            "step_2_status": { # TURN 2
                "patience": 30, "img": "https://images.unsplash.com/photo-1551434678-e076c223a692?q=80&w=800",
                "text": "You found the bug, but restore takes 4 hours! We miss the deadline!",
                "choices": {"A": "Sorry: 'Nothing we can do.'", "B": "Alternative: 'Can we restore partial data manually?'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Passive."}, "B": {"next": "step_3_ceo", "change": +20, "analysis": "✅ Trying to save the day."}}
            },
            "step_3_ceo": { # TURN 3
                "patience": 40, "img": "https://images.unsplash.com/photo-1521791136064-7986c2920216?q=80&w=800",
                "text": "It's still risky. My boss is going to fire me.",
                "choices": {"A": "Reassure: 'It will be fine.'", "B": "Cover: 'I will call your boss and take full blame.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "❌ Empty words."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Saving her job."}}
            },
            "game_over_good": {"type": "WIN", "title": "SAVED", "text": "Contract renewed.", "img": "https://images.unsplash.com/photo-1521791136064-7986c2920216?q=80&w=800", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "CHURNED", "text": "Lost client.", "img": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?q=80&w=800", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "LEGAL", "text": "Breach of contract.", "img": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=800", "score": 0}
        }
    },

    # --- SPA ---
    "SC_SPA_01": {
        "title": "Spa: Allergy",
        "desc": "Bad reaction. 3-Step resolution.",
        "difficulty": "Hard",
        "customer": {"name": "Ms. Chloe", "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=400", "traits": ["Scared", "Pain"], "spending": "New"},
        "steps": {
            "start": { # TURN 1
                "patience": 30, "img": "https://images.unsplash.com/photo-1501594256690-b7a1a14527c5?q=80&w=800",
                "text": "My face is burning! You ruined me!",
                "choices": {"A": "Paperwork: 'You signed waiver.'", "B": "Care: 'Medic!'" },
                "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Cold hearted."}, "B": {"next": "step_2_future", "change": +30, "analysis": "✅ Safety first."}}
            },
            "step_2_future": { # TURN 2
                "patience": 40, "img": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?q=80&w=800",
                "text": "(Ice applied) It's better but still red. I have an audition tomorrow!",
                "choices": {"A": "Hope: 'It should go down.'", "B": "Support: 'Lets see a dermatologist now.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ Uncertainty."}, "B": {"next": "step_3_bill", "change": +20, "analysis": "✅ Proactive care."}}
            },
            "step_3_bill": { # TURN 3
                "patience": 50, "img": "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?q=80&w=800",
                "text": "Doctors are expensive! I won't pay for that.",
                "choices": {"A": "Policy: 'We are not liable.'", "B": "Pay: 'We cover all bills.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "❌ Triggers lawsuit."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Prevents lawsuit."}}
            },
            "game_over_good": {"type": "WIN", "title": "MANAGED", "text": "No lawsuit.", "img": "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?q=80&w=800", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "BAD REP", "text": "Bad reviews.", "img": "https://images.unsplash.com/photo-1522029916167-9c1a97aa3c24?q=80&w=800", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "LAWSUIT", "text": "Sued.", "img": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=800", "score": 0}
        }
    },

    # --- LOGISTICS ---
    "SC_LOGISTICS_01": {
        "title": "Logistics: Damaged Shipment",
        "desc": "Event gear broken. 3-Step resolution.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. Robert", "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=400", "traits": ["Pressure", "Furious"], "spending": "Key Account"},
        "steps": {
            "start": { # TURN 1
                "patience": 10, "img": "https://images.unsplash.com/photo-1586864387967-d021563e6516?q=80&w=800",
                "text": "Late and smashed! Event is tomorrow! $500k event ruined!",
                "choices": {"A": "Insurance: 'File claim.'", "B": "Crisis: 'Fixing this personally.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Bureaucracy kills."}, "B": {"next": "step_2_options", "change": +40, "analysis": "✅ Operations rescue."}}
            },
            "step_2_options": { # TURN 2
                "patience": 30, "img": "https://images.unsplash.com/photo-1494412651409-4963d24a38b8?q=80&w=800",
                "text": "Fix how? You can't ship new ones in time!",
                "choices": {"A": "Rental: 'Try local rental?'", "B": "Charter: 'Chartering truck from other city.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ 'Trying' is weak."}, "B": {"next": "step_3_confirm", "change": +30, "analysis": "✅ Certainty needed."}}
            },
            "step_3_confirm": { # TURN 3
                "patience": 50, "img": "https://images.unsplash.com/photo-1511578314322-379afb476865?q=80&w=800",
                "text": "Truck takes 6 hours. It cuts it too close to the event start.",
                "choices": {"A": "Hope: 'It should make it.'", "B": "Double Down: 'Sent 2 trucks (Backup). Plus crew to help setup.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Still risky."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Overwhelming force."}}
            },
            "game_over_good": {"type": "WIN", "title": "SAVED", "text": "Event succeeded.", "img": "https://images.unsplash.com/photo-1511578314322-379afb476865?q=80&w=800", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "RUINED", "text": "Event failed.", "img": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?q=80&w=800", "score": 30},
            "game_over_bad": {"type": "LOSE", "title": "FIRED", "text": "Account lost.", "img": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=800", "score": 0}
        }
    }
}

DB_FILE = "scenarios.json"

def load_data():
    """Load from JSON or create using INITIAL_DATA."""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(INITIAL_DATA, f, ensure_ascii=False, indent=4)
        return INITIAL_DATA
    
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Auto-update: Add missing scenarios from code to JSON
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

# ==============================================================================
# 3. CREATOR & GAME LOGIC
# ==============================================================================
def create_new_scenario_ui():
    st.header("🛠️ Create New Scenario")
    st.info("Create a 1-step quick scenario.")
    
    with st.form("creator_form"):
        c1, c2 = st.columns(2)
        with c1:
            title = st.text_input("Title", placeholder="e.g. Late Pizza")
            desc = st.text_input("Description", placeholder="e.g. 1 hour late")
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        with c2:
            cust_name = st.text_input("Customer Name", placeholder="e.g. Mr. Joe")
            cust_trait = st.text_input("Trait", placeholder="e.g. Hungry")
            cust_spend = st.text_input("Spending", placeholder="e.g. VIP")

        st.divider()
        start_text = st.text_area("Situation (Customer says...)", placeholder="Where is my food?!")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("### ✅ Correct Choice (A)")
            opt_a_text = st.text_input("Choice A", placeholder="Refund + Free Pizza")
            opt_a_analysis = st.text_input("Why A is good?", placeholder="Fixes the hunger issue.")
            opt_a_result = st.text_input("Win Message", placeholder="Customer is happy.")
        with col_b:
            st.markdown("### ❌ Wrong Choice (B)")
            opt_b_text = st.text_input("Choice B", placeholder="Blame traffic")
            opt_b_analysis = st.text_input("Why B is bad?", placeholder="Excuses don't help.")
            opt_b_result = st.text_input("Lose Message", placeholder="Customer left bad review.")

        if st.form_submit_button("💾 Save"):
            if title and start_text:
                new_id = f"SC_CUSTOM_{int(time.time())}"
                new_entry = {
                    "title": title, "desc": desc, "difficulty": difficulty,
                    "customer": {"name": cust_name, "avatar": "https://images.unsplash.com/photo-1511367461989-f85a21fda167?q=80&w=400", "traits": [cust_trait], "spending": cust_spend},
                    "steps": {
                        "start": {
                            "patience": 40, "img": "https://images.unsplash.com/photo-1528642474493-1df4321024e1?q=80&w=800",
                            "text": start_text,
                            "choices": {"A": opt_a_text, "B": opt_b_text},
                            "consequences": {
                                "A": {"next": "win", "change": 60, "analysis": f"✅ {opt_a_analysis}"},
                                "B": {"next": "lose", "change": -40, "analysis": f"❌ {opt_b_analysis}"}
                            }
                        },
                        "win": {"type": "WIN", "title": "SUCCESS", "text": opt_a_result, "img": "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?q=80&w=800", "score": 100},
                        "lose": {"type": "LOSE", "title": "FAILED", "text": opt_b_result, "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800", "score": 0}
                    }
                }
                data = load_data()
                data[new_id] = new_entry
                save_data(data)
                st.success("Saved! Check Dashboard.")
                time.sleep(1)
                st.rerun()

if 'current_scenario' not in st.session_state: st.session_state.current_scenario = None
if 'current_step' not in st.session_state: st.session_state.current_step = None
if 'patience_meter' not in st.session_state: st.session_state.patience_meter = 50
if 'history' not in st.session_state: st.session_state.history = []

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
# 4. MAIN APP
# ==============================================================================
with st.sidebar:
    st.title("🎛️ Menu")
    menu = st.radio("Navigate", ["Dashboard", "🛠️ Create New Scenario"])
    st.divider()
    st.caption("Training Master v7.0")

ALL_SCENARIOS = load_data()

if menu == "🛠️ Create New Scenario":
    reset_game()
    create_new_scenario_ui()

elif menu == "Dashboard":
    if st.session_state.current_scenario is None:
        st.title("🎓 TRAINING DASHBOARD")
        st.caption(f"Total Scenarios: {len(ALL_SCENARIOS)}")
        st.divider()
        
        cols = st.columns(2)
        count = 0
        for key, data in ALL_SCENARIOS.items():
            with cols[count % 2]:
                with st.container(border=True):
                    c1, c2 = st.columns([5, 1])
                    with c1: st.subheader(data['title'])
                    with c2: 
                        if st.button("🗑️", key=f"del_{key}"):
                            delete_scenario(key)
                            st.rerun()
                    st.write(f"📝 {data['desc']}")
                    if st.button(f"🚀 Play", key=f"btn_{key}", use_container_width=True):
                        st.session_state.current_scenario = key
                        st.session_state.current_step = 'start'
                        st.session_state.patience_meter = data['steps']['start']['patience']
                        st.session_state.history = []
                        st.rerun()
            count += 1
            
    else:
        s_key = st.session_state.current_scenario
        if s_key not in ALL_SCENARIOS: reset_game(); st.rerun()
        s_data = ALL_SCENARIOS[s_key]
        step_data = s_data['steps'][st.session_state.current_step]
        
        with st.sidebar:
            st.divider()
            st.button("❌ Exit", on_click=reset_game, use_container_width=True)
            st.divider()
            cust = s_data['customer']
            st.image(cust['avatar'], width=100)
            st.write(f"**{cust['name']}**")
            st.write(f"Traits: {', '.join(cust['traits'])}")
            st.progress(st.session_state.patience_meter / 100, text=f"Patience: {st.session_state.patience_meter}%")

        if "type" in step_data:
            st.markdown(f"# {step_data['title']}")
            c1, c2 = st.columns([1, 1.5])
            with c1: st.image(step_data['img'], use_container_width=True)
            with c2:
                if step_data['type'] == 'WIN': st.success(step_data['text']); st.balloons()
                else: st.error(step_data['text'])
                st.metric("Score", step_data['score'])
                if st.button("🔄 Replay"): 
                    st.session_state.current_step = 'start'
                    st.session_state.patience_meter = 50
                    st.session_state.history = []
                    st.rerun()
            st.divider()
            for h in st.session_state.history:
                icon = "✅" if h['change'] > 0 else "❌"
                bg = "analysis-box-good" if h['change'] > 0 else "analysis-box-bad"
                st.markdown(f"<div class='{bg}'><b>{icon} Analysis:</b> {h['analysis']}</div>", unsafe_allow_html=True)
        else:
            st.subheader(s_data['title'])
            c1, c2 = st.columns([1, 2])
            with c1: st.image(step_data['img'], use_container_width=True)
            with c2:
                st.markdown(f"<div class='chat-container'><div class='customer-name'>🗣️ {cust['name']}</div><div class='dialogue'>\"{step_data['text']}\"</div></div>", unsafe_allow_html=True)
                for k, v in step_data['choices'].items():
                    if st.button(f"{k}. {v}", use_container_width=True): make_choice(k, step_data); st.rerun()
