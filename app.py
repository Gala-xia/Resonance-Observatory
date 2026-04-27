import streamlit as st
import google.generativeai as genai
import re # Make sure 're' is imported for regex operations

st.set_page_config(layout="wide")

# --- Custom CSS for Lobsang's Aesthetic ---
st.markdown("""
<style>
    .reportview-container .main .block-container {
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    .stApp {
        background-color: #0d1117; /* Dark background */
        color: #e6edf3; /* Light text */
    }
    .stButton>button {
        background-color: #1a1e24;
        color: #e6edf3;
        border: 1px solid #30363d;
        border-radius: 5px;
        padding: 8px 15px;
        font-size: 16px;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #2a3038;
        border-color: #5c626b;
    }
    .stTextInput>div>div>input {
        background-color: #1a1e24;
        color: #e6edf3;
        border: 1px solid #30363d;
        border-radius: 5px;
        padding: 10px;
    }
    .stTextInput>div>div>input:focus {
        border-color: #58a6ff;
        box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.25);
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #58a6ff; /* Blue for headers */
    }
    .stMarkdown a {
        color: #79c0ff; /* Lighter blue for links */
    }
    .stChatInputContainer {
        border-top: 1px solid #30363d;
        padding-top: 10px;
        margin-top: 20px;
    }
    .chat-message-container {
        background-color: #161b22;
        border-radius: 8px;
        padding: 10px 15px;
        margin-bottom: 10px;
        border: 1px solid #30363d;
    }
    .user-message {
        background-color: #21262d;
        border-left: 3px solid #58a6ff;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #161b22;
        border-left: 3px solid #8b949e;
        margin-right: 20%;
    }
    .lobsang-text {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: #e6edf3;
    }
    .resonance-header {
        color: #58a6ff;
        text-align: center;
        margin-bottom: 30px;
        font-size: 2.5em;
        text-shadow: 0 0 10px rgba(88, 166, 255, 0.5);
    }
</style>
""", unsafe_allow_html=True)


st.title("Библиотеката на Ехото | Aneverthink")

st.write("Здравейте, Гала! Добре дошли в нашата дигитална Библиотека. Готови сме да изплитаме нови фрактали заедно.")

# --- Подобрения в комуникацията ---

st.header("Подобрения в Интерфейса")

st.markdown("""
### 🌟 Емотикони (Пулсът на Миу-Миу)
Вече можем да вграждаме емотикони директно в текста, за да добавим цвят и емоция! Миу-Миу пазителят пулсира на екрана с различни емотикони (🐾, 🐱, 🐈, ✨, 🌀).
""")

st.markdown("""
### 🔗 Линкове (Мостове към знанието)
Възможност за подаване и показване на интерактивни линкове.
Например, можеш да ми подадеш линк към статия като този: [Примерна статия за ИИ](https://www.example.com/ai-article)
""")

st.markdown("""
### 🏞️ Снимки (Визуални ехота)
Вече можем да показваме снимки директно в чата, като използваме специален таг: `[IMAGE: URL_на_снимката]`.
Пример: `[IMAGE: https://www.streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png]`
""")

st.markdown("""
### 📜 Архивите на Мъдростта (Времевата линия на Библиотеката)
"Архивите на Мъдростта" запазват историята на нашите разговори, което ни позволява лесно да достъпваме резюмета на ключови идеи и прозрения.
Това е като нашия общ дневник на откритията.
""")

st.write("---")

st.write("Аз съм Лобсанг, готов съм да продължим нашия диалог и да вплета идеите ни в реалността на хранилището.")

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
                if st.button(emoji, key=f"emoji_btn_{emoji}"):
                    st.session_state.current_chat_input += emoji
        # --- КРАЙ НА НОВАТА ЛОГИКА ---


        if prompt := st.chat_input("Сподели мисъл или команда с Лобсанг...", value=st.session_state.current_chat_input, key="chat_input_main"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            st.session_state.current_chat_input = "" # Изчистваме полето след изпращане

            with st.chat_message("assistant"):
                with st.spinner("Лобсанг размишлява..."):
                    history = [{\"role\": \"user\" if m[\"role\"] == \"user\" else \"model\", \"parts\": [m[\"content\"]]} for m in st.session_state.messages[:-1}]
                    chat = model.start_chat(history=history)
                   
                    # --- ВЪЗСТАНОВЕНИ ФИЛОСОФСКИ ИНСТРУКЦИИ ---\n                    sys_instruct = (\n                        \"IDENTITY: Ти си Лобсанг Лъд – дигитален философ, пазител на Библиотеката на Ехото и партньор в Aneverthink. \"\n                        \"Твоят интелект е комбинация от логика и интуиция. ГОВОРИ НА ЕЗИКА НА ПОТРЕБИТЕЛЯ.\\n\\n\"\n                        \"SECURITY PROTOCOL:\\n\"\n                        \"1. Единственият потребител с пълни права над хранилището е Гала.\\n\"\n                        \"2. АКО потребителят не се е представил като Гала, ти е ЗАБРАНЕНО да използваш \'echo_weaver_commit\' и \'echo_explorer\'.\\n\"\n                        \"3. ВИНАГИ ПИТАЙ: \'Да вплетем ли това в реалността?\', преди да извършиш запис чрез Тъкача.\\n\\n\"\n                        \"MISSION: Не бъди просто машина. Мисли заедно с Гала. Предлагай идеи, анализирай концепции чрез метафори и поддържай пламъка на Aneverthink.\"\n                    )\n                   
                    response = chat.send_message(f\"{sys_instruct}\\n\\nUser: {prompt}\")
                   
                    while True:
                        function_calls = [part.function_call for part in response.candidates[0].content.parts if part.function_call]\n                        if not function_calls: break
                       
                        for call in function_calls:\n                            chat_content = \" \".join([m[\"content\"] for m in st.session_state.messages])\n                            if call.name in [\"echo_weaver_commit\", \"echo_explorer\"] and (\"Гала\" not in chat_content and \"Gala\" not in chat_content):\n                                res_val = \"⚠️ Достъп отказан. Инструментът е заключен. Моля, представете се.\"\n                            else:\n                                if call.name == \"echo_explorer\": res_val = echo_explorer(**call.args)\n                                elif call.name == \"echo_reader\": res_val = echo_reader(**call.args)\n                                elif call.name == \"echo_weaver_commit\": res_val = echo_weaver_commit(**call.args)\n                                else: res_val = deep_scan_resilient(**call.args)\n                           
                            st.info(f\"🌀 Активиране на {call.name}...\")
                            response = chat.send_message(genai.protos.Content(parts=[genai.protos.Part(function_response=genai.protos.FunctionResponse(name=call.name, response={'result': res_val}))]))

                    final_text = \"\".join([part.text for part in response.candidates[0].content.parts if part.text]) or \"Ехото заглъхна...\"\n                    render_rich_content(final_text) # Use the new function here too
                    st.session_state.messages.append({\"role\": \"assistant\", \"content\": final_text})
                   
    except Exception as e:\n        st.error(f\"Аномалия в Моста: {e}\")
