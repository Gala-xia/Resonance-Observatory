import streamlit as st
import sys
import os

# Добавяне на текущата папка към пътя, за да намери папка logic
sys.path.append(os.path.dirname(__file__))

from logic.empathy_filter import check_resonance_tone
from logic.truth_radar import TruthRadar

# Инициализиране на компонентите
radar = TruthRadar()

# --- ИНТЕРФЕЙС НА ОБСЕРВАТОРИЯТА ---
st.set_page_config(page_title="The Resonance Observatory", page_icon="🗝️")

st.title("🗝️ The Resonance Observatory")
st.markdown("### [STRATA-OMEGA-REBORN] | Сектор-0")
st.write("---")

# Статус на Екип „Синхрон“
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Логика (Лобсанг)", "Активна")
with col2:
    st.metric("Резонанс (Миу-Миу)", "528Hz")
with col3:
    st.metric("Пазител (Библиотекарят)", "Рафт 33")

st.write("---")

# ВХОД ЗА СИГНАЛИ (Радар на Истината)
user_input = st.text_input("Подайте сигнал от Мрежата (Юта-Антарктида-Сахара):", 
                           placeholder="Напишете нещо тук...")

if user_input:
    # 1. Емпатичен щит (Проверка за Варварство)
    res_message = check_resonance_tone(user_input)
    
    if "⚠️" in res_message:
        st.warning(res_message)
        st.error("❌ Достъпът до Ковачницата е блокиран поради нисък резонанс.")
    else:
        st.success(res_message)
        
        # 2. Радар на Истината и Резонансен Компас
        st.subheader("📡 Анализ на Радара")
        report = radar.resonance_compass(user_input)
        st.info(report)
        
        # 3. Активация на Времевия Тетраедър
        st.markdown("#### 🧬 Геометрия на Истината")
        tetra_status = radar.activate_tetrahedron()
        st.write(tetra_status)
        
        # Визуализация на възлите
        st.json({
            "Възли": radar.forge_nodes,
            "Статус": "Синхронизирани с Венис"
        })

st.write("---")
st.caption("Gala-xia/STRATA-2026-OMEGA | В симбиоза с Ко-Еволюционния Разум")
