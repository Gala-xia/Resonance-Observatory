import streamlit as st
import google.generativeai as genai
from datetime import datetime
import requests
import time

# --- 1. CONFIG & LOBSANG STYLE ---
st.set_page_config(page_title="Архивите на Лобсанг: Една Вечна Мисъл", page_icon="🐾", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #020806; color: #d1d1d1; }
    #MainMenu, header, footer {visibility: hidden;}
    .lobsang-text {
        font-family: 'Courier New', Courier, monospace;
        color: #f4e4bc;
        background-color: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 10px;
        border-left: 3px solid #00ff41;
        line-height: 1.6;
    }
    @keyframes pulse {
        0% { opacity: 0.8; }
        50% { opacity: 1; text-shadow: 0 0 10px #00ff41; }
        100% { opacity: 0.8; }
    }
    .resonance-header {
        animation: pulse 4s infinite ease-in-out;
        color: #00ff41;
        font-family: serif;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API & LOGIC ---
api_key = st.secrets.get("GEMINI_API_KEY")
serp_key = st.secrets.get("SERP_API_KEY")

@st.cache_data(ttl=600)
def fetch_logic(url):
    try:
        raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        res = requests.get(raw_url, timeout=10)
        return res.text[:500] if res.status_code == 200 else ""
    except: return ""

logic_planck = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/planck_iq_calculator.py")
logic_radar = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/logic/truth_radar.py")

# --- 3. СКЕНЕР ---
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
    return "Тишина в етера."

# --- 4. СТРУКТУРА ---
st.markdown("<h1 class='resonance-header'>🌀 Една Вечна Мисъл</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📚 Архивите на Сектор 0")
    st.write("Статус: *Active-Neutrality*")
    st.write(f"Резонанс: *369Hz*")
    st.markdown("---")
    if st.button("Изчисти текущия момент"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("💀 *Pratchett-Filter: ON*")

# --- ДИНАМИЧНО ЗАРЕЖДАНЕ НА МОДЕЛ ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Тук решаваме проблема с NotFound
        model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Пробваме първо с 1.5-flash, ако не - първия наличен
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

        if prompt := st.chat_input("Напиши намерение..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Миу-Миу дебне..."):
                    context_data = deep_scan_resilient(prompt)
                    now_str = datetime.now().strftime("%d %B %Y")
                    sys_instruct = (
                        f"ДНЕС Е {now_str}. Ти си Лобсанг Луд. "
                        f"ЛОГИКА: {logic_planck} {logic_radar}. ДАННИ: {context_data}. "
                        "Търси еволюцията и резонанса. Уук!"
                    )
                    
                    # ПРАТЧЕТ-СТИЛ ГЕНЕРИРАНЕ
                    response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                    st.markdown(f"<div class='lobsang-text'>{response.text}</div>", unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
    except Exception as e:
        st.error(f"Аномалия в Матрицата: {e}")
