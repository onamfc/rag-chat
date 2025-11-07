"""Factory for creating vector store instances based on configuration."""

from pathlib import Path
from llama_index.core.vector_stores.types import VectorStore
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

from xantus.config.settings import VectorStoreConfig


def create_vector_store(config: VectorStoreConfig) -> VectorStore:
    """
    Create a vector store instance based on the configuration.

    Args:
        config: Vector store configuration

    Returns:
        Configured vector store instance

    Raises:
        ValueError: If the provider is not supported
    """
    if config.provider == "chroma":
        return _create_chroma_vector_store(config)
    elif config.provider == "qdrant":
        return _create_qdrant_vector_store(config)
    else:
        raise ValueError(f"Unsupported vector store provider: {config.provider}")


def _create_chroma_vector_store(config: VectorStoreConfig) -> ChromaVectorStore:
    """Create a ChromaDB vector store instance."""
    # Ensure persist directory exists
    persist_path = Path(config.persist_path)
    persist_path.mkdir(parents=True, exist_ok=True)

    # Create ChromaDB client with persistence
    chroma_client = chromadb.PersistentClient(
        path=str(persist_path)
    )

    # Get or create collection
    collection = chroma_client.get_or_create_collection(
        name=config.collection_name
    )

    # Create and return the vector store
    return ChromaVectorStore(
        chroma_collection=collection
    )


def _create_qdrant_vector_store(config: VectorStoreConfig) -> "QdrantVectorStore":
    """Create a Qdrant vector store instance."""
    try:
        from llama_index.vector_stores.qdrant import QdrantVectorStore
        from qdrant_client import QdrantClient
    except ImportError:
        raise ImportError(
            "Qdrant packages are not installed. "
            "Uncomment the qdrant lines in requirements.txt and run: "
            "pip install llama-index-vector-stores-qdrant qdrant-client"
        )

    # Ensure persist directory exists
    persist_path = Path(config.persist_path)
    persist_path.mkdir(parents=True, exist_ok=True)

    # Create Qdrant client with persistence
    client = QdrantClient(
        path=str(persist_path)
    )

    # Create and return the vector store
    return QdrantVectorStore(
        client=client,
        collection_name=config.collection_name,
    )
