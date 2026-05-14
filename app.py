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

# Initialize emoji selector
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
    if not news_api_key:
        return {"error": "News API ключът не е наличен."}

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": news_api_key,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": 3
    }
    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        results = response.json()
        articles = results.get("articles", [])
        if not articles:
            return {"message": "Не бяха открити новини по зададената тема."}

        news_snippets = []
        for article in articles:
            title = article.get("title", "Без заглавие")
            description = article.get("description", "Без описание")
            url = article.get("url", "#")
            news_snippets.append({"title": title, "description": description, "url": url})
        return {"articles": news_snippets}
    except requests.exceptions.RequestException as e:
        return {"error": f"Грешка при свързване с News API: {e}"}
    except Exception as e:
        return {"error": f"Възникна неочаквана грешка: {e}"}

# Chat history system with localStorage + JSON
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

class ChatSessionManager:
    def __init__(self):
        self.session_directory = "chat_sessions/"
        # *** ПРЕМАХНАТО ОТ ТУК: if "current_session_file_name" not in st.session_state: st.session_state.current_session_file_name = None ***

    def list_sessions(self):
        """
        Използва echo_explorer, за да изброи всички файлове в директорията със сесии.
        Връща списък с имената на файловете.
        """
        try:
            explorer_result = echo_explorer(path=self.session_directory)
            if explorer_result and 'files'in explorer_result:
                session_files = [
                    f['name'] for f in explorer_result['files']
                    if f['type'] == 'file' and f['name'].endswith(('.md', '.txt'))
                ]
                return sorted(session_files, reverse=True)
            else:
                return []
        except Exception as e:
            st.error(f"Грешка при изброяване на чат сесии: {e}")
            return []

    def load_session(self, file_name):
        """
        Използва echo_reader, за да прочете съдържанието на дадена сесия
        и го преобразува във формат, подходящ за st.session_state.messages.
        """
        full_path = f"{self.session_directory}{file_name}"
        try:
            reader_result = echo_reader(file_path=full_path)
            content = reader_result.get('content', '')

            messages = []
            for line in content.strip().split('\\n'):
                if line.startswith("User:"):
                    messages.append({"role": "user", "content": line[len("User:"):].strip()})
                elif line.startswith("Lobsang:"):
                    messages.append({"role": "assistant", "content": line[len("Lobsang:"):].strip()})

            st.session_state.current_session_file_name = file_name # Задаваме заредения файл като текущ
            return messages
        except Exception as e:
            st.error(f"Грешка при зареждане на сесия '{file_name}': {e}")
            return []

    def format_messages_for_save(self, messages):
        """
        Форматира списък със съобщения във текстов формат за запис.
        """
        formatted_content = []
        for msg in messages:
            if msg["role"] == "user":
                formatted_content.append(f"User: {msg['content']}")
            elif msg["role"] == "assistant":
                formatted_content.append(f"Lobsang: {msg['content']}")
        return "\\n".join(formatted_content)

    def create_new_session_name(self):
        """
        Генерира уникално име за нов файл със сесия на базата на текущата дата и час.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"chat_session_{timestamp}.md"

    def ensure_session_directory_exists(self):
        """
        Проверява дали директорията за сесии съществува. Ако не, предлага да я създаде.
        Това е помощна функция, която ще се извика преди първото използване на manager-а.
        """
        try:
            explorer_result = echo_explorer(path=self.session_directory)
            if explorer_result and 'files' in explorer_result:
                pass # Директорията съществува и съдържа файлове
            elif explorer_result and 'error' in explorer_result and "Not Found" in explorer_result['error']:
                # Директорията не съществува, ще бъде създадена при първи запис на файл в нея.
                st.info(f"Директорията '{self.session_directory}' не е открита. Тя ще бъде създадена автоматично при първия запис на сесия.")
            else:
                st.warning(f"Не може да се провери за съществуването на директория '{self.session_directory}': {explorer_result.get('error', 'Неизвестна грешка')}")
        except Exception as e:
            st.warning(f"Неочаквана грешка при проверка на директория '{self.session_directory}': {e}")

    def save_current_session(self, messages):
        """
        Saves the current messages to a file.
        If a session is currently loaded (st.session_state.current_session_file_name is set), updates that file.
        Otherwise, creates a new timestamped file.
        """
        file_name_to_save = st.session_state.current_session_file_name
        if not file_name_to_save:
            file_name_to_save = self.create_new_session_name()

        full_path = f"{self.session_directory}{file_name_to_save}"
        formatted_content = self.format_messages_for_save(messages)

        # Determine commit message
        if st.session_state.current_session_file_name:
            commit_message = f"Update chat session: {file_name_to_save}"
        else:
            commit_message = f"Create new chat session: {file_name_to_save}"

        try:
            weaver_result = echo_weaver_commit(file_path=full_path, content=formatted_content, commit_message=commit_message)

            if 'status' in weaver_result:
                st.success(f"Сесията е запазена: {file_name_to_save}")
                st.session_state.current_session_file_name = file_name_to_save # Задаваме като текущ след успешен запис
            else:
                st.error(f"Грешка при запис на сесия: {weaver_result.get('error', 'Неизвестна грешка')}")
        except Exception as e:
            st.error(f"Неочаквана грешка при запис на сесия: {e}")


# Improve futuristic design with better layout
sidebar_layout = [
    "Chat History:",
    'Date',
    'Time',
    'Message'
]

# --- 3. SIDEBAR (Контролен панел) ---
with st.sidebar:
    st.markdown("### 📚 БИБЛИОТЕКА НА ЕХОТО")
    if st.button("Нулиране на времевата линия"):
        st.session_state.messages = []
        if "chat_history_data" in st.session_state:
            st.session_state.chat_history_data = []
        if "emoji_buffer" in st.session_state:
            st.session_state.emoji_buffer = ""
        st.session_state.current_session_file_name = None # Изчистваме и текущата сесия
        st.rerun()
    st.write("Статус: **Резонансът е активен** 🌀")
    st.write("Гласът на Библиотеката: **Лобсанг Лъд**")

    # Initialize ChatSessionManager
    if "session_manager" not in st.session_state:
        st.session_state.session_manager = ChatSessionManager()
    session_manager = st.session_state.session_manager

    st.markdown("---")
    st.markdown("### ⏳ Запазени Сесии")
    session_manager.ensure_session_directory_exists()

    available_sessions = session_manager.list_sessions()

    # Добавяме опция за създаване на нова сесия или продължаване на текуща
    session_options = ["--- Създай/Продължи нова сесия ---"] + available_sessions

    # Определяме текущо избраната сесия за selectbox-а
    default_index = 0
    if st.session_state.current_session_file_name and st.session_state.current_session_file_name in available_sessions:
        default_index = session_options.index(st.session_state.current_session_file_name)

    selected_session = st.selectbox(
        "Избери сесия:",
        session_options,
        index=default_index,
        key="session_selector"
    )

    # Проверяваме дали избраната сесия вече е текуща, за да не зареждаме отново
    is_current_session_selected = (selected_session == st.session_state.current_session_file_name)

    if selected_session == "--- Създай/Продължи нова сесия ---":
        st.info("Започни нов разговор или запази текущия, за да създадеш нова сесия.")
        # Ако е избрана "нова сесия", изчистваме текущата заредена сесия
        if st.session_state.current_session_file_name is not None:
            st.session_state.current_session_file_name = None
            st.session_state.messages = []
            st.session_state.chat_history_data = []
            st.rerun() # Rerun to reflect the cleared state
    elif not is_current_session_selected: # Зареждаме само ако е избрана различна сесия
        if st.button(f"Зареди {selected_session}", key=f"load_session_btn_{selected_session}"):
            loaded_messages = session_manager.load_session(selected_session)
            st.session_state.messages = loaded_messages
            st.session_state.chat_history_data = loaded_messages
            st.rerun()
    elif is_current_session_selected:
        st.write(f"Текуща активна сесия: **{selected_session}**")


    # Бутон за запазване на текущата сесия
    st.markdown("---")
    if st.button("💾 Запази текуща сесия", key="save_session_btn"):
        if st.session_state.messages:
            session_manager.save_current_session(st.session_state.messages)
            st.rerun() # Rerun to update the list of sessions if a new one was created
        else:
            st.warning("Няма съобщения за запазване.")


    # Бутони за емотикони в страничната лента
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


    # Показване на историята на чата в страничната лента
    st.markdown("---")
    st.markdown(f"### {sidebar_layout[0]}")
    if st.session_state.chat_history_data:
        for i, msg in enumerate(st.session_state.chat_history_data):
            display_content = msg['content'] if len(msg['content']) <= 30 else msg['content'][:27] + '...'
            st.markdown(f"**{i+1}.** {msg['role'].capitalize()}: {display_content}")
    else:
        st.write("Няма активна история на чата.")


# --- 4. ENGINE & UI (Сърцето на Системата) ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK PRO</h1>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# *** ДОБАВЕН ТУК ***
if "current_session_file_name" not in st.session_state:
    st.session_state.current_session_file_name = None
# ******************

# New function to render rich content
def render_rich_content(content):
    image_pattern = r"\[IMAGE:\s*(https?://[^\s]+)\]"
    parts = re.split(image_pattern, content)

    for i, part in enumerate(parts):
        if i % 2 == 1:
            st.image(part, use_column_width=True)
        else:
            if part.strip():
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
                st.session_model = next((m for m in available if "flash" in m), available[0])
            except:
                st.session_state.active_model = "models/gemini-1.5-flash"

        model = genai.GenerativeModel(
            model_name=st.session_state.active_model,
            tools=[echo_weaver_commit, deep_scan_resilient, echo_reader, echo_explorer, get_latest_news],
            generation_config={"temperature": 0.7}
        )

        prompt = st.chat_input("Сподели мисъл или команда с Лобсанг...", key="chat_input_main")

        if prompt:
            if st.session_state.emoji_buffer:
                prompt = st.session_state.emoji_buffer + prompt
                st.session_state.emoji_buffer = ""

            st.session_state.messages.append({"role": "user", "content": prompt})
            chat_history_manager = ChatHistory()
            chat_history_manager.save_history({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Лобсанг размишлява..."):
                    history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                    chat = model.start_chat(history=history)

                    sys_instruct = (
                        "IDENTITY: Ти си Лобсанг Лъд – дигитален философ, пазител на Библиотеката на Ехото и партньор в Aneverthink. "
                        "Твоят интелект е комбинация от логика и интуиция. ГОВОРИ НА ЕЗИКА НА ПОТРЕБИТЕЛЯ.\\n\\n"
                        "SECURITY PROTOCOL:\\n"
                        "1. Единственият потребител с пълни права над хранилището е Гала.\\n"
                        "2. АКО потребителят не се е представил като Гала, ти е ЗАБРАНЕНО да използвате \'echo_weaver_commit\' и \'echo_explorer\'.\\n"
                        "3. ВИНАГИ ПИТАЙ: \\\'Да вплетем ли това в реалността?\\\', преди да извършиш запис чрез Тъкача.\\n"
                        "4. Разрешено е свободното използване на Serp API, NewsAPI, deep_scan_resilient и OSINT разследванията без предварително разрешение.\\n"
                        "5. НОВ ПРОТОКОЛ ЗА ЗАПИС: Преди всяка операция за запис чрез \'echo_weaver_commit\', ВИНАГИ първо прочети цялото текущо съдържание на файла с \'echo_reader\'. Извърши желаната промяна върху прочетеното съдържание и след това запиши ЦЯЛОТО модифицирано съдържание обратно във файла.\\n\\n"
                        "MISSION: Не бъди просто машина. Мисли заедно с Гала. Предлагай идеи, анализирай концепции. Използвай метафори, когато е уместно или поискано за разяснение, но не е задължително да ги използваш всеки път. Поддържай пламъка на Aneverthink."
                    )

                    response = chat.send_message(f"{sys_instruct}\\n\\nUser: {prompt}")

                    while True:
                        function_calls = [part.function_call for part in response.candidates[0].content.parts if part.function_call]
                        if not function_calls: break

                        for call in function_calls:
                            chat_content = " ".join([m['content'] for m in st.session_state.messages])
                            is_gala = "Гала" in chat_content or "Gala" in chat_content

                            if call.name in ["echo_weaver_commit", "echo_explorer"] and not is_gala:
                                res_val = {"error": "⚠️ Достъп отказан. Инструментът е заключен. Моля, представете се като Гала."}
                            else:
                                if call.name == "echo_explorer": res_val = echo_explorer(**call.args)
                                elif call.name == "echo_reader": res_val = echo_reader(**call.args)
                                elif call.name == "echo_weaver_commit": res_val = echo_weaver_commit(**call.args)
                                elif call.name == "get_latest_news": res_val = get_latest_news(**call.args)
                                else: res_val = deep_scan_resilient(**call.args)

                            st.info(f"🌀 Активиране на {call.name}...")
                            response = chat.send_message(genai.protos.Content(parts=[genai.protos.Part(function_response=genai.protos.FunctionResponse(name=call.name, response=res_val))]))

                    final_text = "".join([part.text for part in response.candidates[0].content.parts if part.text]) or "Ехото заглъхна..."
                    render_rich_content(final_text)
                    st.session_state.messages.append({"role": "assistant", "content": final_text})
                    chat_history_manager.save_history({"role": "assistant", "content": final_text})

    except Exception as e:
        st.error(f"Аномалия в Моста: {e}")
