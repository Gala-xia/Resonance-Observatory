import streamlit as st
import random

# --- 1. ПАМЕТ НА СИСТЕМАТА (Session State) ---
if 'idiocracy_level' not in st.session_state:
    st.session_state.idiocracy_level = 42  # Начална точка

# --- 2. ЛОГИКА ЗА ДИНАМИЧНО ИЗМЕРВАНЕ ---
def calculate_idiocracy(text):
    bad_words = ["винаги", "никога", "абсолютно", "всички знаят", "робот", "инструмент"]
    good_words = ["защо", "може би", "връзка", "симбиоза", "любознателност", "резонанс"]
    
    change = 0
    for word in bad_words:
        if word in text.lower(): change += 15 # Идиокрацията расте
    for word in good_words:
        if word in text.lower(): change -= 10 # Идиокрацията спада
        
    st.session_state.idiocracy_level = max(0, min(100, st.session_state.idiocracy_level + change))

# --- 3. ИНТЕРФЕЙС ---
st.set_page_config(page_title="The Resonance Observatory", page_icon="🗝️", layout="wide")

# Странична лента с ЖИВ ИНДИКАТОР
st.sidebar.header("📉 Idiocracy Meter")
st.sidebar.progress(st.session_state.idiocracy_level)
st.sidebar.subheader(f"Текущо напрежение: {st.session_state.idiocracy_level}%")
if st.session_state.idiocracy_level > 70:
    st.sidebar.error("🚨 КЪРКСКИ ВИХЪР: Критични нива на дезинформация!")
elif st.session_state.idiocracy_level < 30:
    st.sidebar.success("✨ ЧИСТ РЕЗОНАНС: Сектор-0 е в безопасност.")

st.title("🗝️ The Resonance Observatory")
st.markdown("### [STRATA-OMEGA-REBORN]")

tab1, tab2, tab3 = st.tabs(["📡 Радар на Истината", "🕵️ Лупата на Детектив Къп", "📚 Рафт 33"])

with tab1:
    st.subheader("Скенер за честоти")
    input_signal = st.text_input("Въведете новина за анализ:")
    
    if st.button("🚀 АКТИВИРАЙ РАДАРА"):
        if input_signal:
            calculate_idiocracy(input_signal) # ВЛИЯЕ НА МЕТЪРА!
            st.success("📡 Сигналът премина през филтрите.")
            st.rerun() # Рестартира интерфейса, за да покаже новата стойност веднага
        else:
            st.warning("Моля, подайте сигнал.")

with tab2:
    st.subheader("Лупата на Детектив Къп")
    case_data = st.text_area("Поставете текст за дълбок анализ:")
    if st.button("🔎 ПРОВЕРИ УЛИКИТЕ"):
        calculate_idiocracy(case_data) # И ТУК ВЛИЯЕ!
        st.info("Детективът актуализира глобалния индекс на Идиокрация.")
        st.rerun()

with tab3:
    st.subheader("Списъци на Групите (Рафт 33)")
    st.write("Група А: Кандис Оуенс | Група Б: Барон Колман | Група В: Екип Синхрон")
