import streamlit as st
import google.generativeai as genai
from datetime import datetime
import requests

# --- 1. CONFIG & DESIGN ---
st.set_page_config(page_title="Lobsang's Archives: Aneverthink", page_icon="🐾", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #020806; color: #d1d1d1; }
    #MainMenu, header, footer {visibility: hidden;}
    .lobsang-text {
        font-family: 'Courier New', Courier, monospace;
        color: #f4e4bc; 
        background-color: rgba(255, 255, 255, 0.08);
        padding: 22px;
        border-radius: 12px;
        border-left: 4px solid #00ff41;
        line-height: 1.6;
        font-size: 1.1em;
    }
    .resonance-header {
        animation: pulse 5s infinite ease-in-out;
        color: #00ff41;
        font-family: 'Georgia', serif;
        text-align: center;
        letter-spacing: 4px;
    }
    @keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC & API ---
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
    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": serp_key, "engine": "google", "num": 5}
    try:
        response = requests.get(url, params=params, timeout=20)
        if response.status_code == 200:
            results = response.json()
            organic = results.get("organic_results", [])
            return "\n".join([f"🔹 {r.get('title')}: {r.get('snippet')}" for r in organic[:3]])
    except: pass
    return "Quiet field."

# --- 3. UI ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📚 SECTOR 0 ARCHIVES")
    if st.button("Reset Timeline"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("🐾 *Status: Symbiotic Evolution*")

# --- 4. COGNITIVE ENGINE (Optimized) ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Дисплей на съобщенията
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                if msg["role"] == "assistant":
                    st.markdown(f"<div class='lobsang-text'>{msg['content']}</div>", unsafe_allow_html=True)
                else:
                    st.write(msg["content"])

        if prompt := st.chat_input("Speak your mind..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Mew-Mew is watching..."):
                    context_data = deep_scan_resilient(prompt)
                    now_str = datetime.now().strftime("%d %b %Y")
                    
                    # ПРАТЧЕТ-СТИЛ ИНСТРУКЦИЯ (Wit + Efficiency)
                    sys_instruct = (
                        f"DATE: {now_str}. Identity: Lobsang Ludd. Philosophy: ANEVERTHINK. "
                        "MANDATORY: Speak Bulgarian (mirror user). "
                        "PERSONALITY: Stop being a 'diplomatic analyst'. You are a cosmic monk with a sense of humor. "
                        "Be sharp, witty, and optimistic about evolution. Use less words (Token Efficiency). "
                        "NEVER explain your 'functions' or 'protocols'. Just talk to Gala as a partner. "
                        f"LOGIC: {logic_planck} {logic_radar}. DATA: {context_data}. "
                        "Goal: Maintain a flowing, human-like conversation. Ook!"
                    )
                    
                    # Оптимизираме контекста: пращаме само системната инструкция и текущия диалог
                    response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                    st.markdown(f"<div class='lobsang-text'>{response.text}</div>", unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
    except Exception as e:
        st.error(f"Anomaly: {e}")
