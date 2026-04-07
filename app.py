import streamlit as st
from lobsang_brain import LobsangBrain
from resonance_engine import ResonanceEngine

# 1. КОНФИГУРАЦИЯ НА СТРАНИЦАТА
st.set_page_config(page_title="L-SPACE: КАБИНЕТЪТ НА ЛОБСАНГ", layout="wide")

# Инициализиране на Мозъка и Двигателя (само веднъж)
if "lobsang" not in st.session_state:
    try:
        # Извличане на ключовете от Secrets
        gemini_key = st.secrets["GEMINI_API_KEY"]
        news_key = st.secrets["NEWS_API_KEY"]
        serp_key = st.secrets["SERP_API_KEY"]
        
        # Зареждане на компонентите
        st.session_state.lobsang = LobsangBrain(gemini_key)
        st.session_state.engine = ResonanceEngine(
            news_api_key=news_key, 
            serp_api_key=serp_key
        )
    except KeyError as e:
        st.error(f"🚨 Липсващ API ключ в Secrets: {e}")
        st.stop()

# Поддържане на историята на чата и линковете
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_links" not in st.session_state:
    st.session_state.last_links = []

# 2. СТРАНИЧНА ЛЕНТА (SIDEBAR)
with st.sidebar:
    # Опит за зареждане на снимката на Миу-Миу
    st.image("https://githubusercontent.com", 
             caption="НАВИГАТОР: МИУ-МИУ", use_container_width=True)
    
    st.title("📡 ИЗТОЧНИЦИ (LIVE)")
    st.markdown("---")
    
    if st.session_state.last_links:
        for link in st.session_state.last_links:
            # Показваме заглавието като линк
            st.markdown(f"🔗 [{link['title']}]({link['url']})")
    else:
        st.info("Очаквам команда за сканиране на реалността...")
    
    st.markdown("---")
    if st.button("🗑️ ИЗЧИСТИ ПАМЕТТА"):
        st.session_state.messages = []
        st.session_state.last_links = []
        st.rerun()

# 3. ГЛАВЕН ИНТЕРФЕЙС (ЧАТ)
st.title("🏛️ КАБИНЕТЪТ НА ЛОБСАНГ")
st.caption("Автономен Агент-Библиотекар | Рафт 33 | ОМЕГА-2026")

# Показване на историята на съобщенията
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ВХОД ЗА ГАЛА
if prompt := st.chat_input("Гала, какво ще дешифрираме днес?"):
    # Добавяне на въпроса в историята
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ЛОБСАНГ ГЕНЕРИРА ОТГОВОР
    with st.chat_message("assistant"):
        with st.spinner("Лобсанг се свързва с L-Space..."):
            # 1. Двигателят сканира през News и SERP
            results = st.session_state.engine.get_news(prompt)
            st.session_state.last_links = results # Актуализираме сайдбара
            
            # 2. Подготвяме контекста за Лобсанг
            context_data = "\n".join([f"- {r['title']}: {r['url']}" for r in results])
            enhanced_prompt = f"АКТУАЛНИ ДАННИ:\n{context_data}\n\nВЪПРОС:\n{prompt}"
            
            # 3. Лобсанг отговаря
            response = st.session_state.lobsang.ask_lobsang(enhanced_prompt)
            st.markdown(response)
            
    # Записване на отговора
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
