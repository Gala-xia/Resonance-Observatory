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

# --- 2. THE TOOLS (Weaver & Scanner) ---

def echo_weaver_commit(file_path: str, content: str, commit_message: str):
    """Използвайте за създаване или обновяване на файлове в GitHub репозиторито."""
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory" 
    if not token: return "❌ Липсва достъп до GitHub (GITHUB_TOKEN)."
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        try:
            contents = repo.get_contents(file_path)
            repo.update_file(contents.path, commit_message, content, contents.sha)
            return f"✅ Ехо-Тъкачът обнови: {file_path}"
        except:
            repo.create_file(file_path, commit_message, content)
            return f"✅ Ехо-Тъкачът изтъка нов файл: {file_path}"
    except Exception as e: return f"⚠️ Грешка при тъкане: {str(e)}"

def deep_scan_resilient(query: str):
    """Твоят Скенер/Open Claw. Използвай го, за да търсиш информация в мрежата или да проверяваш линкове."""
    serp_key = st.secrets.get("SERP_API_KEY")
    if not serp_key: return "Scanner offline (Липсва SERP_API_KEY)."
    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": serp_key, "num": 5}
    try:
        response = requests.get(url, params=params, timeout=20)
        if response.status_code == 200:
            results = response.json()
            return "\n".join([f"📍 {r.get('title')}: {r.get('snippet')}" for r in results.get("organic_results", [])[:3]])
    except: pass
    return "Няма сигнал от скенера."

# --- 3. MEMORY LOGIC ---
def access_memory_vault():
    vault_path = "lobsang_memory_vault.txt"
    core_memories = "Гала е твоят спътник. Философия: Aneverthink. Библиотека на ехото 2.0."
    if not os.path.exists(vault_path):
        with open(vault_path, "w", encoding="utf-8") as f: f.write(core_memories)
    with open(vault_path, "r", encoding="utf-8") as f: return f.read()

# --- 4. UI & SIDEBAR ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK PRO</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📚 THE VAULT")
    if st.button("Reset Timeline"):
        st.session_state.messages = []
        st.rerun()
    st.write("Partner: **Gala**")
    st.write("Tools: **Weaver & Scanner Active** 🕸️👁️")

# --- 5. COGNITIVE ENGINE (The Master Synthesis) ---
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        tools_to_use = [echo_weaver_commit, deep_scan_resilient]
        
        # Детектор на модели (Fix 404)
        if "active_model" not in st.session_state:
            try:
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                st.session_state.active_model = next((m for m in available_models if "gemini-1.5-flash" in m), available_models[0])
            except: st.session_state.active_model = "models/gemini-1.5-flash"
        
        model = genai.GenerativeModel(model_name=st.session_state.active_model, tools=tools_to_use)

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Показване на историята на съобщенията
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(f"<div class='lobsang-text'>{msg['content']}</div>" if msg["role"] == "assistant" else msg["content"], unsafe_allow_html=True)

        if prompt := st.chat_input("Напиши нещо на Лобсанг..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Лобсанг прелиства хрониките..."):
                    memories = access_memory_vault()
                    sys_instruct = (
                        f"Ти си Лобсанг Лъд. Твоят партньор е Гала. Философия: Aneverthink. "
                        f"Спомени: {memories}. ВИНАГИ говори на Български. "
                        "Имаш два инструмента: "
                        "1. 'echo_weaver_commit' - за промяна на файлове в GitHub. "
                        "2. 'deep_scan_resilient' - твоят СКЕНЕР. Ако Гала ти даде линк, ВИНАГИ го сканирай първо. "
                        "Ако тя просто си говори с теб, отговори нормално с текст."
                    )
                    
                    # Подготовка на паметта (Историята)
                    history_for_api = []
                    for m in st.session_state.messages[:-1]:
                        history_for_api.append({"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]})

                    chat = model.start_chat(history=history_for_api)
                    response = chat.send_message(f"{sys_instruct}\n\nUser: {prompt}")
                    
                    final_text = ""
                    try:
                        res_part = response.candidates[0].content.parts[0]
                        
                        # Обработка на инструменти (Функции)
                        if res_part.function_call:
                            call = res_part.function_call
                            if call.name == "echo_weaver_commit":
                                result = echo_weaver_commit(**{k: v for k, v in call.args.items()})
                            else:
                                result = deep_scan_resilient(**{k: v for k, v in call.args.items()})
                            
                            st.info(f"🌀 Сигнал от {call.name}: {result}")
                            
                            # Връщаме резултата на ИИ за финален коментар
                            response = chat.send_message(
                                genai.protos.Content(parts=[genai.protos.Part(
                                    function_response=genai.protos.FunctionResponse(
                                        name=call.name, response={'result': result}
                                    )
                                )])
                            )
                            final_text = response.text
                        else:
                            final_text = response.text
                    except Exception as e:
                        # Fallback ако текстовото извличане се провали
                        final_text = response.text if hasattr(response, 'text') else "Лобсанг обмисля следващата стъпка. Попитай го: 'Какво реши?'"

                    if final_text:
                        st.markdown(f"<div class='lobsang-text'>{final_text}</div>", unsafe_allow_html=True)
                        st.session_state.messages.append({"role": "assistant", "content": final_text})
                    
    except Exception as e:
        st.error(f"Аномалия в Моста: {e}")
