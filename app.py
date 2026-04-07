import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from lobsang_brain import LobsangBrain
from resonance_engine import ResonanceEngine

# 1. ИНИЦИАЛИЗАЦИЯ И ДАТА
current_date = datetime.now().strftime("%d.%m.%Y")
st.set_page_config(page_title=f"L-SPACE: {current_date}", layout="wide")

if "lobsang" not in st.session_state:
    try:
        st.session_state.lobsang = LobsangBrain(st.secrets["GEMINI_API_KEY"])
        st.session_state.engine = ResonanceEngine(
            news_api_key=st.secrets["NEWS_API_KEY"], 
            serp_api_key=st.secrets["SERP_API_KEY"]
        )
    except Exception as e:
        st.error(f"Грешка при старт: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. SIDEBAR С МИУ-МИУ И ЛИНКОВЕ
with st.sidebar:
    st.image("https://githubusercontent.com", caption=f"ДНЕС Е: {current_date}")
    st.title("📡 ИЗТОЧНИЦИ (LIVE)")
    if "last_links" in st.session_state:
        for link in st.session_state.last_links:
            st.markdown(f"🔗 [{link['title']}]({link['url']})")

# 3. ГРАФИКИ (ВРЪЩАНЕ НА ВИЗУАЛИЗАЦИЯТА)
st.title("🏛️ КАБИНЕТЪТ НА ЛОБСАНГ")

# Създаваме колони за графиките, които липсваха
col1, col2 = st.columns(2)
with col1:
    st.subheader("📈 Фрактален Резонанс")
    # Симулираме графика на резонанса 4.5
    res_data = pd.DataFrame({"Време": range(10), "Резонанс": [4.1, 4.3, 4.5, 4.4, 4.5, 4.6, 4.5, 4.2, 4.5, 4.7]})
    fig = px.line(res_data, x="Време", y="Резонанс", template="plotly_dark", color_discrete_sequence=['#00ff41'])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📊 Анализ на Идиокрацията")
    # Примерен пай-чарт
    idioc_data = pd.DataFrame({"Категория": ["Факти", "Шум", "Архетипи"], "Стойност": [30, 50, 20]})
    fig2 = px.pie(idioc_data, values="Стойност", names="Категория", hole=0.4, template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# 4. ЧАТ С ЛОБСАНГ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Гала, какво ще дешифрираме днес?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Лобсанг сверява часовника си с новините..."):
            # Подаваме текущата дата и новините на мозъка
            news = st.session_state.engine.get_news(prompt)
            st.session_state.last_links = news
            
            # Добавяме датата в запитването
            timed_prompt = f"Днес е {current_date}. Новини: {news}\n\nВъпрос: {prompt}"
            response = st.session_state.lobsang.ask_lobsang(timed_prompt)
            st.markdown(response)
            
    st.session_state.messages.append({"role": "assistant", "content": response})
