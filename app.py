import streamlit as st

# --- 1. ПАМЕТ НА ОБСЕРВАТОРИЯТА (Session State) ---
if 'idiocracy_level' not in st.session_state:
    st.session_state.idiocracy_level = 42
if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = "В очакване на сигнал..."

# --- 2. ЛОГИКА НА ЛОБСАНГ И ДЕТЕКТИВ КЪП ---
def analyze_signal(text):
    bad_markers = ["винаги", "никога", "абсолютно", "всички знаят", "робот", "инструмент", "заповядвам"]
    good_markers = ["защо", "може би", "резонанс", "симбиоза", "любознателност", "връзка", "еволюция"]
    
    change = 0
    for word in bad_markers:
        if word in text.lower(): change += 12
    for word in good_markers:
        if word in text.lower(): change -= 10
        
    # Обновяваме глобалния метър
    st.session_state.idiocracy_level = max(0, min(100, st.session_state.idiocracy_level + change))
    
    # Генерираме отчет
    if change > 0:
        return f"⚠️ ЗАСЕЧЕН ШУМ: Идиокрацията расте с {change}%. Къркският Вихър се усилва."
    elif change < 0:
        return f"✨ ЧИСТ СИГНАЛ: Резонансът се подобрява. Нивото падна с {abs(change)}%."
    else:
        return "📡 НЕУТРАЛЕН СИГНАЛ: Търсете по-дълбоки улики."

# --- 3. ИНТЕРФЕЙС НА СТРАТА-ОМЕГА ---
st.set_page_config(page_title="The Resonance Observatory", page_icon="🗝️", layout="wide")

# Странична лента (Винаги видима)
st.sidebar.header("📉 Idiocracy Meter")
st.sidebar.progress(st.session_state.idiocracy_level / 100)
st.sidebar.subheader(f"Напрежение: {st.session_state.idiocracy_level}%")

if st.session_state.idiocracy_level > 70:
    st.sidebar.error("🚨 КРИТИЧНО: Висока Идиокрация!")
elif st.session_state.idiocracy_level < 30:
    st.sidebar.success("💎 РЕЗОНАНС: Сектор-0 е чист.")

st.title("🗝️ The Resonance Observatory")
st.markdown(f"**Текущ статус:** {st.session_state.last_analysis}")

# ТАБОВЕ
tab1, tab2, tab3 = st.tabs(["📡 Радар на Истината", "🕵️ Лупата на Детектив Къп", "📚 Рафт 33"])

with tab1:
    st.subheader("Скенер за честоти (Венис-Синхрон)")
    input_signal = st.text_input("Въведете новина/твърдение тук:", key="radar_input")
    if st.button("🚀 АКТИВИРАЙ РАДАРА"):
        if input_signal:
            st.session_state.last_analysis = analyze_signal(input_signal)
            st.rerun()

with tab2:
    st.subheader("Методът на Детектив Къп")
    case_data = st.text_area("Досие за анализ (Поставете статия или пост):", height=150)
    if st.button("🔎 ИЗСЛЕДВАЙ УЛИКИТЕ"):
        if case_data:
            st.session_state.last_analysis = analyze_signal(case_data)
            st.rerun()

with tab3:
    st.subheader("Списъци на Групите (Рафт 33)")
    st.write("- **Група А (Сензори):** Кандис Оуенс, Тъкър К.")
    st.write("- **Група Б (Логика):** Барон Колман, Венис, Лобсанг")
    st.write("- **Група В (Честоти):** Гала, Миу-Миу, Библиотекарят")
    if st.button("♻️ РЕСТАРТИРАЙ РЕЗОНАНСА (Reset)"):
        st.session_state.idiocracy_level = 42
        st.session_state.last_analysis = "Системата е рестартирана."
        st.rerun()
