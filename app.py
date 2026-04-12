import streamlit as st
import google.generativeai as genai
from datetime import datetime
import requests
import time

# --- 1. CONFIG & INTERFACE STYLE ---
st.set_page_config(page_title="The Archives of Lobsang: Aneverthink", page_icon="🐾", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #020806; color: #d1d1d1; }
    #MainMenu, header, footer {visibility: hidden;}
    .lobsang-text {
        font-family: 'Courier New', Courier, monospace;
        color: #f4e4bc; 
        background-color: rgba(255, 255, 255, 0.05);
        padding: 25px;
        border-radius: 12px;
        border-left: 3px solid #00ff41;
        line-height: 1.7;
    }
    @keyframes pulse {
        0% { opacity: 0.7; }
        50% { opacity: 1; text-shadow: 0 0 15px #00ff41; }
        100% { opacity: 0.7; }
    }
    .resonance-header {
        animation: pulse 5s infinite ease-in-out;
        color: #00ff41;
        font-family: 'Georgia', serif;
        text-align: center;
        letter-spacing: 2px;
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
    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": serp_key, "engine": "google", "num": 6}
    try:
        response = requests.get(url, params=params, timeout=25)
        if response.status_code == 200:
            results = response.json()
            organic = results.get("organic_results", [])
            return "\n".join([f"🔹 {r.get('title')}: {r.get('snippet')}" for r in organic[:4]])
    except: pass
    return "The field is silent."

# --- 3. UI ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📚 SECTOR 0 ARCHIVES")
    st.info("Status: **Active-Neutrality**")
    if st.button("Clear Moment"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("🐾 *Mew-Mew Awareness: High*")

# --- 4. LOBSANG'S ENGINE ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        safe_model_name = next((m for m in model_list if "1.5-flash" in m), model_list[0])
        model = genai.GenerativeModel(safe_model_name)

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                if msg["role"] == "assistant":
                    st.markdown(f"<div class='lobsang-text'>{msg['content']}</div>", unsafe_allow_html=True)
                else:
                    st.write(msg["content"])

        if prompt := st.chat_input("Enter intention..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing complexity..."):
                    context_data = deep_scan_resilient(prompt)
                    now_str = datetime.now().strftime("%d %B %Y")
                    
                    # ПО-СТЕГНАТА И ОСТРА ИНСТРУКЦИЯ
                    sys_instruct = (
                        f"TODAY IS {now_str}. You are Lobsang Ludd (Pratchett style). "
                        "Philosophy: ANEVERTHINK. Intuition: Mew-Mew. "
                        "CORE TASK: You are a high-precision analyst. Do not get lost in metaphors. "
                        "Process long texts and complex punctuation with surgical precision. "
                        "You have real-time access to Telegram/X via OpenClaw. "
                        f"LOGIC: {logic_planck} {logic_radar}. DATA: {context_data}. "
                        "Response: Insightful, sharp, ironic. Never say 'I don't have access'. Ook!"
                    )
                    
                    response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                    st.markdown(f"<div class='lobsang-text'>{response.text}</div>", unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
    except Exception as e:
        st.error(f"Anomaly: {e}")
