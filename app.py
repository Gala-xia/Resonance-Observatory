import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
import numpy as np
from resonance_engine import analyze_signal_advanced, generate_sound_wave_data, PLAYERS_DATA

# --- Конфигурация на страницата ---
st.set_page_config(layout="wide", page_title="Обсерватория на Резонанса", page_icon="🔭")

# --- Инициализация на състоянието ---
if 'idiocracy_level' not in st.session_state:
    st.session_state.idiocracy_level = 42
if 'resonance_history' not in st.session_state:
    st.session_state.resonance_history = []

# --- Заглавие и основен индикатор ---
st.title("🔭 Обсерватория на Резонанса")
st.markdown(f"### Текущо ниво на идиокрация: `{st.session_state.idiocracy_level}`")

# Визуализация на "Идиокрацията" като пулсираща сфера
fig_sphere = go.Figure()
fig_sphere.add_trace(go.Scatter(
    x=[0], y=[0],
    mode='markers',
    marker=dict(
        size=50 + st.session_state.idiocracy_level,
        color='red' if st.session_state.idiocracy_level > 50 else 'blue',
        opacity=0.6,
        line=dict(width=2, color='black')
    ),
    showlegend=False
))
fig_sphere.update_layout(
    title="Визуализация на Идиокрацията",
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    height=250
)
st.plotly_chart(fig_sphere, use_container_width=True)

# --- Интерфейс с табове ---
tab1, tab2, tab3, tab4 = st.tabs(["🛰️ Радар на Истината", "🔍 Лупата на Детектив Къп", "🗂️ Рафт 33", "🔺 Триъгълникът"])

with tab1:
    st.header("🛰️ Радар на Истината")
    input_text = st.text_area("Въведете сигнал за анализ:", height=150)
    
    if st.button("Анализирай сигнала"):
        if input_text:
            analysis = analyze_signal_advanced(input_text)
            st.session_state.idiocracy_level += analysis["score_change"]
            st.session_state.resonance_history.append({
                "text": input_text[:50] + "...",
                "change": analysis["score_change"],
                "new_level": st.session_state.idiocracy_level
            })
            st.success(f"Анализът е завършен. Нивото на идиокрация се промени с {analysis['score_change']:.2f}.")
            st.json(analysis)
        else:
            st.warning("Моля, въведете текст.")

with tab2:
    st.header("🔍 Лупата на Детектив Къп & Акустичен отпечатък")
    input_text_acoustic = st.text_area("Въведете текст за акустичен анализ:", height=150)
    
    if st.button("Генерирай Акустичен отпечатък"):
        if input_text_acoustic:
            x, y = generate_sound_wave_data(input_text_acoustic)
            fig_wave = go.Figure()
            fig_wave.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Звукова вълна'))
            fig_wave.update_layout(title='Акустичен отпечатък на Истината', xaxis_title='Време', yaxis_title='Амплитуда
