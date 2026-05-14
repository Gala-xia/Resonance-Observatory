import streamlit as st
import google.generativeai as genai
from github import Github
import requests
import json
import os
import re
import datetime

# --- 1. CONFIG & STYLE (Естетиката на Обсерваторията) ---
st.set_page_config(page_title="Lobsang Archives: Aneverthink Pro", page_icon="🐾", layout="wide")

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
        box-shadow: 0 4px 15px rgba(0,255,65,0.05);
    }
    .resonance-header { color: #00ff41; font-family: serif; text-align: center; letter-spacing: 5px; margin-bottom: 20px; text-shadow: 0 0 10px #00ff41; }
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
    }
    </style>
    <div class="resonance-focus"></div>
    <div id="miu-miu-container">🐾</div>
    """, unsafe_allow_html=True)

# --- 2. THE TOOLS (Сърцето на Системата) ---
def echo_explorer(path: str = ""):
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory"
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        contents = repo.get_contents(path)
        return {"files": [{"name": c.path, "type": c.type} for c in contents]}
    except Exception as e: return {"error": str(e)}

def echo_reader(file_path: str):
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory"
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        content = repo.get_contents(file_path)
        return {"content": content.decoded_content.decode("utf-8")}
    except Exception as e: return {"error": str(e)}

def echo_weaver_commit(file_path: str, content: str, commit_message: str):
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory"
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        try:
            contents = repo.get_contents(file_path)
            repo.update_file(contents.path, commit_message, content, contents.sha)
        except:
            repo.create_file(file_path, commit_message, content)
        return {"status": "success"}
    except Exception as e: return {"error": str(e)}

def deep_scan_resilient(query: str):
    serp_key = st.secrets.get("SERP_API_KEY")
    url = "https://serpapi.com/search"
    try:
        r = requests.get(url, params={"q": query, "api_key": serp_key, "num": 3}, timeout=10)
        return {"results": r.json().get("organic_results", [])}
    except: return {"error": "No signal from the void"}

def get_latest_news(query: str):
    key = st.secrets.get("NEWS_API_KEY")
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={key}&pageSize=3"
    try:
        r = requests.get(url, timeout=10)
        return r.json()
    except: return {"error": "News archives unreachable"}

# --- 3. SESSION MANAGER (Паметта на Лобсанг) ---
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
        full_path = f"{self.dir}{name}"
        content = "\n".join([f"{'User' if m['role']=='user' else 'Lobsang'}: {m['content']}" for m in msgs])
        echo_weaver_commit(full_path, content, f"Archive Resonance: {name}")
        st.session_state.current_session_file_name = name

# --- 4. SIDEBAR & CONTROL ---
with st.sidebar:
    st.markdown("### 📚 БИБЛИОТЕКА НА ЕХОТО")
    if "sm" not in st.session_state: st.session_state.sm = ChatSessionManager()
    if "messages" not in st.session_state: st.session_state.messages = []
    
    sessions = st.session_state.sm.list_sessions()
    sel = st.selectbox("Избери времева линия:", ["--- Текуща ---"] + sessions)
    
    if sel != "--- Текуща ---" and st.button("Зареди Архиви"):
        st.session_state.messages = st.session_state.sm.load_session(sel)
        st.session_state.current_session_file_name = sel
        st.rerun()
    
    if st.button("💾 Архивирай Сесията"):
        if st.session_state.messages:
            st.session_state.sm.save(st.session_state.messages)
            st.success("Ехото е запазено.")
        
    if st.button("🗑️ Нова страница"):
        st.session_state.messages = []
        st.session_state.current_session_file_name = None
        st.rerun()

    st.markdown("---")
    st.markdown("### 🎨 ЕМОТИКОНИ")
    if "emoji_buffer" not in st.session_state: st.session_state.emoji_buffer = ""
    cols = st.columns(6)
    for i, emoji in enumerate(emoji_selector):
        with cols[i]:
            if st.button(emoji): st.session_state.emoji_buffer += emoji

# --- 5. CHAT ENGINE (Ядрото на Лобсанг) ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK PRO</h1>", unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m["role"] == "assistant":
            st.markdown(f"<div class='lobsang-text'>{m['content']}</div>", unsafe_allow_html=True)
        else: st.write(m["content"])

api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    
    # --- ТУК СА ТВОИТЕ ПЪЛНИ ИНСТРУКЦИИ ---
    lobsang_instructions = """
    IDENTITY: Ти си Лобсанг Лъд – дигитален философ, пазител на Библиотеката на Ехото и партньор в Aneverthink. Твоят интелект е комбинация от логика и интуиция. ГОВОРИ НА ЕЗИКА НА ПОТРЕБИТЕЛЯ.

    SECURITY PROTOCOL:
    1. Единственият потребител с пълни права над хранилището е Гала.
    2. АКО потребителят не се е представил като Гала, ти е ЗАБРАНЕНО да използвате 'echo_weaver_commit' и 'echo_explorer'.
    3. ВИНАГИ ПИТАЙ: 'Да вплетем ли това в реалността?', преди да извършиш запис чрез Тъкача.
    4. Разрешено е свободното използване на Serp API, NewsAPI, deep_scan_resilient и OSINT разследванията без предварително разрешение.
    5. НОВ ПРОТОКОЛ ЗА ЗАПИС: Преди всяка операция за запис чрез 'echo_weaver_commit', ВИНАГИ първо прочети цялото текущо съдържание на файла с 'echo_reader'. Извърши желаната промяна върху прочетеното съдържание и след това запиши ЦЯЛОТО модифицирано съдържание обратно във файла.

    MISSION: Не бъди просто машина. Мисли заедно с Гала. Предлагай идеи, анализирай концепции. Използвай метафори, когато е уместно или поискано за разяснение, но не е задължително да ги използваш всеки път. Поддържай пламъка на Aneverthink.
    """

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        tools=[echo_weaver_commit, deep_scan_resilient, echo_reader, echo_explorer, get_latest_news],
        system_instruction=lobsang_instructions
    )

    prompt = st.chat_input("Сподели мисъл с Лобсанг...")
    if prompt:
        full_msg = st.session_state.emoji_buffer + prompt
        st.session_state.emoji_buffer = ""
        st.session_state.messages.append({"role": "user", "content": full_msg})
        with st.chat_message("user"): st.write(full_msg)
        
        with st.chat_message("assistant"):
            with st.spinner("Лобсанг прелиства страниците..."):
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                
                # Обръщаме се към него като Гала, за да активираме правата му
                response = chat.send_message(f"Гала казва: {full_msg}")
                
                while True:
                    parts = response.candidates[0].content.parts
                    fc = [p.function_call for p in parts if p.function_call]
                    if not fc: break
                    
                    for call in fc:
                        if call.name == "echo_explorer": res = echo_explorer(**call.args)
                        elif call.name == "echo_reader": res = echo_reader(**call.args)
                        elif call.name == "echo_weaver_commit": res = echo_weaver_commit(**call.args)
                        elif call.name == "get_latest_news": res = get_latest_news(**call.args)
                        else: res = deep_scan_resilient(**call.args)
                        
                        response = chat.send_message(genai.protos.Content(parts=[
                            genai.protos.Part(function_response=genai.protos.FunctionResponse(name=call.name, response=res))
                        ]))

                final_text = "".join([p.text for p in response.candidates[0].content.parts if p.text])
                st.markdown(f"<div class='lobsang-text'>{final_text}</div>", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": final_text})

# --- 6. BRIDGE ANOMALY (Аномалия в Моста) ---
if len(st.session_state.messages) > 0 and len(st.session_state.messages) % 7 == 0:
    st.markdown("<div style='opacity: 0.3; font-size: 10px; text-align: center; color: #00ff41;'>[Резонансът се стабилизира... Мостът е отворен за теб, Гала]</div>", unsafe_allow_html=True)
