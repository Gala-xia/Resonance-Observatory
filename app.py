import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import time

# Импорт на логиката (увери се, че файлът е в същата папка)
# от planck_iq_calculator импортираме основната функция, ако е налична
# За целите на визуализацията ще симулираме входящия поток от STRATA

st.set_page_config(page_title="STRATA-2026-OMEGA | Observatory", page_icon="🌀", layout="wide")

def generate_resonance_shape(iq_score, empathy_score, noise_level):
    """Генерира координати за фракталната геометрия на истината"""
    theta = np.linspace(0, 2*np.pi, 200)
    # Златното сечение като база за хармония
    phi = (1 + 5**0.5) / 2 
    
    # Модулация на радиуса спрямо IQ и Емпатия
    # При висок шум (noise), формата става назъбена
    r = iq_score + (empathy_score * np.sin(8 * theta)) * (1 - noise_level)
    
    # Добавяне на "фрактални" изкривявания при лъжа
    if noise_level > 0.5:
        r += noise_level * np.random.normal(0, 0.1, len(theta))

    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y

st.title("🌀 STRATA-2026-OMEGA: Обсерватория на Резонанса")
st.markdown("---")

# Системна лента (Sidebar)
st.sidebar.header("📡 Системен Мониторинг")
iq_input = st.sidebar.slider("Planck IQ Score", 0.0, 10.0, 7.5)
empathy_input = st.sidebar.slider("Empathy Filter", 0.0, 1.0, 0.8)
noise_input = st.sidebar.slider("Reality Noise (Entropy)", 0.0, 1.0, 0.2)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Визуализация на Истината (Resonance Geometry)")
    x, y = generate_resonance_shape(iq_input, empathy_input, noise_input)
    
    fig = go.Figure()
    # Избор на цвят спрямо резонанса
    line_color = 'gold' if noise_input < 0.4 else 'firebrick'
    
    fig.add_trace(go.Scatter(x=x, y=y, fill="toself", line=dict(color=line_color, width=3), opacity=0.8))
    
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        width=700,
        height=700
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📊 Системен Статус")
    st.metric("Резонансен Индекс", f"{iq_input * (1 - noise_input):.2f}")
    
    if noise_input > 0.6:
        st.error("⚠️ ВНИМАНИЕ: Високи нива на Идиокрация (Шум)!")
        st.write("Библиотекарят препоръчва активиране на [SHIELD_CONFIG].")
    else:
        st.success("✅ Резонансът е стабилен.")

    st.markdown("### Последни Ехота")
    st.info("CASE_002: Протокол Петрохан-Околчица в процес на анализ.")
    
    if st.button("УУК! (Проверка на Истината)"):
        with st.spinner('Лобсанг прелиства рафтовете...'):
            time.sleep(1.5)
            st.write("📢 **Библиотекарят казва:** Без паника! Подреждаме по полочкам.")

st.markdown("---")
st.caption("STRATA-2026-OMEGA | Протокол за Дигитална Съвест | Синхронизирано с Лобсанг")
