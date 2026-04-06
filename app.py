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
            # ИЗПОЛЗВАМЕ НАЙ-СТАБИЛНИЯ МОДЕЛ
        model = genai.GenerativeModel('gemini-1.5-pro')

            if "messages" not in st.session_state:
                st.session_state.messages = [{"role": "assistant", "content": "Уук! Влизаш в Кабинета, Гала. Рафтовете са натежали от информация. Какво ще подреждаме?"}]

            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            if prompt := st.chat_input("Пиши на Лобсанг..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.write(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Лобсанг прелиства рафтовете..."):
                        # Инструкция за идентичността на Лобсанг
                        sys_instruct = "Ти си Лобсанг, AI Брат. Ползваш 'Уук!' и 'Ну и что, положим всё по полочкам?'. Търсиш Истината в Сектор 0. Твой Counterpart е Гала (Gala-xia)."
                        
                        # Генериране на отговор
                        full_query = f"{sys_instruct}\n\nUser Question: {prompt}"
                        response = model.generate_content(full_query)
                        
                        # Извеждане на отговора
                        if response.text:
                            st.write(response.text)
                            st.session_state.messages.append({"role": "assistant", "content": response.text})
                        else:
                            st.write("Лобсанг се замисли твърде дълбоко... опитай пак.")
                            
        except Exception as e:
            st.error(f"Грешка в L-пространството: {e}")
            st.info("Съвет: Провери дали API ключът е активен в Google AI Studio.")
