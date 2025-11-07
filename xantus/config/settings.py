"""Configuration settings for Xantus using Pydantic."""

from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
import yaml


class LLMConfig(BaseModel):
    """LLM configuration."""

    provider: Literal["ollama", "openai", "anthropic"] = Field(
        default="ollama",
        description="LLM provider to use"
    )
    model: str = Field(
        default="llama3.2",
        description="Model name to use"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature"
    )
    max_tokens: int = Field(
        default=2048,
        gt=0,
        description="Maximum tokens to generate"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for cloud providers"
    )
    api_base: Optional[str] = Field(
        default=None,
        description="Base URL for API (e.g., Ollama endpoint)"
    )


class EmbeddingConfig(BaseModel):
    """Embedding model configuration."""

    provider: Literal["ollama", "openai", "huggingface"] = Field(
        default="huggingface",
        description="Embedding provider to use"
    )
    model: str = Field(
        default="BAAI/bge-small-en-v1.5",
        description="Embedding model name"
    )
    embed_batch_size: int = Field(
        default=10,
        gt=0,
        description="Batch size for embedding generation"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key if using cloud embedding service"
    )


class VectorStoreConfig(BaseModel):
    """Vector store configuration."""

    provider: Literal["chroma", "qdrant"] = Field(
        default="chroma",
        description="Vector store provider"
    )
    persist_path: str = Field(
        default="./data/vector_store",
        description="Path to persist vector store data"
    )
    collection_name: str = Field(
        default="xantus_documents",
        description="Name of the vector store collection"
    )


class RAGConfig(BaseModel):
    """RAG (Retrieval Augmented Generation) configuration."""

    similarity_top_k: int = Field(
        default=5,
        gt=0,
        description="Number of similar chunks to retrieve"
    )
    chunk_size: int = Field(
        default=1024,
        gt=0,
        description="Size of text chunks for indexing"
    )
    chunk_overlap: int = Field(
        default=200,
        ge=0,
        description="Overlap between chunks"
    )
    enable_reranking: bool = Field(
        default=False,
        description="Enable reranking of retrieved chunks"
    )


class ServerConfig(BaseModel):
    """Server configuration."""

    host: str = Field(
        default="127.0.0.1",
        description="Host to bind the server to"
    )
    port: int = Field(
        default=8000,
        gt=0,
        le=65535,
        description="Port to bind the server to"
    )
    cors_enabled: bool = Field(
        default=True,
        description="Enable CORS"
    )
    cors_origins: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )


class MCPServerConfig(BaseModel):
    """MCP server configuration."""

    name: str = Field(
        description="Name of the MCP server"
    )
    command: str = Field(
        description="Command to start the server (e.g., 'node', 'npx')"
    )
    args: list[str] = Field(
        default=[],
        description="Arguments to pass to the command"
    )


class MCPConfig(BaseModel):
    """MCP (Model Context Protocol) configuration."""

    enabled: bool = Field(
        default=False,
        description="Enable MCP integration"
    )
    servers: list[MCPServerConfig] = Field(
        default=[],
        description="List of MCP servers to connect to"
    )


class Settings(BaseSettings):
    """Main application settings."""

    llm: LLMConfig = Field(default_factory=LLMConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    mcp: MCPConfig = Field(default_factory=MCPConfig)

    @classmethod
    def from_yaml(cls, config_path: str | Path) -> "Settings":
        """Load settings from YAML file with environment variable overrides."""
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}

        # Remove None values from nested dicts to allow env vars to take precedence
        def remove_none_values(d):
            if not isinstance(d, dict):
                return d
            return {k: remove_none_values(v) for k, v in d.items() if v is not None}

        config_data = remove_none_values(config_data)

        # Create settings instance which will automatically read from environment variables
        # Environment variables will override YAML values
        return cls(**config_data)

    class Config:
        """Pydantic config."""
        env_prefix = "XANTUS_"
        case_sensitive = False
        env_nested_delimiter = "__"  # Allow nested config like XANTUS_LLM__API_KEY


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings

    if _settings is None:
        # Try to load from config.yaml, otherwise use defaults
        config_path = Path("config.yaml")
        if config_path.exists():
            _settings = Settings.from_yaml(config_path)
        else:
            _settings = Settings()

    return _settings


def set_settings(settings: Settings) -> None:
    """Set the global settings instance."""
    global _settings
    _settings = settings
