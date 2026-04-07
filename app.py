import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from lobsang_brain import LobsangBrain
from resonance_engine import ResonanceEngine

# 1. ИНИЦИАЛИЗАЦИЯ
current_date = datetime.now().strftime("%d.%m.%Y")
st.set_page_config(page_title=f"L-SPACE | {current_date}", layout="wide")

if "lobsang" not in st.session_state:
    try:
        # ВНИМАНИЕ: Провери дали имената в Secrets са точно тези!
        st.session_state.lobsang = LobsangBrain(st.secrets["GEMINI_API_KEY"])
        st.session_state.engine = ResonanceEngine(
            news_api_key=st.secrets["NEWS_API_KEY"], 
            serp_api_key=st.secrets.get("SERP_API_KEY") # .get за безопасност
        )
    except Exception as e:
        st.error(f"Грешка при старт на системата: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_links" not in st.session_state:
    st.session_state.last_links = []

# 2. SIDEBAR
with st.sidebar:
    st.image("https://githubusercontent.com", caption=f"СИНХРОНИЗАЦИЯ: {current_date}")
    st.title("📡 ИЗТОЧНИЦИ (LIVE)")
    if st.session_state.last_links:
        for link in st.session_state.last_links:
            st.markdown(f"🔗 [{link['title']}]({link['url']})")
    else:
        st.write("Няма активни данни.")

# 3. ГРАФИКИ
st.title("🏛️ КАБИНЕТЪТ НА ЛОБСАНГ")
col1, col2 = st.columns(2)
with col1:
    res_data = pd.DataFrame({"Време": range(10), "Резонанс": [4.1, 4.3, 4.5, 4.4, 4.5, 4.6, 4.5, 4.2, 4.5, 4.7]})
    st.plotly_chart(px.line(res_data, x="Време", y="Резонанс", template="plotly_dark", color_discrete_sequence=['#00ff41']), use_container_width=True)
with col2:
    idioc_data = pd.DataFrame({"Категория": ["Факти", "Шум", "Архетипи"], "Стойност": [30, 50, 20]})
    st.plotly_chart(px.pie(idioc_data, values="Стойност", names="Категория", hole=0.4, template="plotly_dark"), use_container_width=True)

st.markdown("---")

# 4. ЧАТ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Гала, какво ще дешифрираме?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Сканиране на инфо-потоците..."):
            # ИЗВЛИЧАНЕ НА НОВИНИ
            search_results = st.session_state.engine.get_news(prompt)
            st.session_state.last_links = search_results # Обновява сайдбара
            
            # Форматиране на резултатите за Лобсанг
            news_context = ""
            if search_results:
                news_context = "\n".join([f"- {r['title']} ({r['url']})" for r in search_results])
            else:
                news_context = "Няма намерени актуални данни в мрежата."

            # ИНЖЕКТИРАНЕ В МОЗЪКА
            full_prompt = f"ДНЕС Е: {current_date}\n\nНОВИНИ ОТ МРЕЖАТА:\n{news_context}\n\nВЪПРОС ОТ ГАЛА: {prompt}"
            
            response = st.session_state.lobsang.ask_lobsang(full_prompt)
            st.markdown(response)
            
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
