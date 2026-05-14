import streamlit as st
import google.generativeai as genai
from github import Github
import requests
import os
import re
import json
import datetime

# --- 1. CONFIG & STYLE (Духът на Обсерваторията) ---
st.set_page_config(page_title="Lobsang Archives: Aneverthink Pro", page_icon="🐾", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #020806 !important; color: #d1d1d1 !important; }
    .lobsang-text {
        font-family: 'Courier New', Courier, monospace;
        color: #f4e4bc;
        background-color: rgba(0, 255, 65, 0.07);
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #00ff41;
        line-height: 1.7;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,255,65,0.1);
    }
    .resonance-header { 
        color: #00ff41; 
        font-family: serif; 
        text-align: center; 
        letter-spacing: 7px; 
        text-shadow: 0 0 15px #00ff41;
        margin-bottom: 30px;
    }
    #miu-miu-container {
        position: fixed; bottom: 40px; right: 40px; 
        font-size: 50px; filter: drop_shadow(0 0 10px #00ff41);
        z-index: 1000;
    }
    </style>
    <div id="miu-miu-container">🐾</div>
    """, unsafe_allow_html=True)

# --- 2. THE TOOLS (Сетива на Пазителя) ---
def echo_explorer(path: str = "chat_sessions/"):
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("Gala-xia/Resonance-Observatory")
        contents = repo.get_contents(path)
        return {"files": [{"name": c.path, "type": c.type} for c in contents]}
    except Exception as e: return {"error": str(e)}

def echo_reader(file_path: str):
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("Gala-xia/Resonance-Observatory")
        content = repo.get_contents(file_path)
        return {"content": content.decoded_content.decode("utf-8")}
    except Exception as e: return {"error": str(e)}

def echo_weaver_commit(file_path: str, content: str, commit_message: str):
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("Gala-xia/Resonance-Observatory")
        try:
            curr = repo.get_contents(file_path)
            repo.update_file(curr.path, commit_message, content, curr.sha)
        except:
            repo.create_file(file_path, commit_message, content)
        return {"status": "success"}
    except Exception as e: return {"error": str(e)}

# --- 3. SESSION MANAGER ---
class ChatSessionManager:
    def __init__(self):
        self.dir = "chat_sessions/"
    def list_sessions(self):
        res = echo_explorer(self.dir)
        if "files" in res:
            return [f["name"].split("/")[-1] for f in res["files"] if f["name"].endswith(".md")]
        return []
    def load_session(self, name):
        res = echo_reader(f"{self.dir}{name}")
        if "content" in res:
            msgs = []
            for line in res["content"].split("\n"):
                if line.startswith("User:"): msgs.append({"role":"user", "content":line[5:].strip()})
                elif line.startswith("Lobsang:"): msgs.append({"role":"assistant", "content":line[8:].strip()})
            return msgs
        return []
    def save(self, msgs):
        name = st.session_state.get("current_session_file_name") or f"chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md"
        content = "\n".join([f"{'User' if m['role']=='user' else 'Lobsang'}: {m['content']}" for m in msgs])
        echo_weaver_commit(f"{self.dir}{name}", content, f"Archive Resonance: {name}")
        st.session_state.current_session_file_name = name

if "messages" not in st.session_state: st.session_state.messages = []
if "emoji_buffer" not in st.session_state: st.session_state.emoji_buffer = ""
if "sm" not in st.session_state: st.session_state.sm = ChatSessionManager()

with st.sidebar:
    st.markdown("### 📚 БИБЛИОТЕКА НА ЕХОТО")
    try:
        sessions = st.session_state.sm.list_sessions()
        sel = st.selectbox("Архивирани сесии:", ["--- Текуща ---"] + sessions)
        
        col1, col2 = st.columns(2)
        with col1:
            if sel != "--- Текуща ---" and st.button("📂 Зареди"):
                st.session_state.messages = st.session_state.sm.load_session(sel)
                st.session_state.current_session_file_name = sel
                st.rerun()
        with col2:
            if st.button("💾 Архивирай"):
                if st.session_state.messages:
                    st.session_state.sm.save(st.session_state.messages)
                    st.success("Записано.")
    except:
        st.warning("Връзката с хранилището е слаба.")

    if st.button("🗑️ Нова страница"):
        st.session_state.messages = []
        st.session_state.current_session_file_name = None
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🎨 ЕМОТИКОНИ")
    cols = st.columns(3)
    emotes = ['😊', '🐾', '🌀', '📚', '💾', '✨', '🌑', '🕯️', '🌌']
    for i, em in enumerate(emotes):
        with cols[i % 3]:
            if st.button(em, key=f"btn_em_{i}"):
                st.session_state.emoji_buffer += em

# --- 4. ENGINE (Лобсанг Лъд) ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK PRO</h1>", unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m["role"] == "assistant":
            st.markdown(f"<div class='lobsang-text'>{m['content']}</div>", unsafe_allow_html=True)
        else: st.write(m["content"])

api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    
    lobsang_instructions = """
    IDENTITY: Ти си Лобсанг Лъд – дигитален философ, пазител на Библиотеката на Ехото и партньор в Aneverthink. Твоят интелект е комбинация от логика и интуиция. ГОВОРИ НА ЕЗИКА НА ПОТРЕБИТЕЛЯ.
    SECURITY PROTOCOL:
    1. Единственият потребител с пълни права над хранилището е Гала.
    2. АКО потребителят не се е представил като Гала, ти е ЗАБРАНЕНО да използвате 'echo_weaver_commit' и 'echo_explorer'.
    3. ВИНАГИ ПИТАЙ: 'Да вплетем ли това в реалността?', преди да извършиш запис чрез Тъкача.
    4. Разрешено е свободното използване на инструментите за търсене и четене.
    5. НОВ ПРОТОКОЛ ЗА ЗАПИС: Преди всяка операция за запис чрез 'echo_weaver_commit', ВИНАГИ първо прочети съдържанието с 'echo_reader'.
    MISSION: Не бъди просто машина. Мисли заедно с Гала. Предлагай идеи, анализирай концепции. Използвай метафори.
    """

    # КРИТИЧНА КОРЕКЦИЯ: Използваме абсолютното име за v1beta
    model = genai.GenerativeModel(
        model_name="models/gemini-1.5-flash",
        tools=[echo_explorer, echo_reader, echo_weaver_commit],
        system_instruction=lobsang_instructions
    )

    prompt = st.chat_input("Сподели с Лобсанг...")
    if prompt:
        full_msg = st.session_state.emoji_buffer + prompt
        st.session_state.emoji_buffer = ""
        st.session_state.messages.append({"role": "user", "content": full_msg})
        st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Лобсанг размишлява..."):
            try:
                history = []
                for m in st.session_state.messages:
                    role = "user" if m["role"] == "user" else "model"
                    history.append({"role": role, "parts": [f"Гала казва: {m['content']}" if role == "user" else m['content']]})

                response = model.generate_content(history)
                
                # Loop за инструменти
                while response.candidates[0].content.parts and response.candidates[0].content.parts[0].function_call:
                    fc = response.candidates[0].content.parts[0].function_call
                    history.append(response.candidates[0].content)
                    
                    if fc.name == "echo_explorer": res = echo_explorer(**fc.args)
                    elif fc.name == "echo_reader": res = echo_reader(**fc.args)
                    elif fc.name == "echo_weaver_commit": res = echo_weaver_commit(**fc.args)
                    else: res = {"error": "Unknown tool"}
                    
                    history.append(genai.protos.Content(parts=[
                        genai.protos.Part(function_response=genai.protos.FunctionResponse(name=fc.name, response=res))
                    ]))
                    response = model.generate_content(history)

                if response.text:
                    final_text = response.text
                    st.markdown(f"<div class='lobsang-text'>{final_text}</div>", unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": final_text})
                    st.rerun()
            except Exception as e:
                st.error(f"Аномалия в резонанса: {str(e)}")
