"""Streamlit UI for Xantus - Chat with your documents."""

import json
import requests
import streamlit as st
from typing import List, Dict

# Configuration
API_BASE_URL = "http://localhost:8000"


def init_session_state():
    """Initialize Streamlit session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "use_context" not in st.session_state:
        st.session_state.use_context = True
    if "show_sources" not in st.session_state:
        st.session_state.show_sources = False
    if "documents" not in st.session_state:
        st.session_state.documents = []
    if "message_sources" not in st.session_state:
        st.session_state.message_sources = {}


def upload_document(file) -> Dict:
    """
    Upload a document to the API.

    Args:
        file: File uploaded via Streamlit

    Returns:
        Response from the API
    """
    files = {"file": (file.name, file, file.type)}
    response = requests.post(f"{API_BASE_URL}/v1/ingest/file", files=files)
    response.raise_for_status()
    return response.json()


def list_documents() -> List[Dict]:
    """
    List all ingested documents.

    Returns:
        List of document metadata
    """
    response = requests.get(f"{API_BASE_URL}/v1/documents")
    response.raise_for_status()
    return response.json()["documents"]


def delete_document(document_id: str) -> Dict:
    """
    Delete a document.

    Args:
        document_id: ID of the document to delete

    Returns:
        Response from the API
    """
    response = requests.delete(f"{API_BASE_URL}/v1/documents/{document_id}")
    response.raise_for_status()
    return response.json()


def send_chat_message(messages: List[Dict], use_context: bool = True, include_sources: bool = False) -> tuple[str, List[Dict]]:
    """
    Send a chat message to the API.

    Args:
        messages: List of chat messages
        use_context: Whether to use RAG context
        include_sources: Whether to include source citations

    Returns:
        Tuple of (assistant's response, list of sources)
    """
    payload = {
        "messages": messages,
        "use_context": use_context,
        "include_sources": include_sources,
        "stream": False,
    }
    response = requests.post(
        f"{API_BASE_URL}/v1/chat/completions",
        json=payload,
    )
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    sources = data.get("sources", [])
    return content, sources


def check_api_health() -> bool:
    """
    Check if the API is healthy.

    Returns:
        True if API is healthy, False otherwise
    """
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Xantus - Private RAG Chat",
        page_icon="🔒",
        layout="wide",
    )

    init_session_state()

    # Header
    st.title("🔒 Xantus - Private Document Chat")
    st.markdown("Chat with your documents using AI, completely private and local.")

    # Check API health
    if not check_api_health():
        st.error(
            "⚠️ Cannot connect to Xantus API. "
            "Make sure the server is running on http://localhost:8000"
        )
        st.info("Start the server with: `python -m xantus.main`")
        return

    # Sidebar for document management
    with st.sidebar:
        st.header("📄 Document Management")

        # Upload section
        st.subheader("Upload Documents")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "txt", "docx", "md"],
            help="Upload documents to chat with them",
        )

        if uploaded_file is not None:
            if st.button("Upload Document", type="primary"):
                with st.spinner("Uploading and processing document..."):
                    try:
                        result = upload_document(uploaded_file)
                        st.success(
                            f"✅ Successfully ingested {result['file_name']} "
                            f"({result['num_chunks']} chunks)"
                        )
                        # Refresh documents list
                        st.session_state.documents = list_documents()
                    except Exception as e:
                        st.error(f"Error uploading document: {str(e)}")

        # List documents
        st.subheader("Ingested Documents")
        if st.button("Refresh Documents"):
            try:
                st.session_state.documents = list_documents()
            except Exception as e:
                st.error(f"Error fetching documents: {str(e)}")

        if st.session_state.documents:
            for doc in st.session_state.documents:
                with st.expander(f"📄 {doc['file_name']}"):
                    st.text(f"ID: {doc['document_id']}")
                    st.text(f"Chunks: {doc['num_chunks']}")
                    st.text(f"Ingested: {doc['ingested_at'][:19]}")

                    if st.button(f"Delete", key=f"delete_{doc['document_id']}"):
                        try:
                            delete_document(doc['document_id'])
                            st.success("Document deleted!")
                            st.session_state.documents = list_documents()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting document: {str(e)}")
        else:
            st.info("No documents ingested yet. Upload some documents to get started!")

        # Settings
        st.divider()
        st.subheader("⚙️ Settings")
        st.session_state.use_context = st.checkbox(
            "Use RAG Context",
            value=st.session_state.use_context,
            help="Enable to retrieve relevant context from documents",
        )

        st.session_state.show_sources = st.checkbox(
            "Show Sources",
            value=st.session_state.show_sources,
            help="Display source citations with page numbers and excerpts",
        )

        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.session_state.message_sources = {}
            st.rerun()

    # Main chat interface
    st.header("💬 Chat")

    # Display chat messages
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Display sources if this is an assistant message and sources exist
            if message["role"] == "assistant" and idx in st.session_state.message_sources:
                sources = st.session_state.message_sources[idx]
                if sources:
                    st.divider()
                    st.caption(f"📚 {len(sources)} source(s) referenced:")

                    for source_idx, source in enumerate(sources, 1):
                        page_info = f", Page {source['page_label']}" if source.get('page_label') else ""
                        chunk_info = f" (Chunk {source['chunk_index']})"
                        score_info = f" - Relevance: {source['score']:.2%}"

                        with st.expander(f"📄 {source['file_name']}{page_info}{chunk_info}{score_info}"):
                            st.markdown(source['text'])

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response, sources = send_chat_message(
                        st.session_state.messages,
                        use_context=st.session_state.use_context,
                        include_sources=st.session_state.show_sources,
                    )
                    st.markdown(response)

                    # Add assistant response to history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )

                    # Store sources for this message (index is the current message count)
                    message_idx = len(st.session_state.messages) - 1
                    if sources and st.session_state.show_sources:
                        st.session_state.message_sources[message_idx] = sources

                        # Display sources immediately
                        st.divider()
                        st.caption(f"📚 {len(sources)} source(s) referenced:")

                        for source_idx, source in enumerate(sources, 1):
                            page_info = f", Page {source['page_label']}" if source.get('page_label') else ""
                            chunk_info = f" (Chunk {source['chunk_index']})"
                            score_info = f" - Relevance: {source['score']:.2%}"

                            with st.expander(f"📄 {source['file_name']}{page_info}{chunk_info}{score_info}"):
                                st.markdown(source['text'])

                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )

    # Info section
    if not st.session_state.messages:
        st.info(
            "👋 Welcome! Upload documents using the sidebar, then ask questions about them. "
            "All processing happens locally - your data never leaves your system."
        )

        # Example questions
        st.markdown("### Example Questions")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("- What are the main topics in these documents?")
            st.markdown("- Summarize the key points")
        with col2:
            st.markdown("- What does the document say about [topic]?")
            st.markdown("- Compare the different approaches mentioned")


if __name__ == "__main__":
    main()
