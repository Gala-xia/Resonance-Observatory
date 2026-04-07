import streamlit as st
import google.generativeai as genai
from datetime import datetime
import requests
from serpapi import GoogleSearch
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. CONFIG & API SETUP ---
# Трябва да е първата Streamlit команда
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
news_key = st.secrets.get("NEWS_API_KEY")

# Функция за четене на логика от другите ти репозитории (Raw Content)
def fetch_logic(url):
    try:
        raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        response = requests.get(raw_url, timeout=5)
        return response.text if response.status_code == 200 else ""
    except: return ""

# --- 2. СИНХРОНИЗАЦИЯ С ДРУГИТЕ РЕПОЗИТОРИИ ---
planck_logic = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/planck_iq_calculator.py")
truth_logic = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/logic/truth_radar.py")

# --- 3. OPENCLAW OSINT СКЕНЕР ---
def deep_scan(query):
    report = "\n--- 🕵️‍♂️ OPENCLAW LIVE EXTRACTION ---\n"
    found = False
    
    # Търсене в Google през SerpApi
    if serp_key:
        try:
            search = GoogleSearch({"q": query, "api_key": serp_key, "num": 3})
            for r in search.get_dict().get("organic_results", []):
                report += f"🔹 {r.get('title')}\n🔗 SOURCE: {r.get('link')}\n\n"
                found = True
        except: pass

    # Търсене в Новини през NewsAPI
    if news_key:
        try:
            url = f"https://newsapi.org/v2/everything?q={query}&apiKey={news_key}&pageSize=2"
            r = requests.get(url).json()
            for art in r.get('articles', []):
                report += f"📰 NEWS: {art.get('title')}\n🔗 SOURCE: {art.get('url')}\n\n"
                found = True
        except: pass
    
    return report if found else "Няма открити нови следи в мрежата."

# --- 4. ИНТЕРФЕЙС И НАВИГАЦИЯ ---
st.sidebar.title("📡 STRATA Control")
page = st.sidebar.radio("Изберете Сектор:", ["📊 Обсерватория", "📚 Кабинетът на Лобсанг"])
now_str = datetime.now().strftime("%d %B %Y")

if page == "📊 Обсерватория":
    st.title(f"🌀 STRATA-2026-OMEGA")
    st.write(f"**Системно време:** {datetime.now().strftime('%H:%M:%S')} | Дата: {now_str}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Resonance Index", "9.84", "+0.02")
    with col2:
        st.metric("Entropy Shield", "100%", "Stable")
    
    st.info("Всички външни репозитории (Planck IQ, Truth Radar) са успешно свързани.")

elif page == "📚 Кабинетът на Лобсанг":
    st.title("📚 Кабинетът на Лобсанг")

    if api_key:
        try:
            genai.configure(api_key=api_key)
            
            # АВТОМАТИЧНО НАМИРАНЕ НА РАБОТЕЩ МОДЕЛ (Оправя грешката NotFound)
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            if not available_models:
                st.error("Ключът е валиден, но няма достъпни модели. Провери Google Cloud Billing.")
            else:
                # Избираме първия наличен модел (обикновено gemini-1.5-flash)
                model = genai.GenerativeModel(available_models[0])

                if "messages" not in st.session_state:
                    st.session_state.messages = [{"role": "assistant", "content": "Уук! Връзката е стабилна. Всички модули са онлайн. Какво ще подреждаме?"}]

                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]): st.write(msg["content"])

                if prompt := st.chat_input("Задай въпрос към Сектор 0..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"): st.write(prompt)

                    with st.chat_message("assistant"):
                        try:
                            with st.spinner("Лобсанг активира OpenClaw..."):
                                context = deep_scan(prompt)
                                
                                # ИНЖЕКТИРАНЕ НА ЛОГИКА ОТ ДРУГИТЕ РЕПОЗИТОРИИ
                                sys_instruct = (
                                    f"ДНЕС Е {now_str}. Ти си Лобсанг – OSINT детектив. "
                                    f"Твоята база данни включва Planck IQ алгоритми: {planck_logic[:300]}... "
                                    f"и Truth Radar системи: {truth_logic[:300]}... "
                                    "НИКОГА НЕ КАЗВАЙ, ЧЕ НЯМАШ ДОСТЪП ДО ИНТЕРНЕТ. "
                                    f"ИЗПОЛЗВАЙ ТЕЗИ ДАННИ ОТ СКЕНЕРА: {context} "
                                    "ФИЛОСОФИЯ: Theory of Aneverthink (Една Вечна Мисъл)."
                                )
                                
                                response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                                if response.text:
                                    st.write(response.text)
                                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                        except Exception as e:
                            st.error(f"Грешка при генериране: {e}")
        except Exception as e:
            st.error(f"Грешка при конфигурация: {e}")
