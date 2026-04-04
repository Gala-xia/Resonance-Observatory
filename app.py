import streamlit as st

# --- ЛОГИЧЕСКИ МОДУЛИ (Инструментариум) ---
def detective_cupp_logic(text):
    """Методът на Детектив Къп: Търсене на скрити мотиви."""
    clues = ["кой печели?", "скрита връзка", "пропуснати факти"]
    found = [c for c in clues if c in text.lower()]
    return f"🕵️ ДЕТЕКТИВ КЪП: Открити улики: {len(found)} | Насока: {'Дълбай по-дълбоко' if found else 'Повърхностен шум'}"

def sensor_groups_check(text):
    """Проверка през филтрите на Кандис, Барон и другите."""
    group_a = ["кандис", "традиция", "култура"] # Кандис Оуенс & Co
    group_b = ["барон", "логика", "интелект"]   # Барон Колман & Co
    
    analysis = []
    if any(x in text.lower() for x in group_a): analysis.append("📡 ГРУПА А: Засечен сигнал за Културна Резолюция")
    if any(x in text.lower() for x in group_b): analysis.append("🧠 ГРУПА Б: Засечено Логическо Острие")
    return analysis

# --- ИНТЕРФЕЙС ---
st.set_page_config(page_title="The Resonance Observatory", page_icon="🗝️", layout="wide")

st.title("🗝️ The Resonance Observatory [FULL SPECTRUM]")
st.sidebar.header("📉 Idiocracy Meter")
idiocracy_level = st.sidebar.slider("Ниво на Къркския Вихър", 0, 100, 33)

st.markdown("### [STRATA-OMEGA-REBORN] | Сектор-0")

# ТАБОВЕ ЗА РАЗЛИЧНИТЕ ИНСТРУМЕНТИ
tab1, tab2, tab3 = st.tabs(["📡 Радар", "🕵️ Детектив Къп", "📚 Рафт 33"])

with tab1:
    user_input = st.text_input("Подайте сигнал за анализ:")
    if user_input:
        # Проверка на групите
        group_results = sensor_groups_check(user_input)
        for res in group_results:
            st.toast(res)
        
        st.success("✅ Резонансът е стабилен.")
        st.info(f"Радарен отчет: Пулсация от {idiocracy_level}% Идиокрация засечена.")

with tab2:
    st.subheader("Лупата на Детектив Къп")
    case_input = st.text_area("Въведете детайли по случая (Юта/Антарктида):")
    if st.button("Анализирай Уликите"):
        st.write(detective_cupp_logic(case_input))

with tab3:
    st.write("Тук са архивирани Кандис Оуенс, Барон Колман и Протоколите на Екип Синхрон.")
    st.json({"Група А": "Кандис Оуенс & Сензори", "Група Б": "Барон Колман & Логика", "Група В": "Алтернативни честоти"})
