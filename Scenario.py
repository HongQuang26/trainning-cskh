import streamlit as st
import json
import os
import time

# ==============================================================================
# 1. CONFIGURATION & UI
# ==============================================================================
st.set_page_config(
    page_title="Training Master V6 - Ultimate",
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
# 2. HUGE DATASET (11 SCENARIOS)
# ==============================================================================
# Đây là kho dữ liệu tích hợp sẵn (Hardcoded)
INITIAL_DATA = {
    # --- OLD SCENARIOS (5) ---
    "SC_FNB_01": {
        "title": "F&B: Foreign Object Incident",
        "desc": "Customer discovers a hair in their soup at a 5-star restaurant.",
        "difficulty": "Hard",
        "customer": {"name": "Ms. Jade", "avatar": "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?q=80&w=400", "traits": ["Picky", "Famous Reviewer"], "spending": "New Customer"},
        "steps": {
            "start": {
                "patience": 30, "img": "https://images.unsplash.com/photo-1533777857889-4be7c70b33f7?q=80&w=800",
                "text": "Manager! Look at this! A long hair in my soup! Are you feeding me garbage?",
                "choices": {"A": "Denial: 'That hair is blonde, our staff has black hair. Is it yours?'", "B": "Action: 'I am terribly sorry! I will remove this immediately.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -40, "analysis": "❌ Never blame the customer."}, "B": {"next": "step_compensate", "change": +20, "analysis": "✅ Acknowledge and act fast."}}
            },
            "step_compensate": {
                "patience": 50, "img": "https://images.unsplash.com/photo-1552581234-26160f608093?q=80&w=800",
                "text": "My appetite is gone. How will you fix this?",
                "choices": {"A": "Standard: 'New soup + 10% discount.'", "B": "WOW: 'Free meal tonight + Special dessert.'"},
                "consequences": {"A": {"next": "game_over_fail", "change": -10, "analysis": "⚠️ 10% is not enough."}, "B": {"next": "game_over_good", "change": +50, "analysis": "🏆 Over-compensation saves reputation."}}
            },
            "game_over_good": {"type": "WIN", "title": "TRUST RESTORED", "text": "She wrote a great review.", "img": "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?q=80&w=800", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "CUSTOMER LOST", "text": "She left unhappy.", "img": "https://images.unsplash.com/photo-1522029916167-9c1a97aa3c24?q=80&w=800", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "PR DISASTER", "text": "Viral TikTok exposing the restaurant.", "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800", "score": 0}
        }
    },
    "SC_HOTEL_01": {
        "title": "Hotel: Overbooked",
        "desc": "Honeymoon couple arrives, Ocean View room is unavailable.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. Mike", "avatar": "https://images.unsplash.com/photo-1542909168-82c3e7fdca5c?q=80&w=400", "traits": ["Tired", "High Expectations"], "spending": "Honeymoon"},
        "steps": {
            "start": {
                "patience": 20, "img": "https://images.unsplash.com/photo-1542596594-6eb9880fb7a6?q=80&w=800",
                "text": "I booked Ocean View months ago! I will NOT accept a Garden View!",
                "choices": {"A": "Blame System: 'System error. Sorry.'", "B": "Ownership: 'This is our fault. I apologize.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -30, "analysis": "❌ Don't blame the system."}, "B": {"next": "step_upgrade", "change": +20, "analysis": "✅ Take ownership immediately."}}
            },
            "step_upgrade": {
                "patience": 40, "img": "https://images.unsplash.com/photo-1618773928121-c32242e63f39?q=80&w=800",
                "text": "But we dreamed about the ocean...",
                "choices": {"A": "Upgrade: 'Free upgrade to Presidential Suite.'", "B": "Refund: 'Refund difference + 20% off.'"},
                "consequences": {"A": {"next": "game_over_good", "change": +60, "analysis": "🏆 Give something better to fix the mood."}, "B": {"next": "game_over_fail", "change": -20, "analysis": "⚠️ Money doesn't fix a ruined honeymoon."}}
            },
            "game_over_good": {"type": "WIN", "title": "DREAM TRIP", "text": "They loved the Suite.", "img": "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?q=80&w=800", "score": 100},
            "game_over_fail": {"type": "LOSE", "title": "SAD TRIP", "text": "They stayed but won't return.", "img": "https://images.unsplash.com/photo-1583323731095-d7c9bd2690f6?q=80&w=800", "score": 40},
            "game_over_bad": {"type": "LOSE", "title": "LOBBY RAGE", "text": "They demanded a full refund and left.", "img": "https://images.unsplash.com/photo-1574790502501-701452c15414?q=80&w=800", "score": 0}
        }
    },
    "SC_ECOMM_01": {
        "title": "Online: Lost Package",
        "desc": "App says 'Delivered' but customer has nothing.",
        "difficulty": "Medium",
        "customer": {"name": "Tom", "avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?q=80&w=400", "traits": ["Worried", "Suspicious"], "spending": "Low"},
        "steps": {
            "start": {
                "patience": 40, "img": "https://images.unsplash.com/photo-1566576912321-d58ba2188273?q=80&w=800",
                "text": "App says delivered, I have nothing! Did the driver steal it?",
                "choices": {"A": "Deflect: 'Check with neighbors.'", "B": "Reassure: 'We take full responsibility.'"},
                "consequences": {"A": {"next": "step_panic", "change": -20, "analysis": "⚠️ Don't push back."}, "B": {"next": "step_investigate", "change": +20, "analysis": "✅ Be on their side."}}
            },
            "step_panic": {
                "patience": 20, "img": "https://images.unsplash.com/photo-1633934542430-0905ccb5f050?q=80&w=800",
                "text": "This is a scam! Refund me!",
                "choices": {"A": "Firm: 'Calm down.'", "B": "Promise: 'If not found by 6PM, we ship a new one.'"},
                "consequences": {"A": {"next": "game_over_bad", "change": -20, "analysis": "❌ Antagonistic."}, "B": {"next": "game_over_good", "change": +50, "analysis": "✅ Worst-case guarantee works."}}
            },
            "step_investigate": {
                "patience": 60, "img": "https://images.unsplash.com/photo-1528736047006-d320da8a2437?q=80&w=800",
                "text": "Driver left it at the back gate security.",
                "choices": {"A": "Simple: 'Please go get it.'", "B": "Thoughtful: 'Sorry for the worry. Here is a voucher.'"},
                "consequences": {"A": {"next": "game_over_normal", "change": +10, "analysis": "🙂 Average experience."}, "B": {"next": "game_over_good_found", "change": +30, "analysis": "✅ Small gift smooths things over."}}
            },
            "game_over_good": {"type": "WIN", "title": "RESCUE", "text": "Shipped a new pair. Loyal customer.", "img": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=800", "score": 100},
            "game_over_good_found": {"type": "WIN", "title": "FOUND", "text": "He appreciated the voucher.", "img": "https://images.unsplash.com/photo-1556740758-90de374c12ad?q=80&w=800", "score": 90},
            "game_over_normal": {"type": "WIN", "title": "RECEIVED", "text": "He got it but was annoyed.", "img": "https://images.unsplash.com/photo-1598942610451-9573a059795c?q=80&w=800", "score": 70},
            "game_over_bad": {"type": "LOSE", "title": "TRUST LOST", "text": "He reported the shop.", "img": "https://images.unsplash.com/photo-1586866016892-117e620d5520?q=80&w=800", "score": 10}
        }
    },
    "SC_RETAIL_01": {
        "title": "Retail: Broken Vase",
        "desc": "VIP customer received a broken vase.",
        "difficulty": "Hard",
        "customer": {"name": "Ms. Lan", "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=400", "traits": ["VIP", "Urgent"], "spending": "High"},
        "steps": {
            "start": {
                "patience": 40, "img": "https://images.unsplash.com/photo-1596496050844-461dc5b7263f?q=80&w=800",
                "text": "My $200 vase is broken! Are you scamming me?",
                "choices": {"A": "Empathy: 'So sorry! I will handle it.'", "B": "Policy: 'Give me Order ID.'"},
                "consequences": {"A": {"next": "step_solution", "change": 20, "analysis": "✅ Empathy first."}, "B": {"next": "step_rage", "change": -20, "analysis": "⚠️ Don't ask ID yet."}}
            },
            "step_solution": {
                "patience": 60, "img": "https://images.unsplash.com/photo-1556740738-b6a63e27c4df?q=80&w=800",
                "text": "I need it by 6PM!",
                "choices": {"A": "Flexible: 'Express shipping now.'", "B": "Rigid: 'Return it first.'"},
                "consequences": {"A": {"next": "win", "change": 30, "analysis": "✅ Bend rules for VIPs."}, "B": {"next": "lose", "change": -50, "analysis": "❌ Lost the customer."}}
            },
            "step_rage": {
                "patience": 20, "img": "https://images.unsplash.com/photo-1555861496-0666c8981751?q=80&w=800",
                "text": "I don't have time for IDs!",
                "choices": {"A": "Soft: 'I'll look up by phone.'", "B": "Hard: 'System needs ID.'"},
                "consequences": {"A": {"next": "step_solution", "change": 10, "analysis": "✅ Good recovery."}, "B": {"next": "bad", "change": -20, "analysis": "❌ Don't argue."}}
            },
            "win": {"type": "WIN", "title": "EXCELLENT", "text": "She is happy.", "img": "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?q=80&w=800", "score": 100},
            "lose": {"type": "LOSE", "title": "VIP LOST", "text": "She left.", "img": "https://images.unsplash.com/photo-1444312645910-ffa973656eba?q=80&w=800", "score": 40},
            "bad": {"type": "LOSE", "title": "CRISIS", "text": "Viral bad review.", "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800", "score": 0}
        }
    },
    "SC_TECH_01": {
        "title": "IT: Internet Outage",
        "desc": "Internet down during important meeting.",
        "difficulty": "Medium",
        "customer": {"name": "Mr. Ken", "avatar": "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=400", "traits": ["Techie", "Urgent"], "spending": "Enterprise"},
        "steps": {
            "start": {
                "patience": 30, "img": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?q=80&w=800",
                "text": "Net is down! Meeting in progress!",
                "choices": {"A": "Tech Q: 'What color is PON light?'", "B": "Apology: 'Maybe shark bit cable.'"},
                "consequences": {"A": {"next": "step_check", "change": 10, "analysis": "✅ Straight to business."}, "B": {"next": "bad", "change": -30, "analysis": "❌ Don't make excuses."}}
            },
            "step_check": {
                "patience": 40, "img": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=800",
                "text": "Red light. Need net in 5 mins!",
                "choices": {"A": "Wait: 'Tech in 30 mins.'", "B": "Workaround: 'Use 4G, I'll add data.'"},
                "consequences": {"A": {"next": "lose", "change": -10, "analysis": "⚠️ Too slow."}, "B": {"next": "win", "change": 40, "analysis": "✅ Save the meeting first."}}
            },
            "win": {"type": "WIN", "title": "SMART", "text": "Meeting saved via 4G.", "img": "https://images.unsplash.com/photo-1552581234-26160f608093?q=80&w=800", "score": 90},
            "lose": {"type": "LOSE", "title": "FAILED", "text": "Meeting missed.", "img": "https://images.unsplash.com/photo-1506784983877-45594efa4cbe?q=80&w=800", "score": 50},
            "bad": {"type": "LOSE", "title": "FIRED", "text": "Contract cancelled.", "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800", "score": 0}
        }
    },

    # --- 6 NEW SCENARIOS (ADDED DIRECTLY) ---
    "SC_AIRLINE_01": {
        "title": "Airline: Flight Cancelled",
        "desc": "Flight cancelled due to weather. Passenger will miss a vital wedding.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. David", "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=400", "traits": ["Stressed", "Time-critical"], "spending": "Gold Flyer"},
        "steps": {
            "start": {
                "patience": 20, "img": "https://images.unsplash.com/photo-1590523741831-ab7e8b8f9c7f?q=80&w=800",
                "text": "Cancelled?! I am the best man at a wedding in 6 hours! Get me on a plane NOW!",
                "choices": {"A": "Blame Weather: 'It's a typhoon. Please understand.'", "B": "Empathy: 'Oh no! Let me check all partner airlines immediately.'"},
                "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Don't hide behind 'weather' when emotions are high."}, "B": {"next": "step_opt", "change": +30, "analysis": "✅ Excellent acknowledgment."}}
            },
            "step_opt": {
                "patience": 50, "img": "https://images.unsplash.com/photo-1580894908361-967195033215?q=80&w=800",
                "text": "Checking isn't enough! Do whatever it takes!",
                "choices": {"A": "Standard: 'Next flight is tomorrow.'", "B": "Creative: 'Partner flight from nearby city. We cover taxi.'"},
                "consequences": {"A": {"next": "fail", "change": -20, "analysis": "⚠️ Tomorrow is too late."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Going the extra mile."}}
            },
            "win": {"type": "WIN", "title": "SAVED THE DAY", "text": "He made it. Thank you email sent.", "img": "https://images.unsplash.com/photo-1519741497674-611481863552?q=80&w=800", "score": 100},
            "fail": {"type": "LOSE", "title": "MISSED WEDDING", "text": "He missed it. Never flying again.", "img": "https://images.unsplash.com/photo-1610128070660-d90571d7192c?q=80&w=800", "score": 40},
            "lose": {"type": "LOSE", "title": "MELTDOWN", "text": "Security called.", "img": "https://images.unsplash.com/photo-1574790502501-701452c15414?q=80&w=800", "score": 0}
        }
    },
    "SC_BANK_01": {
        "title": "Banking: ATM Ate Card",
        "desc": "ATM swallowed card on Saturday night. Elderly customer needs cash.",
        "difficulty": "Hard",
        "customer": {"name": "Mrs. Evelyn", "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=400", "traits": ["Elderly", "Panicked"], "spending": "Loyal"},
        "steps": {
            "start": {
                "patience": 30, "img": "https://images.unsplash.com/photo-1601597111637-3229586107b5?q=80&w=800",
                "text": "Help! Machine stole my card! I need cash for medicine! Branch is closed!",
                "choices": {"A": "Protocol: 'Come back Monday with ID.'", "B": "Reassure: 'Card is safe. Let's get you cash cardless.'"},
                "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Dangerous to tell elderly to wait for medicine."}, "B": {"next": "step_sol", "change": +30, "analysis": "✅ Prioritize immediate needs."}}
            },
            "step_sol": {
                "patience": 60, "img": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?q=80&w=800",
                "text": "Cash without card? I don't understand technology.",
                "choices": {"A": "Instruction: 'Use the app.'", "B": "Guided: 'Stay on the phone. I will guide you step by step.'"},
                "consequences": {"A": {"next": "fail", "change": -20, "analysis": "⚠️ Don't confuse her."}, "B": {"next": "win", "change": +40, "analysis": "🏆 Hand-holding is key."}}
            },
            "win": {"type": "WIN", "title": "CASH SECURED", "text": "She got her medicine.", "img": "https://images.unsplash.com/photo-1556742031-c6961e8560b0?q=80&w=800", "score": 100},
            "fail": {"type": "LOSE", "title": "GAVE UP", "text": "She couldn't do it.", "img": "https://images.unsplash.com/photo-1573497491208-6b1acb260507?q=80&w=800", "score": 30},
            "lose": {"type": "LOSE", "title": "LOST TRUST", "text": "She left the bank.", "img": "https://images.unsplash.com/photo-1522029916167-9c1a97aa3c24?q=80&w=800", "score": 0}
        }
    },
    "SC_REALESTATE_01": {
        "title": "Real Estate: Moldy Apartment",
        "desc": "Tenant found mold in luxury apartment.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. Chen", "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=400", "traits": ["Rich", "Health-conscious"], "spending": "Luxury"},
        "steps": {
            "start": {
                "patience": 20, "img": "https://images.unsplash.com/photo-1581876883325-32a5b8f7fb5a?q=80&w=800",
                "text": "I pay $4000/month and found toxic mold! My son has asthma!",
                "choices": {"A": "Defensive: 'Did you keep windows closed?'", "B": "Alarmed: 'Omg, get out of that room. I am coming.'"},
                "consequences": {"A": {"next": "lose", "change": -40, "analysis": "❌ Don't blame tenant."}, "B": {"next": "step_act", "change": +30, "analysis": "✅ Treat as health emergency."}}
            },
            "step_act": {
                "patience": 50, "img": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?q=80&w=800",
                "text": "We cannot stay here tonight.",
                "choices": {"A": "Standard: 'Use other bedroom.'", "B": "Luxury: 'I booked a 5-star hotel for you.'"},
                "consequences": {"A": {"next": "fail", "change": -20, "analysis": "⚠️ Unacceptable for luxury."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Matches price point."}}
            },
            "win": {"type": "WIN", "title": "CRISIS AVERTED", "text": "Family happy with hotel.", "img": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=800", "score": 100},
            "fail": {"type": "LOSE", "title": "LEASE BROKEN", "text": "They left.", "img": "https://images.unsplash.com/photo-1596496321628-16711bb94e68?q=80&w=800", "score": 30},
            "lose": {"type": "LOSE", "title": "LAWSUIT", "text": "Legal battle incoming.", "img": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=800", "score": 0}
        }
    },
    "SC_SAAS_01": {
        "title": "SaaS: Data Loss",
        "desc": "System update deleted critical data before client deadline.",
        "difficulty": "Very Hard",
        "customer": {"name": "Sarah", "avatar": "https://images.unsplash.com/photo-1573496799652-408c2ac9fe98?q=80&w=400", "traits": ["Furious", "High stakes"], "spending": "Enterprise"},
        "steps": {
            "start": {
                "patience": 10, "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800",
                "text": "WHERE IS OUR DATA?! We have a presentation in 2 hours!",
                "choices": {"A": "Standard: 'Clear cache?'", "B": "Emergency: 'This is SEV1. Escalating now.'"},
                "consequences": {"A": {"next": "lose", "change": -20, "analysis": "❌ Insulting suggestion."}, "B": {"next": "step_upd", "change": +30, "analysis": "✅ Correct severity identification."}}
            },
            "step_upd": {
                "patience": 40, "img": "https://images.unsplash.com/photo-1551434678-e076c223a692?q=80&w=800",
                "text": "My CEO is asking. Am I going to get fired?",
                "choices": {"A": "Slow: 'Wait 2 hours.'", "B": "Mitigation: 'I will call your CEO and take the blame.'"},
                "consequences": {"A": {"next": "fail", "change": -10, "analysis": "⚠️ Not enough."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Ultimate partnership."}}
            },
            "win": {"type": "WIN", "title": "SAVED", "text": "Sarah safe, contract renewed.", "img": "https://images.unsplash.com/photo-1521791136064-7986c2920216?q=80&w=800", "score": 100},
            "fail": {"type": "LOSE", "title": "CHURNED", "text": "Missed deadline.", "img": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?q=80&w=800", "score": 30},
            "lose": {"type": "LOSE", "title": "LEGAL", "text": "Breach of contract.", "img": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=800", "score": 0}
        }
    },
    "SC_SPA_01": {
        "title": "Spa: Allergy",
        "desc": "Bad reaction to facial treatment.",
        "difficulty": "Hard",
        "customer": {"name": "Ms. Chloe", "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=400", "traits": ["Scared", "Pain"], "spending": "New"},
        "steps": {
            "start": {
                "patience": 30, "img": "https://images.unsplash.com/photo-1501594256690-b7a1a14527c5?q=80&w=800",
                "text": "My face is burning! What did you do?!",
                "choices": {"A": "Form: 'You checked No Allergies.'", "B": "Medical: 'Sit down. Medic!'" },
                "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Victim blaming."}, "B": {"next": "step_care", "change": +30, "analysis": "✅ Health first."}}
            },
            "step_care": {
                "patience": 50, "img": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?q=80&w=800",
                "text": "I have an audition tomorrow! If I lose it, it's your fault.",
                "choices": {"A": "Liability: 'We followed procedure.'", "B": "Support: 'We cover dermatologist bills.'"},
                "consequences": {"A": {"next": "fail", "change": -20, "analysis": "⚠️ Too cold."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Focus on helping her."}}
            },
            "win": {"type": "WIN", "title": "MANAGED", "text": "Swelling down. No lawsuit.", "img": "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?q=80&w=800", "score": 100},
            "fail": {"type": "LOSE", "title": "BAD REP", "text": "Bad word of mouth.", "img": "https://images.unsplash.com/photo-1522029916167-9c1a97aa3c24?q=80&w=800", "score": 40},
            "lose": {"type": "LOSE", "title": "NEGLIGENCE", "text": "Lawsuit filed.", "img": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=800", "score": 0}
        }
    },
    "SC_LOGISTICS_01": {
        "title": "Logistics: Damaged Shipment",
        "desc": "Event equipment arrived broken.",
        "difficulty": "Very Hard",
        "customer": {"name": "Mr. Robert", "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=400", "traits": ["Pressure", "Furious"], "spending": "Key Account"},
        "steps": {
            "start": {
                "patience": 10, "img": "https://images.unsplash.com/photo-1586864387967-d021563e6516?q=80&w=800",
                "text": "Late and smashed! Event is tomorrow! You destroyed a $500k event!",
                "choices": {"A": "Insurance: 'File a claim.'", "B": "Crisis Mode: 'I am fixing this personally.'"},
                "consequences": {"A": {"next": "lose", "change": -30, "analysis": "❌ Bureaucracy kills."}, "B": {"next": "step_fix", "change": +40, "analysis": "✅ Operational rescue needed."}}
            },
            "step_fix": {
                "patience": 40, "img": "https://images.unsplash.com/photo-1494412651409-4963d24a38b8?q=80&w=800",
                "text": "How? No time to order new ones!",
                "choices": {"A": "Try: 'We'll try rentals.'", "B": "Guarantee: 'Chartering private truck overnight.'"},
                "consequences": {"A": {"next": "fail", "change": -10, "analysis": "⚠️ Trying isn't enough."}, "B": {"next": "win", "change": +50, "analysis": "🏆 Extreme measures required."}}
            },
            "win": {"type": "WIN", "title": "SAVED", "text": "Arrived at dawn.", "img": "https://images.unsplash.com/photo-1511578314322-379afb476865?q=80&w=800", "score": 100},
            "fail": {"type": "LOSE", "title": "RUINED", "text": "Event failed.", "img": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?q=80&w=800", "score": 30},
            "lose": {"type": "LOSE", "title": "FIRED", "text": "Account lost.", "img": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=800", "score": 0}
        }
    }
}

DB_FILE = "scenarios.json"

def load_data():
    """Load from JSON or create using INITIAL_DATA."""
    # Check if file exists
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(INITIAL_DATA, f, ensure_ascii=False, indent=4)
        return INITIAL_DATA
    
    # If file exists, load it
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # MERGE LOGIC: Add new hardcoded scenarios if they are missing in JSON
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

# ==============================================================================
# 3. CREATOR & GAME LOGIC
# ==============================================================================
def create_new_scenario_ui():
    st.header("🛠️ Create New Scenario")
    st.info("Create a simple 1-step scenario (Start -> Win/Lose).")
    
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
    st.caption("Training Master v6.0")

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
