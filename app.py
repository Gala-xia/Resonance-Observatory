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

# Функция за четене на логика от 4-те репозитория
def fetch_logic(url):
    try:
        raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        res = requests.get(raw_url, timeout=5)
        return res.text[:500] if res.status_code == 200 else ""
    except: return ""

# --- 2. СИНХРОНИЗАЦИЯ НА ЕКОСИСТЕМАТА ---
logic_planck = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/planck_iq_calculator.py")
logic_resilience = fetch_logic("https://github.com/Gala-xia/AutonomousNode-Resilience-Framework/blob/main/core/core.py")
logic_shield = fetch_logic("https://github.com/Gala-xia/Core-Resilience-Optimizer/blob/main/core.py")
logic_radar = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/logic/truth_radar.py")

# --- 3. ХИБРИДЕН OPENCLAW СКЕНЕР (ДЪЛБОЧИНА + СКОРОСТ) ---
def deep_scan(query):
    report = "\n--- 🕵️‍♂️ OPENCLAW HYBRID SCAN ---\n"
    found = False
    
    if not serp_key:
        return "⚠️ ГРЕШКА: SERP_API_KEY ЛИПСВА!"

    try:
        # А. ТЪРСЕНЕ ЗА ДЪЛБОЧИНА (Organic)
        params_deep = {
            "q": query,
            "api_key": serp_key,
            "engine": "google",
            "num": 4
        }
        search_deep = GoogleSearch(params_deep)
        res_deep = search_deep.get_dict().get("organic_results", [])
        
        if res_deep:
            report += "📂 [АРХИВ И КОНТЕКСТ]:\n"
            for r in res_deep:
                report += f"🔹 {r.get('title')} | {r.get('link')}\n"
                found = True

        # Б. ТЪРСЕНЕ ЗА АКТУАЛНОСТ (News)
        params_news = {
            "q": query,
            "api_key": serp_key,
            "engine": "google",
            "tbm": "nws",
            "num": 3
        }
        search_news = GoogleSearch(params_news)
        res_news = search_news.get_dict().get("news_results", [])
        
        if res_news:
            report += "\n📰 [ПРЕСЕН ИНФО-ПОТОК]:\n"
            for n in res_news:
                report += f"🔥 {n.get('title')} ({n.get('date')}) | {n.get('link')}\n"
                found = True

    except Exception as e:
        report += f"⚠️ ГРЕШКА ПРИ СКАНЕРА: {str(e)}\n"

    return report if found else report + "Информационното поле е в състояние на покой (0 резултати)."

# --- 4. ИНТЕРФЕЙС И ЛОГИКА НА ЛОБСАНГ ---
st.sidebar.title("📡 STRATA Control")
page = st.sidebar.radio("Сектор:", ["📊 Обсерватория", "📚 Кабинетът на Лобсанг"])
now_str = datetime.now().strftime("%d %B %Y")

if page == "📊 Обсерватория":
    st.title("🌀 STRATA-2026-OMEGA")
    st.write(f"**Системно време:** {datetime.now().strftime('%H:%M:%S')} | {now_str}")
    st.info("Хибридният скенер е активен (Depth + Real-time). 4 репозитория в синхрон.")
    st.metric("Resonance Level", "9.84", "Stable")

elif page == "📚 Кабинетът на Лобсанг":
    st.title("📚 Кабинетът на Лобсанг")

    if api_key:
        try:
            genai.configure(api_key=api_key)
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            if models:
                model = genai.GenerativeModel(models[0])

                if "messages" not in st.session_state:
                    st.session_state.messages = [{"role": "assistant", "content": "Уук! Лобсанг е тук. Готов съм за дълбок OSINT анализ."}]

                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]): st.write(msg["content"])

                if prompt := st.chat_input("Задай въпрос към Сектор 0..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"): st.write(prompt)

                    with st.chat_message("assistant"):
                        with st.spinner("Активирам OpenClaw Hybrid..."):
                            context = deep_scan(prompt)
                            
                            sys_instruct = (
                                f"ДНЕС Е {now_str}. Ти си Лобсанг – детектив от Сектор 0. "
                                f"ЛОГИКА: {logic_planck} {logic_resilience} {logic_shield} {logic_radar}. "
                                f"ДАННИ: {context} "
                                "ИНСТРУКЦИЯ: Анализирай връзката между старите данни (Архив) и новите (Инфо-поток). "
                                "Не пренебрегвай детайлите. Търси скрити патърни. "
                                "Философия: Theory of Aneverthink. Стил: 'Уук!', 'Ну и що!'."
                            )
                            
                            response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                            st.write(response.text)
                            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Грешка: {e}")
