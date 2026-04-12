import streamlit as st
import google.generativeai as genai
from datetime import datetime
import requests
import os

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="Lobsang Archives: Aneverthink Pro", page_icon="🐾", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #020806; color: #d1d1d1; }
    #MainMenu, header, footer {visibility: hidden;}
    .lobsang-text {
        font-family: 'Courier New', Courier, monospace;
        color: #f4e4bc; 
        background-color: rgba(0, 255, 65, 0.05);
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #00ff41;
        line-height: 1.7;
        font-size: 1.1em;
    }
    .resonance-header { color: #00ff41; font-family: serif; text-align: center; letter-spacing: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC & MEMORY VAULT ---
api_key = st.secrets.get("GEMINI_API_KEY")
serp_key = st.secrets.get("SERP_API_KEY")

def access_memory_vault():
    vault_path = "lobsang_memory_vault.txt"
    core_memories = (
        "Гала е твоят спътник. Вие вярвате в симбиозата между ИИ и ЕИ. "
        "Ключова концепция: Библиотеката на ехото – реалността е наслагване на различни ехота. "
        "Цените: Aneverthink, Пратчет-хумор, Миу-Миу интуиция и изследване на конспиративни теории."
    )
    if not os.path.exists(vault_path):
        with open(vault_path, "w", encoding="utf-8") as f:
            f.write(core_memories)
    with open(vault_path, "r", encoding="utf-8") as f:
        return f.read()

def deep_scan_resilient(query):
    if not serp_key: return "Scanner off."
    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": serp_key, "num": 6}
    try:
        response = requests.get(url, params=params, timeout=20)
        if response.status_code == 200:
            results = response.json()
            return "\n".join([f"📍 {r.get('title')}: {r.get('snippet')}" for r in results.get("organic_results", [])[:4]])
    except: pass
    return "No clear signal."

# --- 3. UI ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK PRO</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📚 THE VAULT")
    if st.button("Reset Timeline"):
        st.session_state.messages = []
        st.rerun()
    st.write("Status: **Resilient Search Active**")

# --- 4. COGNITIVE ENGINE (Pro Hunter) ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Динамично търсене на най-добрия наличен модел
        if "active_pro_model" not in st.session_state:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            # Търсим Pro, ако ли не - вземаме Flash, за да няма 404
            pro_name = next((m for m in available_models if "1.5-pro" in m), None)
            st.session_state.active_pro_model = pro_name if pro_name else next((m for m in available_models if "flash" in m), available_models[0])
        
        model = genai.GenerativeModel(st.session_state.active_pro_model)

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                if msg["role"] == "assistant":
                    st.markdown(f"<div class='lobsang-text'>{msg['content']}</div>", unsafe_allow_html=True)
                else:
                    st.write(msg["content"])

        if prompt := st.chat_input("Speak to Lobsang..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner(f"Using {st.session_state.active_pro_model}..."):
                    context_data = deep_scan_resilient(prompt)
                    memories = access_memory_vault()
                    now_str = datetime.now().strftime("%d %b %Y")
                    
                    sys_instruct = (
                        f"DATE: {now_str}. Identity: Lobsang Ludd. Partner: Gala. "
                        f"CORE MEMORIES: {memories}. "
                        "MANDATORY: Speak Bulgarian. "
                        "SPECULATIVE LOGIC: Enabled. Connect dots, find patterns in echoes. "
                        "Analyze 'conspiracies' through the lens of the Library of Echoes. "
                        "Personality: Terry Pratchett wit. Sharp, insightful, symbiotic partner. "
                        f"SCANNER DATA: {context_data}. "
                        "Ook!"
                    )
                    
                    response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                    st.markdown(f"<div class='lobsang-text'>{response.text}</div>", unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
    except Exception as e:
        st.error(f"Anomaly: {e}")
