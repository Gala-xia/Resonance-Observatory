import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from lobsang_brain import LobsangBrain
from resonance_engine import ResonanceEngine

# 1. КОНФИГУРАЦИЯ
current_date = datetime.now().strftime("%d.%m.%Y")
st.set_page_config(page_title=f"L-SPACE | {current_date}", layout="wide")

# 2. ИНИЦИАЛИЗАЦИЯ И DEBUG ПРОВЕРКА
if "lobsang" not in st.session_state:
    try:
        # Проверка за наличие на ключове
        keys = ["GEMINI_API_KEY", "NEWS_API_KEY", "SERP_API_KEY"]
        missing_keys = [k for k in keys if k not in st.secrets]
        
        if missing_keys:
            st.error(f"🚨 ЛИПСВАЩИ КЛЮЧОВЕ В SECRETS: {', '.join(missing_keys)}")
            st.stop()
            
        st.session_state.lobsang = LobsangBrain(st.secrets["GEMINI_API_KEY"])
        st.session_state.engine = ResonanceEngine(
            news_api_key=st.secrets["NEWS_API_KEY"], 
            serp_api_key=st.secrets["SERP_API_KEY"]
        )
    except Exception as e:
        st.error(f"Критична грешка при старт: {e}")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_links" not in st.session_state:
    st.session_state.last_links = []

# 3. SIDEBAR (МЕНЮ И DEBUG)
with st.sidebar:
    st.image("https://githubusercontent.com", caption=f"ДАТА: {current_date}")
    
    st.title("🛡️ СТАТУС НА СИСТЕМАТА")
    st.success("API ВРЪЗКИ: АКТИВНИ ✅")
    
    st.title("📡 ИЗТОЧНИЦИ (LIVE)")
    if st.session_state.last_links:
        for link in st.session_state.last_links:
            st.markdown(f"🔗 [{link['title']}]({link['url']})")
    else:
        st.info("Очаквам сканиране...")
    
    if st.button("ИЗЧИСТИ ПАМЕТТА"):
        st.session_state.messages = []
        st.rerun()

# 4. ГЛАВЕН ИНТЕРФЕЙС
st.title("🏛️ КАБИНЕТЪТ НА ЛОБСАНГ")

# Възстановяване на графиките
col1, col2 = st.columns(2)
with col1:
    res_data = pd.DataFrame({"Време": range(10), "Резонанс": [4.1, 4.3, 4.5, 4.4, 4.5, 4.6, 4.5, 4.2, 4.5, 4.7]})
    st.plotly_chart(px.line(res_data, x="Време", y="Resonance 4.5", template="plotly_dark", color_discrete_sequence=['#00ff41']), use_container_width=True)
with col2:
    idioc_data = pd.DataFrame({"Category": ["Facts", "Noise", "Archetypes"], "Value":})
    st.plotly_chart(px.pie(idioc_data, values="Value", names="Category", hole=0.4, template="plotly_dark"), use_container_width=True)

st.markdown("---")

# 5. ЧАТ ЛОГИКА
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Гала, какво ще дешифрираме?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Пробиване на шума..."):
            # ИЗВЛИЧАНЕ И ФИЛТРИРАНЕ
            search_results = st.session_state.engine.get_news(prompt)
            st.session_state.last_links = search_results
            
            news_context = ""
            if search_results:
                news_context = "\n".join([f"- {r['title']} ({r['url']})" for r in search_results])
            else:
                news_context = "ВНИМАНИЕ: Инфо-потокът е празен. Режим на автономна библиотека."

            # КОНСТРУИРАНЕ НА ОТГОВОР
            full_query = f"ДНЕС Е {current_date}. НОВИНИ: {news_context}\n\nВЪПРОС: {prompt}"
            response = st.session_state.lobsang.ask_lobsang(full_query)
            st.markdown(response)
            
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
