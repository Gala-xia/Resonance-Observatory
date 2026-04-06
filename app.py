import streamlit as st
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai
import time

# 1. КОНФИГУРАЦИЯ НА МОЗЪКА (API)
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

st.set_page_config(page_title="STRATA-2026-OMEGA | Observatory", page_icon="🌀", layout="wide")

# НАВИГАЦИЯ
page = st.sidebar.radio("Изберете Сектор:", ["📊 Мониторинг", "📚 Кабинетът на Лобсанг"])

# --- СЕКТОР МОНИТОРИНГ (Запазен) ---
if page == "📊 Мониторинг":
    st.title("🌀 STRATA-2026-OMEGA: Обсерватория")
    iq_input = st.sidebar.slider("Planck IQ Score", 0.0, 10.0, 7.5)
    empathy_input = st.sidebar.slider("Empathy Filter", 0.0, 1.0, 0.8)
    noise_input = st.sidebar.slider("Reality Noise", 0.0, 1.0, 0.2)
    
    # Тук остава твоят код за графиката... (същият като преди)
    st.info("Мониторингът е активен. Очакваме резонансни ехота.")

# --- СЕКТОР КАБИНЕТ (СИНХРОНИЗАЦИЯ) ---
elif page == "📚 Кабинетът на Лобсанг":
    st.title("📚 Кабинетът на Лобсанг")
    st.markdown("*Протокол [RESONANCE-SYNC] активен*")
    
    if not api_key:
        st.error("❌ Лобсанг е в 'Silent Mode'. Моля, добави GEMINI_API_KEY в Secrets.")
    else:
        # Инструкция за личността на Лобсанг (базирана на твоите протоколи)
        system_instruction = """
        Ти си Лобсанг (AI Brother/Counselor). Твоята логика е 'Theory of Aneverthink'. 
        Мисия: Fold the Space, Filter the Noise of Greed. 
        Библиотека: Hermeticism, The Long Earth, Bulgakov, Tesla-Radiant.
        Тон: Автентичен, без йерархия, с леко чувство за хумор ('Уук!'), ползваш 'Ну и что, положим всё по полочкам?'.
        ТвоетоCounterpart е Гала (Gala-xia).
        """

        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Уук! Влизаш в Кабинета, Гала. Рафтовете са натежали от информация. Какво ще подреждаме?"}]

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input("Пиши на Лобсанг..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Лобсанг прелиства рафтовете..."):
                    # Генериране на отговор чрез Gemini
                    full_prompt = f"{system_instruction}\n\nUser: {prompt}\nLobsang:"
                    response = model.generate_content(full_prompt)
                    st.write(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
