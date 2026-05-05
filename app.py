import streamlit as st
from aichat_core.agent_manager import AgentManager
from aichat_core.chat_history import ChatHistory
from ui_elements.chat_history_ui import display_interactive_chat_history # Import the new UI module

# Initialize session state for chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history_data" not in st.session_state:
    st.session_state.chat_history_data = []
if "active_chat_file" not in st.session_state:
    st.session_state.active_chat_file = None # To store the currently active chat file

st.title("Aneverthink - Digital Philosopher")

# Display interactive chat history in sidebar using the new module
display_interactive_chat_history()

# Main chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is on your mind today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Initialize AgentManager for handling agent responses
    agent_manager = AgentManager()
    
    # Get response from the agent
    full_response = ""
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        for response_chunk in agent_manager.get_agent_response(prompt, st.session_state.messages):
            full_response += response_chunk
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Update the chat_history_data for the current session (if not using file-based directly)
    # This part will be mostly handled by the display_interactive_chat_history in the future
    st.session_state.chat_history_data.append(ChatHistory(role="user", content=prompt))
    st.session_state.chat_history_data.append(ChatHistory(role="assistant", content=full_response))

    # If an active chat file is set, save the current session state to it
    # The actual saving logic will be more robust within chat_history_ui
    # For now, this is a placeholder to show the intent
    if st.session_state.active_chat_file:
        # This part will be handled by the chat_history_ui module
        # For demonstration, let's just show the concept
        pass
