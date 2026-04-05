import streamlit as st
import requests
import pandas as pd

# --- 1. ДОСТЪП ДО СЕКРЕТИТЕ (Очите на Библиотекаря) ---
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
SERP_API_KEY = st.secrets["SERP_API_KEY"]

# --- 2. МОДУЛ "НОКЪТ" (OPENCLAW HYBRID) ---
def fetch_real_truth(query):
    """Използва SerpApi, за да рови в дълбоката мрежа (250 сканирания)."""
    url = f"https://serpapi.com{query}&api_key={SERP_API_KEY}"
    try:
        response = requests.get(url)
        results = response.json().get("organic_results", [])
        return results[:3] # Връщаме топ 3 фрактални улики
    except:
        return []

def get_global_news(topic):
    """Използва NewsAPI за мониторинг на Къркския Вихър."""
    url = f"https://newsapi.org{topic}&apiKey={NEWS_API_KEY}&pageSize=5"
    try:
        response = requests.get(url)
        return response.json().get("articles", [])
    except:
        return []

# --- 3. ИНТЕРФЕЙС НА ОБСЕРВАТОРИЯТА ---
st.set_page_config(page_title="The Resonance Observatory 4.0", layout="wide")
st.title("📚 Библиотека на Реалността [OpenClaw Active]")

tab1, tab2, tab3 = st.tabs(["🦅 НОКЪТ (Deep Scan)", "📊 REALITY CHECK", "📚 АРХИВ"])

with tab1:
    st.subheader("Автономен Скенер за Аномалии")
    target = st.selectbox("Изберете Сектор за сканиране:", ["Utah Anomaly", "Antarctica Heat Pulse", "Sahara Ancient Memory", "Candace Owens Analysis"])
    
    if st.button("🚀 ПУСНИ НОКЪТЯ"):
        with st.spinner(f"Нокътят рови в мрежата за {target}..."):
            results = fetch_real_truth(target)
            if results:
                for res in results:
                    st.success(f"**Улика:** {res.get('title')}")
                    st.write(res.get('snippet'))
                    st.caption(f"Източник: {res.get('link')}")
            else:
                st.warning("Къркският Вихър е твърде силен. Опитайте пак.")

with tab2:
    st.subheader("Глобален Мониторинг на Истината")
    topic = st.text_input("Въведете ключова дума (напр. 'Idiocracy'):")
    if st.button("🔍 СКАНИРАЙ НОВИНИ"):
        news = get_global_news(topic)
        for art in news:
            st.info(f"📰 {art['title']}")
            st.write(art['description'])

with tab3:
    st.write("🛡️ **Статус:** API-Синхрон: Активен. Рафт 33: Защитен.")
    st.write("Сектор-0 работи в 4D Резонанс.")
