"""FastAPI router for chat completions."""

import logging
from typing import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from xantus.models.schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChunkRetrievalRequest,
    ChunkRetrievalResponse,
)
from xantus.services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["chat"])


def get_chat_service() -> ChatService:
    """Dependency to get chat service instance."""
    from xantus.main import get_injector
    return get_injector().get(ChatService)


@router.post("/chat/completions", response_model=None)
async def chat_completions(
    request: ChatCompletionRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Generate a chat completion with optional RAG context.

    This endpoint follows the OpenAI chat completions API format.
    """
    logger.info(f"Received chat completion request with {len(request.messages)} messages")

    result = await chat_service.chat_completion(request)

    # Handle streaming response
    if isinstance(result, AsyncIterator):

        async def stream_generator():
            """Generate SSE formatted stream."""
            async for chunk in result:
                yield f"data: {chunk.model_dump_json()}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
        )

    # Return normal response
    return result


@router.post("/chunks/retrieve")
async def retrieve_chunks(
    request: ChunkRetrievalRequest,
    chat_service: ChatService = Depends(get_chat_service),
) -> ChunkRetrievalResponse:
    """
    Retrieve similar chunks from the vector store.

    This is useful for debugging or building custom RAG flows.
    """
    logger.info(f"Retrieving chunks for query: {request.query[:100]}...")

    return await chat_service.retrieve_chunks(request)
