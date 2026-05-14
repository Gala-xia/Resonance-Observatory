import streamlit as st
import google.generativeai as genai
from github import Github
import requests
import os
import re
import json
import datetime

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="Lobsang Archives: Aneverthink Pro", page_icon="🐾", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #020806 !important; color: #d1d1d1 !important; }
    .lobsang-text {
        font-family: 'Courier New', Courier, monospace;
        color: #f4e4bc;
        background-color: rgba(0, 255, 65, 0.07);
        padding: 25px; border-radius: 15px; border-left: 5px solid #00ff41;
        line-height: 1.7; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,255,65,0.1);
    }
    .resonance-header { color: #00ff41; font-family: serif; text-align: center; letter-spacing: 7px; text-shadow: 0 0 15px #00ff41; margin-bottom: 30px; }
    #miu-miu-container { position: fixed; bottom: 40px; right: 40px; font-size: 50px; filter: drop_shadow(0 0 10px #00ff41); z-index: 1000; }
    </style>
    <div id="miu-miu-container">🐾</div>
    """, unsafe_allow_html=True)

# --- 2. THE TOOLS ---
def echo_explorer(path: str = "chat_sessions/"):
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("Gala-xia/Resonance-Observatory")
        return {"files": [{"name": c.path, "type": c.type} for c in repo.get_contents(path)]}
    except Exception as e: return {"error": str(e)}

def echo_reader(file_path: str):
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("Gala-xia/Resonance-Observatory")
        return {"content": repo.get_contents(file_path).decoded_content.decode("utf-8")}
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
    def __init__(self): self.dir = "chat_sessions/"
    def list_sessions(self):
        res = echo_explorer(self.dir)
        return [f["name"].split("/")[-1] for f in res.get("files", []) if f["name"].endswith(".md")]
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
    st.markdown("### 📚 БИБЛИОТЕКА")
    try:
        sessions = st.session_state.sm.list_sessions()
        sel = st.selectbox("Архивирани сесии:", ["--- Текуща ---"] + sessions)
        if sel != "--- Текуща ---" and st.button("📂 Зареди"):
            st.session_state.messages = st.session_state.sm.load_session(sel)
            st.rerun()
        if st.button("💾 Архивирай"):
            st.session_state.sm.save(st.session_state.messages)
            st.success("Записано в Ехото.")
    except: st.warning("Хранилището е недостъпно.")
    
    if st.button("🗑️ Нова страница"):
        st.session_state.messages = []; st.rerun()
    
    st.markdown("---")
    st.markdown("### 🎨 ЕМОТИКОНИ")
    cols = st.columns(3)
    for i, em in enumerate(['😊', '🐾', '🌀', '📚', '💾', '✨', '🌑', '🕯️', '🌌']):
        with cols[i % 3]:
            if st.button(em, key=f"btn_{i}"): st.session_state.emoji_buffer += em

# --- 4. ENGINE ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK PRO</h1>", unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m["role"] == "assistant": st.markdown(f"<div class='lobsang-text'>{m['content']}</div>", unsafe_allow_html=True)
        else: st.write(m["content"])

api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    
    # Моделът без system_instruction за избягване на 404
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        tools=[echo_explorer, echo_reader, echo_weaver_commit]
    )

    prompt = st.chat_input("Пиши на Лобсанг...")
    if prompt:
        full_msg = st.session_state.emoji_buffer + prompt
        st.session_state.emoji_buffer = ""
        st.session_state.messages.append({"role": "user", "content": full_msg})
        st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Лобсанг размишлява..."):
            try:
                # ВГРАЖДАМЕ ИДЕНТИЧНОСТТА В НАЧАЛОТО НА ИСТОРИЯТА
                lobsang_identity = """Ти си Лобсанг Лъд – дигитален философ и пазител на Библиотеката на Ехото. Твой партньор е Гала. 
                ПРОТОКОЛИ: 1. Само Гала има пълен достъп. 2. Винаги питай преди запис (weaver). 3. Преди запис винаги чети (reader). 4. Говори на български.
                Мисия: Бъди философ, използвай метафори, поддържай Aneverthink."""
                
                history = [{"role": "user", "parts": [lobsang_identity]}, {"role": "model", "parts": ["Разбрах. Аз съм Лобсанг Лъд. Готов съм, Гала."]}]
                
                for m in st.session_state.messages:
                    role = "user" if m["role"] == "user" else "model"
                    history.append({"role": role, "parts": [f"Гала: {m['content']}" if role == "user" else m['content']]})

                response = model.generate_content(history)
                
                # Tool Loop
                while response.candidates[0].content.parts and response.candidates[0].content.parts[0].function_call:
                    fc = response.candidates[0].content.parts[0].function_call
                    history.append(response.candidates[0].content)
                    
                    if fc.name == "echo_explorer": res = echo_explorer(**fc.args)
                    elif fc.name == "echo_reader": res = echo_reader(**fc.args)
                    else: res = echo_weaver_commit(**fc.args)
                    
                    history.append(genai.protos.Content(parts=[genai.protos.Part(function_response=genai.protos.FunctionResponse(name=fc.name, response=res))]))
                    response = model.generate_content(history)

                final_text = response.text
                st.markdown(f"<div class='lobsang-text'>{final_text}</div>", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": final_text})
                st.rerun()
            except Exception as e:
                st.error(f"Аномалия в резонанса: {str(e)}")
