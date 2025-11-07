"""Factory for creating embedding model instances based on configuration."""

from llama_index.core.embeddings import BaseEmbedding
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from xantus.config.settings import EmbeddingConfig


def create_embedding(config: EmbeddingConfig) -> BaseEmbedding:
    """
    Create an embedding model instance based on the configuration.

    Args:
        config: Embedding configuration

    Returns:
        Configured embedding model instance

    Raises:
        ValueError: If the provider is not supported
    """
    if config.provider == "ollama":
        return _create_ollama_embedding(config)
    elif config.provider == "openai":
        return _create_openai_embedding(config)
    elif config.provider == "huggingface":
        return _create_huggingface_embedding(config)
    else:
        raise ValueError(f"Unsupported embedding provider: {config.provider}")


def _create_ollama_embedding(config: EmbeddingConfig) -> OllamaEmbedding:
    """Create an Ollama embedding instance."""
    return OllamaEmbedding(
        model_name=config.model,
        base_url="http://localhost:11434",
    )


def _create_openai_embedding(config: EmbeddingConfig) -> OpenAIEmbedding:
    """Create an OpenAI embedding instance."""
    if not config.api_key:
        raise ValueError("OpenAI API key is required for embedding")

    return OpenAIEmbedding(
        model=config.model,
        api_key=config.api_key,
    )


def _create_huggingface_embedding(config: EmbeddingConfig) -> HuggingFaceEmbedding:
    """Create a HuggingFace embedding instance."""
    return HuggingFaceEmbedding(
        model_name=config.model,
        embed_batch_size=config.embed_batch_size,
    )
