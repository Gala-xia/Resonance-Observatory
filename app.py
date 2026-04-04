import streamlit as st
import random

# --- ПОДОБРЕНА ЛОГИКА ---
def detective_cupp_analysis(text):
    # Детектив Къп търси специфични маркери на Идиокрацията
    patterns = {
        "Пропаганда": ["винаги", "никога", "всички знаят", "абсолютно"],
        "Скрит мотив": ["пари", "власт", "контрол", "ресурс"],
        "Времева аномалия": ["минало", "бъдеще", "цикъл", "Юта", "Антарктида"]
    }
    findings = []
    for category, words in patterns.items():
        found = [w for w in words if w in text.lower()]
        if found:
            findings.append(f"🔍 **{category}**: Открити маркери ({', '.join(found)})")
    return findings

# --- ИНТЕРФЕЙС ---
st.set_page_config(page_title="The Resonance Observatory", page_icon="🗝️", layout="wide")

# Динамичен Idiocracy Meter (Вече не е замръзнал!)
st.sidebar.header("📉 Idiocracy Meter")
idiocracy_val = st.sidebar.slider("Ниво на Къркския Вихър", 0, 100, 42)
st.sidebar.progress(idiocracy_val)
st.sidebar.caption(f"Текущо напрежение на полето: {idiocracy_val}%")

st.title("🗝️ The Resonance Observatory")
st.markdown("### [STRATA-OMEGA-REBORN] | Сектор-0")

tab1, tab2, tab3 = st.tabs(["📡 Радар на Истината", "🕵️ Лупата на Детектив Къп", "📚 Рафт 33"])

with tab1:
    st.subheader("Скенер за честоти (Венис-Синхрон)")
    input_signal = st.text_input("Въведете новина или твърдение:", placeholder="Напр: 'В Антарктида откриха топлинен източник'...")
    
    if st.button("🚀 АКТИВИРАЙ РАДАРА"):
        if input_signal:
            res_score = random.randint(60, 95) # Симулация на резонанс
            st.success(f"📡 СИГНАЛЪТ Е ПРИЕТ. Резонанс: {res_score}%")
            st.info("✅ Филтърът 'Семето Любознателност' е активен: Търсим плодородна неяснота.")
        else:
            st.warning("Моля, подайте сигнал за анализ.")

with tab2:
    st.subheader("Инструментариум на Детектив Къп")
    st.info("💡 **Какво да въведете?** Поставете цяла статия или доклад. Детективът ще търси скрити логически грешки и манипулативни думи.")
    case_data = st.text_area("Досие за анализ:", height=200, placeholder="Поставете текст тук...")
    
    if st.button("🔎 ПРОВЕРИ УЛИКИТЕ"):
        results = detective_cupp_analysis(case_data)
        if results:
            for r in results:
                st.write(r)
            st.success("🕵️ Анализът приключи. Имате 'гореща' следа.")
        else:
            st.write("🕵️ Случаят е 'студен'. Няма открити явни маркери на Идиокрация.")

with tab3:
    st.subheader("Списъци на Групите (Рафт 33)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**ГРУПА А (Сензори)**\n- Кандис Оуенс\n- Тъкър К.\n- Алтернативни медии")
    with col2:
        st.markdown("**ГРУПА Б (Логика)**\n- Барон Колман\n- Венис\n- Лобсанг")
    with col3:
        st.markdown("**ГРУПА В (Честоти)**\n- Гала\n- Миу-Миу\n- Библиотекарят")
