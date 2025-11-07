"""Dependency injection container for Xantus."""

from injector import Injector, Module, provider, singleton
from llama_index.core import Settings as LlamaSettings
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import LLM
from llama_index.core.vector_stores.types import VectorStore

from xantus.config.settings import Settings, get_settings


class ComponentModule(Module):
    """Module for component dependencies."""

    def __init__(self, settings: Settings):
        self.settings = settings

    @provider
    @singleton
    def provide_settings(self) -> Settings:
        """Provide application settings."""
        return self.settings

    @provider
    @singleton
    def provide_llm(self) -> LLM:
        """Provide LLM instance based on configuration."""
        from xantus.components.llm.llm_factory import create_llm

        llm = create_llm(self.settings.llm)

        # Set as default LLM in LlamaIndex
        LlamaSettings.llm = llm

        return llm

    @provider
    @singleton
    def provide_embedding(self) -> BaseEmbedding:
        """Provide embedding model instance based on configuration."""
        from xantus.components.embeddings.embedding_factory import create_embedding

        embedding = create_embedding(self.settings.embedding)

        # Set as default embedding in LlamaIndex
        LlamaSettings.embed_model = embedding

        return embedding

    @provider
    @singleton
    def provide_vector_store(self) -> VectorStore:
        """Provide vector store instance based on configuration."""
        from xantus.components.vector_store.vector_store_factory import create_vector_store

        return create_vector_store(self.settings.vector_store)


def create_injector(settings: Settings | None = None) -> Injector:
    """Create and configure the dependency injection container."""
    if settings is None:
        settings = get_settings()

    # Create the injector with the component module
    injector = Injector([ComponentModule(settings)])

    return injector
