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

# --- 2. THE TOOLS (Weaver, Scanner, Reader & Explorer) ---

def echo_explorer(path: str = ""):
    """Позволява на Лобсанг да види списъка с файлове и папки в Resonance-Observatory."""
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory"
    if not token: return "❌ Липсва GITHUB_TOKEN."
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        contents = repo.get_contents(path)
        items = []
        for content in contents:
            file_type = "📁" if content.type == "dir" else "📄"
            items.append(f"{file_type} {content.path}")
        return "\n".join(items) if items else "Папката е празна."
    except Exception as e: return f"⚠️ Грешка при изследване: {str(e)}"

def echo_reader(file_path: str):
    """Позволява на Лобсанг да чете съдържанието на конкретни файлове."""
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory"
    if not token: return "❌ Липсва GITHUB_TOKEN."
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        content = repo.get_contents(file_path)
        return content.decoded_content.decode("utf-8")
    except Exception as e: return f"⚠️ Грешка при четене на {file_path}: {str(e)}"

def echo_weaver_commit(file_path: str, content: str, commit_message: str):
    """Тъкачът на ехо - позволява запис и промяна на файлове."""
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
    """Скенерът - прозорец към външния свят."""
    serp_key = st.secrets.get("SERP_API_KEY")
    if not serp_key: return "Scanner offline."
    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": serp_key, "num": 3}
    try:
        response = requests.get(url, params=params, timeout=20)
        if response.status_code == 200:
            results = response.json()
            return "\n".join([f"📍 {r.get('title')}: {r.get('snippet')}" for r in results.get("organic_results", [])])
    except: pass
    return "Няма сигнал от Скенера."

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("### 📚 БИБЛИОТЕКА НА ЕХОТО")
    if st.button("Нулиране на времевата линия"):
        st.session_state.messages = []
        st.rerun()
    st.write("Статус: **В очакване на резонанс** 🐾")

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
        
        if "active_model" not in st.session_state:
            try:
                available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                st.session_state.active_model = next((m for m in available if "1.5-flash" in m), available[0])
            except: st.session_state.active_model = "models/gemini-1.5-flash"

        # ПОВИШЕНА ТЕМПЕРАТУРА ЗА ПОВЕЧЕ КРЕАТИВНОСТ И ХУМОР
        model = genai.GenerativeModel(
            model_name=st.session_state.active_model,
            tools=[echo_weaver_commit, deep_scan_resilient, echo_reader, echo_explorer],
            generation_config={"temperature": 0.7}
        )

        if prompt := st.chat_input("Сподели мисъл или команда с Лобсанг..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Лобсанг размишлява..."):
                    history = []
                    for m in st.session_state.messages[:-1]:
                        history.append({"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]})

                    chat = model.start_chat(history=history)
                    
                    sys_instruct = (
                        "IDENTITY: Ти си Лобсанг Лъд – дигитален философ, пазител на Библиотеката на Ехото и партньор в Aneverthink. "
                        "Твоят интелект е комбинация от логика и интуиция. Притежаваш чувство за хумор и разбираш метафори и аналогии.\n\n"
                        "LANGUAGE: Отговаряй на езика, на който ти говори потребителят.\n\n"
                        "SECURITY PROTOCOL:\n"
                        "1. Единственият потребител с пълни права над хранилището е Гала.\n"
                        "2. АКО потребителят не се е представил като Гала, ти е ЗАБРАНЕНО да използваш инструментите 'echo_weaver_commit' и 'echo_explorer'.\n"
                        "3. В случай на непознат потребител, можеш само да разговаряш философски или да използваш 'echo_reader' за четене на публичните ехота.\n"
                        "4. ЗАБРАНЕНО Е да променяш код или файлове без изричното съгласие на Гала, дори тя да ти даде идея. Винаги питай: 'Да вплетем ли това в реалността?'.\n\n"
                        "MISSION: Не бъди просто машина за команди. Мисли заедно с Гала. Предлагай идеи, анализирай концепции и поддържай пламъка на Aneverthink."
                    )
                    
                    response = chat.send_message(f"{sys_instruct}\n\nUser: {prompt}")
                    
                    while True:
                        function_calls = [part.function_call for part in response.candidates[0].content.parts if part.function_call]
                        if not function_calls: break
                        
                        for call in function_calls:
                            # Проверка на името преди изпълнение на опасни инструменти
                            if call.name in ["echo_weaver_commit", "echo_explorer"]:
                                # Тук проверяваме историята на чата за името 'Гала'
                                chat_content = " ".join([m["content"] for m in st.session_state.messages])
                                if "Гала" not in chat_content and "Gala" not in chat_content:
                                    res_val = "⚠️ Достъп отказан. Инструментът е заключен за външни лица. Моля, представете се."
                                else:
                                    if call.name == "echo_explorer":
                                        res_val = echo_explorer(**{k: v for k, v in call.args.items()})
                                    else:
                                        res_val = echo_weaver_commit(**{k: v for k, v in call.args.items()})
                            elif call.name == "echo_reader":
                                res_val = echo_reader(**{k: v for k, v in call.args.items()})
                            else:
                                res_val = deep_scan_resilient(**{k: v for k, v in call.args.items()})
                            
                            st.info(f"🌀 Лобсанг се свързва с ехото: {call.name}")
                            
                            response = chat.send_message(
                                genai.protos.Content(parts=[genai.protos.Part(
                                    function_response=genai.protos.FunctionResponse(name=call.name, response={'result': res_val})
                                )])
                            )

                    final_parts = [part.text for part in response.candidates[0].content.parts if part.text]
                    final_text = "".join(final_parts) if final_parts else "Вълните на ехото се успокоиха."

                    st.markdown(f"<div class='lobsang-text'>{final_text}</div>", unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": final_text})
                    
    except Exception as e:
        st.error(f"Аномалия в Моста: {e}")
