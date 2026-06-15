import streamlit as st
import google.generativeai as genai
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# =====================================================================
# 1. PAGE CONFIGURATION & PREMIUM DARK GREEN UI (CSS)
# =====================================================================
st.set_page_config(page_title="PromptCraft Chat", layout="centered", page_icon="💬")

st.markdown("""
    <style>
    /* Dark Mode Aesthetic */
    .stApp {
        background-color: #0b141a;
    }
    
    /* App Bar Header */
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

    /* Horizontal Tabs Style */
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
    
    /* Container Info Cards */
    .chat-card {
        background-color: #121b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #202c33;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    
    /* Result Pill Styling */
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
    
    /* Execution Action Buttons styling */
    div.stButton > button:first-child, div.stDownloadButton > button:first-child {
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
    div.stButton > button:first-child:hover, div.stDownloadButton > button:first-child:hover {
        background-color: #008f72;
        border: none;
    }
    
    /* System Form Elements */
    textarea, input {
        background-color: #2a3942 !important;
        color: #e9edef !important;
        border: 1px solid #2a3942 !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. AUTOMATED BACKEND CLOUD STORAGE LOGGING
# =====================================================================
def log_data_to_sheets(category, user_prompt, improved_prompt, final_output):
    """
    Authenticates securely using service account keys and commits active data rows 
    straight to the cloud Google Sheet to prevent structural history erasure.
    """
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        
        # Connect explicitly to the target database sheet layout
        sheet = client.open("PromptCraft_Database").sheet1
        
        # Structure the persistent array log parameters
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_data = [timestamp, category, user_prompt, improved_prompt, final_output]
        
        sheet.append_row(row_data)
    except Exception as e:
        # System alert safely outputted to side terminal if verification links fail
        st.sidebar.warning(f"Database Logging Event: {str(e)}")

# =====================================================================
# 3. BRAND APP BAR NAVIGATION HEAD
# =====================================================================
st.markdown("""
    <div class="brand-header">
        <h1>Prompt<span>Craft</span> Chat</h1>
        <p style="color: #8696a0; margin: 5px 0 0 0; font-size:0.95rem;">Enter your API key below, select a workspace scenario, and generate optimized production results.</p>
    </div>
""", unsafe_allow_html=True)

# =====================================================================
# 4. SECURE FRONT-END USER API KEY FIELD
# =====================================================================
user_api_key = st.text_input(
    "🔑 Enter Your Gemini API Key:", 
    type="password", 
    placeholder="AIzaSy..."
)

if user_api_key:
    genai.configure(api_key=user_api_key)
else:
    st.info("💡 Notice: Please configure your active Gemini API key in the field above to initialize live evaluations.")

# =====================================================================
# 5. HORIZONTAL WORKSPACE SCENARIO MATRIX TABS
# =====================================================================
tab_labels = ["📝 Creative", "💻 Tech Code", "📢 Marketing", "📊 Analytics", "🎓 Academic"]
tabs = st.tabs(tab_labels)

scenarios_mapping = {
    0: {"name": "Creative Writing 📝", "desc": "Design compelling copy structures, blogs, narratives, or creative scripts."},
    1: {"name": "Coding & Technical 💻", "desc": "Optimize logic structures, generate ultra-clean scripts, and analyze algorithm runtimes."},
    2: {"name": "Marketing & Copywriting 📢", "desc": "Engine high-conversion target audience ad scripts, hooks, and email loops."},
    3: {"name": "Data & Business Analysis 📊", "desc": "Process data constraints, chart parameters, dynamic summaries, and data metrics."},
    4: {"name": "Academic & Research 🎓", "desc": "Simplify highly dense logic frameworks, structures, and foundational research variables."}
}

# Workspace Layout Generator
def render_workspace(active_index):
    chosen_scope = scenarios_mapping[active_index]
    
    st.markdown(f"""
        <div class="chat-card">
            <div style="color:#00a884; font-size:0.85rem; text-transform:uppercase; font-weight:700; letter-spacing:1px;">Active Category Workspace</div>
            <div style="font-size:1.3rem; color:#e9edef; font-weight:600; margin-top:2px;">{chosen_scope['name']}</div>
            <div style="color:#8696a0; font-size:0.9rem; margin-top:4px;">Scope: {chosen_scope['desc']}</div>
        </div>
    """, unsafe_allow_html=True)

    user_prompt = st.text_area(
        "Type your intent here...",
        key=f"text_{active_index}",
        height=120,
        placeholder="Provide descriptions or draft raw instructions here...",
        label_visibility="collapsed"
    )

    st.write("")
    
    if st.button("Evaluate & Generate Output ✔️", key=f"btn_{active_index}"):
        if not user_api_key:
            st.error("🛑 Action Halted: Missing active API Key configuration field at the top workspace container.")
        elif not user_prompt.strip():
            st.warning("Warning: Prompt description input field cannot remain empty.")
        else:
            with st.spinner("Processing architectural metrics and compilation loops..."):
                # Phase 1: Structured Evaluation Execution Call
                res = run_evaluation(chosen_scope['name'], user_prompt)
                
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.markdown("<h3 style='color:#e9edef; font-size:1.3rem; margin-top:25px; margin-bottom:15px;'>📊 Analysis Matrix</h3>", unsafe_allow_html=True)
                    
                    score = res.get("score", 6)
                    st.metric(label="Prompt Engineering Match Rate", value=f"{score * 10}% Optimal")
                    st.progress(score / 10)
                    st.write("")
                    
                    st.markdown("<p style='color:#00a884; font-weight:600; margin-bottom:6px;'>🟢 Structural Strengths (Working Components):</p>", unsafe_allow_html=True)
                    for item in res.get("strengths", []):
                        st.markdown(f'<div class="whatsapp-green-box">✓ {item}</div>', unsafe_allow_html=True)
                    
                    st.markdown("<p style='color:#ffc107; font-weight:600; margin-bottom:6px; margin-top:15px;'>🟡 Optimizations Required (Missing Parameters):</p>", unsafe_allow_html=True)
                    for item in res.get("weaknesses", []):
                        st.markdown(f'<div class="whatsapp-yellow-box">⚠ {item}</div>', unsafe_allow_html=True)
                    
                    st.markdown("<p style='color:#e9edef; font-weight:600; margin-bottom:6px; margin-top:15px;'>✨ Re-Engineered Message Structure:</p>", unsafe_allow_html=True)
                    improved_prompt_text = res.get("improved_prompt", "")
                    st.code(improved_prompt_text, language="text")
                    
                    # Phase 2: Short-Form Output Execution Box
                    st.markdown("---")
                    st.markdown("<h3 style='color:#00a884; font-size:1.3rem; margin-top:20px; margin-bottom:10px;'>🚀 Direct Code & Content Output</h3>", unsafe_allow_html=True)
                    st.write("Production material generated directly via your re-engineered prompt framework:")
                    
                    final_execution_output = generate_final_content(chosen_scope['name'], improved_prompt_text)
                    
                    # Coding syntax selection
                    code_lang = "python" if active_index == 1 else "text"
                    st.code(final_execution_output, language=code_lang)
                    
                    st.write("")
                    
                    # Download Output File Button
                    file_extension = "py" if active_index == 1 else "txt"
                    st.download_button(
                        label="📥 Download Output File",
                        data=final_execution_output,
                        file_name=f"promptcraft_output.{file_extension}",
                        mime="text/plain",
                        key=f"dl_{active_index}"
                    )
                    
                    # Automated cloud row tracking execution call
                    log_data_to_sheets(chosen_scope['name'], user_prompt, improved_prompt_text, final_execution_output)
                    
                    st.balloons()

# =====================================================================
# 6. INTENSITY CONDITIONED LLM ENGINES (SHORTEST COMPILATION LOGIC)
# =====================================================================
def run_evaluation(scope_name, raw_prompt):
    system_instruction = f"""
    You are an expert Prompt Engineer. Analyze the user's prompt for the scenario: '{scope_name}'.
    Evaluate it strictly based on Clarity, Context, and Constraints.
    Provide the response in a strict valid JSON format with the following keys:
    1. "score": An integer out of 10.
    2. "strengths": A list of things done well in English.
    3. "weaknesses": A list of things missing or that need work in English.
    4. "improved_prompt": A perfectly optimized version of their prompt.
    
    CRITICAL: Ensure your response is ONLY the raw JSON object. No conversational fillers.
    """
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(f"{system_instruction}\n\nUser's Prompt: {raw_prompt}")
        clean = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean)
    except Exception as e:
        return {"error": f"Execution delay. Connection details: {str(e)}"}

def generate_final_content(scope_name, optimized_prompt):
    """
    Evaluates the optimized engineered prompt.
    CRITICAL CONSTRAINT: If the category is related to code, it strictly enforces the AI 
    to write the absolute SHORTEST, minimal, compact, and optimized code possible. No fluff.
    """
    shortest_code_instruction = (
        "You are a master compiler. If generating code, write the absolute SHORTEST, cleanest, "
        "and most minimal production-ready lines of code possible. Avoid unnecessary verbose comments, "
        "remove duplicate logical blocks, and condense the algorithm to minimal syntax without losing core functionality."
    )
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        combined_payload = f"{shortest_code_instruction}\n\nExecute this Prompt:\n{optimized_prompt}"
        response = model.generate_content(combined_payload)
        return response.text.replace("```python", "").replace("```", "").strip()
    except Exception as e:
        return f"Output Generation Stopped. Logs: {str(e)}"

# Thread isolation dispatcher
for idx, tab_object in enumerate(tabs):
    with tab_object:
        render_workspace(idx)
