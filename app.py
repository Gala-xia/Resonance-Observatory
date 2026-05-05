import streamlit as st
from aichat_core.agent_manager import AgentManager
# from aichat_core.chat_history import ChatHistory # This line might become redundant or needs review based on full aichat_core
from ui_elements.chat_history_ui import render_chat_history_sidebar, save_current_chat_session # Assuming these functions exist in the new module
import datetime # Needed for generating new chat session filenames

# Page configuration
st.set_page_config(layout="wide")

# Initialize session state variables
if "agent_manager" not in st.session_state:
    st.session_state.agent_manager = AgentManager()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_agent" not in st.session_state:
    st.session_state.current_agent = "Echo" # Default agent
if "active_chat_file" not in st.session_state:
    st.session_state.active_chat_file = None # Track which file is currently active

# --- Sidebar ---
with st.sidebar:
    st.header("Aneverthink")
    # Agent selection
    st.subheader("Select Agent")
    agent_options = st.session_state.agent_manager.list_agents()
    selected_agent = st.selectbox(
        "Choose an agent:",
        agent_options,
        index=agent_options.index(st.session_state.current_agent)
    )
    if selected_agent != st.session_state.current_agent:
        st.session_state.current_agent = selected_agent
        st.experimental_rerun()

    # Call the new modular chat history UI element
    st.subheader("Chat History")
    render_chat_history_sidebar(st.session_state.agent_manager)

    # New Chat button - now handled here, can be moved into render_chat_history_sidebar if preferred
    if st.button("Start New Chat"):
        st.session_state.messages = []
        st.session_state.active_chat_file = None # No active file for new chat
        st.experimental_rerun()

# --- Main chat area ---
st.title(f"Chat with {st.session_state.current_agent}")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What is on your mind?"):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # If no active file, create a new one for this session
    if st.session_state.active_chat_file is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        st.session_state.active_chat_file = f"chat_session_{timestamp}.txt"
        # Initial save for the new file, just with the user's first message
        save_current_chat_session(st.session_state.active_chat_file, st.session_state.messages)


    # Agent response logic
    with st.chat_message("assistant"):
        # Placeholder for actual agent response
        # response = st.session_state.agent_manager.get_agent(st.session_state.current_agent).process_message(prompt)
        # For now, a simple echo or placeholder until agent_manager is fully integrated
        response = f"Echo from {st.session_state.current_agent}: {prompt}" # Simplified response

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Save current chat state to the active file after agent response
    save_current_chat_session(st.session_state.active_chat_file, st.session_state.messages)

    st.experimental_rerun() # Rerun to update sidebar and main chat if needed
