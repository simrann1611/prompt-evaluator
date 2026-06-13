import streamlit as st
import google.generativeai as genai
import json

# =====================================================================
# 1. API CONFIGURATION
# =====================================================================
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE" 

if GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=GEMINI_API_KEY)

# =====================================================================
# 2. WHATSAPP-INSPIRED GREEN & AMBER UI (CSS INJECTION)
# =====================================================================
st.set_page_config(page_title="PromptCraft Chat", layout="centered", page_icon="💬")

st.markdown("""
    <style>
    /* WhatsApp Dark Mode Aesthetic Background */
    .stApp {
        background-color: #0b141a;
    }
    
    /* Header Container */
    .brand-header {
        background-color: #121b22;
        padding: 20px;
        border-radius: 0px 0px 16px 16px;
        text-align: center;
        border-bottom: 2px solid #00a884;
        margin-bottom: 25px;
    }
    
    .brand-header h1 {
        color: #e9edef !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        margin: 0;
    }
    
    .brand-header span {
        color: #00a884;
    }

    /* WhatsApp Style Navigation Tabs customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #121b22;
        padding: 8px;
        border-radius: 12px;
        border: 1px solid #202c33;
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px;
        white-space: pre;
        background-color: #202c33;
        border-radius: 8px;
        color: #8696a0 !important;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background-color: #00a884 !important;
        color: #ffffff !important;
    }
    
    /* Chat Content Card */
    .chat-card {
        background-color: #121b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #202c33;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    
    /* Dynamic Feedback Boxes (Green & Yellow) */
    .whatsapp-green-box {
        background-color: rgba(0, 168, 132, 0.15);
        border: 1px solid #00a884;
        padding: 14px;
        border-radius: 10px;
        color: #e9edef;
        margin-bottom: 12px;
    }
    
    .whatsapp-yellow-box {
        background-color: rgba(255, 193, 7, 0.12);
        border: 1px solid #ffc107;
        padding: 14px;
        border-radius: 10px;
        color: #e9edef;
        margin-bottom: 12px;
    }
    
    /* Action Floating Button */
    div.stButton > button:first-child {
        background-color: #00a884;
        color: #ffffff;
        border: none;
        padding: 14px;
        font-size: 1.05rem;
        font-weight: 600;
        border-radius: 10px;
        width: 100%;
        box-shadow: 0 3px 10px rgba(0,168,132,0.3);
        transition: background 0.2s;
    }
    div.stButton > button:first-child:hover {
        background-color: #008f72;
        border: none;
    }
    
    /* Text Input Area */
    textarea {
        background-color: #2a3942 !important;
        color: #e9edef !important;
        border: 1px solid #2a3942 !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 3. WHATSAPP APP BAR HEAD
# =====================================================================
st.markdown("""
    <div class="brand-header">
        <h1>Prompt<span>Craft</span> Chat</h1>
        <p style="color: #8696a0; margin: 5px 0 0 0; font-size:0.95rem;">Tap on a scenario tab below to analyze your string syntax</p>
    </div>
""", unsafe_allow_html=True)

# Missing API Banner (Minimalistic Amber Yellow alert)
if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    st.markdown("""
        <div style='background-color: rgba(255,193,7,0.15); border: 1px solid #ffc107; padding: 12px; border-radius: 10px; color: #ffe082; font-size:0.9rem; text-align:center; margin-bottom:20px;'>
            ⚠️ <b>System Alert:</b> Please connect your Gemini API key string inside the script code.
        </div>
    """, unsafe_allow_html=True)

# =====================================================================
# 4. HORIZONTAL SCENARIO TABS (WHATSAPP CALLS/CHATS LOOK)
# =====================================================================
# 5 tabs mapped out neatly across the center deck
tab_labels = ["📝 Creative", "💻 Tech Code", "📢 Marketing", "📊 Analytics", "🎓 Academic"]
t1, t2, t3, t4, t5 = st.tabs(tab_labels)

# Mapping tabs to structured information definitions
scenarios_mapping = {
    0: {"name": "Creative Writing 📝", "desc": "Stories, scripts, hooks, or aesthetic content arrays."},
    1: {"name": "Coding & Technical 💻", "desc": "Compilers, debugging sequences, and script formatting rules."},
    2: {"name": "Marketing & Copywriting 📢", "desc": "Conversion copywriting, active campaigns, and tone setting."},
    3: {"name": "Data & Business Analysis 📊", "desc": "Metric parameters, summary trends, and computational requests."},
    4: {"name": "Academic & Research 🎓", "desc": "Literature breakdowns, conceptual simplification models."}
}

# Variable placeholder for checking which tab scope is selected
active_index = 0
current_tab = t1

# Streamlit updates active states implicitly depending on content inside blocks
with t1: active_index = 0
with t2: active_index = 1
with t3: active_index = 2
with t4: active_index = 3
with t5: active_index = 4

chosen_scope = scenarios_mapping[active_index]

# =====================================================================
# 5. CHAT TEXTBOX COMPONENT WORKSPACE
# =====================================================================
st.markdown(f"""
    <div class="chat-card">
        <div style="color:#00a884; font-size:0.85rem; text-transform:uppercase; font-weight:700; letter-spacing:1px;">Active Category</div>
        <div style="font-size:1.3rem; color:#e9edef; font-weight:600; margin-top:2px;">{chosen_scope['name']}</div>
        <div style="color:#8696a0; font-size:0.9rem; margin-top:4px;">{chosen_scope['desc']}</div>
    </div>
""", unsafe_allow_html=True)

user_prompt = st.text_area(
    "Type message...",
    height=120,
    placeholder="Write your raw instructions here..."
)

st.write("")

# =====================================================================
# 6. LLM DISPATCH ENGINE
# =====================================================================
def run_evaluation(scope_name, raw_prompt):
    system_instruction = f"""
    You are an expert Prompt Engineer. Analyze the user's prompt for the scenario: '{scope_name}'.
    Evaluate it based on Clarity, Context, and Constraints.
    Provide the response in a strict valid JSON format with the following keys:
    1. "score": An integer out of 10.
    2. "strengths": A list of things done well.
    3. "weaknesses": A list of things missing or that need work.
    4. "improved_prompt": A perfectly optimized version of their prompt.
    
    Ensure your response is ONLY the raw JSON object. No intro/outro text.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"{system_instruction}\n\nUser's Prompt: {raw_prompt}")
        clean = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean)
    except Exception as e:
        return {"error": f"Execution delay timeout. Connection logs: {str(e)}"}

# Trigger Processing Matrix
if st.button("Evaluate Structure ✔️"):
    if not user_prompt.strip():
        st.warning("Please draft a text payload sequence first.")
    elif GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        st.error("Authentication Missing: Insert an active API string.")
    else:
        with st.spinner("Analyzing message architecture..."):
            res = run_evaluation(chosen_scope['name'], user_prompt)
            
            if "error" in res:
                st.error(res["error"])
            else:
                st.markdown("<h3 style='color:#e9edef; font-size:1.3rem; margin-top:25px; margin-bottom:15px;'>📊 Analysis Matrix</h3>", unsafe_allow_html=True)
                
                # Dynamic Grid
                score = res.get("score", 6)
                st.metric(label="Engineering Match Rate", value=f"{score * 10}% Optimal")
                st.progress(score / 10)
                st.write("")
                
                # Green Box for Strengths
                st.markdown("<p style='color:#00a884; font-weight:600; margin-bottom:6px;'>🟢 Structure Strengths (What's Working):</p>", unsafe_allow_html=True)
                for item in res.get("strengths", []):
                    st.markdown(f'<div class="whatsapp-green-box">✓ {item}</div>', unsafe_allow_html=True)
                
                # Yellow Box for Weaknesses
                st.markdown("<p style='color:#ffc107; font-weight:600; margin-bottom:6px; margin-top:15px;'>🟡 Optimizations Needed (What's Missing):</p>", unsafe_allow_html=True)
                for item in res.get("weaknesses", []):
                    st.markdown(f'<div class="whatsapp-yellow-box">⚠ {item}</div>', unsafe_allow_html=True)
                
                # Re-engineered output block
                st.markdown("<p style='color:#e9edef; font-weight:600; margin-bottom:6px; margin-top:15px;'>✨ Re-Engineered Message Payload:</p>", unsafe_allow_html=True)
                st.code(res.get("improved_prompt", ""), language="text")
