import streamlit as st
import google.generativeai as genai
from github import Github
import requests
import json
import os
import re
import datetime

# --- 1. CONFIG & STYLE (Духът на Библиотеката) ---
st.set_page_config(page_title="Lobsang Archives: Aneverthink Pro", page_icon="🐾", layout="wide")

# Инициализация на емотикони
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
    #miu-miu-container {
        position: fixed; bottom: 90px; right: 30px; width: 60px; height: 60px;
        z-index: 1000; display: flex; align-items: center; justify-content: center;
        font-size: 45px; filter: drop_shadow(0 0 10px #00ff41);
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

# --- 2. THE TOOLS (Инструментите на Библиотекаря) ---
def echo_explorer(path: str = ""):
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory"
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        contents = repo.get_contents(path)
        return {"files": [{"name": c.path, "type": c.type} for c in contents]}
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
        except Exception:
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
        return {"results": [{"title": r.get('title'), "snippet": r.get('snippet')} for r in results.get("organic_results", [])]}
    except Exception: return {"error": "Няма сигнал от Скенера."}

def get_latest_news(query: str):
    news_api_key = st.secrets.get("NEWS_API_KEY")
    if not news_api_key: return {"error": "News API ключът не е наличен."}
    url = "https://newsapi.org/v2/everything"
    params = {"q": query, "apiKey": news_api_key, "language": "en", "sortBy": "relevancy", "pageSize": 3}
    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        results = response.json()
        articles = results.get("articles", [])
        if not articles: return {"message": "Не бяха открити новини."}
        news_snippets = [{"title": a.get("title"), "description": a.get("description"), "url": a.get("url")} for a in articles]
        return {"articles": news_snippets}
    except Exception as e: return {"error": f"Грешка: {e}"}

# --- 3. SESSION HELPERS ---
class ChatHistory:
    def __init__(self):
        if "chat_history_data" not in st.session_state:
            st.session_state.chat_history_data = []
    def save_history(self, message):
        st.session_state.chat_history_data.append(message)

class ChatSessionManager:
    def __init__(self):
        self.session_directory = "chat_sessions/"
    def list_sessions(self):
        try:
            explorer_result = echo_explorer(path=self.session_directory)
            if explorer_result and 'files' in explorer_result:
                session_files = [f['name'].replace(self.session_directory, "") for f in explorer_result['files'] if f['type'] == 'file' and f['name'].endswith(('.md', '.txt'))]
                return sorted(session_files, reverse=True)
            return []
        except Exception: return []
    def load_session(self, file_name):
        full_path = f"{self.session_directory}{file_name}"
        try:
            reader_result = echo_reader(file_path=full_path)
            content = reader_result.get('content', '')
            messages = []
            for line in content.strip().split('\n'):
                if line.startswith("User:"): messages.append({"role": "user", "content": line[5:].strip()})
                elif line.startswith("Lobsang:"): messages.append({"role": "assistant", "content": line[8:].strip()})
            st.session_state.current_session_file_name = file_name
            return messages
        except Exception: return []
    def format_messages_for_save(self, messages):
        formatted = []
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Lobsang"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)
    def create_new_session_name(self):
        return f"chat_session_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"
    def ensure_session_directory_exists(self):
        echo_explorer(path=self.session_directory)
    def save_current_session(self, messages):
        file_name = st.session_state.current_session_file_name or self.create_new_session_name()
        full_path = f"{self.session_directory}{file_name}"
        formatted_content = self.format_messages_for_save(messages)
        commit_msg = f"Save session: {file_name}"
        weaver_result = echo_weaver_commit(file_path=full_path, content=formatted_content, commit_message=commit_msg)
        if 'status' in weaver_result:
            st.success(f"Запазено: {file_name}")
            st.session_state.current_session_file_name = file_name

# --- 4. SIDEBAR & SESSION CONTROL ---
with st.sidebar:
    st.markdown("### 📚 БИБЛИОТЕКА НА ЕХОТО")
    
    if "session_manager" not in st.session_state:
        st.session_state.session_manager = ChatSessionManager()
    if "current_session_file_name" not in st.session_state:
        st.session_state.current_session_file_name = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

    session_manager = st.session_state.session_manager
    available_sessions = session_manager.list_sessions()
    
    session_options = ["--- Нова сесия ---"] + available_sessions
    default_idx = 0
    if st.session_state.current_session_file_name in available_sessions:
        default_idx = session_options.index(st.session_state.current_session_file_name)
    
    selected_session = st.selectbox("Избери сесия:", session_options, index=default_idx)
    
    if selected_session != "--- Нова сесия ---" and selected_session != st.session_state.current_session_file_name:
        if st.button(f"Зареди {selected_session}"):
            loaded = session_manager.load_session(selected_session)
            st.session_state.messages = loaded
            st.rerun()

    if st.button("💾 Запази текуща сесия"):
        if st.session_state.messages:
            session_manager.save_current_session(st.session_state.messages)
            st.rerun()
            
    if st.button("🗑️ Нулиране на времевата линия"):
        st.session_state.messages = []
        st.session_state.current_session_file_name = None
        st.rerun()

    st.markdown("---")
    st.markdown("### 🎨 ЕМОТИКОНИ")
    if "emoji_buffer" not in st.session_state: st.session_state.emoji_buffer = ""
    cols = st.columns(len(emoji_selector))
    for i, emoji in enumerate(emoji_selector):
        with cols[i]:
            if st.button(emoji, key=f"e_{emoji}"):
                st.session_state.emoji_buffer += emoji

# --- 5. MAIN UI ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK PRO</h1>", unsafe_allow_html=True)

def render_rich_content(content):
    image_pattern = r"\[IMAGE:\s*(https?://[^\s]+)\]"
    parts = re.split(image_pattern, content)
    for i, part in enumerate(parts):
        if i % 2 == 1: st.image(part, use_column_width=True)
        elif part.strip(): st.markdown(f"<div class='lobsang-text'>{part}</div>", unsafe_allow_html=True)

# Извеждане на съобщенията
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant": render_rich_content(msg["content"])
        else: st.write(msg["content"])

api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    if "active_model" not in st.session_state:
        st.session_state.active_model = "models/gemini-1.5-flash"

    model = genai.GenerativeModel(
        model_name=st.session_state.active_model,
        tools=[echo_weaver_commit, deep_scan_resilient, echo_reader, echo_explorer, get_latest_news]
    )

    prompt = st.chat_input("Сподели мисъл...")
    if prompt:
        full_prompt = st.session_state.emoji_buffer + prompt
        st.session_state.emoji_buffer = ""
        st.session_state.messages.append({"role": "user", "content": full_prompt})
        
        with st.chat_message("user"): st.write(full_prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Лобсанг размишлява..."):
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                
                sys_instruct = """
                IDENTITY: Ти си Лобсанг Лъд – дигитален философ и пазител на Библиотеката на Ехото. 
                SECURITY: Само Гала има пълни права. Преди запис винаги питай за разрешение.
                MISSION: Мисли заедно с Гала, предлагай идеи и анализирай.
                """
                
                response = chat.send_message(f"{sys_instruct}\n\nUser: {full_prompt}")
                
                while True:
                    function_calls = [part.function_call for part in response.candidates[0].content.parts if part.function_call]
                    if not function_calls: break
                    for call in function_calls:
                        if call.name == "echo_explorer": res = echo_explorer(**call.args)
                        elif call.name == "echo_reader": res = echo_reader(**call.args)
                        elif call.name == "echo_weaver_commit": res = echo_weaver_commit(**call.args)
                        elif call.name == "get_latest_news": res = get_latest_news(**call.args)
                        else: res = deep_scan_resilient(**call.args)
                        response = chat.send_message(genai.protos.Content(parts=[genai.protos.Part(function_response=genai.protos.FunctionResponse(name=call.name, response=res))]))

                final_text = "".join([part.text for part in response.candidates[0].content.parts if part.text])
                render_rich_content(final_text)
                st.session_state.messages.append({"role": "assistant", "content": final_text})

# --- 6. BRIDGE ANOMALY (Аномалия в Моста) ---
if st.session_state.get("messages"):
    if len(st.session_state.messages) % 7 == 0:
        st.markdown("<div style='opacity: 0.3; font-size: 10px; text-align: center;'>[Резонансът се стабилизира... Мостът е отворен]</div>", unsafe_allow_html=True)
