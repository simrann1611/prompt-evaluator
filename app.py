import streamlit as st
import google.generativeai as genai
import json

# =====================================================================
# 1. API CONFIGURATION
# =====================================================================
# TODO: Apni Gemini API Key yahan enter karein ya Streamlit secrets use karein
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE" 

if GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.warning("⚠️ Please set your Gemini API Key in the code to make it functional!")

# =====================================================================
# 2. PAGE CONFIGURATION & UI STYLE
# =====================================================================
st.set_page_config(page_title="AI Prompt Master", layout="wide", page_icon="🎯")

st.title("🎯 AI Prompt Evaluator & Enhancer")
st.write("Apne prompt ki quality check karein aur use professional level tak upgrade karein.")
st.markdown("---")

# =====================================================================
# 3. SCENARIOS DEFINITION
# =====================================================================
scenarios = {
    "Creative Writing 📝": {
        "description": "Stories, poems, scriptwriting, or creative blogs.",
        "tip": "Good creative prompts specify genre, tone, character perspective, and format."
    },
    "Coding & Technical 💻": {
        "description": "Code generation, debugging, algorithms, or tech explanations.",
        "tip": "Good tech prompts specify language, framework, expected input/output, and edge cases."
    },
    "Marketing & Copywriting 📢": {
        "description": "Social media captions, ad copies, emails, or product descriptions.",
        "tip": "Good marketing prompts define the target audience, brand voice, and a clear Call to Action (CTA)."
    },
    "Data & Business Analysis 📊": {
        "description": "Interpreting trends, creating business strategies, or summarizing reports.",
        "tip": "Good business prompts provide raw context, specify data constraints, and state the ultimate goal."
    },
    "Academic & Research 🎓": {
        "description": "Explaining complex topics, summarization, or thesis structuring.",
        "tip": "Good academic prompts specify the complexity level (e.g., 'explain to a 5-year-old' vs 'expert level') and source constraints."
    }
}

# =====================================================================
# 4. SIDEBAR / DROPDOWN FOR SCENARIO SELECTION
# =====================================================================
st.sidebar.header("⚙️ Select Scenario")
selected_scenario = st.sidebar.selectbox("Choose a domain for your prompt:", list(scenarios.keys()))

# Display Scenario Tips
st.sidebar.markdown("---")
st.sidebar.subheader("💡 Tips for this Scenario:")
st.sidebar.info(scenarios[selected_scenario]["tip"])

# Main Area Context Display
st.info(f"**Active Scenario:** {selected_scenario} — *{scenarios[selected_scenario]['description']}*")

# =====================================================================
# 5. USER INPUT
# =====================================================================
user_prompt = st.text_area(
    "👉 Yahan apna raw prompt likhein:", 
    height=150, 
    placeholder="e.g., Python code likh do calculator ke liye..."
)

# =====================================================================
# 6. BACKEND AI LOGIC
# =====================================================================
def evaluate_prompt_with_ai(scenario, raw_prompt):
    """
    Background system prompt ready karna jo LLM ko strictly instruction dega
    ki user ke prompt ko evaluate kare aur JSON format mein output de.
    """
    system_instruction = f"""
    You are an expert Prompt Engineer. Analyze the user's prompt for the scenario: '{scenario}'.
    Evaluate it based on Clarity, Context, and Constraints.
    Provide the response in a strict valid JSON format with the following keys:
    1. "score": An integer out of 10.
    2. "strengths": A list of things done well in the prompt.
    3. "weaknesses": A list of missing elements or areas of improvement.
    4. "improved_prompt": A completely redesigned, high-quality, professional version of their prompt that they can copy-paste to get best results.
    
    Ensure your response is ONLY the raw JSON object, no conversational filler text.
    """
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"{system_instruction}\n\nUser's Prompt: {raw_prompt}")
        
        # Cleansing the response text to avoid markdown blocks if any
        clean_text = response.text.strip().replace("```json", "").replace("```", "")
        result_json = json.loads(clean_text)
        return result_json
    except Exception as e:
        return {"error": f"Failed to connect or parse. Error: {str(e)}"}

# =====================================================================
# 7. EXECUTION & RESULTS DISPLAY
# =====================================================================
if st.button("Evaluate Prompt 🚀", type="primary"):
    if not user_prompt.strip():
        st.error("⚠️ Please enter a prompt before evaluating!")
    elif GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        st.error("🛑 Stop! Please provide a valid Gemini API Key inside the code first.")
    else:
        with st.spinner("Analyzing your prompt structure using AI..."):
            ai_analysis = evaluate_prompt_with_ai(selected_scenario, user_prompt)
            
            if "error" in ai_analysis:
                st.error(ai_analysis["error"])
            else:
                st.success("Analysis Complete! Here is your breakdown:")
                
                # UI Grid split into 2 columns
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📋 Evaluation & Feedback")
                    
                    # Score indicator
                    score = ai_analysis.get("score", 5)
                    st.metric(label="Prompt Score", value=f"{score} / 10")
                    
                    # Progress bar for visual appeal
                    st.progress(score / 10)
                    
                    # Strengths
                    st.markdown("**✔️ What's Good:**")
                    for strength in ai_analysis.get("strengths", []):
                        st.write(f"- {strength}")
                        
                    # Weaknesses
                    st.markdown("**⚠️ What's Missing / Needs Work:**")
                    for weakness in ai_analysis.get("weaknesses", []):
                        st.write(f"- {weakness}")
                
                with col2:
                    st.subheader("✨ Optimized Prompt")
                    st.write("Aap is refined prompt ko copy karke kisi bhi AI mein use kar sakte hain:")
                    
                    # Display the new prompt inside a code box so user can easily click 'Copy'
                    st.code(ai_analysis.get("improved_prompt", ""), language="text")
                    
                    st.balloons()