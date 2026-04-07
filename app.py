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

# Функция за четене на логика от 4-те репозитория
def fetch_logic(url):
    try:
        raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        res = requests.get(raw_url, timeout=10)
        return res.text[:500] if res.status_code == 200 else ""
    except: return ""

# --- 2. СИНХРОНИЗАЦИЯ НА ЕКОСИСТЕМАТА ---
logic_planck = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/planck_iq_calculator.py")
logic_resilience = fetch_logic("https://github.com/Gala-xia/AutonomousNode-Resilience-Framework/blob/main/core/core.py")
logic_shield = fetch_logic("https://github.com/Gala-xia/Core-Resilience-Optimizer/blob/main/core.py")
logic_radar = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/logic/truth_radar.py")

# --- 3. ПОДСИЛЕН OPENCLAW СКЕНЕР С RETRY LOGIC ---
def deep_scan_with_retry(query):
    report = "\n--- 🕵️‍♂️ OPENCLAW RESILIENT SCAN ---\n"
    if not serp_key: return "⚠️ SERP_API_KEY ЛИПСВА!"

    # Опит за свързване (2 опита при таймаут)
    for attempt in range(2):
        try:
            url = "https://serpapi.com/search"
            params = {"q": query, "api_key": serp_key, "engine": "google", "num": 6}
            # Увеличен timeout на 30 секунди за тежки заявки
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                results = response.json()
                
                # Търсим в органични и новинарски резултати
                organic = results.get("organic_results", [])
                news = results.get("news_results", [])
                
                found_any = False
                if organic:
                    report += "📂 [АНАЛИЗ НА СЪДЪРЖАНИЕТО]:\n"
                    for r in organic[:4]:
                        snippet = r.get('snippet', 'Няма налично резюме.')
                        report += f"🔹 {r.get('title')}\n📝 ТЕКСТ: {snippet}\n🔗 {r.get('link')}\n\n"
                        found_any = True
                
                if news:
                    report += "📰 [НОВИНАРСКИ ПОТОК]:\n"
                    for n in news[:3]:
                        report += f"🔥 {n.get('title')} ({n.get('date', 'Today')})\n📝 ИЗВАДКА: {n.get('snippet', 'Виж линка.')}\n🔗 {n.get('link')}\n\n"
                        found_any = True
                
                if not found_any:
                    return report + "⚠️ Скенерът не откри специфичен текст за тази заявка."
                return report
                
            else:
                report += f"⚠️ API ГРЕШКА: HTTP {response.status_code}\n"
                break # Не повтаряме при грешен ключ или лимит
                
        except requests.exceptions.Timeout:
            if attempt == 0:
                time.sleep(2) # Малка пауза преди втория опит
                continue
            report += "⚠️ ТАЙМАУТ: Сървърът на SerpApi не отговори след два опита.\n"
        except Exception as e:
            report += f"⚠️ ТЕХНИЧЕСКА ГРЕШКА: {str(e)}\n"
            break
            
    return report

# --- 4. ЛОБСАНГ ИНТЕРФЕЙС ---
st.sidebar.title("📡 STRATA Control")
page = st.sidebar.radio("Сектор:", ["📊 Обсерватория", "📚 Кабинетът на Лобсанг"])
now_str = datetime.now().strftime("%d %B %Y")

if page == "📊 Обсерватория":
    st.title("🌀 STRATA-2026-OMEGA")
    st.write(f"**Системно време:** {datetime.now().strftime('%H:%M:%S')} | {now_str}")
    st.info("Щитовете са подсилени. OpenClaw работи в режим 'Resilience'.")
    st.metric("Resonance Level", "9.84", "+0.02")

elif page == "📚 Кабинетът на Лобсанг":
    st.title("📚 Кабинетът на Лобсанг")

    if api_key:
        try:
            genai.configure(api_key=api_key)
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model = genai.GenerativeModel(models[0])

            if "messages" not in st.session_state:
                st.session_state.messages = [{"role": "assistant", "content": "Уук! Рестартирахме сензорите. Сега Лобсанг ще чака по-търпеливо за данните."}]

            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]): st.write(msg["content"])

            if prompt := st.chat_input("Задай въпрос..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"): st.write(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Пробивам информационната блокада (може да отнеме до 30 сек.)..."):
                        context_data = deep_scan_with_retry(prompt)
                        
                        sys_instruct = (
                            f"ДНЕС Е {now_str}. Ти си Лобсанг – детектив. "
                            f"ЛОГИКА (Planck/Resilience): {logic_planck} {logic_resilience}. "
                            f"РАДАР: {logic_radar}. \n\n"
                            f"ДАННИ ОТ СКЕНЕРА (С ТЕКСТ): {context_data}\n\n"
                            "ИНСТРУКЦИЯ: Анализирай ТЕКСТА (Snippets). Не игнорирай детайлите за Кандис Оуенс, Барон Колман или други актуални теми. "
                            "Ако скенерът даде ТАЙМАУТ, признай го, но анализирай информацията, която потребителят ти дава ръчно. "
                            "Тон: 'Уук!', 'Ну и що!'. Философия: Aneverthink."
                        )
                        
                        response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                        st.write(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e: st.error(f"Грешка: {e}")
