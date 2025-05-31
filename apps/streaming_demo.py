import asyncio
import streamlit as st
from openai.types.responses import ResponseTextDeltaEvent
import sys
import os
from dotenv import load_dotenv
load_dotenv()


api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables")
# Add the parent directory to the path so we can import the agents module

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import Agent, Runner

st.set_page_config(
    page_title="OpenAI Agents Streaming Demo",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 OpenAI Agents Streaming Demo")
st.write("See the streaming capabilities of OpenAI Agents with visual effects.")

with st.sidebar:
    st.header("Configuration")
    agent_name = st.text_input("Agent Name", "StreamBot")
    agent_instructions = st.text_area(
        "Agent Instructions", 
        "You are a helpful assistant. Your responses should be creative and engaging."
    )
    
    model_options = [
        "gpt-4o",
        "gpt-4o-mini",
        "o3-mini"
    ]
    selected_model = st.selectbox("Model", model_options, index=1)
    
    demo_options = [
        "Tell me 5 jokes",
        "Write a short story about a robot",
        "Explain how AI works to a 5-year-old",
        "Create a short poem about technology",
        "Give me 3 interesting facts about space"
    ]
    demo_prompt = st.selectbox("Quick Prompts", demo_options)
    
    st.markdown("---")
    st.markdown("Made with ❤️ using OpenAI Agents")

# User input area
user_input = st.text_area("Your message:", value=demo_prompt, height=100)
send_button = st.button("Send", type="primary")

# Response area with custom styling
response_container = st.container()

async def stream_response(agent: Agent, user_input: str) -> None:
    """Stream agent response and update the UI."""
    response_parts = ""
    try:
        result = Runner.run_streamed(agent, input=user_input)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                print(event.data.delta)
                response_parts += event.data.delta
                # Update the UI with a trailing cursor symbol for a live effect
                message_placeholder.markdown(response_parts + "▌")
        message_placeholder.markdown(response_parts)
    except Exception as e:
        st.error(f"An error occurred: {e}")

if send_button and user_input:
    agent = Agent(
        name=agent_name,
        instructions=agent_instructions,
        model=selected_model,
    )
    
    with response_container:
        message_placeholder = st.empty()
        
        with st.spinner("Thinking..."):
            asyncio.run(stream_response(agent, user_input))
        
        # Add clear button
        if st.button("Clear"):
            st.experimental_rerun()

# Instructions
if not send_button:
    with response_container:
        st.info("👆 Enter your message above and click 'Send' to see the streaming response.")
        st.markdown("""
        ### Tips:
        - Choose from the quick prompts or enter your own
        - Try complex prompts to see how the agent responds in real-time
        """)
