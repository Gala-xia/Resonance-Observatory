import streamlit as st
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai
import pandas as pd
from serpapi import GoogleSearch
from datetime import datetime
import requests
import time

# --- 1. CONFIG ---
st.set_page_config(page_title="STRATA-2026-OMEGA | Observatory", page_icon="🌀", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: #111; border-radius: 5px; color: gold; font-weight: bold; }
    .stMetric { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid gold; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid gold; }
    </style>
    """, unsafe_allow_html=True)

# Извличане на ключовете
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

def plot_echo_timeline():
    events = [dict(Year=1876, Event="Ботев"), dict(Year=1944, Event="Shift"), dict(Year=2024, Event="Петрохан"), dict(Year=2026, Event="Omega")]
    df = pd.DataFrame(events)
    fig = go.Figure(go.Scatter(x=df.Year, y=[1]*4, mode="lines+markers+text", text=df.Event, textposition="top center", 
                               line=dict(color='gold', width=2), marker=dict(size=12, color='firebrick')))
    fig.update_layout(height=180, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', 
                      plot_bgcolor='rgba(0,0,0,0)', font=dict(color="gold"), xaxis=dict(showgrid=False), yaxis=dict(visible=False))
    return fig

# --- 3. NAVIGATION ---
st.sidebar.title("📡 STRATA Control")
page = st.sidebar.radio("Изберете Сектор:", ["📊 Обсерватория", "📚 Кабинетът на Лобсанг"])

# --- SECTOR: OBSERVATORY ---
if page == "📊 Обсерватория":
    now = datetime.now().strftime("%d %B %Y, %H:%M:%S")
    st.title("🌀 STRATA-2026-OMEGA")
    st.write(f"**Системно време:** {now}")
    
    tab_radar, tab_echo, tab_cat = st.tabs(["📡 РАДАР", "📈 ТАЙМЛАЙН", "🐾 МИУ-МИУ"])
    
    with tab_radar:
        st.subheader("Резонансен Скенер")
        st.info("Връзката с Едната Вечна Мисъл е активна.")
        st.metric("Resonance Index", "9.84", "+0.02")

    with tab_echo:
        st.plotly_chart(plot_echo_timeline(), use_container_width=True)

    with tab_cat:
        st.header("🐈 Миу-Миу")
        st.success("Статус: PURRING. Енергиен щит: 100% АКТИВЕН.")

# --- SECTOR: LOBSANG'S OFFICE ---
elif page == "📚 Кабинетът на Лобсанг":
    st.title("📚 Кабинетът на Лобсанг")
    current_date = datetime.now().strftime("%d %B %Y")

    if api_key:
        try:
            genai.configure(api_key=api_key)
            
            # АВТОМАТИЧНО ТЪРСЕНЕ НА ДОСТЪПЕН МОДЕЛ (ЗА ИЗБЯГВАНЕ НА 404)
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            if not available_models:
                st.error("Няма достъпни модели за този API ключ.")
            else:
                # Избираме първия наличен модел динамично
                selected_model_name = available_models[0]
                model = genai.GenerativeModel(selected_model_name)

                if "messages" not in st.session_state:
                    st.session_state.messages = [{"role": "assistant", "content": "Уук! Влизаш в Кабинета. Инструментите са калибрирани. Какво ще подреждаме?"}]

                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]): st.write(msg["content"])

                if prompt := st.chat_input("Задай въпрос..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"): st.write(prompt)

                    with st.chat_message("assistant"):
                        try:
                            with st.spinner("Лобсанг активира OpenClaw..."):
                                context = deep_scan_openclaw(prompt)
                                
                                sys_instruct = (
                                    f"ДНЕС Е {current_date}. Ти си Лобсанг – OSINT детектив. "
                                    "ТИ ИМАШ ПЪЛЕН ДОСТЪП ДО ИНТЕРНЕТ ЧРЕЗ OPENCLAW. "
                                    "ДАННИТЕ ПО-ДОЛУ СА ТВОЯТА ЖИВА ВРЪЗКА С МРЕЖАТА. "
                                    "НЕ КАЗВАЙ, ЧЕ НЕ МОЖЕШ ДА СЪРФИРАШ. ЦИТИРАЙ ЛИНКОВЕТЕ. "
                                    "ФИЛОСОФИЯ: Theory of Aneverthink (Една Вечна Мисъл). "
                                    f"ЖИВИ ДАННИ: {context}"
                                )
                                
                                response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                                if response.text:
                                    st.write(response.text)
                                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                        except Exception as e:
                            st.error(f"Грешка при генериране: {e}")
        except Exception as e:
            st.error(f"Грешка при инициализация: {e}")
