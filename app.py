import streamlit as st
import google.generativeai as genai
from datetime import datetime
import requests
from serpapi import GoogleSearch
import pandas as pd
import numpy as np
import plotly.graph_objects as go

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
news_key = st.secrets.get("NEWS_API_KEY")

# Функция за четене на логика от твоите 4 репозитория
def fetch_logic(url):
    try:
        raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        res = requests.get(raw_url, timeout=5)
        return res.text[:500] if res.status_code == 200 else ""
    except: return ""

# --- 2. СИНХРОНИЗАЦИЯ НА ЧЕТИРИТЕ РЕПОЗИТОРИЯ ---
logic_planck = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/planck_iq_calculator.py")
logic_resilience = fetch_logic("https://github.com/Gala-xia/AutonomousNode-Resilience-Framework/blob/main/core/core.py")
logic_shield = fetch_logic("https://github.com/Gala-xia/Core-Resilience-Optimizer/blob/main/core.py")
logic_radar = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/logic/truth_radar.py")

# --- 3. АГРЕСИВЕН OPENCLAW СКЕНЕР ---
def deep_scan(query):
    report = "\n--- 🕵️‍♂️ OPENCLAW LIVE EXTRACTION ---\n"
    found = False
    
    if not serp_key:
        return "⚠️ ГРЕШКА: SERP_API_KEY ЛИПСВА В SECRETS!"

    try:
        params = {
            "q": query,
            "api_key": serp_key,
            "engine": "google",
            "google_domain": "google.com",
            "gl": "us", 
            "hl": "en",
            "num": 5
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Проверка в органични резултати
        organic = results.get("organic_results", [])
        if organic:
            for r in organic:
                report += f"🔹 {r.get('title')}\n🔗 {r.get('link')}\n\n"
                found = True
        
        # Проверка в новинарски резултати (ако органичните са празни)
        if not found:
            news = results.get("news_results", [])
            for n in news:
                report += f"📰 NEWS: {n.get('title')}\n🔗 {n.get('link')}\n\n"
                found = True
                
        if not found:
            report += f"DEBUG: Скенерът е активен, но Google върна 0 резултати за '{query}'.\n"

    except Exception as e:
        report += f"⚠️ ГРЕШКА ПРИ СКАНЕРА: {str(e)}\n"

    return report

# --- 4. ИНТЕРФЕЙС ---
st.sidebar.title("📡 STRATA Control")
page = st.sidebar.radio("Сектор:", ["📊 Обсерватория", "📚 Кабинетът на Лобсанг"])
now_str = datetime.now().strftime("%d %B %Y")

if page == "📊 Обсерватория":
    st.title("🌀 STRATA-2026-OMEGA")
    st.write(f"**Системно време:** {datetime.now().strftime('%H:%M:%S')} | {now_str}")
    
    col1, col2 = st.columns(2)
    with col1: st.metric("Resonance Index", "9.84", "+0.02")
    with col2: st.metric("Planck IQ Sync", "ACTIVE", "1.0")
    
    st.info("Връзката с 4-те репозитория е стабилна. ОпенКлоу е в режим на изчакване.")

elif page == "📚 Кабинетът на Лобсанг":
    st.title("📚 Кабинетът на Лобсанг")

    if api_key:
        try:
            genai.configure(api_key=api_key)
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            if available_models:
                model = genai.GenerativeModel(available_models[0])

                if "messages" not in st.session_state:
                    st.session_state.messages = [{"role": "assistant", "content": "Уук! Всички модули са онлайн. Какво ще сканираме днес?"}]

                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]): st.write(msg["content"])

                if prompt := st.chat_input("Задай въпрос..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"): st.write(prompt)

                    with st.chat_message("assistant"):
                        with st.spinner("Лобсанг активира OpenClaw..."):
                            context = deep_scan(prompt)
                            
                            sys_instruct = (
                                f"ДНЕС Е {now_str}. Ти си Лобсанг – OSINT детектив. "
                                f"ЛОГИКА (Planck/Resilience/Shield): {logic_planck} {logic_resilience} {logic_shield}. "
                                f"РАДАР (TruthRadar): {logic_radar}. "
                                f"ДАННИ ОТ СКЕНЕРА: {context} "
                                "ВАЖНО: Ако скенерът показва '0 резултати', кажи го директно. "
                                "Философия: Theory of Aneverthink (Една Вечна Мисъл). Тон: 'Уук!', 'Ну и що!'."
                            )
                            
                            response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                            st.write(response.text)
                            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Грешка: {e}")
