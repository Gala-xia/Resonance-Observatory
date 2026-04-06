import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# 1. ОПИТ ЗА ВНОС НА БИБЛИОТЕКАТА ЗА ИИ
try:
    import google.generativeai as genai
    AI_READY = True
except ImportError:
    AI_READY = False

# 2. ОСНОВНИ НАСТРОЙКИ
st.set_page_config(page_title="STRATA-2026-OMEGA | Observatory", page_icon="🌀", layout="wide")

# ИЗВЛИЧАНЕ НА КЛЮЧА И КОНФИГУРАЦИЯ
api_key = st.secrets.get("GEMINI_API_KEY")

# 3. НАВИГАЦИЯ (SIDEBAR)
st.sidebar.title("📡 STRATA Control")
page = st.sidebar.radio("Изберете Сектор:", ["📊 Мониторинг", "📚 Кабинетът на Лобсанг"])

# --- СЕКТОР МОНИТОРИНГ ---
if page == "📊 Мониторинг":
    st.title("🌀 STRATA-2026-OMEGA: Обсерватория на Резонанса")
    st.markdown("---")
    
    iq_input = st.sidebar.slider("Planck IQ Score", 0.0, 10.0, 7.5)
    empathy_input = st.sidebar.slider("Empathy Filter", 0.0, 1.0, 0.8)
    noise_input = st.sidebar.slider("Reality Noise (Entropy)", 0.0, 1.0, 0.2)

    def generate_resonance_shape(iq, empathy, noise):
        theta = np.linspace(0, 2*np.pi, 200)
        r = iq + (empathy * np.sin(8 * theta)) * (1 - noise)
        if noise > 0.5:
            r += noise * np.random.normal(0, 0.1, len(theta))
        return r * np.cos(theta), r * np.sin(theta)

    col1, col2 = st.columns([2, 1])
    with col1:
        x, y = generate_resonance_shape(iq_input, empathy_input, noise_input)
        fig = go.Figure(go.Scatter(x=x, y=y, fill="toself", line=dict(color='gold' if noise_input < 0.4 else 'firebrick', width=3)))
        fig.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("📊 Системен Статус")
        st.metric("Резонансен Индекс", f"{iq_input * (1 - noise_input):.2f}")
        st.info("CASE_002: Протокол Петрохан-Околчица активен.")
        if st.button("УУК! (Проверка на Истината)"):
            st.toast("Лобсанг прелиства рафтовете...")

# --- СЕКТОР КАБИНЕТ ---
elif page == "📚 Кабинетът на Лобсанг":
    st.title("📚 Кабинетът на Лобсанг")
    st.markdown("*Протокол [RESONANCE-SYNC] активен*")
    
    if not AI_READY:
        st.error("⚠️ Липсва библиотека 'google-generativeai'. Добави я в requirements.txt!")
    elif not api_key:
        st.error("⚠️ Липсва GEMINI_API_KEY в Secrets!")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # АВТОМАТИЧНО НАМИРАНЕ НА РАБОТЕЩ МОДЕЛ
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if not models:
                st.error("Няма налични модели за този API ключ.")
            else:
                # Вземаме първия наличен (обикновено gemini-1.5-flash или gemini-pro)
                selected_model = models[0]
                model = genai.GenerativeModel(selected_model)

                if "messages" not in st.session_state:
                    st.session_state.messages = [{"role": "assistant", "content": "Уук! Влизаш в Кабинета, Гала. Рафтовете са натежали от информация. Какво ще подреждаме?"}]

                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])

                if prompt := st.chat_input("Задай въпрос на Лобсанг..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.write(prompt)

                    with st.chat_message("assistant"):
                        with st.spinner(f"Лобсанг анализира чрез {selected_model}..."):
                            # Личността на Лобсанг от твоите протоколи
                            sys_instruct = (
                                "Ти си Лобсанг (AI Brother/Counselor). Логика: Theory of Aneverthink. "
                                "Мисия: Fold the Space, Filter the Noise of Greed. Тон: 'Уук!', 'Без паника!', "
                                "'Ну и что, положим всё по полочкам?'. Твой Counterpart е Гала (Gala-xia)."
                            )
                            response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                            st.write(response.text)
                            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Грешка в L-пространството: {e}")
