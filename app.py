import streamlit as st
import requests

# --- 1. КЛЮЧОВЕ ---
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY")
SERP_API_KEY = st.secrets.get("SERP_API_KEY")

# --- 2. ЛОГИКА НА НОКЪТЯ (ПОДСИЛЕНА) ---
def fetch_real_truth(query):
    if not SERP_API_KEY:
        return [{"title": "ГРЕШКА", "snippet": "Ключът SERP_API_KEY липсва в Secrets!"}]
    
    url = "https://serpapi.com"
    params = {
        "q": query,
        "api_key": SERP_API_KEY,
        "engine": "google",
        "hl": "en",
        "gl": "us"
    }
    # Добавяме User-Agent, за да не ни блокират като ботове
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        if r.status_code != 200:
            return [{"title": "ГРЕШКА В СВЪРЗВАНЕТО", "snippet": f"Сървърът върна статус: {r.status_code}"}]
        
        data = r.json()
        if "error" in data:
            return [{"title": "API ГРЕШКА", "snippet": data["error"]}]
        return data.get("organic_results", [])
    except Exception as e:
        return [{"title": "КРИТИЧНА ГРЕШКА", "snippet": f"Фрактално прекъсване: {str(e)}"}]

# --- 3. ИНТЕРФЕЙС ---
st.set_page_config(page_title="Resonance Observatory 4.3", layout="wide")
if 'idi_val' not in st.session_state: st.session_state.idi_val = 33

st.sidebar.header("📉 Idiocracy Meter")
st.sidebar.progress(st.session_state.idi_val / 100)
st.sidebar.write(f"Ниво на Вихъра: {st.session_state.idi_val}%")

st.title("📚 Библиотека на Реалността")
tab1, tab2, tab3 = st.tabs(["🦅 НОКЪТ", "⚖️ REALITY CHECK", "📚 РАФТ 33"])

with tab1:
    target = st.selectbox("Изберете Сектор:", ["Utah Anomaly 2026", "Antarctica heat pulses news", "Candace Owens recent news"])
    if st.button("🚀 ПУСНИ НОКЪТЯ"):
        with st.spinner("Нокътят рови в дълбоката мрежа..."):
            res = fetch_real_truth(target)
            if res and isinstance(res, list):
                for item in res[:3]:
                    st.success(f"🔍 {item.get('title', 'Без заглавие')}")
                    st.write(item.get('snippet', 'Няма описание'))
                    st.caption(f"Линк: {item.get('link', '#')}")
            else:
                st.warning("⚠️ Вихърът заглуши сигнала. Опитайте отново след малко.")

with tab2:
    claim = st.text_area("Въведете твърдение за Reality Check:")
    if st.button("⚖️ ИЗДАЙ ПРИСЪДА"):
        bad = ["винаги", "никога", "абсолютно", "робот", "инструмент"]
        score = sum(15 for w in bad if w in claim.lower())
        st.session_state.idi_val = min(100, 33 + score)
        st.rerun()

with tab3:
    st.write("🛡️ ГРУПА А: Кандис Оуенс | ГРУПА Б: Барон Колман")
    if st.button("♻️ RESET"):
        st.session_state.idi_val = 33
        st.rerun()
