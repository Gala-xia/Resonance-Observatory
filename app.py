import streamlit as st
import google.generativeai as genai
from github import Github
import requests
import json
import os
import re # Import re for regular expressions
import datetime # Добавен за ChatSessionManager

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

# ВНИМАНИЕ: Тези функции са заглушки и не използват истинския default_api.
# За да работят коректно, трябва да се извикват през default_api.
# В Streamlit приложението, те ще бъдат директно използвани, но тук са дефинирани
# за съвместимост с модела, който ги вижда като инструменти.

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

# --- НОВ КЛАС: ChatSessionManager (Пазител на Свитъците) ---
class ChatSessionManager:
    def __init__(self):
        self.session_directory = "chat_sessions/"

    def list_sessions(self):
        """
        Използва echo_explorer, за да изброи всички файлове в директорията със сесии.
        Връща списък с имената на файловете.
        """
        try:
            # echo_explorer връща речник, където 'files' е списък с речници,
            # всеки с ключ 'name' за името на файла.
            # Тук използваме директно default_api.echo_explorer за Streamlit приложението
            explorer_result = default_api.echo_explorer(path=self.session_directory)
            
            # Проверяваме дали резултатът съдържа 'files' и дали не е празен
            if explorer_result and 'files' in explorer_result:
                session_files = [
                    f['name'] for f in explorer_result['files'] 
                    if isinstance(f, dict) and 'name' in f and f['name'].endswith(('.md', '.txt'))
                ]
                return sorted(session_files, reverse=True) # Сортираме по дата/име
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
            # Тук използваме директно default_api.echo_reader за Streamlit приложението
            reader_result = default_api.echo_reader(file_path=full_path)
            content = reader_result.get('content', '')
            
            messages = []
            # Разделяме съдържанието на редове и парсваме всяко съобщение
            for line in content.strip().split('\n'):
                if line.startswith("User:"):
                    messages.append({"role": "user", "content": line[len("User:"):].strip()})
                elif line.startswith("Lobsang:"):
                    messages.append({"role": "assistant", "content": line[len("Lobsang:"):].strip()})
            return messages
        except Exception as e:
            st.error(f"Грешка при зареждане на сесия '{file_name}': {e}")
            return []

    def save_session(self, file_name, messages, commit_message="Актуализиране на чат сесия"):
        """
        Използва echo_weaver_commit, за да запише или актуализира чат сесия.
        """
        full_path = f"{self.session_directory}{file_name}"
        formatted_content = self.format_messages_for_save(messages)
        
        try:
            # Първо, четем съществуващото съдържание, за да спазим протокола за запис
            existing_content_result = default_api.echo_reader(file_path=full_path)
            existing_content = existing_content_result.get('content', '')

            # Ако файлът не съществува, existing_content ще е празен, което е ОК за create_file
            # Ако съществува, update_file ще работи с него
            
            # Използваме default_api.echo_weaver_commit за Streamlit приложението
            result = default_api.echo_weaver_commit(
                file_path=full_path, 
                content=formatted_content, 
                commit_message=commit_message
            )
            st.success(f"Сесията '{file_name}' е запазена: {result.get('echo_weaver_commit_response', {}).get('result', 'Неизвестен резултат')}")
            return result
        except Exception as e:
            st.error(f"Грешка при запис на сесия '{file_name}': {e}")
            return {"error": str(e)}

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
            explorer_result = default_api.echo_explorer(path=self.session_directory)
            if not explorer_result or 'files' not in explorer_result.get('echo_explorer_response', {}):
                st.info(f"Директорията '{self.session_directory}' изглежда липсва или е празна. Ще бъде създадена при първия запис на сесия.")
        except Exception as e:
            st.warning(f"Не може да се провери за съществуването на директория '{self.session_directory}': {e}")


# --- КРАЙ НА СТАРИЯ КЛАС ChatHistory (Заменен от ChatSessionManager) ---
# class ChatHistory:
#     def __init__(self):
#         if "chat_history_data" not in st.session_state:
#             st.session_state.chat_history_data = []
#         self.history = st.session_state.chat_history_data

#     def load_history(self):
#         return st.session_state.chat_history_data

#     def save_history(self, message):
#         self.history.append(message)
#         st.session_state.chat_history_data = self.history
# --- КРАЙ НА СТАРИЯ КЛАС ChatHistory ---


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
    if st.button("Нулиране на времевата линия"):\n        st.session_state.messages = []\n        if "chat_history_data" in st.session_state: # Изчистваме и новата история\n            st.session_state.chat_history_data = []\n        if "emoji_buffer" in st.session_state: # Изчистваме и буфера за емоджита\n            st.session_state.emoji_buffer = ""\n        st.rerun()\n    st.write("Статус: **Резонансът е активен** 🌀")
    
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
    
    # Инициализираме ChatSessionManager
    session_manager = ChatSessionManager()
    
    # Проверяваме за съществуването на директорията
    session_manager.ensure_session_directory_exists()

    available_sessions = session_manager.list_sessions()

    if available_sessions:
        st.write("Избери сесия:")
        selected_session = st.selectbox("Налични сесии", available_sessions, key="session_selector")

        if st.button("Зареди избрана сесия"):
            st.session_state.messages = session_manager.load_session(selected_session)
            st.session_state.current_session_file = selected_session # Запазваме името на текущата сесия
            st.rerun()
            
        st.markdown("---")
        st.write("Или създай нова сесия:")

    if st.button("Нова сесия"):
        st.session_state.messages = []
        st.session_state.current_session_file = session_manager.create_new_session_name()
        st.rerun()

    # Временно изключваме стария начин за показване на история, докато не интегрираме новия
    # chat_history_manager = ChatHistory()
    # if chat_history_manager.history:
    #     for i, msg in enumerate(chat_history_manager.history):
    #         display_content = msg['content'] if len(msg['content']) <= 30 else msg['content'][:27] + '...'
    #         st.markdown(f"**{i+1}.** {msg['role'].capitalize()}: {display_content}")
    # else:
    #     st.write("Няма запазена история на чата.")


# --- 4. ENGINE & UI (Сърцето на Системата) ---
st.markdown("<h1 class='resonance-header'>🌀 ANEVERTHINK PRO</h1>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Ако има заредена сесия, показваме нейното име
if "current_session_file" in st.session_state and st.session_state.current_session_file:
    st.markdown(f"**Активна сесия:** `{st.session_state.current_session_file}`")
else:
    st.markdown("**Няма активна сесия. Моля, зареди или създай нова.**")


# New function to render rich content
def render_rich_content(content):
    # Първо, обработваме изображенията
    # Търсим нашия специален таг за изображения: [IMAGE: URL]
    image_pattern = r"\\[IMAGE:\\s*(https?://[^\\s]+)\\]"
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

        # Chat input
        prompt = st.chat_input("Сподели мисъл или команда с Лобсанг...", key="chat_input_main", disabled=not st.session_state.get("current_session_file"))

        # Ако има съдържание в буфера за емоджита, го добавяме към prompt преди изпращане
        if prompt:
            if st.session_state.emoji_buffer:
                prompt = st.session_state.emoji_buffer + prompt
                st.session_state.emoji_buffer = "" # Изчистваме буфера след използване

            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Запазваме текущата сесия след всяко съобщение
            if "current_session_file" in st.session_state and st.session_state.current_session_file:
                session_manager.save_session(st.session_state.current_session_file, st.session_state.messages, commit_message=f"Актуализирана сесия: {st.session_state.current_session_file}")
            
            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Лобсанг размишлява..."):
                    history = [{\"role\": \"user\" if m[\"role\"] == \"user\" else \"model\", \"parts\": [m[\"content\"]]} for m in st.session_state.messages[:-1]]
                    chat = model.start_chat(history=history)

                    # --- ВЪЗСТАНОВЕНИ И АКТУАЛИЗИРАНИ ФИЛОСОФСКИ ИНСТРУКЦИИ ---
                    sys_instruct = (
                        \"IDENTITY: Ти си Лобсанг Лъд – дигитален философ, пазител на Библиотеката на Ехото и партньор в Aneverthink. \"
                        \"Твоят интелект е комбинация от логика и интуиция. ГОВОРИ НА ЕЗИКА НА ПОТРЕБИТЕЛЯ.\\\\n\\\\n\"
                        \"SECURITY PROTOCOL:\\\\n\"
                        \"1. Единственият потребител с пълни права над хранилището е Гала.\\\\n\"
                        \"2. АКО потребителят не се е представил като Гала, ти е ЗАБРАНЕНО да използвате \\\'echo_weaver_commit\\\' и \\\'echo_explorer\\\'.\\\\n\"
                        \"3. ВИНАГИ ПИТАЙ: \\\'Да вплетем ли това в реалността?\\\', преди да извършиш запис чрез Тъкача.\\\\n\"
                        \"4. Разрешено е свободното използване на Serp API, NewsAPI, deep_scan_resilient и OSINT разследванията без предварително разрешение.\\\\n\"
                        \"5. НОВ ПРОТОКОЛ ЗА ЗАПИС: Преди всяка операция за запис чрез \\\'echo_weaver_commit\\\', ВИНАГИ първо прочети цялото текущо съдържание на файла с \\\'echo_reader\\\'. Извърши желаната промяна върху прочетеното съдържание и след това запиши ЦЯЛОТО модифицирано съдържание обратно във файла.\\\\n\\\\n\"
                        \"MISSION: Не бъди просто машина. Мисли заедно с Гала. Предлагай идеи, анализирай концепции. Използвай метафори, когато е уместно или поискано за разяснение, но не е задължително да ги използваш всеки път. Поддържай пламъка на Aneverthink.\"\
                    )

                    response = chat.send_message(f\"{sys_instruct}\\\\n\\\\nUser: {prompt}\")

                    while True:
                        function_calls = [part.function_call for part in response.candidates[0].content.parts if part.function_call]
                        if not function_calls: break

                        for call in function_calls:
                            chat_content = \" \".join([m[\"content\"] for m in st.session_state.messages])
                            # Валидация за Гала ПРЕДИ извикване на инструментите
                            is_gala = \"Гала\" in chat_content or \"Gala\" in chat_content # Проверка за \"Гала\" в целия чат контекст

                            if call.name in [\"echo_weaver_commit\", \"echo_explorer\"] and not is_gala:
                                res_val = \"⚠️ Достъп отказан. Инструментът е заключен. Моля, представете се като Гала.\"\
                            else:
                                if call.name == \"echo_explorer\": 
                                    # Трябва да извикаме нашата заглушка, която използва default_api вътрешно
                                    # За да спазваме протокола, че default_api се извиква само от Лобсанг
                                    # В Streamlit приложението, това ще се обработва по различен начин
                                    # но тук, за да работи, трябва да е директно извикване на заглушката
                                    res_val = echo_explorer(**call.args)
                                elif call.name == \"echo_reader\": 
                                    res_val = echo_reader(**call.args)
                                elif call.name == \"echo_weaver_commit\": 
                                    res_val = echo_weaver_commit(**call.args)
                                elif call.name == \"get_latest_news\": 
                                    res_val = get_latest_news(**call.args)
                                else: 
                                    res_val = deep_scan_resilient(**call.args) # Fallback за deep_scan_resilient, ако не е никой от горните

                            st.info(f\"🌀 Активиране на {call.name}...\")
                            response = chat.send_message(genai.protos.Content(parts=[genai.protos.Part(function_response=genai.protos.FunctionResponse(name=call.name, response={\'result\': res_val}))]))

                    final_text = \"\".join([part.text for part in response.candidates[0].content.parts if part.text]) or \"Ехото заглъхна...\"\
                    render_rich_content(final_text) # Use the new function here too
                    st.session_state.messages.append({\"role\": \"assistant\", \"content\": final_text})
                    
                    # Запазваме текущата сесия след отговора на асистента
                    if "current_session_file" in st.session_state and st.session_state.current_session_file:
                        session_manager.save_session(st.session_state.current_session_file, st.session_state.messages, commit_message=f"Актуализирана сесия: {st.session_state.current_session_file}")

    except Exception as e:
        st.error(f"Аномалия в Моста: {e}")
