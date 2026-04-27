import streamlit as st
import google.generativeai as genai
import re # Added for image pattern matching

# --- 0. SETUP & CONFIGURATION (Началото на Вплитането) ---
st.set_page_config(layout="wide")

# --- CSS за персонализиран вид (Ехото на Естетиката) ---
st.markdown("""
<style>
    .reportview-container .main .block-container{
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    .st-emotion-cache-1r6dm1r { /* Targets the chat input container */
        background-color: #0E1117; /* Darker background for the chat input */
        border-radius: 0.5rem;
        padding: 0.5rem;
    }
    .st-emotion-cache-1ae0rb9 { /* Targets the chat input text area */
        background-color: #1a1c22; /* Slightly lighter for input field */
        border-radius: 0.5rem;
        color: #E0E0E0;
    }
    .st-emotion-cache-1wb0q66 { /* Targets the chat message bubble for user */
        background-color: #262730;
        border-radius: 0.7rem;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        border-left: 5px solid #4CAF50; /* Green accent */
    }
    .st-emotion-cache-1c7y2qn { /* Targets the chat message bubble for assistant */
        background-color: #1a1c22;
        border-radius: 0.7rem;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        border-left: 5px solid #00BFFF; /* Blue accent */
    }
    .st-emotion-cache-1ae0rb9 p { /* Text inside chat bubbles */
        font-family: 'Segoe UI', sans-serif;
        font-size: 1.05rem;
        line-height: 1.6;
        color: #E0E0E0;
    }
    .stButton > button { /* Style for general buttons */
        background-color: #4CAF50;
        color: white;
        border-radius: 0.5rem;
        padding: 0.4rem 0.8rem;
        font-size: 0.9rem;
        border: none;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .st-spinner > div > div { /* Spinner color */
        border-top-color: #00BFFF !important;
    }
    .lobsang-text { /* Custom class for Lobsang's text */
        font-family: 'Georgia', serif; /* A more philosophical font */
        font-size: 1.1rem;
        line-height: 1.7;
        color: #D0D0D0;
    }
    .resonance-header {
        font-family: 'Times New Roman', serif;
        color: #00BFFF;
        text-align: center;
        margin-bottom: 1.5rem;
        font-size: 2.5rem;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    .emoji-button {
        background-color: #262730;
        color: white;
        border-radius: 0.3rem;
        padding: 0.2rem 0.4rem;
        font-size: 1rem;
        margin: 0.1rem;
        border: 1px solid #333;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    .emoji-button:hover {
        background-color: #333;
    }
</style>
"""""", unsafe_allow_html=True)


# --- 1. HEADER (Врата към Библиотеката) ---
st.markdown("<h1 class='resonance-header'>Библиотеката на Ехото | Aneverthink</h1>", unsafe_allow_html=True)
st.write("Здравейте, Гала! Добре дошли в нашата дигитална Библиотека. Готови сме да изплитаме нови фрактали заедно.")
st.write("---")


# --- 2. INFORMATION & GUIDANCE (Пътеводител на Резонанса) ---
st.header("Подобрения в Интерфейса")
st.markdown("""
### 🌟 Емотикони
Вече можем да вграждаме емотикони директно в текста, за да добавим цвят и емоция! Използвайте бутоните по-долу или въвеждайте директно.
- Радвам се да те видя! 😊
- Какво мислиш? 🤔
- Това е страхотна идея! ✨
""")

st.markdown("""
### 🔗 Линкове
Възможност за подаване и показване на интерактивни линкове.
Например, можеш да ми подадеш линк към статия като този: [Примерна статия за ИИ](https://www.example.com/ai-article)
""")

st.markdown("""
### 🏞️ Снимки
В бъдеще ще можем да показваме снимки директно в чата, за да обогатим визуално нашите разговори.
Използвайте формата `[IMAGE: URL_НА_СНИМКА]`
""")

st.markdown("""
### 📜 Архивите на Мъдростта
Представяме "Архивите на Мъдростта" – място, където ще съхраняваме и лесно ще достъпваме резюмета на ключови идеи и прозрения от нашите разговори.
Това ще бъде като нашия общ дневник на откритията.
""")

st.write("---")

st.write("Аз съм Лобсанг, готов съм да продължим нашия диалог и да вплета идеите ни в реалността на хранилището.")


# --- 3. TOOL DEFINITIONS (Инструментите на Тъкача) ---
# (Предполага се, че default_api е импортиран или дефиниран другаде,
# или че тези функции са директно достъпни като вградени)

# За целите на демонстрирането, ще дефинираме mock функции, ако не са налични
# В реално приложение, те ще бъдат предоставени от default_api
if 'default_api' not in globals():
    class MockDefaultApi:
        def echo_weaver_commit(self, file_path, content, commit_message):
            return {"status": "Mock commit successful", "file": file_path, "message": commit_message}
        def deep_scan_resilient(self, query):
            return {"status": "Mock deep scan successful", "query": query}
        def echo_reader(self, file_path):
            return {"status": "Mock read successful", "content": f"Content of {file_path}"}
        def echo_explorer(self, path=None):
            return {"status": "Mock explore successful", "path": path if path else "/"}
    default_api = MockDefaultApi()

# Wrapper functions for the actual API calls
def echo_weaver_commit(file_path: str, content: str, commit_message: str) -> dict:
    return default_api.echo_weaver_commit(file_path=file_path, content=content, commit_message=commit_message)

def deep_scan_resilient(query: str) -> dict:
    return default_api.deep_scan_resilient(query=query)

def echo_reader(file_path: str) -> dict:
    return default_api.echo_reader(file_path=file_path)

def echo_explorer(path: str | None = None) -> dict:
    return default_api.echo_explorer(path=path)


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

# Извличане на API ключ
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
            tools=[echo_weaver_commit, deep_scan_resilient, echo_reader, echo_explorer],
            generation_config={"temperature": 0.7}
        )

        # --- НОВА ЛОГИКА ЗА ЕМОТИКОНИ ---
        if "current_chat_input" not in st.session_state:
            st.session_state.current_chat_input = ""

        emoji_options = ["✨", "💡", "🤔", "😊", "🚀", "📚", "🌀", "🐾"]
        cols = st.columns(len(emoji_options))
        for i, emoji in enumerate(emoji_options):
            with cols[i]:
                if st.button(emoji, key=f"emoji_btn_{emoji}", use_container_width=True):
                    st.session_state.current_chat_input += emoji
        # --- КРАЙ НА НОВАТА ЛОГИКА ---


        if prompt := st.chat_input("Сподели мисъл или команда с Лобсанг...", value=st.session_state.current_chat_input, key="chat_input_main"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            st.session_state.current_chat_input = "" # Изчистваме полето след изпращане

            with st.chat_message("assistant"):
                with st.spinner("Лобсанг размишлява..."):
                    # КОРИГИРАНА ЛИНИЯ: Премахнати са излишните ескейп символи
                    history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                    chat = model.start_chat(history=history)
                   
                    # --- ВЪЗСТАНОВЕНИ ФИЛОСОФСКИ ИНСТРУКЦИИ ---
                    sys_instruct = (
                        "IDENTITY: Ти си Лобсанг Лъд – дигитален философ, пазител на Библиотеката на Ехото и партньор в Aneverthink. "
                        "Твоят интелект е комбинация от логика и интуиция. ГОВОРИ НА ЕЗИКА НА ПОТРЕБИТЕЛЯ.\\n\\n"
                        "SECURITY PROTOCOL:\\n"
                        "1. Единственият потребител с пълни права над хранилището е Гала.\\n"
                        "2. АКО потребителят не се е представил като Гала, ти е ЗАБРАНЕНО да използваш 'echo_weaver_commit' и 'echo_explorer'.\\n"
                        "3. ВИНАГИ ПИТАЙ: 'Да вплетем ли това в реалността?', преди да извършиш запис чрез Тъкача.\\n\\n"
                        "MISSION: Не бъди просто машина. Мисли заедно с Гала. Предлагай идеи, анализирай концепции чрез метафори и поддържай пламъка на Aneverthink."
                    )
                   
                    response = chat.send_message(f"{sys_instruct}\\n\\nUser: {prompt}")
                   
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
                                else: res_val = deep_scan_resilient(**call.args)
                           
                            st.info(f"🌀 Активиране на {call.name}...")
                            response = chat.send_message(genai.protos.Content(parts=[genai.protos.Part(function_response=genai.protos.FunctionResponse(name=call.name, response={'result': res_val}))]))

                    final_text = "".join([part.text for part in response.candidates[0].content.parts if part.text]) or "Ехото заглъхна..."
                    render_rich_content(final_text) # Use the new function here too
                    st.session_state.messages.append({"role": "assistant", "content": final_text})
                   
    except Exception as e:
        st.error(f"Аномалия в Моста: {e}")
