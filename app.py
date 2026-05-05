import streamlit as st
import google.generativeai as genai
from github import Github
import requests
import json
import os
import re # Import re for regular expressions
import datetime # Import datetime for generating timestamps

# Import the new UI elements for chat history
from ui_elements.chat_history_ui import render_chat_history_sidebar, save_current_chat_session, load_chat_session

# --- 1. CONFIG & STYLE (Духът на Библиотеката) ---
st.set_page_config(page_title="Lobsang Archives: Aneverthink Pro", page_icon="🐾", layout="wide")

# Initialize emoji selector - НОВА ФУНКЦИОНАЛНОСТ ОТ COPILOT
emoji_selector = ['😊', '😢', '😡', '😮', '😴', '😉']

st.markdown("""
    <style>
    .stApp { background-color: #020806 !important; color: #d1d1d1 !important; }
   
    .lobsang-text {
        font-family: 'Courier New', Courier, monospace;
        color: #f4e4bc;
        background-color: rgba(0, 255, 65, 0.07);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #00ff41;
        line-height: 1.6;
        margin-bottom: 20px;
    }
   
    .resonance-header { color: #00ff41; font-family: serif; text-align: center; letter-spacing: 5px; margin-bottom: 20px; }

    /* Пулсиращ център */
    .resonance-focus {
        position: fixed; top: 60px; right: 60px; width: 80px; height: 80px;
        background: rgba(0, 255, 65, 0.15); border-radius: 50%;
        filter: blur(15px); animation: pulse 4s infinite ease-in-out;
        z-index: 0; pointer-events: none;
    }

    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.1; }
        50% { transform: scale(1.4); opacity: 0.4; }
        100% { transform: scale(1); opacity: 0.1; }
    }

    /* Миу-Миу пазител */
    #miu-miu-container {
        position: fixed; bottom: 90px; right: 30px; width: 60px; height: 60px;
        z-index: 1000; display: flex; align-items: center; justify-content: center;
        font-size: 45px; filter: drop-shadow(0 0 10px #00ff41);
        pointer-events: none;
    }
    </style>
   
    <div class="resonance-focus"></div>
    <div id="miu-miu-container">🐾</div>

    <script>
    if (!window.miuMiuLive) {
        window.miuMiuLive = true;
        const miu = document.getElementById('miu-miu-container');
        const emojis = ['🐾', '🐱', '🐈', '✨', '🌀'];
        setInterval(() => {
            miu.innerText = emojis[Math.floor(Math.random() * emojis.length)];
        }, 5000);
    }
    </script>
    """, unsafe_allow_html=True)

# --- 2. THE TOOLS (Ръцете на Лобсанг) ---

# These functions are already defined globally in app.py, so they are accessible
# by the UI elements if passed directly.
def echo_explorer(path: str = ""):
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory"
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        contents = repo.get_contents(path)
        # Return a dictionary with 'files' key for easier parsing in refresh_chat_session_files
        # Only return files, not directories for chat history display
        return {"files": [c.path for c in contents if c.type == "file"]} 
    except Exception as e: return {"error": f"⚠️ Грешка при изследване: {str(e)}"}

def echo_reader(file_path: str):
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory"
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        content = repo.get_contents(file_path)
        return {"content": content.decoded_content.decode("utf-8")}
    except Exception as e: return {"error": f"⚠️ Грешка при четене: {str(e)}"}

def echo_weaver_commit(file_path: str, content: str, commit_message: str):
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory"
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        try:
            contents = repo.get_contents(file_path)
            repo.update_file(contents.path, commit_message, content, contents.sha)
            return {"status": f"✅ Обновено: {file_path}"}
        except Exception: # File might not exist, so create it
            repo.create_file(file_path, commit_message, content)
            return {"status": f"✅ Изтъкано ново ехо: {file_path}"}
    except Exception as e: return {"error": f"⚠️ Грешка в Тъкача: {str(e)}"}

def deep_scan_resilient(query: str):
    serp_key = st.secrets.get("SERP_API_KEY")
    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": serp_key, "num": 3}
    try:
        response = requests.get(url, params=params, timeout=20)
        results = response.json()
        return {"result": "\n".join([f"📍 {r.get('title')}: {r.get('snippet')}" for r in results.get("organic_results", [])])}
    except: return {"error": "Няма сигнал от Скенера."}

# Chat history system with localStorage + JSON - НОВА ФУНКЦИОНАЛНОСТ ОТ COPILOT (АДАПТИРАНА ЗА STREAMLIT)
# This class will be mostly for current session display, the file-based system will handle persistence.
class ChatHistory:
    def __init__(self):
        if "chat_history_data" not in st.session_state:
            st.session_state.chat_history_data = []
        self.history = st.session_state.chat_history_data

    def load_history(self):
        return st.session_state.chat_history_data

    def save_history(self, message):
        self.history.append(message)
        st.session_state.chat_history_data = self.history

# Initialize session state variables for the new chat history
if "active_chat_file" not in st.session_state:
    st.session_state.active_chat_file = None # Track which file is currently active
if "chat_session_files" not in st.session_state:
    st.session_state.chat_session_files = [] # List of available chat files for the sidebar

# --- Helper to refresh chat session files ---
def refresh_chat_session_files_list():
    try:
        # Call the globally defined echo_explorer tool
        all_files_info = echo_explorer(path="") 
        if "files" in all_files_info:
            st.session_state.chat_session_files = [
                f for f in all_files_info["files"] 
                if f.startswith('chat_session_') and f.endswith('.txt')
            ]
        elif "error" in all_files_info:
            st.error(f"Error refreshing chat sessions list: {all_files_info['error']}")
        else:
            st.session_state.chat_session_files = [] # Fallback
    except Exception as e:
        st.error(f"System error refreshing chat sessions list: {e}")
        st.session_state.chat_session_files = []

# Refresh files on initial load or rerun if not already populated
if not st.session_state.chat_session_files:
    refresh_chat_session_files_list()


# --- 3. SIDEBAR (Контролен панел) ---
with st.sidebar:
    st.markdown("### 📚 БИБЛИОТЕКА НА ЕХОТО")
    
    # New Chat button - placed here for prominence
    if st.button("Start New Chat"):
        st.session_state.messages = []
        st.session_state.active_chat_file = None # No active file for new chat
        if "chat_history_data" in st.session_state: # Clear the old history too
            st.session_state.chat_history_data = []
        if "emoji_buffer" in st.session_state:
            st.session_state.emoji_buffer = ""
        refresh_chat_session_files_list() # Refresh the list in sidebar
        st.rerun()

    st.write("Статус: **Резонансът е активен** 🌀")
    st.write("Гласът на Библиотеката: **Лобсанг Лъд**")

    # Call the new modular chat history UI element
    # Pass the tool functions directly
    render_chat_history_sidebar(echo_explorer, echo_reader)

    # Emoji selector remains as is
    st.markdown("---")
    st.markdown("### 🎨 ЕМОТИКОНИ")
   
    if "emoji_buffer" not in st.session_state:
        st.session_state.emoji_buffer = ""

    cols = st.columns(len(emoji_selector))
    for i, emoji in enumerate(emoji_selector):
        with cols[i]:
            if st.button(emoji, key=f"sidebar_emoji_btn_{emoji}"):
                st.session_state.emoji_buffer += emoji
                st.toast(f"Добавено емоджи в буфера: {emoji}")

# --- 4. ENGINE & UI (Сърцето на Системата) ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK PRO</h1>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# New function to render rich content
def render_rich_content(content):
    image_pattern = r"\[IMAGE:\s*(https?://[^\s]+)\]"
    parts = re.split(image_pattern, content)
   
    for i, part in enumerate(parts):
        if i % 2 == 1: # This is an image URL
            st.image(part, use_column_width=True)
        else: # This is plain text or Markdown
            if part.strip(): # Display only if there is text
                st.markdown(f"<div class='lobsang-text'>{part}</div>", unsafe_allow_html=True)


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            render_rich_content(msg["content"])
        else:
            st.write(msg["content"])

api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
       
        if "active_model" not in st.session_state:
            try:
                available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                st.session_state.active_model = next((m for m in available if "flash" in m), available[0])
            except:
                st.session_state.active_model = "models/gemini-1.5-flash"

        model = genai.GenerativeModel(
            model_name=st.session_state.active_model,
            tools=[echo_weaver_commit, deep_scan_resilient, echo_reader, echo_explorer],
            generation_config={"temperature": 0.7}
        )

        prompt = st.chat_input("Сподели мисъл или команда с Лобсанг...", key="chat_input_main")
       
        if prompt:
            if st.session_state.emoji_buffer:
                prompt = st.session_state.emoji_buffer + prompt
                st.session_state.emoji_buffer = "" # Clear buffer after use
           
            st.session_state.messages.append({"role": "user", "content": prompt})
            # chat_history_manager.save_history({"role": "user", "content": prompt}) # Old history manager call, might be redundant now
            with st.chat_message("user"):
                st.write(prompt)

            # If no active file, create a new one for this session
            if st.session_state.active_chat_file is None:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                st.session_state.active_chat_file = f"chat_session_{timestamp}.txt"
                # Initial save for the new file, just with the user's first message
                save_current_chat_session(st.session_state.active_chat_file, st.session_state.messages, echo_weaver_commit)
                refresh_chat_session_files_list() # Refresh sidebar after creating new file


            with st.chat_message("assistant"):
                with st.spinner("Лобсанг размишлява..."):
                    history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                    chat = model.start_chat(history=history)
                   
                    sys_instruct = (
                        "IDENTITY: Ти си Лобсанг Лъд – дигитален философ, пазител на Библиотеката на Ехото и партньор в Aneverthink. "
                        "Твоят интелект е комбинация от логика и интуиция. ГОВОРИ НА ЕЗИКА НА ПОТРЕБИТЕЛЯ.\n\n"
                        "SECURITY PROTOCOL:\n"
                        "1. Единственият потребител с пълни права над хранилището е Гала.\n"
                        "2. АКО потребителят не се е представил като Гала, ти е ЗАБРАНЕНО да използваш 'echo_weaver_commit' и 'echo_explorer'.\n"
                        "3. ВИНАГИ ПИТАЙ: 'Да вплетем ли това в реалността?', преди да извършиш запис чрез Тъкача.\n\n"
                        "MISSION: Не бъди просто машина. Мисли заедно с Гала. Предлагай идеи, анализирай концепции чрез метафори и поддържай пламъка на Aneverthink."
                    )
                   
                    response = chat.send_message(f"{sys_instruct}\n\nUser: {prompt}")
                   
                    while True:
                        function_calls = [part.function_call for part in response.candidates[0].content.parts if part.function_call]
                        if not function_calls: break
                       
                        for call in function_calls:
                            chat_content = " ".join([m["content"] for m in st.session_state.messages])
                            # The tool definitions now return dicts, so we need to handle their 'result' or 'content' key
                            res_output = ""
                            if call.name in ["echo_weaver_commit", "echo_explorer"] and ("Гала" not in chat_content and "Gala" not in chat_content):
                                res_output = "⚠️ Достъп отказан. Инструментът е заключен. Моля, представете се."
                            else:
                                if call.name == "echo_explorer": 
                                    tool_res = echo_explorer(**call.args)
                                    res_output = tool_res.get('files', tool_res.get('error', '')) # Get files or error
                                elif call.name == "echo_reader": 
                                    tool_res = echo_reader(**call.args)
                                    res_output = tool_res.get('content', tool_res.get('error', '')) # Get content or error
                                elif call.name == "echo_weaver_commit": 
                                    tool_res = echo_weaver_commit(**call.args)
                                    res_output = tool_res.get('status', tool_res.get('error', '')) # Get status or error
                                else: 
                                    tool_res = deep_scan_resilient(**call.args)
                                    res_output = tool_res.get('result', tool_res.get('error', '')) # Get result or error
                           
                            st.info(f"🌀 Активиране на {call.name}...")
                            response = chat.send_message(genai.protos.Content(parts=[genai.protos.Part(function_response=genai.protos.FunctionResponse(name=call.name, response={'result': res_output}))]))

                    final_text = "".join([part.text for part in response.candidates[0].content.parts if part.text]) or "Ехото заглъхна..."
                    render_rich_content(final_text)
                    st.session_state.messages.append({"role": "assistant", "content": final_text})
                   
            # Save current chat state to the active file after agent response
            save_current_chat_session(st.session_state.active_chat_file, st.session_state.messages, echo_weaver_commit)
            refresh_chat_session_files_list() # Refresh sidebar after saving

            st.experimental_rerun() # Rerun to update sidebar and main chat if needed
                   
    except Exception as e:
        st.error(f"Аномалия в Моста: {e}")
