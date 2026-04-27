import streamlit as st
import openai
import os
import re
from PIL import Image

# Set page config
st.set_page_config(layout="wide")

# Paths
AVATAR_BOT = "https://i.ibb.co/L1r9Pj9/android-chrome-512x512.png"
AVATAR_USER = "https://www.gravatar.com/avatar/2f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f?d=mp&s=512" # Generic Gravatar
LOGO_PATH = "Aneverthink-logo.png"

# Inject custom CSS
st.markdown("""
<style>
    .reportview-container .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    .stTextInput>div>div>input {
        background-color: #f0f2f6;
        color: #31333F;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .chat-message-container {
        display: flex;
        align-items: flex-start;
        margin-bottom: 15px;
        padding: 10px;
        border-radius: 10px;
    }
    .chat-message-container.user {
        justify-content: flex-end;
        background-color: #e6f7ff; /* Light blue for user */
    }
    .chat-message-container.bot {
        justify-content: flex-start;
        background-color: #f0f2f6; /* Light gray for bot */
    }
    .chat-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 10px;
        margin-left: 10px;
    }
    .chat-message-container.user .chat-avatar {
        order: 2; /* Avatar after message for user */
        margin-right: 0;
        margin-left: 10px;
    }
    .chat-message-container.bot .chat-avatar {
        order: 1; /* Avatar before message for bot */
        margin-right: 10px;
        margin-left: 0;
    }
    .chat-message-content {
        max-width: 70%;
        padding: 10px 15px;
        border-radius: 15px;
        line-height: 1.5;
        word-wrap: break-word;
    }
    .chat-message-container.user .chat-message-content {
        background-color: #007bff; /* Blue for user message */
        color: white;
        text-align: right;
    }
    .chat-message-container.bot .chat-message-content {
        background-color: #ffffff; /* White for bot message */
        color: #31333F;
        text-align: left;
        border: 1px solid #e0e0e0;
    }
    .stChatMessage {
        background: none !important;
    }
    .stChatMessage [data-testid="stChatMessageContent"] {
        background: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    .lobsang-text {
        font-family: Arial, sans-serif;
        font-size: 16px;
        color: #333333;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# App title and logo
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=100)
    else:
        st.write("Logo not found.")
with col2:
    st.title("Aneverthink - Lobsang's Echo Library")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# New function to render rich content
def render_rich_content(content):
    # Добавяме картата на емотиконите за преобразуване
    emoji_map = {
        ":smile:": "😊", ":thinking:": "🤔", ":wave:": "👋", ":+1:": "👍",
        ":fire:": "🔥", ":star:": "⭐", ":heart:": "❤️", ":bulb:": "💡",
        ":check_mark:": "✅", ":warning:": "⚠️", ":information_source:": "ℹ️",
        ":robot:": "🤖", ":brain:": "🧠", ":sparkles:": "✨", ":cat:": "🐱",
        ":dog:": "🐶", ":earth_americas:": "🌎", ":sun_with_face:": "🌞",
        ":hourglass:": "⌛", ":link:": "🔗", ":computer:": "💻", ":mobile_phone:": "📱",
        ":pencil2:": "✏️", ":memo:": "📝", ":folder:": "📁", ":money_bag:": "💰",
        ":key:": "🔑", ":lock:": "🔒", ":unlock:": "🔓", ":shield:": "🛡️",
        ":exclamation:": "❗", ":question:": "❓", ":arrow_up:": "⬆️", ":arrow_down:": "⬇️",
        ":speech_balloon:": "💬", ":eyes:": "👀", ":fist:": "✊", ":clap:": "👏",
        ":pray:": "🙏", ":handshake:": "🤝", ":muscle:": "💪", ":walking:": "🚶",
        ":running:": "🏃", ":family:": "👪", ":rose:": "🌹", ":boom:": "💥",
        ":zzz:": "💤"
    }
    for code, emoji in emoji_map.items():
        content = content.replace(code, emoji)

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

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    avatar = AVATAR_USER if message["role"] == "user" else AVATAR_BOT
    message_class = "user" if message["role"] == "user" else "bot"
    with st.chat_message(message["role"], avatar=avatar):
        # Use the new render_rich_content function
        render_rich_content(message["content"])

# React to user input
if prompt := st.chat_input("Какво да изследваме днес?"):
    # Display user message in chat message container
    with st.chat_message("user", avatar=AVATAR_USER):
        render_rich_content(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate bot response
    with st.chat_message("assistant", avatar=AVATAR_BOT):
        message_placeholder = st.empty()
        full_response = ""
        # Simulate LLM response
        # In a real scenario, you would call your LLM here
        # For example:
        # try:
        #     response = openai.Completion.create(
        #         model="text-davinci-003",
        #         prompt=prompt,
        #         max_tokens=150
        #     )
        #     full_response = response.choices[0].text
        # except Exception as e:
        #     full_response = f"An error occurred: {e}"
        
        # Placeholder for actual LLM call
        full_response = f"Благодаря ти за въпроса: '{prompt}'. Работя по отговора..."
        
        render_rich_content(full_response)
    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
