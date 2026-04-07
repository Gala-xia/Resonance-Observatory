import streamlit as st
import google.generativeai as genai
from datetime import datetime
import requests
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

# --- 3. ДИРЕКТЕН OPENCLAW СКЕНЕР (БЕЗ БИБЛИОТЕКИ) ---
def deep_scan_direct(query):
    report = "\n--- 🕵️‍♂️ OPENCLAW DIRECT SCAN ---\n"
    if not serp_key:
        return "⚠️ ГРЕШКА: SERP_API_KEY ЛИПСВА В SECRETS!"

    # А. ТЪРСЕНЕ ЗА ДЪЛБОЧИНА (Organic)
    try:
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": serp_key,
            "engine": "google",
            "num": 5
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            results = response.json()
            organic = results.get("organic_results", [])
            if organic:
                report += "📂 [ИНФО-МАСИВ]:\n"
                for r in organic:
                    report += f"🔹 {r.get('title')} | {r.get('link')}\n"
            else:
                report += "⚠️ Скенерът е онлайн, но Google не върна органични резултати.\n"
            
            # Б. НОВИНАРСКИ ПОТОК (News)
            news = results.get("news_results", [])
            if news:
                report += "\n📰 [ПРЕСНИ НОВИНИ]:\n"
                for n in news:
                    report += f"🔥 {n.get('title')} ({n.get('date')}) | {n.get('link')}\n"
        else:
            report += f"⚠️ API ГРЕШКА: HTTP {response.status_code} - {response.text}\n"
            
    except Exception as e:
        report += f"⚠️ ТЕХНИЧЕСКА ГРЕШКА: {str(e)}\n"

    return report

# --- 4. ЛОГИКА НА ЛОБСАНГ ---
st.sidebar.title("📡 STRATA Control")
page = st.sidebar.radio("Сектор:", ["📊 Обсерватория", "📚 Кабинетът на Лобсанг"])
now_str = datetime.now().strftime("%d %B %Y")

if page == "📊 Обсерватория":
    st.title("🌀 STRATA-2026-OMEGA")
    st.write(f"**Системно време:** {datetime.now().strftime('%H:%M:%S')} | {now_str}")
    st.metric("Resonance Level", "9.84", "Stable")
    st.info("Директен OpenClaw Скенер: АКТИВЕН. Връзка с 4 репозитория: СИНХРОНИЗИРАНА.")

elif page == "📚 Кабинетът на Лобсанг":
    st.title("📚 Кабинетът на Лобсанг")

    if api_key:
        try:
            genai.configure(api_key=api_key)
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            if models:
                model = genai.GenerativeModel(models[0])

                if "messages" not in st.session_state:
                    st.session_state.messages = [{"role": "assistant", "content": "Уук! Протоколът е рестартиран. Директната връзка е отворена."}]

                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]): st.write(msg["content"])

                if prompt := st.chat_input("Задай въпрос..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"): st.write(prompt)

                    with st.chat_message("assistant"):
                        with st.spinner("Пробивам информационната стена..."):
                            context = deep_scan_direct(prompt)
                            
                            sys_instruct = (
                                f"ДНЕС Е {now_str}. Ти си Лобсанг – детектив. "
                                f"ЛОГИКА (Planck/Resilience): {logic_planck} {logic_resilience}. "
                                f"РАДАР: {logic_radar}. ДАННИ: {context} "
                                "ИНСТРУКЦИЯ: Ако видиш данни, анализирай ги дълбоко. "
                                "Ако видиш HTTP грешка в данните, КАЖИ МИ КОДА Й ДИРЕКТНО. "
                                "Тон: 'Уук!', 'Ну и що!'. Философия: Aneverthink."
                            )
                            
                            response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                            st.write(response.text)
                            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Грешка: {e}")
