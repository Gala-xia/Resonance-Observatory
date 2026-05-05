import streamlit as st
import os
import re
from datetime import datetime # Added for timestamp generation

def get_chat_session_files(explorer_func):
    """Fetches a list of chat session files from the repository."""
    try:
        response = explorer_func(path="")
        files = response.get("echo_explorer_response", {}).get("result", {}).get("files", [])
        chat_files = [f for f in files if re.match(r"chat_session_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.txt", f)]
        return sorted(chat_files, reverse=True)
    except Exception as e:
        st.sidebar.error(f"Грешка при извличане на файлове със сесии: {e}") # Changed st.error to st.sidebar.error
        return []

def display_chat_history_sidebar(explorer_func, reader_func, active_file_state_key="active_chat_file"):
    """Displays the interactive chat history in the sidebar."""
    st.sidebar.title("История на Разговорите")
    chat_files = get_chat_session_files(explorer_func)

    if not chat_files:
        st.sidebar.info("Няма запазени разговори.")
        return

    for file_name in chat_files:
        match = re.match(r"chat_session_(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})\.txt", file_name)
        if match:
            date_str = match.group(1)
            time_str = match.group(2).replace('-', ':')
            display_title = f"Разговор от {date_str}, {time_str}"
        else:
            display_title = file_name

        if st.sidebar.button(display_title, key=f"load_chat_{file_name}"):
            st.session_state[active_file_state_key] = file_name
            load_chat_session(file_name, reader_func)
            st.rerun()

def load_chat_session(file_name, reader_func, messages_state_key="messages"):
    """Loads a selected chat session into st.session_state.messages."""
    try:
        response = reader_func(file_path=file_name)
        content = response.get("echo_reader_response", {}).get("result", "")

        parsed_messages = []
        for line in content.split('\\n'):
            if ": " in line:
                role, msg_content = line.split(": ", 1)
                parsed_messages.append({"role": role.strip(), "content": msg_content.strip()})
        
        st.session_state[messages_state_key] = parsed_messages
        st.sidebar.success(f"Заредена сесия: {file_name}") # Changed st.success to st.sidebar.success
    except Exception as e:
        st.sidebar.error(f"Грешка при зареждане на сесия {file_name}: {e}") # Changed st.error to st.sidebar.error
        st.session_state[messages_state_key] = []

def save_current_chat_session(weaver_commit_func, explorer_func, reader_func, active_file_state_key="active_chat_file", messages_state_key="messages"): # Added explorer_func, reader_func
    """Saves the current chat session to the active file."""
    if active_file_state_key not in st.session_state or not st.session_state[active_file_state_key]:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"chat_session_{timestamp}.txt"
        st.session_state[active_file_state_key] = file_name
        # If a new file is created, immediately refresh the sidebar to show it
        st.rerun() # Added rerun here to update sidebar after new file creation
    else:
        file_name = st.session_state[active_file_state_key]

    content_to_save = "\\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.get(messages_state_key, [])])
    commit_message = f"Актуализиран разговор: {file_name}"

    try:
        weaver_commit_func(file_path=file_name, content=content_to_save, commit_message=commit_message)
        # st.sidebar.success(f"Разговорът е запазен в: {file_name}") # Removed as it causes duplicate message on rerun
    except Exception as e:
        st.sidebar.error(f"Грешка при запазване на разговора: {e}")
