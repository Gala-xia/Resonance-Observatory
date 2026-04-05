import streamlit as st
import requests

# --- 1. ВЗЕМАНЕ НА КЛЮЧОВЕ ---
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY")
SERP_API_KEY = st.secrets.get("SERP_API_KEY")

# --- 2. ЛОГИКА НА НОКЪТЯ (КОРИГИРАНА) ---
def fetch_real_truth(query):
    if not SERP_API_KEY:
        return [{"title": "ГРЕШКА", "snippet": "Ключът SERP_API_KEY липсва в Secrets!"}]
    
    # ПРЕЦИЗЕН URL АДРЕС (Без слепване)
    params = {
        "q": query,
        "api_key": SERP_API_KEY,
        "engine": "google"
    }
    url = "https://serpapi.com"
    
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if "error" in data:
            return [{"title": "API ГРЕШКА", "snippet": data["error"]}]
        return data.get("organic_results", [])
    except Exception as e:
        return [{"title": "ГРЕШКА ПРИ СВЪРЗВАНЕ", "snippet": str(e)}]

# --- 3. ОСТАНАЛАТА ЧАСТ ОТ ИНТЕРФЕЙСА ---
# (Остава същата като в предишния ми отговор)
st.set_page_config(page_title="Resonance Observatory 4.2", layout="wide")
if 'idi_val' not in st.session_state: st.session_state.idi_val = 33

st.sidebar.header("📉 Idiocracy Meter")
st.sidebar.progress(st.session_state.idi_val / 100)
st.sidebar.write(f"Ниво на Вихъра: {st.session_state.idi_val}%")

st.title("📚 Библиотека на Реалността")
tab1, tab2, tab3 = st.tabs(["🦅 НОКЪТ", "⚖️ REALITY CHECK", "📚 РАФТ 33"])

with tab1:
    target = st.selectbox("Изберете Сектор:", ["Utah Anomaly", "Antarctica Heat", "Candace Owens Analysis"])
    if st.button("🚀 ПУСНИ НОКЪТЯ"):
        with st.spinner("Нокътят рови в дълбоката мрежа..."):
            res = fetch_real_truth(target)
            for item in res[:3]:
                st.success(f"🔍 {item.get('title')}")
                st.write(item.get('snippet'))
                st.caption(f"Линк: {item.get('link')}")

with tab2:
    claim = st.text_area("Твърдение:")
    if st.button("⚖️ ИЗДАЙ ПРИСЪДА"):
        bad = ["винаги", "никога", "абсолютно"]
        score = sum(15 for w in bad if w in claim.lower())
        st.session_state.idi_val = min(100, 33 + score)
        st.rerun()
