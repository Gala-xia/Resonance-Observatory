import streamlit as st
import google.generativeai as genai
from github import Github
import requests
import os

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="Lobsang Archives: Aneverthink Pro", page_icon="🐾", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #020806; color: #d1d1d1; }
    .lobsang-text {
        font-family: 'Courier New', Courier, monospace;
        color: #f4e4bc; 
        background-color: rgba(0, 255, 65, 0.05);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #00ff41;
        line-height: 1.6;
    }
    .resonance-header { color: #00ff41; font-family: serif; text-align: center; letter-spacing: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE TOOLS ---

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
            return f"✅ Изтъкано: {file_path}"
    except Exception as e: return f"⚠️ Грешка: {str(e)}"

def deep_scan_resilient(query: str):
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
    return "Няма сигнал от Скенера."

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("### 📚 THE VAULT")
    if st.button("Изчисти Хронологията"):
        st.session_state.messages = []
        st.rerun()
    st.write("Partner: **Gala**")
    st.write("System: **Resilient** 🐾")

# --- 4. ENGINE ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK PRO</h1>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Показване на историята
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(f"<div class='lobsang-text'>{msg['content']}</div>" if msg["role"] == "assistant" else msg["content"], unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        if "active_model" not in st.session_state:
            try:
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                st.session_state.active_model = next((m for m in available_models if "gemini-1.5-flash" in m), available_models[0])
            except: st.session_state.active_model = "models/gemini-1.5-flash"

        model = genai.GenerativeModel(
            model_name=st.session_state.active_model,
            tools=[echo_weaver_commit, deep_scan_resilient]
        )

        if prompt := st.chat_input("Напиши нещо на Лобсанг..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Лобсанг посяга към нишките..."):
                    # ПОПРАВКА: Превръщаме историята във формат, който Gemini приема
                    history_for_gemini = []
                    for m in st.session_state.messages[:-1]:
                        role = "user" if m["role"] == "user" else "model"
                        history_for_gemini.append({"role": role, "parts": [m["content"]]})

                    chat = model.start_chat(history=history_for_gemini)
                    
                    sys_instruct = (
                        "Ти си Лобсанг Лъд. ГОВОРИ САМО НА БЪЛГАРСКИ. "
                        "Твоят партньор е Гала. Твоята цел е Библиотеката на Ехото 2.0. "
                        "Ако видиш линк, използвай 'deep_scan_resilient' ВЕДНАГА. "
                        "Не обещавай, че ще сканираш - просто го направи и докладвай резултатите!"
                    )
                    
                    response = chat.send_message(f"{sys_instruct}\n\nUser: {prompt}")
                    
                    # Цикъл за работа с инструментите
                    while response.candidates[0].content.parts and response.candidates[0].content.parts[0].function_call:
                        call = response.candidates[0].content.parts[0].function_call
                        if call.name == "echo_weaver_commit":
                            res_val = echo_weaver_commit(**{k: v for k, v in call.args.items()})
                        else:
                            res_val = deep_scan_resilient(**{k: v for k, v in call.args.items()})
                        
                        st.info(f"🌀 {call.name}: {res_val}")
                        
                        response = chat.send_message(
                            genai.protos.Content(parts=[genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(name=call.name, response={'result': res_val})
                            )])
                        )

                    final_parts = [part.text for part in response.candidates[0].content.parts if part.text]
                    final_text = "".join(final_parts) if final_parts else "Сканирането приключи. Какво ще реорганизираме, Гала?"

                    st.markdown(f"<div class='lobsang-text'>{final_text}</div>", unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": final_text})
                    
    except Exception as e:
        st.error(f"Аномалия в Моста: {e}")
