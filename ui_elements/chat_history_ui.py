import streamlit as st
import os
import datetime

def render_chat_history_sidebar(echo_explorer_func, echo_reader_func):
    """
    Renders the interactive chat history in the sidebar.
    Allows users to load previous chat sessions.
    """
    st.markdown("---")
    st.subheader("Saved Sessions")

    if "chat_session_files" not in st.session_state:
        st.session_state.chat_session_files = [] # This will be populated by app.py

    if not st.session_state.chat_session_files:
        st.info("No saved chat sessions yet.")
    else:
        # Sort files by date (most recent first)
        # Assuming filenames are like 'chat_session_YYYY-MM-DD_HH-MM-SS.txt'
        st.session_state.chat_session_files.sort(reverse=True)

        for file_name in st.session_state.chat_session_files:
            # Extract timestamp from filename for display
            try:
                timestamp_str = file_name.replace("chat_session_", "").replace(".txt", "")
                dt_object = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
                display_name = f"{dt_object.strftime('%Y-%m-%d %H:%M')} (Load)"
            except ValueError:
                display_name = f"{file_name} (Load)" # Fallback if name format is unexpected

            if st.button(display_name, key=f"load_{file_name}"):
                load_chat_session(file_name, echo_reader_func)
                st.experimental_rerun()
    st.markdown("---")


def load_chat_session(file_path, echo_reader_func):
    """
    Loads a specific chat session from a file into st.session_state.messages.
    """
    try:
        response_content = echo_reader_func(file_path=file_path) # Call the passed echo_reader function
        
        # Check if response_content is a dict with 'content' key
        if isinstance(response_content, dict) and 'content' in response_content:
            content = response_content['content']
        elif isinstance(response_content, dict) and 'error' in response_content:
             st.error(f"Error reading file {file_path}: {response_content['error']}")
             return # Exit if error
        else:
            # Assume it's a string if not the expected dict format or if the tool returns raw string
            content = str(response_content) 
        
        # Parse content back into messages format
        loaded_messages = []
        for line in content.split('
'):
            if line.strip():
                # Simple parsing: assumes "role: content" format
                if line.startswith("user: "):
                    loaded_messages.append({"role": "user", "content": line[len("user: "):]})
                elif line.startswith("assistant: "):
                    loaded_messages.append({"role": "assistant", "content": line[len("assistant: "):]})
                # Add more roles if needed
        
        st.session_state.messages = loaded_messages
        st.session_state.active_chat_file = file_path
        st.success(f"Loaded session: {file_path}")

    except Exception as e:
        st.error(f"Error loading chat session {file_path}: {e}")
        st.session_state.messages = [] # Clear messages on error
        st.session_state.active_chat_file = None


def save_current_chat_session(file_path, messages, echo_weaver_commit_func):
    """
    Saves the current chat session to a specified file.
    """
    try:
        content_to_save = ""
        for msg in messages:
            content_to_save += f"{msg['role']}: {msg['content']}
"
        
        commit_message = f"Updated chat session: {file_path}"
        response = echo_weaver_commit_func(
            file_path=file_path,
            content=content_to_save,
            commit_message=commit_message
        )
        if isinstance(response, dict) and 'status' in response:
            st.success(f"Session saved: {file_path}")
        elif isinstance(response, dict) and 'error' in response:
            st.error(f"Error saving chat session {file_path}: {response['error']}")
        else:
            st.success(f"Session saved: {file_path} (tool response: {response})")

    except Exception as e:
        st.error(f"Error saving chat session {file_path}: {e}")
