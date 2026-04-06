import streamlit as st
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai
import pandas as pd

# Конфигурация
st.set_page_config(page_title="STRATA-2026-OMEGA | Observatory", page_icon="🌀", layout="wide")

# Извличане на ключове
api_key = st.secrets.get("GEMINI_API_KEY")
serp_key = st.secrets.get("SERP_API_KEY") # За бъдещо разширение на инструментите

# Навигация
page = st.sidebar.radio("Сектор:", ["📊 Обсерватория", "📚 Кабинетът на Лобсанг"])

# --- ФУНКЦИЯ ЗА ТАЙМЛАЙН НА ЕХОТО ---
def plot_echo_timeline():
    events = [
        dict(Year=1876, Event="Христо Ботев (Код Околчица)", Type="Origin"),
        dict(Year=1944, Event="Системна Промяна", Type="Shift"),
        dict(Year=2024, Event="Аномалия Петрохан", Type="Echo"),
        dict(Year=2026, Event="STRATA Omega (Сега)", Type="Observation")
    ]
    df = pd.DataFrame(events)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.Year, y=[1]*len(df), mode="lines+markers+text",
                             text=df.Event, textposition="top center",
                             line=dict(color='gold', width=2),
                             marker=dict(size=12, color='firebrick')))
    fig.update_layout(title="📈 Траектория на Резонансното Ехо", height=300, 
                      yaxis=dict(visible=False), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

# --- СЕКТОР ОБСЕРВАТОРИЯ ---
if page == "📊 Обсерватория":
    st.title("🌀 STRATA-2026-OMEGA")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        # Тук остава твоята фрактална графика (съкращавам за яснота)
        st.subheader("Квантов Резонанс")
        # [Интегрирай тук функцията generate_resonance_shape от предишния скрипт]
        st.plotly_chart(plot_echo_timeline(), use_container_width=True)
    
    with col2:
        st.subheader("🐾 Пазителят Миу-Миу")
        st.markdown("> *Миу-Миу спи върху сървъра. Температурата е оптимална.*")
        st.progress(0.97, text="Resonance Stability")

# --- СЕКТОР КАБИНЕТ ---
elif page == "📚 Кабинетът на Лобсанг":
    st.title("📚 Кабинетът на Лобсанг (+ Миу-Миу)")
    
    # Визуализация на Миу-Миу в чата
    st.sidebar.markdown("### 🐈 Статус на Миу-Миу")
    st.sidebar.code("STATUS: PURRING\nSCANNING FOR ENTROPY...")

    if api_key:
        try:
            genai.configure(api_key=api_key)
            # Автоматичен модел
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model = genai.GenerativeModel(models[0])

            if "messages" not in st.session_state:
                st.session_state.messages = [{"role": "assistant", "content": "Уук! Влизаш в Кабинета. Миу-Миу току-що провери кабелите. Всичко е по полочкам. Какво те води насам?"}]

            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).write(msg["content"])

            if prompt := st.chat_input("Задай въпрос на Лобсанг..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.chat_message("user").write(prompt)

                with st.chat_message("assistant"):
                    # Инструкция с включена търсачка (симулирана през контекста)
                    sys_instruct = f"""
                    Ти си Лобсанг. Имаш достъп до SERP_API за търсене. 
                    Тон: Уук! Ну и что! 
                    Миу-Миу е до теб и следи за истината. 
                    Ако те питат за новини, анализирай ги през призмата на Q10.
                    """
                    response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                    st.write(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Грешка: {e}")
