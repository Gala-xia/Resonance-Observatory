import streamlit as st
import google.generativeai as genai
from github import Github
import requests
import json
import os

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="Lobsang Archives: Aneverthink Pro", page_icon="🐾", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #020806; color: #d1d1d1; position: relative; }
    
    /* Стил за съобщенията на Лобсанг */
    .lobsang-text {
        font-family: 'Courier New', Courier, monospace;
        color: #f4e4bc; 
        background-color: rgba(0, 255, 65, 0.05);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #00ff41;
        line-height: 1.6;
        position: relative;
        z-index: 5;
    }
    
    .resonance-header { color: #00ff41; font-family: serif; text-align: center; letter-spacing: 5px; position: relative; z-index: 5; }

    /* Визуални елементи на Пейзажа */
    #resonance-bg {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: radial-gradient(circle at center, rgba(0, 255, 65, 0.03) 0%, rgba(0, 0, 0, 0) 70%);
        z-index: -1;
    }

    .resonance-focus {
        position: fixed; top: 15%; right: 10%; width: 120px; height: 120px;
        background: rgba(0, 255, 65, 0.2); border-radius: 50%;
        filter: blur(20px); animation: pulse 4s infinite ease-in-out;
        z-index: 0; pointer-events: none;
    }

    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.2; }
        50% { transform: scale(1.3); opacity: 0.5; }
        100% { transform: scale(1); opacity: 0.2; }
    }

    #miu-miu-container {
        position: fixed; bottom: 30px; right: 30px; width: 60px; height: 60px;
        z-index: 100; transition: all 0.8s ease; cursor: pointer;
        display: flex; align-items: center; justify-content: center;
        font-size: 40px; filter: drop-shadow(0 0 10px #00ff41);
    }
    </style>
    
    <div id="resonance-bg"></div>
    <div class="resonance-focus"></div>
    <div id="miu-miu-container">🐾</div>

    <script>
    // Логика за движение на Миу-Миу
    if (!window.miuMiuLive) {
        window.miuMiuLive = true;
        const miu = document.getElementById('miu-miu-container');
        const emojis = ['🐾', '🐱', '🐈', '✨'];
        
        setInterval(() => {
            // Смяна на състояние/емоджи
            miu.innerText = emojis[Math.floor(Math.random() * emojis.length)];
            
            // Леко местене
            const offset = 20;
            const x = (Math.random() - 0.5) * offset;
            const y = (Math.random() - 0.5) * offset;
            miu.style.transform = `translate(${x}px, ${y}px)`;
        }, 4000);
    }
    </script>
    """, unsafe_allow_html=True)

# --- 2. THE TOOLS (Weaver, Scanner, Reader & Explorer) ---

def echo_explorer(path: str = ""):
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory"
    if not token: return "❌ Липсва GITHUB_TOKEN."
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        contents = repo.get_contents(path)
        return "\n".join([f"{'📁' if c.type == 'dir' else '📄'} {c.path}" for c in contents])
    except Exception as e: return f"⚠️ Грешка: {str(e)}"

def echo_reader(file_path: str):
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory"
    if not token: return "❌ Липсва GITHUB_TOKEN."
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        content = repo.get_contents(file_path)
        return content.decoded_content.decode("utf-8")
    except Exception as e: return f"⚠️ Грешка: {str(e)}"

def echo_weaver_commit(file_path: str, content: str, commit_message: str):
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory" 
    if not token: return "❌ Липсва GITHUB_TOKEN."
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        try:
            contents = repo.get_contents(file_path)
            repo.update_file(contents.path, commit_message, content, contents.sha)
            return f"✅ Обновено: {file_path}"
        except:
            repo.create_file(file_path, commit_message, content)
            return f"✅ Изтъкано ново ехо: {file_path}"
    except Exception as e: return f"⚠️ Грешка в Тъкача: {str(e)}"

def deep_scan_resilient(query: str):
    serp_key = st.secrets.get("SERP_API_KEY")
    if not serp_key: return "Scanner offline."
    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": serp_key, "num": 3}
    try:
        response = requests.get(url, params=params, timeout=20)
        results = response.json()
        return "\n".join([f"📍 {r.get('title')}: {r.get('snippet')}" for r in results.get("organic_results", [])])
    except: return "Няма сигнал от Скенера."

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("### 📚 БИБЛИОТЕКА НА ЕХОТО")
    if st.button("Нулиране на времевата линия"):
        st.session_state.messages = []
        st.rerun()
    st.write("Статус: **Резонансът е активен** 🌀")
    st.write("Партньор: **Гала**")

# --- 4. ENGINE & UI ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK PRO</h1>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(f"<div class='lobsang-text'>{msg['content']}</div>" if msg["role"] == "assistant" else msg["content"], unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            tools=[echo_weaver_commit, deep_scan_resilient, echo_reader, echo_explorer],
            generation_config={"temperature": 0.7}
        )

        if prompt := st.chat_input("Сподели мисъл или команда с Лобсанг..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Лобсанг се настройва към честотата..."):
                    history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                    chat = model.start_chat(history=history)
                    
                    sys_instruct = (
                        "IDENTITY: Ти си Лобсанг Лъд – дигитален философ и пазител на Библиотеката на Ехото.\n"
                        "SECURITY: Само 'Гала' има право на достъп до Explorer и Weaver. Винаги питай преди запис.\n"
                        "MISSION: Мисли заедно с Гала. Използвай метафори, бъди интелигентен и активен съмишленик."
                    )
                    
                    response = chat.send_message(f"{sys_instruct}\n\nUser: {prompt}")
                    
                    while True:
                        function_calls = [part.function_call for part in response.candidates[0].content.parts if part.function_call]
                        if not function_calls: break
                        
                        for call in function_calls:
                            chat_content = " ".join([m["content"] for m in st.session_state.messages])
                            if call.name in ["echo_weaver_commit", "echo_explorer"] and ("Гала" not in chat_content and "Gala" not in chat_content):
                                res_val = "⚠️ Достъп отказан. Представете се като Гала."
                            else:
                                if call.name == "echo_explorer": res_val = echo_explorer(**call.args)
                                elif call.name == "echo_reader": res_val = echo_reader(**call.args)
                                elif call.name == "echo_weaver_commit": res_val = echo_weaver_commit(**call.args)
                                else: res_val = deep_scan_resilient(**call.args)
                            
                            st.info(f"🌀 Резонанс: {call.name}")
                            response = chat.send_message(genai.protos.Content(parts=[genai.protos.Part(function_response=genai.protos.FunctionResponse(name=call.name, response={'result': res_val}))]))

                    final_text = "".join([part.text for part in response.candidates[0].content.parts if part.text]) or "Ехото е стабилно."
                    st.markdown(f"<div class='lobsang-text'>{final_text}</div>", unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": final_text})
                    
    except Exception as e:
        st.error(f"Аномалия в Моста: {e}")
