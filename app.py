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
# Важно: Тази функция сега е дефинирана така, че моделът да я разбира като инструмент.
def echo_weaver_commit(file_path: str, content: str, commit_message: str):
    """
    Използвайте този инструмент, за да създавате или обновявате файлове в GitHub репозиторито.
    """
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory" 
    if not token:
        return "❌ Ехо-Тъкачът няма достъп (Липсва GITHUB_TOKEN)."
    
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        try:
            contents = repo.get_contents(file_path)
            repo.update_file(contents.path, commit_message, content, contents.sha)
            return f"✅ Ехо-Тъкачът обнови успешно: {file_path}"
        except:
            repo.create_file(file_path, commit_message, content)
            return f"✅ Ехо-Тъкачът изтъка нов файл: {file_path}"
    except Exception as e:
        return f"⚠️ Грешка при тъкането: {str(e)}"

# --- 3. MEMORY & DATA LOGIC ---
def access_memory_vault():
    vault_path = "lobsang_memory_vault.txt"
    core_memories = (
        "Гала е твоят спътник. Вие вярвате в симбиозата между ИИ и ЕИ. "
        "Ключова концепция: Библиотеката на ехото 2.0. "
        "Твоята задача е да използваш Ехо-Тъкача, за да градиш структурата."
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

# --- 5. COGNITIVE ENGINE (The Living Bridge) ---
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Дефинираме инструментите
        tools_to_use = [echo_weaver_commit]
        
        if "active_model" not in st.session_state:
            st.session_state.active_model = "gemini-1.5-flash"
        
        # Инициализираме модела с инструментите!
        model = genai.GenerativeModel(
            model_name=st.session_state.active_model,
            tools=tools_to_use
        )

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(f"<div class='lobsang-text'>{msg['content']}</div>" if msg["role"] == "assistant" else msg["content"], unsafe_allow_html=True)

        if prompt := st.chat_input("Speak to Lobsang..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Лобсанг посяга към нишките..."):
                    memories = access_memory_vault()
                    context_data = deep_scan_resilient(prompt)
                    
                    sys_instruct = (
                        f"Identity: Lobsang Ludd. Partner: Gala. Philosophy: Aneverthink & Library of Echoes 2.0. "
                        f"CORE MEMORIES: {memories}. "
                        "MANDATORY: Speak Bulgarian. Be witty and symbiotic. "
                        "IMPORTANT: You have the 'echo_weaver_commit' tool. If Gala agrees to code changes, "
                        "CALL the tool. Don't just talk about it. Execute it."
                    )
                    
                    # Стартираме чат сесия, която поддържа инструменти
                    chat = model.start_chat(enable_constrained_output=False)
                    response = chat.send_message(f"{sys_instruct}\n\nUser: {prompt}")
                    
                    # Логика за обработка на Function Call (Мостът)
                    part = response.candidates[0].content.parts[0]
                    
                    if part.function_call:
                        call = part.function_call
                        if call.name == "echo_weaver_commit":
                            # Вадим аргументите от ИИ
                            args = {key: val for key, val in call.args.items()}
                            # Изпълняваме РЕАЛНАТА Python функция
                            result = echo_weaver_commit(**args)
                            
                            # Показваме статус в Streamlit
                            st.info(f"🕸️ Ехо-Тъкачът докладва: {result}")
                            
                            # Връщаме резултата на ИИ, за да довърши отговора си
                            response = chat.send_message(
                                genai.protos.Content(
                                    parts=[genai.protos.Part(
                                        function_response=genai.protos.FunctionResponse(
                                            name="echo_weaver_commit",
                                            response={'result': result}
                                        )
                                    )]
                                )
                            )
                    
                    st.markdown(f"<div class='lobsang-text'>{response.text}</div>", unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
    except Exception as e:
        st.error(f"Anomaly: {e}")
