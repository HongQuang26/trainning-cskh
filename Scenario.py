import streamlit as st
import time

# ==============================================================================
# 1. CONFIGURATION & UI (UI/UX)
# ==============================================================================
st.set_page_config(
    page_title="Training Master Pro",
    page_icon="💎",
    layout="wide"
)

# Custom CSS for a "Premium" look
st.markdown("""
<style>
    /* Button Customization */
    .stButton button {
        border-radius: 12px;
        height: auto;
        min-height: 60px;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 1px solid #e0e0e0;
        white-space: pre-wrap; /* Wrap text */
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        border-color: #2E86C1;
        color: #2E86C1;
        background-color: #f8f9fa;
    }
    
    /* Chat Container */
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
    
    /* Left Sidebar Profile Card */
    .profile-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #dee2e6;
    }
    
    /* Analysis Boxes */
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
# 2. SCENARIO DATA WAREHOUSE (ENGLISH)
# ==============================================================================

ALL_SCENARIOS = {
    "SC_FNB_01": {
        "title": "F&B: Foreign Object Incident",
        "desc": "A customer discovers a hair in their soup at a 5-star restaurant.",
        "difficulty": "Hard",
        "customer": {
            "name": "Ms. Jade (Food Reviewer)",
            "avatar": "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?q=80&w=400",
            "traits": ["Picky", "Famous Reviewer", "Perfectionist"],
            "spending": "New Customer (High Risk)"
        },
        "steps": {
            "start": {
                "patience": 30, 
                "img": "https://images.unsplash.com/photo-1533777857889-4be7c70b33f7?q=80&w=800",
                "text": "(Pointing at the soup bowl furiously) Manager! Come here. What kind of 5-star restaurant serves soup with a long hair in it? Are you trying to feed me garbage? This is disgusting!",
                "choices": {
                    "A": "Denial: 'Ma'am, our kitchen staff all have black hair and wear nets. This hair is blonde. Are you sure it isn't yours?'",
                    "B": "Acceptance & Action: 'I am terribly sorry about this awful experience, Ms. Jade! I see it. I will remove this dish immediately.'"
                },
                "consequences": {
                    "A": {"next": "game_over_bad_fnb", "change": -40, "analysis": "❌ FATAL ERROR: Never blame the customer regarding hygiene issues. Arguing at this point is suicide."},
                    "B": {"next": "step_compensate", "change": +20, "analysis": "✅ CORRECT: Acknowledge the problem immediately and take action (remove the dish) to reduce the customer's disgust."}
                }
            },
            "step_compensate": {
                "patience": 50,
                "img": "https://images.unsplash.com/photo-1552581234-26160f608093?q=80&w=800",
                "text": "(Still annoyed) I've lost my appetite. Our anniversary dinner is completely ruined. How are you going to fix this?",
                "choices": {
                    "A": "Standard Solution: 'I will replace it with a new soup and give you a 10% discount on the total bill to apologize.'",
                    "B": "WOW Solution: 'I completely understand your frustration. I would like to COMP the entire meal tonight (Free). Also, the chef would like to send a special dessert as our sincerest apology.'",
                },
                "consequences": {
                    "A": {"next": "game_over_fail_fnb", "change": -10, "analysis": "⚠️ AVERAGE: For a serious hygiene issue in a 5-star place, 10% is not enough. The customer still feels cheated."},
                    "B": {"next": "game_over_good_fnb", "change": +50, "analysis": "🏆 EXCELLENT: 'Over-compensating' is the only way to save your reputation in this disaster."}
                }
            },
            "game_over_good_fnb": {
                "type": "WIN",
                "title": "⭐ TRUST RESTORED",
                "img": "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?q=80&w=800",
                "text": "Ms. Jade was surprised by the generous handling. She wrote a review praising the professional crisis management instead of exposing the issue.",
                "score": 100
            },
            "game_over_fail_fnb": {
                "type": "LOSE",
                "title": "😐 CUSTOMER LOST",
                "img": "https://images.unsplash.com/photo-1522029916167-9c1a97aa3c24?q=80&w=800",
                "text": "She accepted the 10% discount but ate quickly and left. She rated 2 stars on Google Maps regarding hygiene.",
                "score": 40
            },
            "game_over_bad_fnb": {
                "type": "LOSE",
                "title": "☠️ PR DISASTER",
                "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800",
                "text": "Ms. Jade filmed the argument and posted it on TikTok: '5-star restaurant accuses customer of planting hair'. The video went viral.",
                "score": 0
            }
        }
    },

    "SC_HOTEL_01": {
        "title": "Hotel: Overbooked",
        "desc": "Honeymoon couple arrives, but the receptionist says the Ocean View room is unavailable.",
        "difficulty": "Very Hard",
        "customer": {
            "name": "Mr. Mike & Ms. Sara",
            "avatar": "https://images.unsplash.com/photo-1542909168-82c3e7fdca5c?q=80&w=400",
            "traits": ["Tired from flight", "High Expectations", "Emotional"],
            "spending": "Honeymoon Package ($500/night)"
        },
        "steps": {
            "start": {
                "patience": 20,
                "img": "https://images.unsplash.com/photo-1542596594-6eb9880fb7a6?q=80&w=800",
                "text": "(Mr. Mike shouting) What do you mean 'no rooms'? I booked and paid a month ago! This is our honeymoon, I will NOT accept a Garden View room!",
                "choices": {
                    "A": "Blame System: 'I am very sorry. Our system overbooked the rooms, so we couldn't hold the Ocean View. We hope for your understanding.'",
                    "B": "Empathy & Ownership: 'I sincerely apologize, Mr. Mike and Ms. Sara! This is entirely our fault for failing to secure the room for such an important trip.'"
                },
                "consequences": {
                    "A": {"next": "game_over_bad_hotel", "change": -30, "analysis": "❌ BAD: Customers don't care about 'systems'. Asking for 'understanding' sounds like a generic excuse."},
                    "B": {"next": "step_upgrade", "change": +20, "analysis": "✅ GOOD: Direct ownership, using names, and acknowledging the importance of the trip."}
                }
            },
            "step_upgrade": {
                "patience": 40,
                "img": "https://images.unsplash.com/photo-1618773928121-c32242e63f39?q=80&w=800",
                "text": "(Ms. Sara tearing up) But we dreamed about that ocean view... A garden room ruins the honeymoon vibe.",
                "choices": {
                    "A": "Upgrade Solution: 'The Ocean View is gone, but to make it up to you, I would like to UPGRADE you to the PRESIDENTIAL SUITE (Double price) for free for the first 2 nights.'",
                    "B": "Refund Solution: 'If you stay in the Garden View, we will refund the difference and give you an extra 20% discount on the room rate.'"
                },
                "consequences": {
                    "A": {"next": "game_over_good_hotel", "change": +60, "analysis": "🏆 EXCELLENT: When you can't give what they want, give something much better. The Presidential Suite is a 'Wow' factor."},
                    "B": {"next": "game_over_fail_hotel", "change": -20, "analysis": "⚠️ POOR: For a honeymoon, EXPERIENCE matters more than MONEY. A refund doesn't fix the ruined mood."}
                }
            },
            "game_over_good_hotel": {
                "type": "WIN",
                "title": "🥂 DREAM HONEYMOON",
                "img": "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?q=80&w=800",
                "text": "They were overwhelmed by the luxurious Suite. They felt treated like VIPs, and the incident became a happy memory.",
                "score": 100
            },
            "game_over_fail_hotel": {
                "type": "LOSE",
                "title": "😢 SAD TRIP",
                "img": "https://images.unsplash.com/photo-1583323731095-d7c9bd2690f6?q=80&w=800",
                "text": "They reluctantly took the room and refund, but the mood was ruined. They will not return.",
                "score": 40
            },
            "game_over_bad_hotel": {
                "type": "LOSE",
                "title": "🤬 LOBBY RAGE",
                "img": "https://images.unsplash.com/photo-1574790502501-701452c15414?q=80&w=800",
                "text": "Mr. Mike demanded to see the Manager and asked for a 100% refund immediately to switch hotels. The lobby was in chaos.",
                "score": 0
            }
        }
    },

    "SC_ECOMM_01": {
        "title": "Online: Lost Package",
        "desc": "App says 'Delivered' but the customer hasn't received anything.",
        "difficulty": "Medium",
        "customer": {
            "name": "Tom (Student)",
            "avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?q=80&w=400",
            "traits": ["Worried about money", "Suspicious", "Urgent"],
            "spending": "Low"
        },
        "steps": {
            "start": {
                "patience": 40,
                "img": "https://images.unsplash.com/photo-1566576912321-d58ba2188273?q=80&w=800",
                "text": "Hello shop? The app says my shoes were delivered at 10 AM, but I have nothing! I asked the receptionist, and they don't have it either. Did the driver steal it? I need them for my exam tomorrow!",
                "choices": {
                    "A": "Deflect: 'Hi, the system says delivered. Please check with your neighbors or family members.'",
                    "B": "Reassure: 'Hi Tom, I understand. Please don't worry, we will take full responsibility and work with the carrier to locate your package right now.'"
                },
                "consequences": {
                    "A": {"next": "step_panic", "change": -20, "analysis": "⚠️ POOR: Pushing responsibility back to a panicked customer causes frustration. He already said he checked with the receptionist."},
                    "B": {"next": "step_investigate", "change": +20, "analysis": "✅ GOOD: 'We take full responsibility' is a sedative phrase. It confirms you are on their side."}
                }
            },
            "step_panic": {
                "patience": 20,
                "img": "https://images.unsplash.com/photo-1633934542430-0905ccb5f050?q=80&w=800",
                "text": "I live alone! I asked everyone! This is clearly a scam! Refund my money!",
                "choices": {
                    "A": "Firm: 'Calm down, we are a reputable business. Just wait for us to check.'",
                    "B": "Strong Promise: 'I understand your anxiety. I promise if we can't find it by 6 PM, we will EXPRESS SHIP a new pair so you have them for your exam.'",
                },
                "consequences": {
                    "A": {"next": "game_over_bad_ecomm", "change": -20, "analysis": "❌ BAD: Telling a panicked customer to 'Calm down' is useless and antagonistic."},
                    "B": {"next": "game_over_good_ecomm_rescue", "change": +50, "analysis": "✅ EXCELLENT: Offering a 'Worst-case scenario guarantee'. The customer stops worrying because they will get shoes either way."}
                }
            },
             "step_investigate": {
                "patience": 60,
                "img": "https://images.unsplash.com/photo-1528736047006-d320da8a2437?q=80&w=800",
                "text": "(15 mins later) Hi Tom, the driver said he couldn't reach you, so he left it at the back gate security, not the front desk. He apologizes for not texting you. Could you check there?",
                "choices": {
                    "A": "Simple Close: 'So it was the driver's fault. Please go pick it up. Thanks.'",
                    "B": "Thoughtful Close: 'So sorry for the worry, Tom. Please check the back gate. Here is a Free Shipping voucher for next time as an apology from us.'"
                },
                "consequences": {
                    "A": {"next": "game_over_normal_ecomm", "change": +10, "analysis": "🙂 AVERAGE: Problem solved, but customer experience is mediocre (still annoyed about running around)."},
                    "B": {"next": "game_over_good_ecomm", "change": +30, "analysis": "✅ GOOD: Taking the blame for the courier and offering a small gift (voucher) smooths things over."}
                }
            },
            "game_over_good_ecomm": {
                "type": "WIN",
                "title": "👍 PACKAGE FOUND",
                "img": "https://images.unsplash.com/photo-1556740758-90de374c12ad?q=80&w=800",
                "text": "Tom got the shoes. A bit annoyed, but he appreciated the enthusiastic support.",
                "score": 90
            },
            "game_over_good_ecomm_rescue": {
                "type": "WIN",
                "title": "🦸‍♂️ SUCCESSFUL RESCUE",
                "img": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=800",
                "text": "Package was actually lost. Shop kept the promise and express shipped a new pair. Tom became a loyal customer.",
                "score": 100
            },
             "game_over_normal_ecomm": {
                "type": "WIN",
                "title": "📦 RECEIVED",
                "img": "https://images.unsplash.com/photo-1598942610451-9573a059795c?q=80&w=800",
                "text": "Tom went to get the package, slightly irritated. Won't rate 5 stars but won't complain further.",
                "score": 70
            },
            "game_over_bad_ecomm": {
                "type": "LOSE",
                "title": "🤬 TRUST LOST",
                "img": "https://images.unsplash.com/photo-1586866016892-117e620d5520?q=80&w=800",
                "text": "Tom thinks the shop is covering for a scam. He rated 1 star and reported the shop.",
                "score": 10
            }
        }
    },

    "SC_RETAIL_01": {
        "title": "Retail: Broken Vase",
        "desc": "VIP customer received a shattered vase right before gifting time.",
        "difficulty": "Hard",
        "customer": {
            "name": "Ms. Lan (Gold Member)",
            "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=400",
            "traits": ["Hot-tempered", "Powerful", "In a rush"],
            "spending": "$2000/year"
        },
        "steps": {
            "start": {
                "patience": 40,
                "img": "https://images.unsplash.com/photo-1596496050844-461dc5b7263f?q=80&w=800",
                "text": "Hello! How do you do business? The $200 vase I bought for my boss is shattered! Are you scamming me?",
                "choices": {
                    "A": "Empathy: 'I hear you, ma'am. I am very sorry. Please stay calm, I will handle this immediately.'",
                    "B": "Procedure: 'Please give me your Order ID so I can check if it is our product.'",
                },
                "consequences": {
                    "A": {"next": "step_solution", "change": +20, "analysis": "✅ GOOD: Prioritize emotions (Empathy) first, logic second."},
                    "B": {"next": "step_rage", "change": -20, "analysis": "⚠️ POOR: Asking for an ID when the customer is furious adds fuel to the fire."}
                }
            },
            "step_solution": {
                "patience": 60,
                "img": "https://images.unsplash.com/photo-1556740738-b6a63e27c4df?q=80&w=800",
                "text": "(Softer voice) I need it by 6 PM tonight. What can I gift now? Can you replace it immediately?",
                "choices": {
                    "A": "Flexible: 'Given the urgency, I will ask my manager to EXPRESS SHIP a new one to you within 1 hour.'",
                    "B": "Rigid: 'Policy states you must return the broken item first, then we send a new one (takes 3 days).'"
                },
                "consequences": {
                    "A": {"next": "game_over_good_retail", "change": +30, "analysis": "✅ EXCELLENT: For VIPs and emergencies, you must bend the rules."},
                    "B": {"next": "game_over_fail_retail", "change": -50, "analysis": "❌ FAIL: Correct procedure but wrong timing. You lost the customer."}
                }
            },
            "step_rage": {
                "patience": 20,
                "img": "https://images.unsplash.com/photo-1555861496-0666c8981751?q=80&w=800",
                "text": "Order ID?! The vase is destroyed! I don't have time to dig up messages. Fix it now!",
                "choices": {
                    "A": "Soft: 'I apologize. I will look it up by your phone number. Please give me 30 seconds.'",
                    "B": "Preachy: 'Without the ID, the system won't let me access the data.'"
                },
                "consequences": {
                    "A": {"next": "step_solution", "change": +10, "analysis": "✅ FAIR: Fixing the mistake and finding a workaround."},
                    "B": {"next": "game_over_bad_retail", "change": -20, "analysis": "❌ DISASTER: Arguing with the customer is forbidden."}
                }
            },
            "game_over_good_retail": {
                "type": "WIN",
                "title": "🏆 EXCELLENT HANDLING",
                "img": "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?q=80&w=800",
                "text": "Customer received the new vase at 5 PM. She was grateful and recommended your shop to her company.",
                "score": 100
            },
            "game_over_fail_retail": {
                "type": "LOSE",
                "title": "😐 VIP LOST",
                "img": "https://images.unsplash.com/photo-1444312645910-ffa973656eba?q=80&w=800",
                "text": "Customer hung up and bought elsewhere. You followed the rules, but the company lost a VIP.",
                "score": 40
            },
            "game_over_bad_retail": {
                "type": "LOSE",
                "title": "☠️ CRISIS",
                "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800",
                "text": "Her angry post got 10k shares. The boss called you for a meeting.",
                "score": 0
            }
        }
    },

    "SC_TECH_01": {
        "title": "IT: Internet Outage",
        "desc": "Business internet went down during a meeting with foreign partners.",
        "difficulty": "Medium",
        "customer": {
            "name": "Mr. Ken (IT Director)",
            "avatar": "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=400",
            "traits": ["Logical", "Urgent", "Expert"],
            "spending": "Enterprise Plan"
        },
        "steps": {
            "start": {
                "patience": 30,
                "img": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?q=80&w=800",
                "text": "Is this how you do business? I'm in a meeting and the net drops! I restarted the modem 3 times, still nothing!",
                "choices": {
                    "A": "Technical Q: 'Sir, what color is the PON light on your modem?'",
                    "B": "Generic Apology: 'I am sorry sir, maybe a shark bit the cable...'"
                },
                "consequences": {
                    "A": {"next": "step_check", "change": +10, "analysis": "✅ GOOD: With IT customers, getting straight to technical troubleshooting is best."},
                    "B": {"next": "game_over_bad_tech", "change": -30, "analysis": "❌ BAD: Don't blame external factors without checking. IT people hate scripted excuses."}
                }
            },
            "step_check": {
                "patience": 40,
                "img": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=800",
                "text": "It's flashing red. I need internet in 5 minutes. Can you send a technician NOW?",
                "choices": {
                    "A": "Dispatch: 'Signal is lost. I'm sending a tech, but the fastest is 30 mins.'",
                    "B": "Temporary Fix: 'Tech takes 30 mins. Can you use 4G backup? I will add a MAX SPEED data package to your account immediately to save the meeting.'"
                },
                "consequences": {
                    "A": {"next": "game_over_fail_tech", "change": -10, "analysis": "⚠️ AVERAGE: Honest, but doesn't solve the '5 minute' deadline."},
                    "B": {"next": "game_over_good_tech", "change": +40, "analysis": "✅ EXCELLENT: Providing a Workaround to save the meeting is the top priority."}
                }
            },
            "game_over_good_tech": {
                "type": "WIN",
                "title": "💡 SMART SOLUTION",
                "img": "https://images.unsplash.com/photo-1552581234-26160f608093?q=80&w=800",
                "text": "Mr. Ken used 4G to finish the meeting. The tech arrived later to fix the line. He appreciated the flexibility.",
                "score": 90
            },
            "game_over_fail_tech": {
                "type": "LOSE",
                "title": "🕒 MEETING MISSED",
                "img": "https://images.unsplash.com/photo-1506784983877-45594efa4cbe?q=80&w=800",
                "text": "30 mins later the meeting was already over. The customer was very disappointed.",
                "score": 50
            },
            "game_over_bad_tech": {
                "type": "LOSE",
                "title": "🤬 CONTRACT TERMINATED",
                "img": "https://images.unsplash.com/photo-1593529467220-9d721ceb9a78?q=80&w=800",
                "text": "Mr. Ken demanded to cancel the contract immediately due to unprofessionalism.",
                "score": 0
            }
        }
    }
}

# ==============================================================================
# 3. GAME ENGINE LOGIC
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
    
    # Update State
    st.session_state.current_step = consequence['next']
    st.session_state.patience_meter += consequence['change']
    
    # Limit meter 0-100
    st.session_state.patience_meter = max(0, min(100, st.session_state.patience_meter))
    
    # Save History
    st.session_state.history.append({
        "step": step_data['text'],
        "choice": step_data['choices'][choice_key],
        "analysis": consequence['analysis'],
        "change": consequence['change']
    })

# ==============================================================================
# 4. MAIN INTERFACE
# ==============================================================================

# --- DASHBOARD ---
if st.session_state.current_scenario is None:
    st.title("🎓 TRAINING MASTER PRO")
    st.caption("Real-world Situation Training System (Version 3.0)")
    st.divider()
    
    # Grid Display
    cols = st.columns(2)
    count = 0
    for key, data in ALL_SCENARIOS.items():
        with cols[count % 2]:
            with st.container(border=True):
                st.subheader(f"{data['title']}")
                st.write(f"📝 {data['desc']}")
                
                # Difficulty Badge
                if data['difficulty'] == 'Very Hard':
                    st.markdown(":fire: Difficulty: **Very Hard**")
                elif data['difficulty'] == 'Hard':
                    st.markdown(":warning: Difficulty: **Hard**")
                else:
                    st.markdown(":star: Difficulty: **Medium**")
                    
                if st.button(f"🚀 Start Now", key=f"btn_{key}", use_container_width=True):
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
        st.button("❌ Exit Scenario", on_click=reset_game, use_container_width=True)
        st.divider()
        
        # Profile
        cust = s_data['customer']
        st.markdown(f"<div style='text-align:center'><img src='{cust['avatar']}' style='width:100px;border-radius:50%;border:3px solid #2E86C1'></div>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center'>{cust['name']}</h3>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="profile-card">
            <p><b>Traits:</b> {', '.join(cust['traits'])}</p>
            <p><b>Spending:</b> {cust['spending']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Patience Meter
        patience = st.session_state.patience_meter
        st.markdown(f"### 🌡️ Patience Level: {patience}/100")
        
        # Color Logic
        color_hex = "#28a745" # Green
        if patience < 30: color_hex = "#dc3545" # Red
        elif patience < 70: color_hex = "#ffc107" # Orange
            
        st.markdown(f"""
        <div style="width:100%;background-color:#e9ecef;border-radius:10px;height:20px;">
            <div style="width:{patience}%;background-color:{color_hex};height:20px;border-radius:10px;transition:width 0.5s;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        if patience <= 20 and patience > 0:
             st.error("WARNING: CUSTOMER IS ABOUT TO LEAVE!")

    # MAIN AREA
    if "type" in step_data: # End Screen
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
            
            st.metric("Your Score", f"{step_data['score']}/100")
            
            if st.button("🔄 Try Again", use_container_width=True):
                start_scenario(s_key)
                st.rerun()
        
        st.divider()
        st.subheader("🕵️ EXPERT ANALYSIS")
        for idx, item in enumerate(st.session_state.history):
            with st.expander(f"Step {idx+1}: You chose '{item['choice'][:30]}...'", expanded=True):
                st.write(f"💬 **Situation:** {item['step']}")
                st.write(f"👉 **Your Choice:** {item['choice']}")
                
                # Analysis Display
                style_class = "analysis-box-good" if item['change'] > 0 else "analysis-box-bad"
                icon = "✅" if item['change'] > 0 else "❌"
                sign = "+" if item['change'] > 0 else ""
                
                st.markdown(f"""
                <div class="{style_class}">
                    <b>{icon} Analysis:</b> {item['analysis']} <br>
                    (Patience: {sign}{item['change']})
                </div>
                """, unsafe_allow_html=True)

    else: # Playing Screen
        st.subheader(f"📍 {s_data['title']}")
        
        col_img, col_text = st.columns([1.5, 2], gap="large")
        
        with col_img:
            st.image(step_data['img'], use_container_width=True, caption="Surveillance Camera")
        
        with col_text:
            st.markdown(f"""
            <div class="chat-container">
                <div class="customer-name">🗣️ {cust['name']} says:</div>
                <div class="dialogue">"{step_data['text']}"</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("#### 👉 How do you respond?")
            
            for key, val in step_data['choices'].items():
                if st.button(f"{key}. {val}", use_container_width=True):
                    make_choice(key, step_data)
                    st.rerun()

# Footer
st.markdown("---")
st.caption("Training Master Pro v3.0 | Author HQuang")
