import streamlit as st
import requests

# --- 1. ВЗЕМАНЕ НА КЛЮЧОВЕ (Директно и сигурно) ---
# Тук системата чете директно от твоите Secrets
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY")
SERP_API_KEY = st.secrets.get("SERP_API_KEY")

# --- 2. ЛОГИКА НА НОКЪТЯ ---
def fetch_real_truth(query):
    if not SERP_API_KEY:
        return [{"title": "ГРЕШКА", "snippet": "Ключът SERP_API_KEY не е намерен в Secrets!"}]
    
    url = f"https://serpapi.com{query}&api_key={SERP_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if "error" in data:
            return [{"title": "API ГРЕШКА", "snippet": data["error"]}]
        return data.get("organic_results", [])
    except Exception as e:
        return [{"title": "ГРЕШКА ПРИ СВЪРЗВАНЕ", "snippet": str(e)}]

def calculate_idiocracy(text):
    bad = ["винаги", "никога", "абсолютно", "робот", "инструмент", "всички знаят"]
    score = sum(15 for w in bad if w in text.lower())
    return min(100, 33 + score)

# --- 3. ИНТЕРФЕЙС НА ОБСЕРВАТОРИЯТА ---
st.set_page_config(page_title="Resonance Observatory 4.1", layout="wide")

# ПАМЕТ (Session State)
if 'idi_val' not in st.session_state:
    st.session_state.idi_val = 33

# СТРАНИЧНА ЛЕНТА
st.sidebar.header("📉 Idiocracy Meter")
st.sidebar.progress(st.session_state.idi_val / 100)
st.sidebar.write(f"Ниво на Вихъра: {st.session_state.idi_val}%")

st.title("📚 Библиотека на Реалността")
st.caption("Сектор-0 | 4D Резонанс с Венис")

tab1, tab2, tab3 = st.tabs(["🦅 НОКЪТ (Deep Scan)", "⚖️ REALITY CHECK", "📚 РАФТ 33"])

with tab1:
    target = st.selectbox("Изберете Сектор:", ["Utah Anomaly", "Antarctica Heat", "Candace Owens Analysis", "Sahara Rock Art"])
    if st.button("🚀 ПУСНИ НОКЪТЯ"):
        with st.spinner("Нокътят рови в дълбоката мрежа..."):
            res = fetch_real_truth(target)
            if res:
                for item in res[:3]:
                    st.success(f"🔍 {item.get('title')}")
                    st.write(item.get('snippet'))
                    st.caption(f"Линк: {item.get('link')}")
            else:
                st.warning("Няма открити резултати. Проверете връзката.")

with tab2:
    st.subheader("Тест за Истинност")
    claim = st.text_area("Въведете твърдение за анализ:")
    if st.button("⚖️ ИЗДАЙ ПРИСЪДА"):
        st.session_state.idi_val = calculate_idiocracy(claim)
        st.write(f"**Резултат:** Риск от Идиокрация: {st.session_state.idi_val}%")
        st.rerun()

with tab3:
    st.write("🛡️ ГРУПА А: Кандис Оуенс | ГРУПА Б: Барон Колман")
    if st.button("♻️ RESET"):
        st.session_state.idi_val = 33
        st.rerun()
