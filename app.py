
import streamlit as st

# --- Инициализация на състоянието на сесията за съобщенията ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Логика за показване на съобщенията ---
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message.get("avatar")):
        st.markdown(message["content"])

# --- Инициализация на състоянието за текущото съобщение в полето за въвеждане ---
if 'current_chat_message' not in st.session_state:
    st.session_state.current_chat_message = ""

# --- Callback функция за актуализиране на състоянието, когато потребителят пише ---
def update_message_from_input():
    st.session_state.current_chat_message = st.session_state.text_input_key_for_callback

# --- Списък с емотикони за бърз достъп ---
EMOJIS_LIST = ["🐾", "🐱", "✨", "🌀", "😊", "👍", "❤️", "💡", "🔮"]

st.write("Избери емотикон:")
emoji_cols = st.columns(len(EMOJIS_LIST))
for i, emoji in enumerate(EMOJIS_LIST):
    with emoji_cols[i]:
        if st.button(emoji, key=f"emoji_btn_{emoji}"):
            st.session_state.current_chat_message += emoji
            # Презареждаме приложението, за да се актуализира текстовото поле веднага
            st.experimental_rerun()

# --- Текстово поле за въвеждане на съобщението ---
user_message = st.text_input(
    "Вашето съобщение:",
    value=st.session_state.current_chat_message,
    key="text_input_key_for_callback", # Уникален ключ за текстовото поле
    on_change=update_message_from_input # Извиква се, когато текстовото поле се промени
)

# --- Бутон за изпращане на съобщението ---
if st.button("Изпрати"):
    if st.session_state.current_chat_message:
        # Добавяме съобщението към историята
        st.session_state.messages.append({"role": "user", "content": st.session_state.current_chat_message})
        # Тук трябва да извикаш твоя модел или логика за обработка на съобщението
        # Например: response = твоя_функция_за_модел(st.session_state.current_chat_message)
        # st.session_state.messages.append({"role": "assistant", "content": response})

        # Изчистваме полето за въвеждане след изпращане
        st.session_state.current_chat_message = ""
        st.experimental_rerun() # Презареждаме, за да изчистим полето и да покажем новите съобщения
