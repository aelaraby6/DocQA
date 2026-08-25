import streamlit as st
from api_client import DocQAAPIClient
from sidebar import render_sidebar
from chat_interface import render_chat

st.set_page_config(
    page_title="DocQA Assistant",
    layout="wide",
)

client = DocQAAPIClient()
backend_status = client.get_status()

st.title("DocQA: Document Q&A Assistant")
st.markdown("---")

if backend_status is None:
    st.error(
        f"Could not connect to FastAPI backend at {client.base_url}\n\n"
        "Please ensure the FastAPI server is running. Start it by running:\n"
        "```bash\n"
        "uvicorn src.main:app --reload\n"
        "```"
    )
    st.stop()

# Render Sidebar 
render_sidebar(client)

# Render Chat Interface 
render_chat(client)
