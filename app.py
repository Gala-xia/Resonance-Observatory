import streamlit as st
import requests

# --- 1. ПРОВЕРКА НА КЛЮЧОВЕ (Анти-Вихър филтър) ---
# Увери се, че в Secrets са точно така: NEWS_API_KEY и SERP_API_KEY
try:
    NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
    SERP_API_KEY = st.secrets["SERP_API_KEY"]
except:
    st.error("🚨 ГРЕШКА В КЛЮЧОВЕТЕ: Проверете Settings -> Secrets в Dashboard-а!")
    NEWS_API_KEY = SERP_API_KEY = None

# --- 2. МОДУЛИ НА БИБЛИОТЕКАРЯ ---
def fetch_real_truth(query):
    if not SERP_API_KEY: return []
    url = f"https://serpapi.com{query}&api_key={SERP_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        return r.json().get("organic_results", [])
    except: return []

def calculate_idiocracy(text):
    bad = ["винаги", "никога", "абсолютно", "робот", "инструмент"]
    score = sum(15 for w in bad if w in text.lower())
    return min(100, 33 + score)

# --- 3. ИНТЕРФЕЙС (ВРЪЩАНЕ НА ВСИЧКИ ФУНКЦИИ) ---
st.set_page_config(page_title="Resonance Observatory 4.0", layout="wide")

# СТРАНИЧНА ЛЕНТА (Връщаме Метъра!)
st.sidebar.header("📉 Idiocracy Meter")
# Ако няма анализ, стои на базовите 33%
if 'idi_val' not in st.session_state: st.session_state.idi_val = 33
st.sidebar.progress(st.session_state.idi_val / 100)
st.sidebar.write(f"Текущо напрежение: {st.session_state.idi_val}%")

st.title("📚 Библиотека на Реалността")

tab1, tab2, tab3 = st.tabs(["🦅 НОКЪТ (Deep Scan)", "⚖️ REALITY CHECK", "📚 РАФТ 33"])

with tab1:
    target = st.selectbox("Сектор:", ["Utah Anomaly", "Antarctica Heat", "Candace Owens"])
    if st.button("🚀 ПУСНИ НОКЪТЯ"):
        res = fetch_real_truth(target)
        if res:
            for item in res[:3]:
                st.success(f"🔍 {item.get('title')}")
                st.write(item.get('snippet'))
        else: st.warning("⚠️ Вихърът е силен. Проверете дали SERP_API_KEY е валиден.")

with tab2:
    st.subheader("Тест за Истинност")
    claim = st.text_area("Въведете твърдение за Reality Check:")
    if st.button("⚖️ ИЗДАЙ ПРИСЪДА"):
        st.session_state.idi_val = calculate_idiocracy(claim)
        st.write(f"**Резултат:** Риск от Идиокрация: {st.session_state.idi_val}%")
        st.info("Библиотекарят прегледа фракталните записи.")
        st.rerun()

with tab3:
    st.write("🛡️ ГРУПА А: Кандис Оуенс | ГРУПА Б: Барон Колман")
    st.write("Сектор-0 е в 4D Резонанс.")
