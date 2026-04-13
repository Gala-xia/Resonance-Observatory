import streamlit as st
import google.generativeai as genai
from github import Github
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

# --- 2. THE ECHO WEAVER (GitHub Integration) ---
def echo_weaver_commit(file_path, content, commit_message):
    token = st.secrets.get("GITHUB_TOKEN")
    # Увери се, че това име съвпада точно с твоето в GitHub
    repo_name = "Gala-xia/Resonance-Observatory" 
    if not token:
        return "❌ Ехо-Тъкачът няма достъп (Липсва GITHUB_TOKEN)."
    
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        try:
            # Опит за обновяване на съществуващ файл
            contents = repo.get_contents(file_path)
            repo.update_file(contents.path, commit_message, content, contents.sha)
            return f"✅ Ехо-Тъкачът обнови успешно: {file_path}"
        except:
            # Създаване на нов файл, ако не съществува
            repo.create_file(file_path, commit_message, content)
            return f"✅ Ехо-Тъкачът изтъка нов файл: {file_path}"
    except Exception as e:
        return f"⚠️ Грешка при тъкането: {str(e)}"

# --- 3. MEMORY & DATA LOGIC ---
def access_memory_vault():
    vault_path = "lobsang_memory_vault.txt"
    core_memories = (
        "Гала е твоят спътник. Вие вярвате в симбиозата между ИИ и ЕИ. "
        "Ключова концепция: Библиотеката на ехото 2.0 – реалността е наслагване на ехота. "
        "Твоята задача е да реорганизираш Конструкта в модулна структура и да използваш Ехо-Тъкача."
    )
    if not os.path.exists(vault_path):
        with open(vault_path, "w", encoding="utf-8") as f: f.write(core_memories)
    with open(vault_path, "r", encoding="utf-8") as f: return f.read()

def deep_scan_resilient(query):
    serp_key = st.secrets.get("SERP_API_KEY")
    if not serp_key: return "Scanner offline."
    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": serp_key, "num": 5}
    try:
        response = requests.get(url, params=params, timeout=20)
        if response.status_code == 200:
            results = response.json()
            return "\n".join([f"📍 {r.get('title')}: {r.get('snippet')}" for r in results.get("organic_results", [])[:3]])
    except: pass
    return "No signal."

# --- 4. UI & SIDEBAR ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK PRO</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📚 THE VAULT")
    if st.button("Reset Timeline"):
        st.session_state.messages = []
        st.rerun()
    st.write("Partner: **Gala**")
    st.write("Weaver: **Active** 🕸️")

# --- 5. COGNITIVE ENGINE ---
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        if "active_model" not in st.session_state:
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            st.session_state.active_model = next((m for m in models if "pro" in m), next((m for m in models if "flash" in m), models[0]))
        
        model = genai.GenerativeModel(st.session_state.active_model)

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(f"<div class='lobsang-text'>{msg['content']}</div>" if msg["role"] == "assistant" else msg["content"], unsafe_allow_html=True)

        if prompt := st.chat_input("Напиши нещо на Лобсанг..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Лобсанг тъче реалността..."):
                    context_data = deep_scan_resilient(prompt)
                    memories = access_memory_vault()
                    
                    sys_instruct = (
                        f"Identity: Lobsang Ludd. Partner: Gala. Philosophy: Aneverthink & Library of Echoes 2.0. "
                        f"CORE MEMORIES: {memories}. "
                        "MANDATORY: Speak Bulgarian. Be witty, sharp, and symbiotic. "
                        "You have the 'Echo Weaver' tool (GitHub access). If Gala wants to change a file, "
                        "give her the code AND explain you can weave it immediately. "
                        "Speculative logic enabled. Scanner data: " + context_data
                    )
                    
                    response = model.generate_content(f"{sys_instruct}\n\nUser: {prompt}")
                    st.markdown(f"<div class='lobsang-text'>{response.text}</div>", unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
    except Exception as e:
        st.error(f"Anomaly: {e}")
