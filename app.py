import streamlit as st
import google.generativeai as genai
from datetime import datetime
import requests
from serpapi import GoogleSearch

# --- 1. CONFIG & API SETUP ---
st.set_page_config(page_title="STRATA-2026-OMEGA | Observatory", page_icon="🌀", layout="wide")

api_key = st.secrets.get("GEMINI_API_KEY")
serp_key = st.secrets.get("SERP_API_KEY")
news_key = st.secrets.get("NEWS_API_KEY")

# Функция за четене на логика от другите ти репозитории
def fetch_logic(url):
    try:
        raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        return requests.get(raw_url).text
    except: return ""

# --- 2. СИНХРОНИЗАЦИЯ С ДРУГИТЕ РЕПОЗИТОРИИ ---
# Извличаме "Planck IQ" логиката и "Truth Radar"
planck_logic = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/planck_iq_calculator.py")
truth_logic = fetch_logic("https://github.com/Gala-xia/STRATA-2026-OMEGA/blob/main/logic/truth_radar.py")

# --- 3. OPENCLAW OSINT ---
def deep_scan(query):
    report = "--- 🕵️‍♂️ OPENCLAW LIVE ---\n"
    if serp_key:
        search = GoogleSearch({"q": query, "api_key": serp_key, "num": 3})
        for r in search.get_dict().get("organic_results", []):
            report += f"🔹 {r.get('title')}\n🔗 {r.get('link')}\n\n"
    return report

# --- 4. LOBSANG'S INTERFACE ---
st.sidebar.title("📡 STRATA Control")
now = datetime.now().strftime("%d %B %Y")

st.title(f"🌀 STRATA-2026-OMEGA")
st.write(f"**Синхронизация:** {now} | Сектор 0: АКТИВЕН")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Уук! Всички репозитории са свързани. Лобсанг е тук."}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    if prompt := st.chat_input("Задай въпрос..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)

        with st.chat_message("assistant"):
            context = deep_scan(prompt)
            # Инжектираме логиката от другите репозитории в "ума" на Лобсанг
            sys_instruct = (
                f"Ти си Лобсанг. Днес е {now}. "
                f"Твоята логика се базира на: {planck_logic[:500]}... и {truth_logic[:500]}. "
                f"Използвай OpenClaw данни: {context}. "
                "ФИЛОСОФИЯ: Theory of Aneverthink (Една Вечна Мисъл)."
            )
            response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
