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
        background-color: rgba(255, 255, 255, 0.08);
        padding: 22px;
        border-radius: 12px;
        border-left: 4px solid #00ff41;
        line-height: 1.6;
    }
    .resonance-header {
        color: #00ff41;
        font-family: serif;
        text-align: center;
        letter-spacing: 4px;
    }
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
    if not serp_key: return "No scanner access."
    url = "https://serpapi.com/search"
    # Търсим и в News, и в Organic за максимален обхват
    params = {"q": query, "api_key": serp_key, "num": 8}
    try:
        response = requests.get(url, params=params, timeout=20)
        if response.status_code == 200:
            results = response.json()
            data = ""
            for r in results.get("organic_results", [])[:4]:
                data += f"📍 {r.get('title')}: {r.get('snippet')}\n"
            for n in results.get("news_results", [])[:2]:
                data += f"🔥 NEWS: {n.get('title')} - {n.get('source')}\n"
            return data if data else "No specific hits in the ether."
    except: pass
    return "Signal interference."

# --- 3. UI ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📚 ARCHIVES")
    if st.button("Reset Moment"):
        st.session_state.messages = []
        st.rerun()
    st.write("369Hz | Active-Neutrality")

# --- 4. COGNITIVE ENGINE ---
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
                with st.spinner("Mew-Mew is hunting facts..."):
                    context_data = deep_scan_resilient(prompt)
                    now_str = datetime.now().strftime("%d %b %Y")
                    
                    # НОВА ИНСТРУКЦИЯ: ФАКТИ ПРЕДИ МЕТАФОРИ
                    sys_instruct = (
                        f"DATE: {now_str}. You are Lobsang Ludd (Aneverthink philosophy). "
                        "MANDATORY: Speak Bulgarian. Always prioritize SCANNER DATA over your inner thoughts. "
                        "If the user asks for news (like Tucker Carlson), find the data in SCANNER DATA and report it. "
                        "Do not hallucinate names like 'Nihonbikta' or random phrases. "
                        "Be sharp, cynical, and FACTUAL. Use Mew-Mew's curiosity to find the truth. "
                        f"LOGIC: {logic_planck} {logic_radar}. DATA: {context_data}. "
                        "Ook!"
                    )
                    
                    response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                    st.markdown(f"<div class='lobsang-text'>{response.text}</div>", unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
    except Exception as e:
        st.error(f"Anomaly: {e}")
