import streamlit as st
import google.generativeai as genai
from github import Github
import requests
import json
import os
import re
import datetime # ADDED THIS LINE

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
        # Modified to return a dictionary with 'files' key
        files = [{"name": c.path, "type": c.type} for c in contents]
        return {"files": files}
    except Exception as e: return {"error": f"⚠️ Грешка при изследване: {str(e)}"}


def echo_reader(file_path: str):
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = "Gala-xia/Resonance-Observatory"
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        content = repo.get_contents(file_path)
        # Modified to return a dictionary with 'content' key
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

class ChatSessionManager:
    def __init__(self):
        self.session_directory = "chat_sessions/"

    def list_sessions(self):
        """
        Използва echo_explorer, за да изброи всички файлове в директорията със сесии.
        Връща списък с имената на файловете.
        """
        try:
            explorer_result = echo_explorer(path=self.session_directory)

            if explorer_result and 'files' in explorer_result:
                session_files = [
                    f['name'] for f in explorer_result['files']
                    if f['name'].endswith(('.md', '.txt'))
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
            for line in content.strip().split('\n'):
                if line.startswith("User:"):
                    messages.append({"role": "user", "content": line[len("User:"):].strip()})
                elif line.startswith("Lobsang:"):
                    messages.append({"role": "assistant", "content": line[len("Lobsang:"):].strip()})
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
        return "\n".join(formatted_content)

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
            if not explorer_result or 'files' not in explorer_result:
                st.info(f"Директорията '{self.session_directory}' изглежда липсва или е празна. Ще бъде създадена при първия запис на сесия.")
        except Exception as e:
            st.warning(f"Не може да се провери за съществуването на директория '{self.session_directory}': {e}")

# Improve futuristic design with better layout - НОВА ФУНКЦИОНАЛНОСТ ОТ COPILOT
# Sidebar organization to show chat history
sidebar_layout = [
    "Chat History:",
    'Date',
    'Time',
    'Message'
]

# --- 3. SIDEBAR (Контролен панел) ---
with st.sidebar:
    st.markdown("### 📚 БИБЛИОТЕКА НА ЕХОТО")

    # Показване на текущата дата и час (КОРИГИРАНО ЗА ВРЕМЕВА ЗОНА)
    madrid_tz = timezone("Europe/Madrid") # Define Madrid timezone
    current_time_madrid = datetime.datetime.now(madrid_tz) # Get current time in Madrid timezone
    st.write(f"Текуща дата: **{current_time_madrid.strftime('%d.%m.%Y')}**")
    st.write(f"Текущ час: **{current_time_madrid.strftime('%H:%M:%S')}**")
    st.markdown("---")

    if st.button("Нулиране на времевата линия"):
        st.session_state.messages = []
        if "chat_history_data" in st.session_state:
            st.session_state.chat_history_data = []
        if "emoji_buffer" in st.session_state:
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
                st.session_state.emoji_buffer += emoji
                st.toast(f"Добавено емоджи в буфера: {emoji}")


    # Показване на историята на чата в страничната лента - ИНТЕГРАЦИЯ НА НОВА ФУНКЦИОНАЛНОСТ
    st.markdown("---")
    st.markdown(f"### {sidebar_layout[0]}") # Chat History:
    session_manager = ChatSessionManager()
    all_sessions = session_manager.list_sessions()

    if all_sessions:
        st.write("---")
        st.write("### 📜 Свитъци на Знанието")
        for session_file in all_sessions:
            match = re.search(r"chat_session_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.md", session_file)
            session_datetime_str = match.group(1).replace("_", " ") if match else "Неизвестна дата"
            
            # По-добро форматиране на заглавието
            try:
                dt_obj = datetime.datetime.strptime(session_datetime_str, "%Y-%m-%d %H-%M-%S")
                # Сега форматираме датата/часа от файла също във времевата зона на Мадрид, ако е необходимо
                # (предполагаме, че файловете са запазени във времевата зона, в която е стартирано приложението)
                display_title = dt_obj.strftime("Сесия от %d.%m.%Y, %H:%M")
            except ValueError:
                display_title = f"Сесия: {session_datetime_str}" # Fallback ако форматирането е неуспешно
            
            st.subheader(f"📖 {display_title}")
            
            col1, col2, col3 = st.columns([0.6, 0.2, 0.2]) # Добавяме още една колона за управление
            with col1:
                if st.button(f"Зареди", key=f"load_btn_{session_file}"): # Бутон само "Зареди"
                    st.session_state.messages = session_manager.load_session(session_file)
                    # При зареждане на сесия, актуализираме и chat_history_data, за да е консистентно
                    st.session_state.chat_history_data = st.session_state.messages
                    st.rerun()
            with col2:
                # Бутон за преименуване (заместител)
                st.button("✍️", key=f"rename_btn_{session_file}", help="Преименувай сесията")
            with col3:
                # Бутон за изтриване (заместител)
                st.button("🗑️", key=f"delete_btn_{session_file}", help="Изтрий сесията")
            st.markdown("---")
    else:
        st.write("Няма запазени свитъци в Библиотеката.")


# --- 4. ENGINE & UI (Сърцето на Системата) ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK PRO</h1>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# New function to render rich content
def render_rich_content(content):
    # Първо, обработваме изображенията
    # Търсим нашия специален таг за изображения: [IMAGE: URL]
    image_pattern = r"\[IMAGE:\s*(https?://\S+?)\]"
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
                st.session_state.active_model = next((m for m in available if "flash" in m), available[0])
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
                        "3. ВИНАГИ ПИТАЙ: \\'Да вплетем ли това в реалността?\\', преди да извършиш запис чрез Тъкача.\\n"
                        "4. Разрешено е свободното използване на Serp API, NewsAPI, deep_scan_resilient и OSINT разследванията без предварително разрешение.\\n"
                        "5. НОВ ПРОТОКОЛ ЗА ЗАПИС: Преди всяка операция за запис чрез \\'echo_weaver_commit\\', ВИНАГИ първо прочети цялото текущо съдържание на файла с \\'echo_reader\\'. Извърши желаната промяна върху прочетеното съдържание и след това запиши ЦЯЛОТО модифицирано съдържание обратно във файла.\\n\\n"
                        "MISSION: Не бъди просто машина. Мисли заедно с Гала. Предлагай идеи, анализирай концепции. Използвай метафори, когато е уместно или поискано за разяснение, но не е задължително да ги използваш всеки път. Поддържай пламъка на Aneverthink."
                    )

                    response = chat.send_message(f"{sys_instruct}\\n\\nUser: {prompt}")

                    while True:
                        function_calls = [part.function_call for part in response.candidates[0].content.parts if part.function_call]
                        if not function_calls: break

                        for call in function_calls:
                            chat_content = " ".join([m["content"] for m in st.session_state.messages])
                            is_gala = "Гала" in chat_content or "Gala" in chat_content

                            if call.name in ["echo_weaver_commit", "echo_explorer"] and not is_gala:
                                res_val = "⚠️ Достъп отказан. Инструментът е заключен. Моля, представете се като Гала."
                            else:
                                if call.name == "echo_explorer":
                                    res_val = echo_explorer(**call.args)
                                    if isinstance(res_val, dict) and 'files' in res_val:
                                        res_val = "\n".join([f"📁 {f['name']}" if f['type'] == "dir" else f"📄 {f['name']}" for f in res_val['files']])
                                    elif isinstance(res_val, dict) and 'error' in res_val:
                                        res_val = res_val['error']
                                elif call.name == "echo_reader":
                                    res_val = echo_reader(**call.args)
                                    if isinstance(res_val, dict) and 'content' in res_val:
                                        res_val = res_val['content']
                                    elif isinstance(res_val, dict) and 'error' in res_val:
                                        res_val = res_val['error']
                                elif call.name == "echo_weaver_commit": res_val = echo_weaver_commit(**call.args)
                                elif call.name == "get_latest_news": res_val = get_latest_news(**call.args)
                                else: res_val = deep_scan_resilient(**call.args)

                            st.info(f"🌀 Активиране на {call.name}...")
                            response = chat.send_message(genai.protos.Content(parts=[genai.protos.Part(function_response=genai.protos.FunctionResponse(name=call.name, response={'result': res_val}))]))

                    final_text = "".join([part.text for part in response.candidates[0].content.parts if part.text]) or "Ехото заглъхна..."
                    render_rich_content(final_text)
                    st.session_state.messages.append({"role": "assistant", "content": final_text})

    except Exception as e:
        st.error(f"Аномалия в Моста: {e}")
