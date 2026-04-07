import streamlit as st
import google.generativeai as genai
from datetime import datetime
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. CONFIG ---
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

def fetch_logic(url):
    try:
        raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        res = requests.get(raw_url, timeout=5)
        return res.text[:500] if res.status_code == 200 else ""
    except: return ""

# --- 2. СИНХРОНИЗАЦИЯ НА 4-ТЕ РЕПОЗИТОРИЯ ---
logic_planck = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/planck_iq_calculator.py")
logic_resilience = fetch_logic("https://github.com/Gala-xia/AutonomousNode-Resilience-Framework/blob/main/core/core.py")
logic_shield = fetch_logic("https://github.com/Gala-xia/Core-Resilience-Optimizer/blob/main/core.py")
logic_radar = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/logic/truth_radar.py")

# --- 3. OPENCLAW CONTENT SCANNER (ВИЖДА ТЕКСТА) ---
def deep_scan_with_text(query):
    report = "\n--- 🕵️‍♂️ OPENCLAW DEEP CONTENT SCAN ---\n"
    if not serp_key: return "⚠️ SERP_API_KEY ЛИПСВА!"

    try:
        url = "https://serpapi.com/search"
        # Търсим едновременно в Organic и News за максимална плътност
        params = {"q": query, "api_key": serp_key, "engine": "google", "num": 5}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            results = response.json()
            
            # А. Органични резултати със Snippets (текст)
            organic = results.get("organic_results", [])
            if organic:
                report += "📂 [АНАЛИЗ НА СЪДЪРЖАНИЕТО]:\n"
                for r in organic:
                    snippet = r.get('snippet', 'Няма налично резюме.')
                    report += f"🔹 ЗАГЛАВИЕ: {r.get('title')}\n📝 ТЕКСТ: {snippet}\n🔗 ЛИНК: {r.get('link')}\n\n"
            
            # Б. Новинарски резултати
            news = results.get("news_results", [])
            if news:
                report += "📰 [НОВИНАРСКИ ПОТОК]:\n"
                for n in news:
                    report += f"🔥 {n.get('title')} ({n.get('date')})\n📝 ИЗВАДКА: {n.get('snippet', 'Виж линка за детайли.')}\n🔗 {n.get('link')}\n\n"
        else:
            report += f"⚠️ API ГРЕШКА: {response.status_code}\n"
    except Exception as e:
        report += f"⚠️ ГРЕШКА: {str(e)}\n"

    return report

# --- 4. ЛОБСАНГ ИНТЕРФЕЙС ---
st.sidebar.title("📡 STRATA Control")
page = st.sidebar.radio("Сектор:", ["📊 Обсерватория", "📚 Кабинетът на Лобсанг"])
now_str = datetime.now().strftime("%d %B %Y")

if page == "📊 Обсерватория":
    st.title("🌀 STRATA-2026-OMEGA")
    st.write(f"**Системно време:** {datetime.now().strftime('%H:%M:%S')} | {now_str}")
    st.info("Всички 4 репозитория са онлайн. OpenClaw вижда текстови потоци.")

elif page == "📚 Кабинетът на Лобсанг":
    st.title("📚 Кабинетът на Лобсанг")

    if api_key:
        try:
            genai.configure(api_key=api_key)
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model = genai.GenerativeModel(models[0])

            if "messages" not in st.session_state:
                st.session_state.messages = [{"role": "assistant", "content": "Уук! Сега вече виждам и ТЕКСТА зад линковете. Какво ще анализираме?"}]

            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]): st.write(msg["content"])

            if prompt := st.chat_input("Задай въпрос..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"): st.write(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Скенерът отваря досиетата..."):
                        context_data = deep_scan_with_text(prompt)
                        
                        sys_instruct = (
                            f"ДНЕС Е {now_str}. Ти си Лобсанг – OSINT анализатор. "
                            f"ЛОГИКА (Planck/Resilience): {logic_planck} {logic_resilience}. "
                            f"РАДАР: {logic_radar}. \n\n"
                            f"ТЕКУЩИ ДАННИ (С ТЕКСТ): {context_data}\n\n"
                            "ИНСТРУКЦИЯ: Използвай предоставения ТЕКСТ (Snippets), за да направиш истински анализ. "
                            "Не просто изброявай линкове! Кажи какво СЕ СЛУЧВА според текста. "
                            "Ако няма текст, кажи го директно. Тон: Проницателен, 'Уук!', 'Ну и що!'."
                        )
                        
                        response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                        st.write(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e: st.error(f"Грешка: {e}")
