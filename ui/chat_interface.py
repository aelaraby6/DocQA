import streamlit as st
from api_client import DocQAAPIClient

def render_chat(client: DocQAAPIClient):
    """
    Renders the main chat history and handles input/output dialogue.
    """
    st.subheader("Document Q&A")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if len(st.session_state["messages"]) == 0:
        st.chat_message("assistant").markdown(
            "Welcome! Upload a PDF document in the sidebar, then enter your question below. "
            "I will answer based strictly on the content of the document."
        )

    # Display existing chat messages
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User chat input field
    user_input = st.chat_input("Ask a question about the document...")

    if user_input:
        # Display user message
        st.chat_message("user").markdown(user_input)
        st.session_state["messages"].append({"role": "user", "content": user_input})
        
        # Display assistant message
        with st.chat_message("assistant"):
            with st.spinner("Searching document context and generating answer..."):
                success, response_text = client.ask_document(user_input)
                if success:
                    st.markdown(response_text)
                    st.session_state["messages"].append({"role": "assistant", "content": response_text})
                else:
                    st.error(response_text)
