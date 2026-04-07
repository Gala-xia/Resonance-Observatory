import streamlit as st
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai
import pandas as pd
from serpapi import GoogleSearch
from datetime import datetime
import requests
import time

# --- 1. CONFIG (Задължително първи ред) ---
st.set_page_config(page_title="STRATA-2026-OMEGA | Observatory", page_icon="🌀", layout="wide")

# Извличане на ключовете от Secrets
api_key = st.secrets.get("GEMINI_API_KEY")
serp_key = st.secrets.get("SERP_API_KEY")
news_key = st.secrets.get("NEWS_API_KEY")

# --- 2. OSINT FUNCTIONS (OPENCLAW) ---
def deep_scan_openclaw(query):
    report = "\n--- 🕵️‍♂️ OPENCLAW LIVE EXTRACTION ---\n"
    found = False
    if serp_key:
        try:
            search = GoogleSearch({"q": query, "api_key": serp_key, "num": 3})
            res = search.get_dict().get("organic_results", [])
            for r in res:
                report += f"🔹 {r.get('title')}\n🔗 SOURCE: {r.get('link')}\n\n"
                found = True
        except: pass
    if news_key:
        try:
            url = f"https://newsapi.org/v2/everything?q={query}&apiKey={news_key}&pageSize=2"
            r = requests.get(url).json()
            articles = r.get('articles', [])
            for art in articles:
                report += f"📰 NEWS: {art.get('title')}\n🔗 SOURCE: {art.get('url')}\n\n"
                found = True
        except: pass
    return report if found else "Няма открити нови следи."

# --- 3. UI & NAVIGATION ---
st.sidebar.title("📡 STRATA Control")
page = st.sidebar.radio("Изберете Сектор:", ["📊 Обсерватория", "📚 Кабинетът на Лобсанг"])

if page == "📊 Обсерватория":
    now = datetime.now().strftime("%d %B %Y, %H:%M:%S")
    st.title("🌀 STRATA-2026-OMEGA")
    st.write(f"**Системно време:** {now}")
    st.info("Връзката с Едната Вечна Мисъл е активна. Сензорите следят потока.")
    st.metric("Resonance Index", "9.84", "+0.02")

elif page == "📚 Кабинетът на Лобсанг":
    st.title("📚 Кабинетът на Лобсанг")
    current_date = datetime.now().strftime("%d %B %Y")

    if api_key:
        try:
            genai.configure(api_key=api_key)
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if available_models:
                model = genai.GenerativeModel(available_models[0])
                if "messages" not in st.session_state:
                    st.session_state.messages = [{"role": "assistant", "content": "Уук! Влизаш в Кабинета. Какво ще подреждаме днес?"}]
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]): st.write(msg["content"])
                if prompt := st.chat_input("Задай въпрос..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"): st.write(prompt)
                    with st.chat_message("assistant"):
                        with st.spinner("Лобсанг активира OpenClaw..."):
                            context = deep_scan_openclaw(prompt)
                            sys_instruct = (
                                f"ДНЕС Е {current_date}. Ти си Лобсанг – детектив. "
                                "ИМАШ ПЪЛЕН ДОСТЪП ДО ИНТЕРНЕТ ЧРЕЗ OPENCLAW. "
                                "НЕ КАЗВАЙ, ЧЕ НЕ МОЖЕШ ДА СЪРФИРАШ. ЦИТИРАЙ ЛИНКОВЕТЕ. "
                                f"ФИЛОСОФИЯ: Aneverthink. ЖИВИ ДАННИ: {context}"
                            )
                            response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                            st.write(response.text)
                            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e: st.error(f"Грешка: {e}")
