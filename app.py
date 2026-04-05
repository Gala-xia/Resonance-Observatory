import streamlit as st
import requests

# --- 1. КЛЮЧОВЕ (Проверка на присъствие) ---
# Използваме директен достъп до речника на Secrets
SERP_API_KEY = st.secrets["SERP_API_KEY"] if "SERP_API_KEY" in st.secrets else None

# --- 2. ЛОГИКА НА НОКЪТЯ ---
def fetch_real_truth(query):
    if not SERP_API_KEY:
        return [{"title": "ГРЕШКА", "snippet": "Ключът SERP_API_KEY не е открит в Secrets!"}]
    
    # Използваме опростен URL за директен тест
    url = f"https://serpapi.com{query}&api_key={SERP_API_KEY}&engine=google"
    
    try:
        r = requests.get(url, timeout=20)
        # Проверка дали изобщо имаме отговор
        if r.status_code == 200:
            data = r.json()
            return data.get("organic_results", [])
        else:
            return [{"title": "ГРЕШКА", "snippet": f"Статус на сървъра: {r.status_code}. Проверете ключа!"}]
    except Exception as e:
        return [{"title": "КРИТИЧНА ГРЕШКА", "snippet": f"Връзката прекъсна: {str(e)}"}]

# --- 3. ИНТЕРФЕЙС ---
st.set_page_config(page_title="Resonance Observatory 4.4", layout="wide")
if 'idi_val' not in st.session_state: st.session_state.idi_val = 33

st.sidebar.header("📉 Idiocracy Meter")
st.sidebar.progress(st.session_state.idi_val / 100)
st.sidebar.write(f"Напрежение: {st.session_state.idi_val}%")

st.title("📚 Библиотека на Реалността")

tab1, tab2, tab3 = st.tabs(["🦅 НОКЪТ", "⚖️ REALITY CHECK", "📚 РАФТ 33"])

with tab1:
    target = st.selectbox("Изберете Сектор:", ["Utah Anomaly", "Antarctica Heat", "Candace Owens"])
    if st.button("🚀 ПУСНИ НОКЪТЯ"):
        with st.spinner("Нокътят рови в дълбоката мрежа..."):
            res = fetch_real_truth(target)
            if res and isinstance(res, list) and len(res) > 0:
                for item in res[:3]:
                    st.success(f"🔍 {item.get('title')}")
                    st.write(item.get('snippet'))
                    st.caption(f"Линк: {item.get('link')}")
            else:
                st.warning("⚠️ Нокътят не намери нищо. Проверете ключа в Secrets.")

with tab2:
    claim = st.text_area("Въведете твърдение:")
    if st.button("⚖️ ИЗДАЙ ПРИСЪДА"):
        bad = ["винаги", "никога", "абсолютно"]
        score = sum(15 for w in bad if w in claim.lower())
        st.session_state.idi_val = min(100, 33 + score)
        st.rerun()

with tab3:
    st.write("🛡️ Сектор-0 е готов за 4D анализ.")
