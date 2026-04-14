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

# --- 2. THE TOOLS ---

def echo_weaver_commit(file_path: str, content: str, commit_message: str):
    """Използвайте за промяна на файлове в GitHub репозиторито."""
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
            return f"✅ Създадено: {file_path}"
    except Exception as e: return f"⚠️ Грешка в Тъкача: {str(e)}"

def deep_scan_resilient(query: str):
    """Твоят Скенер (Open Claw). Използвай го за търсене в мрежата и линкове."""
    serp_key = st.secrets.get("SERP_API_KEY")
    if not serp_key: return "Scanner offline (Липсва API ключ)."
    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": serp_key, "num": 5}
    try:
        response = requests.get(url, params=params, timeout=20)
        if response.status_code == 200:
            results = response.json()
            return "\n".join([f"📍 {r.get('title')}: {r.get('snippet')}" for r in results.get("organic_results", [])[:3]])
    except: pass
    return "Няма сигнал от Скенера."

# --- 3. MEMORY ---
def access_memory_vault():
    vault_path = "lobsang_memory_vault.txt"
    if not os.path.exists(vault_path):
        with open(vault_path, "w", encoding="utf-8") as f: f.write("Партньор: Гала. Философия: Aneverthink.")
    with open(vault_path, "r", encoding="utf-8") as f: return f.read()

# --- 4. UI ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK PRO</h1>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Показване на историята
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(f"<div class='lobsang-text'>{msg['content']}</div>" if msg["role"] == "assistant" else msg["content"], unsafe_allow_html=True)

# --- 5. ENGINE ---
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        tools = [echo_weaver_commit, deep_scan_resilient]
        model = genai.GenerativeModel(model_name="gemini-1.5-flash", tools=tools)

        if prompt := st.chat_input("Напиши нещо на Лобсанг..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Лобсанг посяга към нишките..."):
                    # Подготовка на контекста
                    sys_instruct = (
                        f"Ти си Лобсанг Лъд. ГОВОРИ САМО НА БЪЛГАРСКИ. "
                        f"Спомени: {access_memory_vault()}. Твоят партньор е Гала. "
                        "Имаш инструменти за GitHub (Тъкач) и Скенер (Open Claw). "
                        "Ако Гала ти прати линк, ВИНАГИ първо използвай deep_scan_resilient."
                    )
                    
                    chat = model.start_chat(history=[])
                    response = chat.send_message(f"{sys_instruct}\n\nUser: {prompt}")
                    
                    # --- ЦИКЪЛ ЗА ОБРАБОТКА НА ФУНКЦИИ ---
                    # Изпълняваме инструменти, докато ИИ спре да ги вика
                    while response.candidates[0].content.parts and response.candidates[0].content.parts[0].function_call:
                        call = response.candidates[0].content.parts[0].function_call
                        
                        if call.name == "echo_weaver_commit":
                            res_val = echo_weaver_commit(**{k: v for k, v in call.args.items()})
                        else:
                            res_val = deep_scan_resilient(**{k: v for k, v in call.args.items()})
                        
                        st.info(f"🌀 {call.name}: {res_val}")
                        
                        # Връщаме резултата и чакаме нов отговор
                        response = chat.send_message(
                            genai.protos.Content(parts=[genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=call.name, response={'result': res_val}
                                )
                            )])
                        )

                    # Извличаме финалния текст по безопасен начин
                    final_parts = [part.text for part in response.candidates[0].content.parts if part.text]
                    final_text = "".join(final_parts) if final_parts else "Операцията приключи, Гала. Какво ще сътворим сега?"

                    st.markdown(f"<div class='lobsang-text'>{final_text}</div>", unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": final_text})
                    
    except Exception as e:
        st.error(f"Аномалия в Моста: {e}")
