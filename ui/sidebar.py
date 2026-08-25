import streamlit as st
from api_client import DocQAAPIClient

def render_sidebar(client: DocQAAPIClient) -> None:
    """
    Renders sidebar configurations and components.
    """
    with st.sidebar:
        st.header("Configuration")
        
        status = client.get_status()
        
        st.subheader("Active Document")
        if status and status.get("status") == "ready":
            st.success(f"**{status.get('filename')}**")
            st.info(f"Chunks indexed: {status.get('chunks_indexed')}")
        else:
            st.warning("No document is currently indexed.")
            st.info("Upload a PDF file below to start.")
            
        st.subheader("Upload Document")
        uploaded_file = st.file_uploader(
            "Select a PDF file",
            type=["pdf"],
            help="Upload a new PDF to replace the current index."
        )
        
        if uploaded_file is not None:
            # Check if this file was already uploaded in session state
            if st.session_state.get("last_uploaded_filename") != uploaded_file.name:
                with st.spinner("Extracting text and building vector index..."):
                    success, message = client.upload_file(uploaded_file.name, uploaded_file.getvalue())
                    if success:
                        st.session_state["last_uploaded_filename"] = uploaded_file.name
                        st.success(message)
                        st.session_state["messages"] = []
                        st.rerun()
                    else:
                        st.error(message)

        st.markdown("---")
        
        if st.button("Clear Chat", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()
