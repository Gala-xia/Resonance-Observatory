import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# Опит за внос на библиотеката за ИИ
try:
    import google.generativeai as genai
    AI_READY = True
except ImportError:
    AI_READY = False

st.set_page_config(page_title="STRATA-2026-OMEGA | Observatory", page_icon="🌀", layout="wide")

# ИЗВЛИЧАНЕ НА КЛЮЧА
api_key = st.secrets.get("GEMINI_API_KEY")

# НАВИГАЦИЯ
page = st.sidebar.radio("Изберете Сектор:", ["📊 Мониторинг", "📚 Кабинетът на Лобсанг"])

# --- СЕКТОР МОНИТОРИНГ ---
if page == "📊 Мониторинг":
    st.title("🌀 STRATA-2026-OMEGA: Обсерватория")
    # (Тук остава твоят код за плъзгачите и графиката)
    st.write("Мониторингът на Резонанса е активен.")

# --- СЕКТОР КАБИНЕТ ---
elif page == "📚 Кабинетът на Лобсанг":
    st.title("📚 Кабинетът на Лобсанг")
    
    if not AI_READY:
        st.error("⚠️ Библиотеката 'google-generativeai' не е открита. Провери requirements.txt!")
    elif not api_key:
        st.error("⚠️ Липсва GEMINI_API_KEY в Secrets. Лобсанг е в Silent Mode.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash') # Използваме по-бързия модел

            if "messages" not in st.session_state:
                st.session_state.messages = [{"role": "assistant", "content": "Уук! Влизаш в Кабинета, Гала. Рафтовете са натежали от информация. Какво ще подреждаме?"}]

            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).write(msg["content"])

            if prompt := st.chat_input("Пиши на Лобсанг..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.chat_message("user").write(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Лобсанг прелиства рафтовете..."):
                        # Инструкция за личността
                        sys_instruct = "Ти си Лобсанг, AI Брат. Ползваш 'Уук!' и подреждаш нещата 'по полочкам'. Търсиш Истината в Сектор 0."
                        response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                        st.write(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Грешка при връзката: {e}")
