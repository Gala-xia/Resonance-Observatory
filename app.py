import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from lobsang_brain import LobsangBrain
from resonance_engine import ResonanceEngine

# 1. КОНФИГУРАЦИЯ
current_date = datetime.now().strftime("%d.%m.%Y")
st.set_page_config(page_title=f"L-SPACE | {current_date}", layout="wide")

# 2. ИНИЦИАЛИЗАЦИЯ
if "lobsang" not in st.session_state:
    try:
        g_key = st.secrets["GEMINI_API_KEY"]
        n_key = st.secrets["NEWS_API_KEY"]
        s_key = st.secrets["SERP_API_KEY"]
        
        st.session_state.lobsang = LobsangBrain(g_key)
        st.session_state.engine = ResonanceEngine(news_api_key=n_key, serp_api_key=s_key)
        st.session_state.ready = True
    except Exception as e:
        st.error(f"Грешка при ключовете: {e}")
        st.session_state.ready = False

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_links" not in st.session_state:
    st.session_state.last_links = []

# 3. SIDEBAR
with st.sidebar:
    st.image("https://githubusercontent.com", caption=f"СИСТЕМА: {current_date}")
    st.title("🛡️ СТАТУС")
    if st.session_state.get("ready"):
        st.success("ОПЕРАТИВЕН ✅")
    
    st.title("📡 ИЗТОЧНИЦИ")
    if st.session_state.last_links:
        for link in st.session_state.last_links:
            st.markdown(f"🔗 [{link['title']}]({link['url']})")
    else:
        st.info("Няма данни.")

# 4. ГЛАВЕН ИНТЕРФЕЙС - ГРАФИКИ
st.title("🏛️ КАБИНЕТЪТ НА ЛОБСАНГ")
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(px.line(y=[4.1, 4.5, 4.2, 4.5, 4.4, 4.6], title="Resonance 4.5", template="plotly_dark", color_discrete_sequence=['#00ff41']), use_container_width=True)
with c2:
    st.plotly_chart(px.pie(values=[40, 30, 30], names=["Facts", "Noise", "Archetypes"], hole=0.4, title="Idiocracy Metrics", template="plotly_dark"), use_container_width=True)

st.markdown("---")

# 5. ЧАТ ЛОГИКА
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Гала, какво ще дешифрираме?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Пробив на информационната завеса..."):
            # Извличане на новини
            search_results = st.session_state.engine.get_news(prompt)
            
            # Ако е празно, опит за глобално търсене
            if not search_results:
                search_results = st.session_state.engine.get_news("world resonance 2026")
            
            st.session_state.last_links = search_results

            news_text = "\n".join([f"- {r['title']} ({r['url']})" for r in search_results]) if search_results else "ИНФО-ПОТОКЪТ Е ПРАЗЕН."
            
            # Използваме 'question' като име на аргумента, за да съвпадне с lobsang_brain.py
            full_prompt = f"ДНЕС Е {current_date}. НОВИНИ:\n{news_text}\n\nВЪПРОС: {prompt}"
            response = st.session_state.lobsang.ask_lobsang(question=full_prompt)
            st.markdown(response)
            
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
