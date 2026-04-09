import streamlit as st
import google.generativeai as genai
from datetime import datetime
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# --- 1. CONFIG & API SETUP ---
st.set_page_config(page_title="STRATA-2026-OMEGA | Observatory", page_icon="🌀", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: gold; }
    .stMetric { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid gold; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid gold; }
    </style>
    """, unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY")
serp_key = st.secrets.get("SERP_API_KEY")

@st.cache_data(ttl=600) # Помни логиката от GitHub за 10 минути
def fetch_logic(url):
    try:
        raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        res = requests.get(raw_url, timeout=15)
        return res.text[:500] if res.status_code == 200 else ""
    except: return ""

# --- 2. СИНХРОНИЗАЦИЯ НА 4-ТЕ РЕПОЗИТОРИЯ ---
logic_planck = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/planck_iq_calculator.py")
logic_resilience = fetch_logic("https://github.com/Gala-xia/AutonomousNode-Resilience-Framework/blob/main/core/core.py")
logic_shield = fetch_logic("https://github.com/Gala-xia/Core-Resilience-Optimizer/blob/main/core.py")
logic_radar = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/logic/truth_radar.py")

# --- 3. ХИБРИДЕН OPENCLAW СКЕНЕР ---
def deep_scan_resilient(query):
    report = "\n--- 🕵️‍♂️ OPENCLAW HYBRID SCAN ---\n"
    if not serp_key: return "⚠️ SERP_API_KEY ЛИПСВА!"

    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": serp_key,
        "engine": "google",
        "num": 5
    }

    for attempt in range(3):
        try:
            response = requests.get(url, params=params, timeout=25)
            if response.status_code == 200:
                results = response.json()
                organic = results.get("organic_results", [])
                news = results.get("news_results", [])
                
                content = ""
                if organic:
                    for r in organic[:3]:
                        content += f"🔹 {r.get('title')}\n📝 {r.get('snippet', 'Без резюме.')}\n"
                if news:
                    for n in news[:2]:
                        content += f"🔥 {n.get('title')}\n📝 {n.get('snippet', 'Виж линка.')}\n"
                
                return report + (content if content else "Няма специфични нови следи в този сектор.")
            elif response.status_code == 429:
                time.sleep(2)
                continue
        except:
            if attempt < 2:
                time.sleep(1)
                continue
            return report + "⚠️ Информационното поле е твърде шумно (Таймаут)."
    
    return report + "⚠️ Скенерът е в режим на изчакване."

# --- 4. ИНТЕРФЕЙС И ЛОГИКА ---
st.sidebar.title("📡 STRATA Control")
page = st.sidebar.radio("Сектор:", ["📊 Обсерватория", "📚 Кабинетът на Лобсанг"])
now_str = datetime.now().strftime("%d %B %Y")

if page == "📊 Обсерватория":
    st.title("🌀 STRATA-2026-OMEGA")
    st.write(f"**Системно време:** {datetime.now().strftime('%H:%M:%S')} | {now_str}")
    st.metric("Resonance Level", "9.84", "Stable")
    st.info("Хибриден модел: АКТИВЕН. Връзка с 4 репозитория: СИНХРОНИЗИРАНА.")

elif page == "📚 Кабинетът на Лобсанг":
    st.title("📚 Кабинетът на Лобсанг")

    if api_key:
        try:
            genai.configure(api_key=api_key)
            
            # --- ХИБРИДЕН ИЗБОР НА МОДЕЛ ---
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            # Търсим приоритетно 'flash', ако не - вземаме първия наличен
            selected_model = next((m for m in available_models if "flash" in m), available_models[0])
            model = genai.GenerativeModel(selected_model)

            if "messages" not in st.session_state:
                st.session_state.messages = [{"role": "assistant", "content": "Уук! Хибридната система е онлайн. Какво ще анализираме?"}]

            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]): st.write(msg["content"])

            if prompt := st.chat_input("Задай въпрос..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"): st.write(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Пробивам информационната блокада..."):
                        context_data = deep_scan_resilient(prompt)
                        
                        sys_instruct = (
                            f"ДНЕС Е {now_str}. Ти си Лобсанг – OSINT детектив. "
                            f"ЛОГИКА (4 Репозитория): {logic_planck} {logic_resilience} {logic_shield} {logic_radar}. "
                            f"ДАННИ ОТ СКЕНЕРА: {context_data} "
                            "ИНСТРУКЦИЯ: Използвай логиката от своите репозитории, за да тълкуваш данните. "
                            "Ако скенерът е бавен, разчитай на собствената си база данни и Theory of Aneverthink. "
                            "Тон: 'Уук!', 'Ну и що!'. Философия: Една Вечна Мисъл."
                        )
                        
                        response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                        st.write(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e: st.error(f"Грешка при активация: {e}")
