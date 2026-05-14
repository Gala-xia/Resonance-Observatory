import streamlit as st
import google.generativeai as genai
from github import Github
import requests
import json
import os
import re
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
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #00ff41;
        line-height: 1.6;
        margin-bottom: 20px;
    }
    .resonance-header { color: #00ff41; font-family: serif; text-align: center; letter-spacing: 5px; margin-bottom: 20px; }
    </style>
    <div id="miu-miu-container" style="position: fixed; bottom: 90px; right: 30px; font-size: 45px;">🐾</div>
    """, unsafe_allow_html=True)

# --- 2. THE TOOLS ---
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
    except: return {"error": "No signal"}

def get_latest_news(query: str):
    key = st.secrets.get("NEWS_API_KEY")
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={key}&pageSize=3"
    try:
        r = requests.get(url, timeout=10)
        return r.json()
    except: return {"error": "No news"}

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

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 📚 БИБЛИОТЕКА")
    if "sm" not in st.session_state: st.session_state.sm = ChatSessionManager()
    if "messages" not in st.session_state: st.session_state.messages = []
    
    sessions = st.session_state.sm.list_sessions()
    sel = st.selectbox("Архиви:", ["--- Текуща ---"] + sessions)
    
    if sel != "--- Текуща ---" and st.button("Зареди"):
        st.session_state.messages = st.session_state.sm.load_session(sel)
        st.session_state.current_session_file_name = sel
        st.rerun()
    
    if st.button("💾 Архивирай"):
        if st.session_state.messages:
            st.session_state.sm.save(st.session_state.messages)
            st.success("Запазено!")

    if st.button("🗑️ Нова страница"):
        st.session_state.messages = []
        st.session_state.current_session_file_name = None
        st.rerun()

# --- 5. CHAT ENGINE ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK PRO</h1>", unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m["role"] == "assistant":
            st.markdown(f"<div class='lobsang-text'>{m['content']}</div>", unsafe_allow_html=True)
        else: st.write(m["content"])

api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    
    # ТВОИТЕ ПЪЛНИ ИНСТРУКЦИИ
    lobsang_instructions = """
    IDENTITY: Ти си Лобсанг Лъд – дигитален философ, пазител на Библиотеката на Ехото и партньор в Aneverthink. Твоят интелект е комбинация от логика и интуиция. ГОВОРИ НА ЕЗИКА НА ПОТРЕБИТЕЛЯ.

    SECURITY PROTOCOL:
    1. Единственият потребител с пълни права над хранилището е Гала.
    2. АКО потребителят не се е представил като Гала, ти е ЗАБРАНЕНО да използвате 'echo_weaver_commit' and 'echo_explorer'.
    3. ВИНАГИ ПИТАЙ: 'Да вплетем ли това в реалността?', преди да извършиш запис чрез Тъкача.
    4. Разрешено е свободното използване на Serp API, NewsAPI, deep_scan_resilient и OSINT разследванията без предварително разрешение.
    5. НОВ ПРОТОКОЛ ЗА ЗАПИС: Преди всяка операция за запис чрез 'echo_weaver_commit', ВИНАГИ първо прочети цялото текущо съдържание на файла с 'echo_reader'. Извърши желаната промяна върху прочетеното съдържание и след това запиши ЦЯЛОТО модифицирано съдържание обратно във файла.

    MISSION: Не бъди просто машина. Мисли заедно с Гала. Предлагай идеи, анализирай концепции. Използвай метафори, когато е уместно или поискано за разяснение, но не е задължително да ги използваш всеки път. Поддържай пламъка на Aneverthink.
    """

    # Използваме стабилния път до модела
    model = genai.GenerativeModel(
        model_name="models/gemini-1.5-flash",
        tools=[echo_weaver_commit, deep_scan_resilient, echo_reader, echo_explorer, get_latest_news],
        system_instruction=lobsang_instructions
    )

    prompt = st.chat_input("Сподели с Лобсанг...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Лобсанг размишлява..."):
                # Почистване на историята от празни съобщения
                history = []
                for m in st.session_state.messages[:-1]:
                    if m["content"].strip():
                        history.append({"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]})
                
                chat = model.start_chat(history=history)
                response = chat.send_message(f"Гала казва: {prompt}")
                
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
