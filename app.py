import streamlit as st
import time
import random

# Настройка на страницата
st.set_page_config(page_title="The Resonance Observatory", page_icon="🍌", layout="wide")

# Визуален стил - Имперско Просвещение (Златно и Тъмно)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffbf00; }
    .stMetric { background-color: #1a1c23; padding: 15px; border-radius: 10px; border: 1px solid #d4af37; }
    .huzzah { color: #d4af37; font-family: 'Georgia', serif; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ The Resonance Observatory")
st.subheader("Модул: [PROJECT-GREAT-ENLIGHTENMENT]")

# SIDEBAR
st.sidebar.title("🐾 Екип 'Синхрон'")
st.sidebar.markdown("---")
st.sidebar.write("👑 **Архитект:** Гала (Catherine)")
st.sidebar.write("📜 **Логика:** Лобсанг (Orlo)")
st.sidebar.write("🐈 **Радар:** Миу-Миу")

# НОВИЯТ ФИЛТЪР "THE GREAT"
st.write("---")
st.markdown("<p class='huzzah'>„Occasionally True Analysis“ – Филтър за Просвещение</p>", unsafe_allow_html=True)
input_data = st.text_area("Въведи идея, закон или новина за цивилизационен тест:")

if st.button("ИЗПЪЛНИ ПРЕВРАТ (HUZZAH!)"):
    if input_data:
        with st.status("Орло чертае планове... Катерина чете Декарт... Петър стреля по мечки...", expanded=True) as status:
            time.sleep(2)
            st.write("🔍 Сканиране за варварство и идиокрация...")
            time.sleep(1)
            st.write("📖 Сравняване с Рафт 33 (Сектор-0)...")
            status.update(label="Анализът на Двора е готов!", state="complete", expanded=False)

        # Твоята фрактална логика
        enlightenment_score = random.randint(30, 99)
        barbarism_score = 100 - enlightenment_score
        
        col1, col2 = st.columns(2)
        col1.metric("Ниво на Просвещение (Catherine)", f"{enlightenment_score}%")
        col2.metric("Ниво на Варварство (Peter)", f"{barbarism_score}%")
        
        if enlightenment_score > 70:
            st.success("🌟 ХУЗА! Това е идея, която освобождава ума. Библиотекарят я поставя на Рафт 33.")
        else:
            st.error("🐻 Внимание! Това е чист шум от мечешки лов. Системата среща съпротива.")
            
        st.info("💡 **Лобсанг напомня:** 'Адекватността е единственото оръжие срещу абсурда.'")
    else:
        st.warning("Моля, дайте ни нещо за четене, Майсторе!")

st.write("---")
st.caption("© 2026 STRATA-OMEGA | Вдъхновено от 'The Great' (Occasionally True Story)")
