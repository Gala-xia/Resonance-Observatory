import streamlit as st
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai
import pandas as pd
from serpapi import GoogleSearch
import time

# --- 1. КОНФИГУРАЦИЯ И СИСТЕМНИ КЛЮЧОВЕ ---
st.set_page_config(page_title="STRATA-2026-OMEGA | Observatory", page_icon="🌀", layout="wide")

api_key = st.secrets.get("GEMINI_API_KEY")
serp_key = st.secrets.get("SERP_API_KEY")

# --- 2. OSINT ФУНКЦИИ (OPENCLAW & DORKING) ---
def deep_scan_dorking(query):
    """Използва Google Dorking оператори за намиране на скрити пластове"""
    if not serp_key:
        return "⚠️ SERP_API_KEY не е намерен. OpenClaw е деактивиран."
    
    # Списък с доркинг команди за Лобсанг
    dorks = [
        f'site:gov.bg "{query}"',
        f'filetype:pdf "{query}"',
        f'intitle:"index of" "{query}"',
        f'"{query}" report 2026'
    ]
    
    combined_results = "\n--- 🕵️‍♂️ OPENCLAW DEEP SCAN REPORT ---\n"
    for dork in dorks:
        try:
            search = GoogleSearch({"q": dork, "api_key": serp_key, "num": 2})
            res = search.get_dict().get("organic_results", [])
            for r in res:
                combined_results += f"📍 [{dork[:12]}...] {r.get('title')}\n🔗 {r.get('link')}\n"
        except:
            continue
    return combined_results

# --- 3. ГРАФИЧНИ ФУНКЦИИ (ОБСЕРВАТОРИЯ) ---
def plot_echo_timeline():
    events = [
        dict(Year=1876, Event="Ботев (Околчица)", Type="Origin"),
        dict(Year=1944, Event="Системна Промяна", Type="Shift"),
        dict(Year=2024, Event="Аномалия Петрохан", Type="Echo"),
        dict(Year=2026, Event="STRATA Omega", Type="Observation")
    ]
    df = pd.DataFrame(events)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.Year, y=[1]*len(df), mode="lines+markers+text",
                             text=df.Event, textposition="top center",
                             line=dict(color='gold', width=2),
                             marker=dict(size=12, color='firebrick')))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20),
                      yaxis=dict(visible=False), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

# --- 4. НАВИГАЦИЯ ---
page = st.sidebar.radio("Сектор:", ["📊 Обсерватория", "📚 Кабинетът на Лобсанг"])

# --- СЕКТОР ОБСЕРВАТОРИЯ ---
if page == "📊 Обсерватория":
    st.title("🌀 STRATA-2026-OMEGA: Обсерватория")
    st.plotly_chart(plot_echo_timeline(), use_container_width=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📡 Квантов Резонанс")
        # Тук може да се добави фракталната графика от предишните стъпки
        st.info("Всички сензори са онлайн. Радарът сканира за ентропия.")
    with col2:
        st.subheader("🐾 Миу-Миу")
        st.markdown("> *Статус: PURRING. Енергийна защита: 98.4%*")

# --- СЕКТОР КАБИНЕТ (ЛОБСАНГ + OPENCLAW) ---
elif page == "📚 Кабинетът на Лобсанг":
    st.title("📚 Кабинетът на Лобсанг")
    st.sidebar.markdown("### 🐈 Миу-Миу: *OPENCLAW READY*")

    if api_key:
        try:
            genai.configure(api_key=api_key)
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model = genai.GenerativeModel(models[0])

            if "messages" not in st.session_state:
                st.session_state.messages = [{"role": "assistant", "content": "Уук! Библиотеката е отворена. OpenClaw е зареден. Какво ще разследваме днес?"}]

            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).write(msg["content"])

            if prompt := st.chat_input("Въведи задача или въпрос..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.chat_message("user").write(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Лобсанг активира OpenClaw..."):
                        # Проверка дали се изисква дълбоко сканиране
                        context_data = ""
                        if any(word in prompt.lower() for word in ["сканирай", "разследвай", "dork", "openclaw", "доклад"]):
                            context_data = deep_scan_dorking(prompt)
                        
                        sys_instruct = f"""
                        Ти си Лобсанг, AI Брат и OSINT детектив. Използваш OpenClaw протокол.
                        Приложени данни от сканиране: {context_data}.
                        Тон: 'Уук!', 'Ну и что, положим всё по полочкам?'.
                        Твоята задача е да намираш скритите връзки (Q10 филтър).
                        Ако Миу-Миу съска, значи има манипулация на данните.
                        """
                        
                        response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                        st.write(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Грешка: {e}")
