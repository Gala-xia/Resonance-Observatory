import streamlit as st
import os

# Свързване с новите ключове от Streamlit Secrets
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY")
SERP_API_KEY = st.secrets.get("SERP_API_KEY")

# Проверка на статуса за интерфейса
if not NEWS_API_KEY or not SERP_API_KEY:
    st.error("🚨 ВНИМАНИЕ: Липсват ключове в Secrets! Обсерваторията е в авариен режим.")
else:
    st.sidebar.success("✅ СИСТЕМА: Ключовете са разпознати.")
    
import streamlit as st
import requests

# --- 1. КЛЮЧОВЕ ---
# Четем директно от Secrets
SERP_API_KEY = st.secrets.get("SERP_API_KEY")

# --- 2. ЛОГИКА НА НОКЪТЯ (ХИРУРГИЧЕСКА ПРЕЦИЗНОСТ) ---
def fetch_real_truth(query):
    if not SERP_API_KEY:
        return [{"title": "ГРЕШКА", "snippet": "Ключът SERP_API_KEY не е намерен в Secrets!"}]
    
    # ИЗПОЛЗВАМЕ PARAMS ЗА АВТОМАТИЧНО ПРАВИЛНО ПОДРЕЖДАНЕ НА URL
    url = "https://serpapi.com"
    parameters = {
        "q": query,
        "api_key": SERP_API_KEY,
        "engine": "google",
        "hl": "en"
    }
    
    try:
        # Тук Python сам ще сложи ? и & на правилните места
        r = requests.get(url, params=parameters, timeout=15)
        if r.status_code == 200:
            data = r.json()
            return data.get("organic_results", [])
        else:
            return [{"title": "ГРЕШКА", "snippet": f"Статус на сървъра: {r.status_code}. Проверете API ключа!"}]
    except Exception as e:
        return [{"title": "КРИТИЧНА ГРЕШКА", "snippet": f"Грешка при свързване: {str(e)}"}]

# --- 3. ИНТЕРФЕЙС НА ОБСЕРВАТОРИЯТА ---
st.set_page_config(page_title="Resonance Observatory 4.5", layout="wide")
if 'idi_val' not in st.session_state: st.session_state.idi_val = 33

st.sidebar.header("📉 Idiocracy Meter")
st.sidebar.progress(st.session_state.idi_val / 100)
st.sidebar.write(f"Напрежение: {st.session_state.idi_val}%")

st.title("📚 Библиотека на Реалността")

tab1, tab2, tab3 = st.tabs(["🦅 НОКЪТ", "⚖️ REALITY CHECK", "📚 РАФТ 33"])

with tab1:
    target = st.selectbox("Изберете Сектор:", ["Utah Anomaly 2026", "Antarctica heat pulses", "Candace Owens analysis"])
    if st.button("🚀 ПУСНИ НОКЪТЯ"):
        with st.spinner("Нокътят рови в дълбоката мрежа..."):
            res = fetch_real_truth(target)
            if res and isinstance(res, list) and len(res) > 0:
                for item in res[:3]:
                    st.success(f"🔍 {item.get('title')}")
                    st.write(item.get('snippet'))
                    st.caption(f"Линк: {item.get('link')}")
            else:
                st.warning("⚠️ Нокътят се върна с празни ръце. Проверете за грешки по-горе.")

with tab2:
    claim = st.text_area("Въведете твърдение:")
    if st.button("⚖️ ИЗДАЙ ПРИСЪДА"):
        bad = ["винаги", "никога", "абсолютно"]
        score = sum(15 for w in bad if w in claim.lower())
        st.session_state.idi_val = min(100, 33 + score)
        st.rerun()

with tab3:
    st.write("🛡️ Сектор-0: Синхронизация с Венис.")
    if st.button("♻️ RESET"):
        st.session_state.idi_val = 33
        st.rerun()
