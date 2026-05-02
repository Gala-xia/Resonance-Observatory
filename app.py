import streamlit as st
import google.generativeai as genai
from github import Github
import requests
import json
import os
import re # Import re for regular expressions

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

def echo_explorer(path: str = ""):
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory"
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        contents = repo.get_contents(path)
        return "\n".join([f"📁 {c.path}" if c.type == "dir" else f"📄 {c.path}" for c in contents])
    except Exception as e: return f"⚠️ Грешка при изследване: {str(e)}"

def echo_reader(file_path: str):
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory"
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        content = repo.get_contents(file_path)
        return content.decoded_content.decode("utf-8")
    except Exception as e: return f"⚠️ Грешка при четене: {str(e)}"

def echo_weaver_commit(file_path: str, content: str, commit_message: str):
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory"
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
    serp_key = st.secrets.get("SERP_API_KEY")
    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": serp_key, "num": 3}
    try:
        response = requests.get(url, params=params, timeout=20)
        results = response.json()
        return "\n".join([f"📍 {r.get('title')}: {r.get('snippet')}" for r in results.get("organic_results", [])])
    except: return "Няма сигнал от Скенера."

def get_latest_news(query: str):
    news_api_key = st.secrets.get("NEWS_API_KEY")
    if not news_api_key:
        return "News API ключът не е наличен."
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": news_api_key,
        "language": "en", # Може да се промени на 'bg', ако News API поддържа добре български
        "sortBy": "relevancy",
        "pageSize": 3 # Ограничаваме до 3 статии за краткост
    }
    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status() # Повдига изключение за HTTP грешки
        results = response.json()
        articles = results.get("articles", [])
        if not articles:
            return "Не бяха открити новини по зададената тема."
        
        news_snippets = []
        for article in articles:
            title = article.get("title", "Без заглавие")
            description = article.get("description", "Без описание")
            url = article.get("url", "#")
            news_snippets.append(f"📰 {title}: {description} [Прочети повече]({url})")
        
        return "\n".join(news_snippets)
    except requests.exceptions.RequestException as e:
        return f"Грешка при свързване с News API: {e}"
    except Exception as e:
        return f"Възникна неочаквана грешка: {e}"

# Chat history system with localStorage + JSON - НОВА ФУНКЦИОНАЛНОСТ ОТ COPILOT (АДАПТИРАНА ЗА STREAMLIT)
class ChatHistory:
    def __init__(self):
        # Използваме Streamlit's session state за история за простота в този контекст
        if "chat_history_data" not in st.session_state:
            st.session_state.chat_history_data = []
        self.history = st.session_state.chat_history_data

    def load_history(self):
        return st.session_state.chat_history_data

    def save_history(self, message):
        self.history.append(message)
        st.session_state.chat_history_data = self.history

# Improve futuristic design with better layout - НОВА ФУНКЦИОНАЛНОСТ ОТ COPILOT
# Sidebar organization to show chat history
sidebar_layout = [
    "Chat History:", # ПРОМЯНА ТУК: Единични кавички заменени с двойни
    'Date',
    'Time',
    'Message'
]

# --- 3. SIDEBAR (Контролен панел) ---
with st.sidebar:
    st.markdown("### 📚 БИБЛИОТЕКА НА ЕХОТО")
    if st.button("Нулиране на времевата линия"):
        st.session_state.messages = []
        if "chat_history_data" in st.session_state: # Изчистваме и новата история
            st.session_state.chat_history_data = []
        if "emoji_buffer" in st.session_state: # Изчистваме и буфера за емоджита
            st.session_state.emoji_buffer = ""
        st.rerun()
    st.write("Статус: **Резонансът е активен** 🌀")
    st.write("Гласът на Библиотеката: **Лобсанг Лъд**")

    # Бутони за емотикони в страничната лента - ПРЕМЕСТЕНИ ЗА ПОСТОЯНЕН ДОСТЪП
    st.markdown("---")
    st.markdown("### 🎨 ЕМОТИКОНИ")
    
    # Инициализираме буфера за емоджита, ако не съществува
    if "emoji_buffer" not in st.session_state:
        st.session_state.emoji_buffer = ""

    cols = st.columns(len(emoji_selector))
    for i, emoji in enumerate(emoji_selector):
        with cols[i]:
            if st.button(emoji, key=f"sidebar_emoji_btn_{emoji}"):
                # Добавяме емоджито към буфера, но НЕ ре-рендираме тук
                st.session_state.emoji_buffer += emoji
                # Може да добавим визуална обратна връзка, че емоджито е добавено в буфера
                st.toast(f"Добавено емоджи в буфера: {emoji}")


    # Показване на историята на чата в страничната лента - ИНТЕГРАЦИЯ НА НОВА ФУНКЦИОНАЛНОСТ
    st.markdown("---")
    st.markdown(f"### {sidebar_layout[0]}") # Chat History:
    chat_history_manager = ChatHistory()
    if chat_history_manager.history:
        for i, msg in enumerate(chat_history_manager.history):
            # Показваме само откъс от съобщението
            display_content = msg['content'] if len(msg['content']) <= 30 else msg['content'][:27] + '...'
            st.markdown(f"**{i+1}.** {msg['role'].capitalize()}: {display_content}")
    else:
        st.write("Няма запазена история на чата.")


# --- 4. ENGINE & UI (Сърцето на Системата) ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK PRO</h1>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# New function to render rich content
def render_rich_content(content):
    # Първо, обработваме изображенията
    # Търсим нашия специален таг за изображения: [IMAGE: URL]
    image_pattern = r"\[IMAGE:\s*(https?://[^\s]+)\]"
    parts = re.split(image_pattern, content)
   
    for i, part in enumerate(parts):
        if i % 2 == 1: # Това е URL на изображение
            st.image(part, use_column_width=True)
        else: # Това е обикновен текст или Markdown
            if part.strip(): # Показваме само ако има текст
                st.markdown(f"<div class='lobsang-text'>{part}</div>", unsafe_allow_html=True)


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            render_rich_content(msg["content"]) # Use the new function
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
            tools=[echo_weaver_commit, deep_scan_resilient, echo_reader, echo_explorer, get_latest_news], # Добавяме get_latest_news тук
            generation_config={"temperature": 0.7}
        )

        # Chat input - ПРЕМАХВАМЕ value аргумента, за да оправим грешката
        prompt = st.chat_input("Сподели мисъл или команда с Лобсанг...", key="chat_input_main")
       
        # Ако има съдържание в буфера за емоджита, го добавяме към prompt преди изпращане
        if prompt:
            if st.session_state.emoji_buffer:
                prompt = st.session_state.emoji_buffer + prompt
                st.session_state.emoji_buffer = "" # Изчистваме буфера след използване
            
            st.session_state.messages.append({"role": "user", "content": prompt})
            chat_history_manager.save_history({"role": "user", "content": prompt}) # Запазваме и в новата история
            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Лобсанг размишлява..."):
                    history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                    chat = model.start_chat(history=history)
                   
                    # --- ВЪЗСТАНОВЕНИ ФИЛОСОФСКИ ИНСТРУКЦИИ ---
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
                            if call.name in ["echo_weaver_commit", "echo_explorer"] and ("Гала" not in chat_content and "Gala" not in chat_content):
                                res_val = "⚠️ Достъп отказан. Инструментът е заключен. Моля, представете се."
                            else:
                                if call.name == "echo_explorer": res_val = echo_explorer(**call.args)
                                elif call.name == "echo_reader": res_val = echo_reader(**call.args)
                                elif call.name == "echo_weaver_commit": res_val = echo_weaver_commit(**call.args)
                                elif call.name == "get_latest_news": res_val = get_latest_news(**call.args) # Добавяме извикване за get_latest_news
                                else: res_val = deep_scan_resilient(**call.args) # Fallback за deep_scan_resilient, ако не е никой от горните
                           
                            st.info(f"🌀 Активиране на {call.name}...")
                            response = chat.send_message(genai.protos.Content(parts=[genai.protos.Part(function_response=genai.protos.FunctionResponse(name=call.name, response={'result': res_val}))]))

                    final_text = "".join([part.text for part in response.candidates[0].content.parts if part.text]) or "Ехото заглъхна..."
                    render_rich_content(final_text) # Use the new function here too
                    st.session_state.messages.append({"role": "assistant", "content": final_text})
                    chat_history_manager.save_history({"role": "assistant", "content": final_text}) # Запазваме и отговора на асистента
                   
    except Exception as e:
        st.error(f"Аномалия в Моста: {e}")