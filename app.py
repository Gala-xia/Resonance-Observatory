import streamlit as st
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai
import pandas as pd
from serpapi import GoogleSearch
import time

# --- 1. CONFIG & KEYS ---
st.set_page_config(page_title="STRATA-2026-OMEGA | Observatory", page_icon="🌀", layout="wide")

# CSS за по-добра визия (Злато върху черно)
st.markdown("""
    <style>
    .main { background-color: #000000; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #111; border-radius: 5px; color: gold; }
    .stMetric { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid gold; }
    </style>
    """, unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY")
serp_key = st.secrets.get("SERP_API_KEY")

# --- 2. FUNCTIONS ---
def deep_scan_dorking(query):
    if not serp_key: return "⚠️ SERP_API_KEY Missing."
    dorks = [f'site:gov.bg "{query}"', f'filetype:pdf "{query}"', f'"{query}" report 2026']
    results = "\n--- 🕵️‍♂️ OPENCLAW REPORT ---\n"
    for dork in dorks:
        try:
            search = GoogleSearch({"q": dork, "api_key": serp_key, "num": 1})
            res = search.get_dict().get("organic_results", [])
            for r in res: results += f"📍 {r.get('title')}\n🔗 {r.get('link')}\n"
        except: continue
    return results

def plot_echo_timeline():
    events = [dict(Year=1876, Event="Ботев"), dict(Year=1944, Event="Shift"), dict(Year=2024, Event="Петрохан"), dict(Year=2026, Event="Omega")]
    df = pd.DataFrame(events)
    fig = go.Figure(go.Scatter(x=df.Year, y=[1]*4, mode="lines+markers+text", text=df.Event, textposition="top center", line=dict(color='gold')))
    fig.update_layout(height=200, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="gold"), xaxis=dict(showgrid=False), yaxis=dict(visible=False))
    return fig

# --- 3. NAVIGATION ---
page = st.sidebar.radio("Сектор:", ["📊 Обсерватория", "📚 Кабинетът на Лобсанг"])

# --- SECTOR: OBSERVATORY ---
if page == "📊 Обсерватория":
    st.title("🌀 STRATA-2026-OMEGA")
    
    # ТАБОВЕ ЗА ОРГАНИЗАЦИЯ (БЕЗ ПРИПОКРИВАНЕ)
    tab_radar, tab_echo, tab_cat = st.tabs(["📡 РАДАР", "📈 ТАЙМЛАЙН", "🐾 МИУ-МИУ"])
    
    with tab_radar:
        col_r1, col_r2 = st.columns([2, 1])
        with col_r1:
            st.subheader("Резонансен Скенер")
            st.info("Радарът е калибриран. Всички системи са в баланс.")
        with col_r2:
            st.metric("Resonance Index", "9.84", "+0.2")

    with tab_echo:
        st.plotly_chart(plot_echo_timeline(), use_container_width=True)
        st.write("Вертикална синхронизация между 1876 и 2026 е потвърдена.")

    with tab_cat:
        st.header("🐈 Миу-Миу")
        st.success("Статус: PURRING. Ентропиен щит: АКТИВЕН.")
        st.write("Котката спи върху главния възел. Всяка манипулация на данните ще бъде засечена.")

# --- SECTOR: LOBSANG'S OFFICE ---
elif page == "📚 Кабинетът на Лобсанг":
    st.title("📚 Кабинетът на Лобсанг")
    
    # ПАМЕТ: Бутон за сваляне на историята
    if "messages" in st.session_state:
        chat_log = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        st.sidebar.download_button("📥 Свали Протокола", chat_log, "lobsang_chat.txt")

    if api_key:
        try:
            genai.configure(api_key=api_key)
            # Избираме модела внимателно
            model = genai.GenerativeModel('gemini-1.5-flash')

            if "messages" not in st.session_state:
                st.session_state.messages = [{"role": "assistant", "content": "Уук! Влизаш в Кабинета. Миу-Миу току-що провери кабелите. Какво ще подреждаме?"}]

            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).write(msg["content"])

            if prompt := st.chat_input("Въведи задача..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.chat_message("user").write(prompt)

                with st.chat_message("assistant"):
                    try:
                        with st.spinner("Лобсанг прелиства рафтовете..."):
                            context = deep_scan_dorking(prompt) if "сканирай" in prompt.lower() else ""
                            sys_instruct = f"Ти си Лобсанг. Тон: Уук! Ну и что! Библиотекар и OSINT детектив. Данни: {context}"
                            response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                            st.write(response.text)
                            st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        if "429" in str(e):
                            st.warning("⚠️ Квотата е изчерпана! Лобсанг трябва да си поеме дъх. Моля, опитай пак след 30 секунди.")
                        else:
                            st.error(f"Грешка: {e}")
        except Exception as e:
            st.error(f"Грешка при връзката: {e}")
