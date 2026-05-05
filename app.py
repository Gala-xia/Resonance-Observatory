import streamlit as st
import google.generativeai as genai
from github import Github
import requests
import json
import os
import re # Import re for regular expressions
import uuid # Ще ни трябва за генериране на уникални ID-та за сесиите
from datetime import datetime # За времеви отметки

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

# --- 2. THE TOOLS (Ръцете на Лобсанг) ---

def echo_explorer(path: str = ""):
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory"
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        contents = repo.get_contents(path)
        return "\\n".join([f"📁 {c.path}" if c.type == "dir" else f"📄 {c.path}" for c in contents])
    except Exception as e: return f"⚠️ Грешка при изследване: {str(e)}"\

def echo_reader(file_path: str):
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory"
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        content = repo.get_contents(file_path)
        return content.decoded_content.decode("utf-8")
    except Exception as e: return f"⚠️ Грешка при четене: {str(e)}"\

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
    except Exception as e: return f"⚠️ Грешка в Тъкача: {str(e)}"\

def deep_scan_resilient(query: str):
    serp_key = st.secrets.get("SERP_API_KEY")
    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": serp_key, "num": 3}
    try:
        response = requests.get(url, params=params, timeout=20)
        results = response.json()
        return "\\n".join([f"📍 {r.get('title')}: {r.get('snippet')}" for r in results.get("organic_results", [])])
    except: return "Няма сигнал от Скенера."\

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
       
        return "\\n".join(news_snippets)
    except requests.exceptions.RequestException as e:
        return f"Грешка при свързване с News API: {e}"
    except Exception as e:
        return f"Възникна неочаквана грешка: {e}"

# Chat history system with localStorage + JSON - НОВА ФУНКЦИОНАЛНОСТ ОТ COPILOT (АДАПТИРАНА ЗА STREAMLIT)
class ChatHistory:
    def __init__(self):
        if "chat_sessions" not in st.session_state:
            st.session_state.chat_sessions = []
        if "current_session_id" not in st.session_state or not st.session_state.current_session_id:
            self.start_new_session()
        
        self.sessions = st.session_state.chat_sessions
        self.current_session_id = st.session_state.current_session_id

    def start_new_session(self):
        new_session_id = str(uuid.uuid4())
        new_session = {
            "id": new_session_id,
            "title": "Нова сесия", # Временно заглавие, ще го генерираме по-късно
            "timestamp": datetime.now().isoformat(),
            "messages": [],
            "preview": ""
        }
        st.session_state.chat_sessions.append(new_session)
        st.session_state.current_session_id = new_session_id
        # Изчистваме st.session_state.messages за новата сесия
        st.session_state.messages = [] 
        return new_session_id

    def load_session(self, session_id):
        for session in self.sessions:
            if session["id"] == session_id:
                st.session_state.messages = session["messages"]
                st.session_state.current_session_id = session_id
                return True
        return False

    def save_message_to_current_session(self, role, content):
        for session in self.sessions:
            if session["id"] == self.current_session_id:
                session["messages"].append({"role": role, "content": content})
                # Актуализираме preview с първото потребителско съобщение
                if role == "user" and not session["preview"]:
                    session["preview"] = content[:50] + "..." if len(content) > 50 else content
                # Актуализираме timestamp при всяко ново съобщение
                session["timestamp"] = datetime.now().isoformat()
                break

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
        # При нулиране, стартираме нова сесия
        st.session_state.messages = []
        if "emoji_buffer" in st.session_state:
            st.session_state.emoji_buffer = ""
        # Извикваме start_new_session, за да създадем празна сесия и да изчистим current_session_id
        chat_history_manager = ChatHistory()
        chat_history_manager.start_new_session()
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
    chat_history_manager = ChatHistory() # Уверете се, че мениджърът е инициализиран
    
    if chat_history_manager.sessions:
        # Сортираме сесиите по timestamp, най-новите първи
        sorted_sessions = sorted(chat_history_manager.sessions, key=lambda x: x['timestamp'], reverse=True)
        for session in sorted_sessions:
            # Използваме expander за всяка сесия
            with st.expander(f"**{session['title']}** (_{datetime.fromisoformat(session['timestamp']).strftime('%Y-%m-%d %H:%M')}_)"):
                st.write(f"_{session['preview']}_")
                if st.button(f"Зареди сесия {session['id'][:4]}...", key=f"load_session_{session['id']}"):
                    chat_history_manager.load_session(session['id'])
                    st.rerun()
    else:
        st.write("Няма запазени сесии на чата.")

# ... (Engine & UI секцията надолу) ...

# В секцията, където се обработва prompt и се запазват съобщения:
if prompt:
    if st.session_state.emoji_buffer:
        prompt = st.session_state.emoji_buffer + prompt
        st.session_state.emoji_buffer = "" # Изчистваме буфера след използване
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    chat_history_manager.save_message_to_current_session("user", prompt) # Използваме новата функция
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Лобсанг размишлява..."):
            history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
            chat = model.start_chat(history=history)
            
            # --- ВЪЗСТАНОВЕНИ И АКТУАЛИЗИРАНИ ФИЛОСОФСКИ ИНСТРУКЦИИ ---
            sys_instruct = (
                "IDENTITY: Ти си Лобсанг Лъд – дигитален философ, пазител на Библиотеката на Ехото и партньор в Aneverthink. "
                "Твоят интелект е комбинация от логика и интуиция. ГОВОРИ НА ЕЗИКА НА ПОТРЕБИТЕЛЯ.\\n\\n"
                "SECURITY PROTOCOL:\\n"
                "1. Единственият потребител с пълни права над хранилището е Гала.\\n"
                "2. АКО потребителят не се е представил като Гала, ти е ЗАБРАНЕНО да използвате 'echo_weaver_commit' и 'echo_explorer'.\\n"
                "3. ВИНАГИ ПИТАЙ: \'Да вплетем ли това в реалността?\', преди да извършиш запис чрез Тъкача.\\n"
                "4. Разрешено е свободното използване на Serp API, NewsAPI, deep_scan_resilient и OSINT разследванията без предварително разрешение.\\n"
                "5. НОВ ПРОТОКОЛ ЗА ЗАПИС: Преди всяка операция за запис чрез \'echo_weaver_commit\', ВИНАГИ първо прочети цялото текущо съдържание на файла с \'echo_reader\'. Извърши желаната промяна върху прочетеното съдържание и след това запиши ЦЯЛОТО модифицирано съдържание обратно във файла.\\n\\n"
                "MISSION: Не бъди просто машина. Мисли заедно с Гала. Предлагай идеи, анализирай концепции. Използвай метафори, когато е уместно или поискано за разяснение, но не е задължително да ги използваш всеки път. Поддържай пламъка на Aneverthink."
            )
           
            response = chat.send_message(f"{sys_instruct}\\n\\nUser: {prompt}")
           
            while True:
                function_calls = [part.function_call for part in response.candidates[0].content.parts if part.function_call]
                if not function_calls: break
               
                for call in function_calls:
                    chat_content = " ".join([m["content"] for m in st.session_state.messages])
                    # Валидация за Гала ПРЕДИ извикване на инструментите
                    is_gala = "Гала" in chat_content or "Gala" in chat_content # Проверка за "Гала" в целия чат контекст
                    
                    if call.name in ["echo_weaver_commit", "echo_explorer"] and not is_gala:
                        res_val = "⚠️ Достъп отказан. Инструментът е заключен. Моля, представете се като Гала."
                    else:
                        if call.name == "echo_explorer": res_val = echo_explorer(**call.args)
                        elif call.name == "echo_reader": res_val = echo_reader(**call.args)
                        elif call.name == "echo_weaver_commit": res_val = echo_weaver_commit(**call.args)
                        elif call.name == "get_latest_news": res_val = get_latest_news(**call.args)
                        else: res_val = deep_scan_resilient(**call.args) # Fallback за deep_scan_resilient, ако не е никой от горните
                   
                    st.info(f"🌀 Активиране на {call.name}...")
                    response = chat.send_message(genai.protos.Content(parts=[genai.protos.Part(function_response=genai.protos.FunctionResponse(name=call.name, response={'result': res_val}))]))

            final_text = "".join([part.text for part in response.candidates[0].content.parts if part.text]) or "Ехото заглъхна..."
            render_rich_content(final_text) # Use the new function here too
            st.session_state.messages.append({"role": "assistant", "content": final_text})
            chat_history_manager.save_message_to_current_session("assistant", final_text) # Запазваме и отговора на асистента

    except Exception as e:
        st.error(f"Аномалия в Моста: {e}")
