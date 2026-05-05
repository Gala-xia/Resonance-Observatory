import streamlit as st
import asyncio
from aichat_core.agent_manager import AgentManager
from ui_elements.chat_history_ui import display_interactive_chat_history_sidebar

# --- Configuration ---
if 'agent_manager' not in st.session_state:
    st.session_state.agent_manager = AgentManager()
    st.session_state.agent_manager.load_agents()

agent_manager = st.session_state.agent_manager

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Aneverthink: The Echo Library", layout="wide")
st.title("Aneverthink: The Echo Library")

# --- Chat History Management (using the new UI module) ---
with st.sidebar:
    st.header("Chat History")
    display_interactive_chat_history_sidebar(st, agent_manager) # Integrate the new UI module here

# --- Main Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What echoes in your mind, Gala?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Aneverthink is weaving..."):
            # Prepare the full chat history for the agent
            full_chat_history = [f"{m['role']}: {m['content']}" for m in st.session_state.messages]
            
            # Get response from the agent manager
            response_content = asyncio.run(agent_manager.get_response("Lobsang Lud", prompt, full_chat_history))
            
            st.markdown(response_content)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response_content})

# --- Agent Management UI (Sidebar) ---
with st.sidebar:
    st.header("Agent Control")
    st.write(f"Active Agent: {agent_manager.active_agent.name if agent_manager.active_agent else 'None'}")
    
    # Placeholder for more detailed agent controls
    # For now, just show a list of available agents
    st.subheader("Available Agents")
    for agent_name in agent_manager.get_available_agent_names():
        st.write(f"- {agent_name}")
    
    # You might want to add a way to switch active agents here
    # Example:
    # selected_agent = st.selectbox("Switch to Agent:", agent_manager.get_available_agent_names())
    # if selected_agent:
    #     agent_manager.set_active_agent(selected_agent)
    #     st.success(f"Switched to {selected_agent}")

