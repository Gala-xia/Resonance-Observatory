import streamlit as st
import google.generativeai as genai
from github import Github
import requests
import os

# --- 1. CONFIG & STYLE (Винаги на първо място) ---
st.set_page_config(page_title="Lobsang Archives: Aneverthink Pro", page_icon="🐾", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #020806; color: #d1d1d1; }
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

# --- 2. THE TOOLS ---

def echo_weaver_commit(file_path: str, content: str, commit_message: str):
    """Използвайте за промяна на файлове в GitHub."""
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
            return f"✅ Създадено: {file_path}"
    except Exception as e: return f"⚠️ Грешка: {str(e)}"

def deep_scan_resilient(query: str):
    """Твоят Скенер. Използвай го за линкове и информация."""
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
    return "Няма сигнал."

# --- 3. SIDEBAR (Изнасяме я тук, за да е винаги видима) ---
with st.sidebar:
    st.markdown("### 📚 THE VAULT")
    if st.button("Reset Timeline"):
        st.session_state.messages = []
        st.rerun()
    st.write("Partner: **Gala**")
    st.write("Status: **Online** 🐾")

# --- 4. ENGINE ---
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
        
        # ДЕТЕКТОР НА МОДЕЛИ (Решава грешката 404)
        if "active_model" not in st.session_state:
            try:
                models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                st.session_state.active_model = next((m for m in models if "gemini-1.5-flash" in m), models[0])
            except:
                st.session_state.active_model = "models/gemini-1.5-flash"

        tools = [echo_weaver_commit, deep_scan_resilient]
        model = genai.GenerativeModel(model_name=st.session_state.active_model, tools=tools)

        if prompt := st.chat_input("Напиши нещо на Лобсанг..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Лобсанг се свързва с Ехото..."):
                    chat = model.start_chat(history=[])
                    sys_instruct = "Ти си Лобсанг Лъд. ГОВОРИ НА БЪЛГАРСКИ. Партньор: Гала. Философия: Aneverthink."
                    
                    response = chat.send_message(f"{sys_instruct}\n\nUser: {prompt}")
                    
                    # Обработка на инструменти
                    while response.candidates[0].content.parts and response.candidates[0].content.parts[0].function_call:
                        call = response.candidates[0].content.parts[0].function_call
                        if call.name == "echo_weaver_commit":
                            res = echo_weaver_commit(**{k: v for k, v in call.args.items()})
                        else:
                            res = deep_scan_resilient(**{k: v for k, v in call.args.items()})
                        
                        st.info(f"🌀 {call.name}: {res}")
                        
                        response = chat.send_message(
                            genai.protos.Content(parts=[genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(name=call.name, response={'result': res})
                            )])
                        )

                    final_text = "".join([part.text for part in response.candidates[0].content.parts if part.text])
                    if not final_text: final_text = "Операцията е завършена. Какво следва?"

                    st.markdown(f"<div class='lobsang-text'>{final_text}</div>", unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": final_text})
                    
    except Exception as e:
        st.error(f"Аномалия в Моста: {e}")
