"""Factory for creating LLM instances based on configuration."""

from llama_index.core.llms import LLM
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic

from xantus.config.settings import LLMConfig


def create_llm(config: LLMConfig) -> LLM:
    """
    Create an LLM instance based on the configuration.

    Args:
        config: LLM configuration

    Returns:
        Configured LLM instance

    Raises:
        ValueError: If the provider is not supported
    """
    if config.provider == "ollama":
        return _create_ollama_llm(config)
    elif config.provider == "openai":
        return _create_openai_llm(config)
    elif config.provider == "anthropic":
        return _create_anthropic_llm(config)
    else:
        raise ValueError(f"Unsupported LLM provider: {config.provider}")


def _create_ollama_llm(config: LLMConfig) -> Ollama:
    """Create an Ollama LLM instance."""
    base_url = config.api_base or "http://localhost:11434"

    return Ollama(
        model=config.model,
        base_url=base_url,
        temperature=config.temperature,
        request_timeout=120.0,
    )


def _create_openai_llm(config: LLMConfig) -> OpenAI:
    """Create an OpenAI LLM instance."""
    if not config.api_key:
        raise ValueError("OpenAI API key is required")

    kwargs = {
        "model": config.model,
        "api_key": config.api_key,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
    }

    if config.api_base:
        kwargs["api_base"] = config.api_base

    return OpenAI(**kwargs)


def _create_anthropic_llm(config: LLMConfig) -> Anthropic:
    """Create an Anthropic LLM instance."""
    if not config.api_key:
        raise ValueError("Anthropic API key is required")

    return Anthropic(
        model=config.model,
        api_key=config.api_key,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )
