import streamlit as st
import google.generativeai as genai
from datetime import datetime
import requests
from serpapi import GoogleSearch

# --- 1. CONFIG ---
st.set_page_config(page_title="STRATA-2026-OMEGA | Observatory", page_icon="🌀", layout="wide")

api_key = st.secrets.get("GEMINI_API_KEY")
serp_key = st.secrets.get("SERP_API_KEY")
news_key = st.secrets.get("NEWS_API_KEY")

def fetch_logic(url):
    try:
        raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        res = requests.get(raw_url, timeout=5)
        return res.text[:500] if res.status_code == 200 else ""
    except: return ""

# --- 2. СИНХРОНИЗАЦИЯ НА ЧЕТИРИТЕ РЕПОЗИТОРИЯ ---
# Репозиторий 2 & 3 & 4 (Логическите ядра)
logic_planck = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/planck_iq_calculator.py")
logic_resilience = fetch_logic("https://github.com/Gala-xia/AutonomousNode-Resilience-Framework/blob/main/core/core.py")
logic_shield = fetch_logic("https://github.com/Gala-xia/Core-Resilience-Optimizer/blob/main/core.py")
logic_radar = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/logic/truth_radar.py")

# --- 3. OPENCLAW СКЕНЕР (С ПРОВЕРКА) ---
def deep_scan(query):
    report = "\n--- 🕵️‍♂️ OPENCLAW LIVE EXTRACTION ---\n"
    found = False
    
    if not serp_key:
        return "⚠️ ГРЕШКА: SERP_API_KEY ЛИПСВА В SECRETS!"

    try:
        search = GoogleSearch({"q": query, "api_key": serp_key, "num": 5})
        results = search.get_dict().get("organic_results", [])
        if results:
            for r in results:
                report += f"🔹 {r.get('title')}\n🔗 {r.get('link')}\n\n"
                found = True
        else:
            report += "Скенерът не откри директни съвпадения в Google за тази заявка.\n"
    except Exception as e:
        report += f"⚠️ ГРЕШКА ПРИ СКАНЕРА: {str(e)}\n"

    return report if found else report + "Информационното поле е тихо."

# --- 4. LOBSANG'S OFFICE ---
st.sidebar.title("📡 STRATA Control")
now_str = datetime.now().strftime("%d %B %Y")

st.title("🌀 STRATA-2026-OMEGA | Сектор 0")

if api_key:
    genai.configure(api_key=api_key)
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model = genai.GenerativeModel(models[0])

        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Уук! Четирите репозитория са в синхрон. Какво ще сканираме?"}]

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.write(msg["content"])

        if prompt := st.chat_input("Задай въпрос..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Активирам OpenClaw..."):
                    context = deep_scan(prompt)
                    
                    # ПЪЛЕН КОНТЕКСТ ОТ ВСИЧКИ РЕПОЗИТОРИИ
                    sys_instruct = (
                        f"ДНЕС Е {now_str}. Ти си Лобсанг. "
                        f"ЛОГИКА (Planck/Resilience/Shield): {logic_planck} {logic_resilience} {logic_shield}. "
                        f"РАДАР (TruthRadar): {logic_radar}. "
                        f"ДАННИ ОТ СКЕНЕРА: {context} "
                        "ВАЖНО: Ако скенерът показва грешка или липса на данни, КАЖИ ГО ДИРЕКТНО, не го замаскирай с философия. "
                        "Тон: Проницателен, детективски, 'Уук!'. Философия: Aneverthink."
                    )
                    
                    response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                    st.write(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Системна грешка: {e}")
