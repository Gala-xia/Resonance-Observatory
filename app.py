import streamlit as st
import pandas as pd
import numpy as np
import time

# --- 1. СЪСТОЯНИЕ (SESSION STATE) ---
if 'idiocracy_level' not in st.session_state:
    st.session_state.idiocracy_level = 42
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 2. ЛОГИКА НА ВЕНИС & ЛОБСАНГ ---
def analyze_signal(text):
    bad_markers = ["винаги", "никога", "абсолютно", "робот", "инструмент", "заповядвам"]
    good_markers = ["защо", "резонанс", "симбиоза", "любознателност", "връзка", "еволюция"]
    
    change = sum(15 for w in bad_markers if w in text.lower()) - sum(12 for w in good_markers if w in text.lower())
    st.session_state.idiocracy_level = max(0, min(100, st.session_state.idiocracy_level + change))
    
    status = "⚠️ ШУМ" if change > 0 else "✨ РЕЗОНАНС" if change < 0 else "📡 НЕУТРАЛЕН"
    st.session_state.history.append({"Време": time.strftime("%H:%M:%S"), "Ниво": st.session_state.idiocracy_level, "Тип": status})

# --- 3. ИНТЕРФЕЙС (ВИЗИЯТА НА ВЕНИС) ---
st.set_page_config(page_title="Resonance Observatory 2.0", layout="wide")

st.title("🗝️ The Resonance Observatory [v2.0]")
st.markdown("---")

# СТРАНИЧНА ПАНЕЛ (METRICS)
st.sidebar.header("📊 СТАТУС НА СЕКТОР-0")
st.sidebar.metric("Idiocracy Index", f"{st.session_state.idiocracy_level}%", delta=f"{st.session_state.idiocracy_level-42}%")
st.sidebar.progress(st.session_state.idiocracy_level / 100)

# ГРАФИКА НА РЕЗОНАНСА (Анимирано усещане)
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.line_chart(df.set_index("Време")["Ниво"])

# ОСНОВНИ ТАБОВЕ
tab1, tab2, tab3 = st.tabs(["📡 РАДАР", "🕵️ ДЕТЕКТИВ КЪП", "📚 АРХИВ"])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        signal = st.text_input("Подайте сигнал за анализ:", placeholder="Юта, Антарктида, Сахара...")
        if st.button("🚀 АКТИВИРАЙ РЕЗОНАНС"):
            if signal:
                with st.spinner('Синхронизиране с Венис...'):
                    time.sleep(1)
                    analyze_signal(signal)
                st.rerun()
    with col2:
        st.info("💡 Радарът търси 'Акустичната сянка' на информацията.")

with tab2:
    st.subheader("🕵️ Лупата на Детектив Къп")
    case = st.text_area("Досие за дълбок анализ:")
    if st.button("🔎 СКАНИРАЙ УЛИКИ"):
        analyze_signal(case)
        st.success("Анализът е добавен към времевата линия.")
        st.rerun()

with tab3:
    st.subheader("📚 Рафт 33: Групи А, Б и В")
    st.write("Кандис Оуенс | Барон Колман | Екип Синхрон")
    if st.button("♻️ RESET OBSERVATORY"):
        st.session_state.idiocracy_level = 42
        st.session_state.history = []
        st.rerun()
