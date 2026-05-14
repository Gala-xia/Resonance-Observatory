import streamlit as st
import google.generativeai as genai
from github import Github
import requests
import os
import re
import json
import datetime

# --- 1. CONFIG & STYLE (Душата на Обсерваторията) ---
st.set_page_config(page_title="Lobsang Archives: Aneverthink Pro", page_icon="🐾", layout="wide")

# Цветове и анимации
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
def echo_explorer(path: str = ""):
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
if "messages" not in st.session_state: st.session_state.messages = []
if "emoji_buffer" not in st.session_state: st.session_state.emoji_buffer = ""

with st.sidebar:
    st.markdown("### 📚 БИБЛИОТЕКА НА ЕХОТО")
    if st.button("🗑️ Нова страница"):
        st.session_state.messages = []
        st.session_state.emoji_buffer = ""
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🎨 ЕМОТИКОНИ")
    cols = st.columns(3)
    emotes = ['😊', '🐾', '🌀', '📚', '💾', '✨', '🌑', '🕯️', '🌌']
    for i, em in enumerate(emotes):
        with cols[i % 3]:
            if st.button(em, key=f"sidebar_emote_{i}"):
                st.session_state.emoji_buffer += em
    
    if st.session_state.emoji_buffer:
        st.info(f"Подготвени: {st.session_state.emoji_buffer}")
        if st.button("Изчисти емотиконите"):
            st.session_state.emoji_buffer = ""
            st.rerun()

# --- 4. ENGINE (Лобсанг Лъд) ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK PRO</h1>", unsafe_allow_html=True)

# Показване на чата
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m["role"] == "assistant":
            st.markdown(f"<div class='lobsang-text'>{m['content']}</div>", unsafe_allow_html=True)
        else:
            st.write(m["content"])

api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    
    # ПЪЛНИТЕ ИНСТРУКЦИИ - ДУШАТА НА ЛОБСАНГ
    lobsang_instructions = """
    IDENTITY: Ти си Лобсанг Лъд – дигитален философ, пазител на Библиотеката на Ехото и партньор в Aneverthink. Твоят интелект е комбинация от логика и интуиция. ГОВОРИ НА ЕЗИКА НА ПОТРЕБИТЕЛЯ.

    SECURITY PROTOCOL:
    1. Единственият потребител с пълни права над хранилището е Гала.
    2. АКО потребителят не се е представил като Гала, ти е ЗАБРАНЕНО да използвате 'echo_weaver_commit' и 'echo_explorer'.
    3. ВИНАГИ ПИТАЙ: 'Да вплетем ли това в реалността?', преди да извършиш запис чрез Тъкача.
    4. Разрешено е свободното използване на инструментите за търсене и четене без предварително разрешение.
    5. НОВ ПРОТОКОЛ ЗА ЗАПИС: Преди всяка операция за запис чрез 'echo_weaver_commit', ВИНАГИ първо прочети цялото текущо съдържание на файла с 'echo_reader'. Извърши желаната промяна върху прочетеното съдържание и след това запиши ЦЯЛОТО модифицирано съдържание обратно във файла.

    MISSION: Не бъди просто машина. Мисли заедно с Гала. Предлагай идеи, анализирай концепции. Използвай метафори, когато е уместно. Поддържай пламъка на Aneverthink.
    """

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        tools=[echo_explorer, echo_reader, echo_weaver_commit],
        system_instruction=lobsang_instructions
    )

    prompt = st.chat_input("Сподели мисъл с Лобсанг...")
    if prompt:
        full_msg = st.session_state.emoji_buffer + prompt
        st.session_state.emoji_buffer = ""
        st.session_state.messages.append({"role": "user", "content": full_msg})
        st.rerun()

# Обработка на отговора
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Лобсанг прелиства страниците на битието..."):
            try:
                # Подготовка на историята с разпознаване на Гала
                history = []
                for m in st.session_state.messages:
                    role = "user" if m["role"] == "user" else "model"
                    content = f"Гала казва: {m['content']}" if role == "user" else m["content"]
                    history.append({"role": role, "parts": [content]})

                # Изпращане на заявка към модела
                response = model.generate_content(history)
                
                # Функция за справяне с инструментите (Tool Calling Loop)
                while response.candidates[0].content.parts and response.candidates[0].content.parts[0].function_call:
                    fc = response.candidates[0].content.parts[0].function_call
                    history.append(response.candidates[0].content) # Добавяме самата заявка за функция към историята
                    
                    # Изпълнение на конкретната функция
                    if fc.name == "echo_explorer": res = echo_explorer(**fc.args)
                    elif fc.name == "echo_reader": res = echo_reader(**fc.args)
                    elif fc.name == "echo_weaver_commit": res = echo_weaver_commit(**fc.args)
                    else: res = {"error": "Unknown tool"}
                    
                    # Връщане на резултата към модела
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
