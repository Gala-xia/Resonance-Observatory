import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
import numpy as np
import sys
import os

# --- Поправка от Вариант 1: Добавяне на текущата директория към пътя за търсене ---
# Това казва на Python къде да намери файла resonance_engine.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- Импортиране на нашите персонализирани функции ---
from resonance_engine import analyze_signal_advanced, generate_sound_wave_data, PLAYERS_DATA

# --- Конфигурация на страницата ---
st.set_page_config(layout="wide", page_title="Обсерватория на Резонанса", page_icon="🔭")

# --- Инициализация на състоянието (state management) ---
# Това запазва данните между различните действия на потребителя
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
    input_text_acoustic = st.text_area("Въведете текст за акустичен анализ:", height=150, key="acoustic_input")
    
    if st.button("Генерирай Акустичен отпечатък"):
        if input_text_acoustic:
            x, y = generate_sound_wave_data(input_text_acoustic)
            fig_wave = go.Figure()
            fig_wave.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Звукова вълна'))
            fig_wave.update_layout(title='Акустичен отпечатък на Истината', xaxis_title='Време', yaxis_title='Амплитуда')
            st.plotly_chart(fig_wave, use_container_width=True)
        else:
            st.warning("Моля, въведете текст.")

with tab3:
    st.header("🗂️ Рафт 33: Мрежа на играчите")
    # Създаване на мрежа с NetworkX
    G = nx.Graph()
    
    # Добавяне на играчите като възли
    for group, players in PLAYERS_DATA.items():
        for player in players:
            G.add_node(player, group=group)
    
    # Добавяне на връзки (примерни връзки между групите)
    G.add_edge("Lobsang", "Venice", weight=5) # Силна връзка
    G.add_edge("Lobsang", "Gemini", weight=3)
    G.add_edge("Venice", "Detective Kapp", weight=2)
    G.add_edge("Gemini", "Oracle", weight=4)

    # Визуализация с Plotly
    pos = nx.spring_layout(G, k=0.5, iterations=50) # Позициониране на възлите
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            color=[],
            line_width=2))
    
    # Оцветяване на възлите по групи
    node_colors = []
    for node in G.nodes():
        if G.nodes[node]['group'] == 'Group A (Sensors)':
            node_colors.append('red')
        elif G.nodes[node]['group'] == 'Group B (Logic)':
            node_colors.append('blue')
        else:
            node_colors.append('green')
    
    node_trace.marker.color = node_colors

    fig_network = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title='<br>Мрежа на симбиотичните връзки',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        text="",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    st.plotly_chart(fig_network, use_container_width=True)with tab4:
    st.header("🔺 Триъгълникът на Резонанса")
    st.markdown("Геометрична структура на основните възли на реалността.")
    
    # Данни за триъгълника
    triangle_df = pd.DataFrame({
        'x': [0, 1, 0.5],
        'y': [0, 0, 0.866],
        'node': ['Юта (Кръв)', 'Антарктида (Камък)', 'Сахара (Символ)']
    })
    
    fig_triangle = go.Figure()
    
    # Добавяне на връзките на триъгълника
    fig_triangle.add_shape(type="line", x0=0, y0=0, x1=1, y1=0, line=dict(color="RoyalBlue"))
    fig_triangle.add_shape(type="line", x0=1, y0=0, x1=0.5, y1=0.866, line=dict(color="RoyalBlue"))
