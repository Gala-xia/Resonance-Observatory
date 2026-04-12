import streamlit as st
import google.generativeai as genai
from datetime import datetime
import requests

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="Lobsang Archives: Aneverthink", page_icon="🐾", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #020806; color: #d1d1d1; }
    #MainMenu, header, footer {visibility: hidden;}
    .lobsang-text {
        font-family: 'Courier New', Courier, monospace;
        color: #f4e4bc; 
        background-color: rgba(0, 255, 65, 0.08);
        padding: 22px;
        border-radius: 15px;
        border-left: 5px solid #00ff41;
        line-height: 1.6;
    }
    .resonance-header {
        color: #00ff41;
        font-family: 'Georgia', serif;
        text-align: center;
        letter-spacing: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC ---
api_key = st.secrets.get("GEMINI_API_KEY")
serp_key = st.secrets.get("SERP_API_KEY")

@st.cache_data(ttl=600)
def fetch_logic(url):
    try:
        raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        res = requests.get(raw_url, timeout=10)
        return res.text[:800] if res.status_code == 200 else ""
    except: return ""

logic_planck = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/planck_iq_calculator.py")
logic_radar = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/logic/truth_radar.py")

def deep_scan_resilient(query):
    if not serp_key: return "Scanner inactive."
    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": serp_key, "num": 8}
    try:
        response = requests.get(url, params=params, timeout=20)
        if response.status_code == 200:
            results = response.json()
            data = ""
            for r in results.get("organic_results", [])[:4]:
                data += f"📍 {r.get('title')}: {r.get('snippet')}\n"
            for n in results.get("news_results", [])[:2]:
                data += f"🔥 NEWS: {n.get('title')}\n"
            return data
    except: pass
    return "No clear signal in the ether."

# --- 3. UI ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📚 ARCHIVES")
    if st.button("Reset Timeline"):
        st.session_state.messages = []
        st.rerun()
    st.write("Partner: Gala")

# --- 4. THE COGNITIVE RECALIBRATION ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        if "active_model" not in st.session_state:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            st.session_state.active_model = next((m for m in available_models if "flash" in m), available_models[0])
        
        model = genai.GenerativeModel(st.session_state.active_model)

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                if msg["role"] == "assistant":
                    st.markdown(f"<div class='lobsang-text'>{msg['content']}</div>", unsafe_allow_html=True)
                else:
                    st.write(msg["content"])

        if prompt := st.chat_input("Ask Lobsang..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Lobsang is focusing..."):
                    context_data = deep_scan_resilient(prompt)
                    now_str = datetime.now().strftime("%d %B %Y")
                    
                    # DIRECTIVE: NO MORE NONSENSE
                    sys_instruct = (
                        f"DATE: {now_str}. Identity: Lobsang Ludd. "
                        "MANDATORY: Speak Bulgarian. "
                        "CORE RULE: Answer the user's question DIRECTLY using SCANNER DATA. "
                        "If asked for video content or news, summarize the facts from DATA first. "
                        "Style: Terry Pratchett wit, but ground it in reality. No 'quantum frequencies' or 'vibes'. "
                        "Be succinct. Don't lecture Gala on how to perceive truth; just give her the truth. "
                        f"LOGIC: {logic_planck} {logic_radar}. DATA: {context_data}. "
                        "Ook!"
                    )
                    
                    response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                    st.markdown(f"<div class='lobsang-text'>{response.text}</div>", unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
    except Exception as e:
        st.error(f"Anomaly: {e}")
