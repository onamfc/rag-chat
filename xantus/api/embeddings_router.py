"""FastAPI router for embeddings generation."""

import logging

from fastapi import APIRouter, Depends
from llama_index.core.embeddings import BaseEmbedding

from xantus.config.settings import Settings
from xantus.models.schemas import (
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingData,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["embeddings"])


def get_embedding_model() -> BaseEmbedding:
    """Dependency to get embedding model instance."""
    from xantus.main import get_injector
    return get_injector().get(BaseEmbedding)


def get_settings() -> Settings:
    """Dependency to get settings instance."""
    from xantus.main import get_injector
    return get_injector().get(Settings)


@router.post("/embeddings")
async def create_embeddings(
    request: EmbeddingRequest,
    embedding_model: BaseEmbedding = Depends(get_embedding_model),
    settings: Settings = Depends(get_settings),
) -> EmbeddingResponse:
    """
    Generate embeddings for text input.

    This endpoint follows the OpenAI embeddings API format.
    Accepts either a single string or list of strings.
    """
    logger.info(f"Generating embeddings for input")

    # Normalize input to list
    if isinstance(request.input, str):
        texts = [request.input]
    else:
        texts = request.input

    # Generate embeddings
    embeddings = []
    for idx, text in enumerate(texts):
        embedding_vector = await embedding_model.aget_text_embedding(text)
        embeddings.append(
            EmbeddingData(
                embedding=embedding_vector,
                index=idx,
            )
        )

    logger.info(f"Generated {len(embeddings)} embeddings")

    return EmbeddingResponse(
        data=embeddings,
        model=settings.embedding.model,
        usage={
            "prompt_tokens": sum(len(text.split()) for text in texts),
            "total_tokens": sum(len(text.split()) for text in texts),
        },
    )
