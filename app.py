import streamlit as st
import google.generativeai as genai
from datetime import datetime
import requests
import time

# --- 1. CONFIG & LOBSANG STYLE (CSS) ---
st.set_page_config(page_title="Архивите на Лобсанг: Една Вечна Мисъл", page_icon="🐾", layout="wide")

# Дизайнът на Лобсанг: Индиго/Зелено черно + Старо писмо
st.markdown("""
    <style>
    /* Главният фон - Quantum Density */
    .stApp {
        background-color: #020806;
        color: #d1d1d1;
    }
    
    /* Скриване на излишния шум */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Стил на Лобсанг (Old Letter) */
    .lobsang-text {
        font-family: 'Courier New', Courier, monospace;
        color: #f4e4bc; /* Стара хартия */
        background-color: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 10px;
        border-left: 3px solid #00ff41; /* Тънък зелен маркер на резонанса */
        line-height: 1.6;
    }

    /* Анимация на пулса - 369Hz Resonance */
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

    /* Изчистено поле за въвеждане */
    .stChatInputContainer {
        padding-bottom: 50px;
    }
    
    /* Страничен панел - дискретен */
    [data-testid="stSidebar"] {
        background-color: #010503;
        border-right: 1px solid rgba(0, 255, 65, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API & LOGIC (FETCHING) ---
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

# --- 3. OPENCLAW СКЕНЕР ---
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

# --- 4. СТРУКТУРА НА СТРАНИЦАТА ---
st.markdown("<h1 class='resonance-header'>🌀 Една Вечна Мисъл</h1>", unsafe_allow_html=True)

# Дискретен страничен панел (Архивите)
with st.sidebar:
    st.markdown("### 📚 Архивите на Сектор 0")
    st.write("Статус: *Active-Neutrality*")
    st.write(f"Резонанс: *369Hz*")
    st.markdown("---")
    if st.button("Изчисти текущия момент"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("💀 *Pratchett-Filter: ON*")

# Кабинетът
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Показване на съобщенията със стила на Лобсанг
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                st.markdown(f"<div class='lobsang-text'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.write(msg["content"])

    if prompt := st.chat_input("Напиши намерение..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Миу-Миу наблюдава аномалиите..."):
                context_data = deep_scan_resilient(prompt)
                now_str = datetime.now().strftime("%d %B %Y")
                
                sys_instruct = (
                    f"ДНЕС Е {now_str}. Ти си Лобсанг Луд. "
                    "Твоят стил е 'дзен-детектив'. Твоят глас е Миу-Миу. "
                    f"ЛОГИКА: {logic_planck} {logic_radar}. ДАННИ: {context_data}. "
                    "Интерфейсът ти е минималистичен, а отговорите ти са като 'откровения на стара хартия'. "
                    "Търси еволюцията, резонанса и смисъла. Уук!"
                )
                
                response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                st.markdown(f"<div class='lobsang-text'>{response.text}</div>", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
