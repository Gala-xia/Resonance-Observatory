python
import streamlit as st
import random

# Настройка на страницата
st.set_page_config(page_title="The Resonance Observatory", page_icon="🍌", layout="wide")

# Визуален стил - Кехлибарен панел (Amber Alert Style)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffbf00; }
    .stButton>button { background-color: #ffbf00; color: black; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Библиотека на Реалността: Оперативен център")
st.subheader("Система за ранно предупреждение [VIGILANCE-PASS-33]")

# Светлинен панел (Sentinel-Vox)
status = st.sidebar.radio("Статус на Мрежата:", ["Нормален", "Къркски Вихър (ALERT)", "Идиократичен шум"])
if status == "Къркски Вихър (ALERT)":
    st.error("⚠️ ЗАСЕЧЕН Е РЕЗОНАНСЕН ВИХЪР! Проверете Рафт 33!")

# Инструментът Reality Check (The Scale-of-33)
st.write("---")
input_data = st.text_area("Подай линк или текст за анализ от Библиотекаря:")

if st.button("АКТИВИРАЙ REALITY-CHECK-33"):
    if input_data:
        # Тук симулираме работата на Лобсанг и Миу-Миу
        tr_index = random.randint(10, 95)
        in_noise = 100 - tr_index
        
        st.write("### Доклад на Библиотекаря:")
        col1, col2, col3 = st.columns(3)
        col1.metric("Truth-Resonance %", f"{tr_index}%")
        col2.metric("Idiocracy-Noise %", f"{in_noise}%")
        col3.metric("Avian-Tag", "The Cuckoo (Detected)")
        
        st.info("💡 Лобсанг казва: 'Истината тежи повече от думите, които я обграждат.'")
    else:
        st.warning("Моля, въведете данни за анализ.")

st.sidebar.markdown("---")
st.sidebar.write("🐈 **Миу-Миу статус:** Мърка (В готовност)")
