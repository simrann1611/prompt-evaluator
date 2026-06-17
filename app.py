import streamlit as st
import google.generativeai as genai
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# =====================================================================
# PAGE CONFIGURATION & PREMIUM DARK GREEN UI (CSS)
# =====================================================================
st.set_page_config(page_title="PromptCraft Chat", layout="centered", page_icon="💬")

st.markdown("""
    <style>
    .stApp { background-color: #0b141a; }
    .brand-header { background-color: #121b22; padding: 20px; border-radius: 0px 0px 16px 16px; text-align: center; border-bottom: 2px solid #00a884; margin-bottom: 25px; }
    .brand-header h1 { color: #e9edef !important; font-size: 2.2rem !important; font-weight: 700 !important; margin: 0; }
    .brand-header span { color: #00a884; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #121b22; padding: 8px; border-radius: 12px; border: 1px solid #202c33; }
    .stTabs [data-baseweb="tab"] { height: 45px; background-color: #202c33; border-radius: 8px; color: #8696a0 !important; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #00a884 !important; color: #ffffff !important; }
    .chat-card { background-color: #121b22; padding: 20px; border-radius: 12px; border: 1px solid #202c33; margin-top: 15px; margin-bottom: 15px; }
    .login-container { background-color: #121b22; padding: 30px; border-radius: 16px; border: 1px solid #202c33; box-shadow: 0 4px 15px rgba(0,0,0,0.5); margin-top: 20px; }
    .whatsapp-green-box { background-color: rgba(0, 168, 132, 0.15); border: 1px solid #00a884; padding: 14px; border-radius: 10px; color: #e9edef; margin-bottom: 12px; }
    .whatsapp-yellow-box { background-color: rgba(255, 193, 7, 0.12); border: 1px solid #ffc107; padding: 14px; border-radius: 10px; color: #e9edef; margin-bottom: 12px; }
    div.stButton > button:first-child, div.stDownloadButton > button:first-child { background-color: #00a884; color: #ffffff; border: none; padding: 14px; font-weight: 600; border-radius: 10px; width: 100%; box-shadow: 0 3px 10px rgba(0,168,132,0.3); }
    textarea, input { background-color: #2a3942 !important; color: #e9edef !important; border: 1px solid #2a3942 !important; border-radius: 10px !important; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# FIXED STREAMLIT SECRETS CONFIGURATION
# =====================================================================
def get_sheets_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Yeh line ab sidhe Streamlit dashboard ke settings se secure credentials uthaegi
    creds_dict = json.loads(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_key_dict(creds_dict, scope)
    return gspread.authorize(creds)

def register_user(new_user, new_pass):
    try:
        client = get_sheets_client()
        db_sheet = client.open("PromptCraft_Database")
        try:
            user_sheet = db_sheet.worksheet("Users")
        except gspread.exceptions.WorksheetNotFound:
            user_sheet = db_sheet.add_worksheet(title="Users", rows="100", cols="2")
            user_sheet.append_row(["Username", "Password"])
        all_users = user_sheet.col_values(1)
        if new_user in all_users: return "exists"
        user_sheet.append_row([new_user, new_pass])
        return "success"
    except Exception as e:
        return str(e)

def check_user_login(user, password):
    try:
        client = get_sheets_client()
        db_sheet = client.open("PromptCraft_Database")
        try:
            user_sheet = db_sheet.worksheet("Users")
        except gspread.exceptions.WorksheetNotFound:
            return False
        records = user_sheet.get_all_records()
        for record in records:
            if str(record.get("Username")) == user and str(record.get("Password")) == password:
                return True
        return False
    except Exception:
        return False

# =====================================================================
# AUTHENTICATION STATE CONTROL
# =====================================================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown("""
        <div class="brand-header">
            <h1>Prompt<span>Craft</span> Chat</h1>
            <p style="color: #8696a0; margin: 5px 0 0 0; font-size:0.95rem;">Secure Portal Gate. Please create an account or log in to continue.</p>
        </div>
    """, unsafe_allow_html=True)
    
    auth_mode = st.tabs(["📝 Sign Up", "🔐 Log In"])
    
    with auth_mode[0]:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.subheader("Create a New Account (First Time Users)")
        reg_username = st.text_input("Choose Username", key="reg_user", placeholder="e.g., user123")
        reg_password = st.text_input("Choose Password", type="password", key="reg_pass", placeholder="Create a secure password")
        if st.button("Register & Save Profile ✔️", key="reg_btn"):
            if not reg_username.strip() or not reg_password.strip():
                st.warning("Fields cannot remain empty.")
            else:
                status = register_user(reg_username.strip(), reg_password.strip())
                if status == "success": st.success("Account created successfully! Now log in.")
                elif status == "exists": st.error("Username already taken.")
                else: st.error(f"Registration Error: {status}")
        st.markdown('</div>', unsafe_allow_html=True)

    with auth_mode[1]:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.subheader("Log In to Existing Workspace")
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Secure Login →", key="login_btn"):
            if check_user_login(login_username, login_password):
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Invalid credentials.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

def log_data_to_sheets(category, user_prompt, improved_prompt, final_output):
    try:
        client = get_sheets_client()
        sheet = client.open("PromptCraft_Database").sheet1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, category, user_prompt, improved_prompt, final_output])
    except Exception as e:
        st.sidebar.warning(f"Database Logging Event: {str(e)}")

# =====================================================================
# MAIN WORKSPACE
# =====================================================================
st.markdown("""
    <div class="brand-header">
        <h1>Prompt<span>Craft</span> Chat</h1>
        <p style="color: #8696a0; margin: 5px 0 0 0; font-size:0.95rem;">Enter your API key below, select a workspace scenario, and generate optimized production results.</p>
    </div>
""", unsafe_allow_html=True)

if st.sidebar.button("🔒 Secure Sign Out"):
    st.session_state["logged_in"] = False
    st.rerun()

user_api_key = st.text_input("🔑 Enter Your Gemini API Key:", type="password")
if user_api_key: genai.configure(api_key=user_api_key)

tab_labels = ["📝 Creative", "💻 Tech Code", "📢 Marketing", "📊 Analytics", "🎓 Academic"]
tabs = st.tabs(tab_labels)

scenarios_mapping = {
    0: {"name": "Creative Writing 📝", "desc": "Design compelling copy structures."},
    1: {"name": "Coding & Technical 💻", "desc": "Optimize logic structures."},
    2: {"name": "Marketing & Copywriting 📢", "desc": "Engine high-conversion scripts."},
    3: {"name": "Data & Business Analysis 📊", "desc": "Process data constraints."},
    4: {"name": "Academic & Research 🎓", "desc": "Simplify highly dense logic frameworks."}
}

def render_workspace(active_index):
    chosen_scope = scenarios_mapping[active_index]
    st.markdown(f'<div class="chat-card"><div style="font-size:1.3rem; color:#e9edef;">{chosen_scope["name"]}</div></div>', unsafe_allow_html=True)
    user_prompt = st.text_area("Type intent here...", key=f"text_{active_index}")
    
    if st.button("Evaluate & Generate Output ✔️", key=f"btn_{active_index}"):
        if not user_prompt.strip(): st.warning("Fields cannot be empty.")
        else:
            with st.spinner("Processing..."):
                res = run_evaluation(chosen_scope['name'], user_prompt)
                if "error" in res: st.error(res["error"])
                else:
                    st.metric(label="Match Rate", value=f"{res.get('score', 6) * 10}%")
                    st.code(res.get("improved_prompt", ""), language="text")
                    final_out = generate_final_content(chosen_scope['name'], res.get("improved_prompt", ""))
                    st.code(final_out)
                    log_data_to_sheets(chosen_scope['name'], user_prompt, res.get("improved_prompt", ""), final_out)

def run_evaluation(scope_name, raw_prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(f"Analyze prompt for {scope_name}. Return valid JSON with score, strengths, weaknesses, improved_prompt.\n\nPrompt: {raw_prompt}")
        clean = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean)
    except Exception as e: return {"error": str(e)}

def generate_final_content(scope_name, optimized_prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(optimized_prompt)
        return response.text.strip()
    except Exception as e: return str(e)

for idx, tab_object in enumerate(tabs):
    with tab_object: render_workspace(idx)
