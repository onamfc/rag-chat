"""Service for chat completions with optional RAG context."""

import logging
import time
import uuid
from typing import AsyncIterator

from injector import inject
from llama_index.core import (
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.base.llms.types import ChatMessage as LlamaMessage, MessageRole
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import LLM
from llama_index.core.vector_stores.types import VectorStore

from xantus.config.settings import Settings
from xantus.models.schemas import (
    ChatChoice,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    ChatStreamChunk,
    ChatUsage,
    ChunkRetrievalRequest,
    ChunkRetrievalResponse,
    RetrievedChunk,
    ChunkMetadata,
)

logger = logging.getLogger(__name__)


class ChatService:
    """Service for chat completion operations with RAG support."""

    @inject
    def __init__(
        self,
        settings: Settings,
        llm: LLM,
        embedding: BaseEmbedding,
        vector_store: VectorStore,
    ):
        """
        Initialize the chat service.

        Args:
            settings: Application settings
            llm: Language model instance
            embedding: Embedding model
            vector_store: Vector store instance
        """
        self.settings = settings
        self.llm = llm
        self.embedding = embedding
        self.vector_store = vector_store

        # Create storage context and index for RAG
        self.storage_context = StorageContext.from_defaults(
            vector_store=vector_store
        )
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=embedding,
        )

    async def chat_completion(
        self,
        request: ChatCompletionRequest,
    ) -> ChatCompletionResponse | AsyncIterator[ChatStreamChunk]:
        """
        Generate a chat completion with optional RAG context.

        Args:
            request: Chat completion request

        Returns:
            Chat completion response or stream of chunks
        """
        logger.info(f"Processing chat request with {len(request.messages)} messages")

        # Convert messages to LlamaIndex format
        messages = [
            LlamaMessage(
                role=MessageRole(msg.role),
                content=msg.content,
            )
            for msg in request.messages
        ]

        # Store retrieved nodes for source citations
        retrieved_nodes = []

        # Retrieve context if enabled
        if request.use_context:
            # Get the last user message as the query
            user_messages = [msg for msg in request.messages if msg.role == "user"]
            if user_messages:
                query = user_messages[-1].content
                context, retrieved_nodes = await self._retrieve_context(query)

                if context:
                    # Add context to the messages as a system message
                    context_message = LlamaMessage(
                        role=MessageRole.SYSTEM,
                        content=f"Use the following context to answer the user's question:\n\n{context}",
                    )
                    messages.insert(0, context_message)
                    logger.info("Added RAG context to messages")

        # Generate completion
        if request.stream:
            return self._stream_completion(request, messages)
        else:
            return await self._generate_completion(request, messages, retrieved_nodes)

    async def _retrieve_context(self, query: str) -> tuple[str, list]:
        """
        Retrieve relevant context from the vector store.

        Args:
            query: Query text

        Returns:
            Tuple of (concatenated context string, list of retrieved nodes)
        """
        logger.info(f"Retrieving context for query: {query[:100]}...")

        # Create retriever
        retriever = self.index.as_retriever(
            similarity_top_k=self.settings.rag.similarity_top_k
        )

        # Retrieve nodes
        nodes = await retriever.aretrieve(query)

        if not nodes:
            logger.info("No relevant context found")
            return "", []

        # Concatenate text from nodes
        context_parts = []
        for node in nodes:
            context_parts.append(f"[Source: {node.metadata.get('file_name', 'unknown')}]\n{node.text}")

        context = "\n\n".join(context_parts)
        logger.info(f"Retrieved {len(nodes)} chunks for context")

        return context, nodes

    async def _generate_completion(
        self,
        request: ChatCompletionRequest,
        messages: list[LlamaMessage],
        retrieved_nodes: list = None,
    ) -> ChatCompletionResponse:
        """Generate a non-streaming completion."""
        completion_id = f"chat-{uuid.uuid4()}"
        created_timestamp = int(time.time())

        # Override temperature and max_tokens if provided
        kwargs = {}
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens

        # Generate response
        response = await self.llm.achat(messages, **kwargs)

        # Create response object
        choice = ChatChoice(
            index=0,
            message=ChatMessage(
                role="assistant",
                content=response.message.content,
            ),
            finish_reason="stop",
        )

        # Build source citations if requested
        sources = None
        if request.include_sources and retrieved_nodes:
            from xantus.models.schemas import SourceCitation

            sources = []
            for node in retrieved_nodes:
                source = SourceCitation(
                    file_name=node.metadata.get("file_name", "unknown"),
                    page_label=node.metadata.get("page_label"),
                    chunk_index=node.metadata.get("chunk_index", 0),
                    score=node.score or 0.0,
                    text=node.text,
                )
                sources.append(source)

            logger.info(f"Added {len(sources)} source citations to response")

        return ChatCompletionResponse(
            id=completion_id,
            created=created_timestamp,
            model=self.settings.llm.model,
            choices=[choice],
            usage=ChatUsage(
                prompt_tokens=0,  # LlamaIndex doesn't provide this easily
                completion_tokens=0,
                total_tokens=0,
            ),
            sources=sources,
        )

    async def _stream_completion(
        self,
        request: ChatCompletionRequest,
        messages: list[LlamaMessage],
    ) -> AsyncIterator[ChatStreamChunk]:
        """Generate a streaming completion."""
        completion_id = f"chat-{uuid.uuid4()}"
        created_timestamp = int(time.time())

        # Override temperature and max_tokens if provided
        kwargs = {}
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens

        # Stream response
        response_stream = await self.llm.astream_chat(messages, **kwargs)

        async for chunk in response_stream:
            yield ChatStreamChunk(
                id=completion_id,
                created=created_timestamp,
                model=self.settings.llm.model,
                choices=[
                    {
                        "index": 0,
                        "delta": {"content": chunk.delta},
                        "finish_reason": None,
                    }
                ],
            )

        # Send final chunk
        yield ChatStreamChunk(
            id=completion_id,
            created=created_timestamp,
            model=self.settings.llm.model,
            choices=[
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop",
                }
            ],
        )

    async def retrieve_chunks(
        self,
        request: ChunkRetrievalRequest,
    ) -> ChunkRetrievalResponse:
        """
        Retrieve similar chunks for a query.

        Args:
            request: Chunk retrieval request

        Returns:
            Retrieved chunks with metadata
        """
        logger.info(f"Retrieving chunks for query: {request.query[:100]}...")

        top_k = request.top_k or self.settings.rag.similarity_top_k

        # Create retriever
        retriever = self.index.as_retriever(similarity_top_k=top_k)

        # Retrieve nodes
        nodes = await retriever.aretrieve(request.query)

        # Convert to response format
        chunks = []
        for node in nodes:
            chunk = RetrievedChunk(
                text=node.text,
                metadata=ChunkMetadata(
                    document_id=node.metadata.get("document_id", "unknown"),
                    file_name=node.metadata.get("file_name", "unknown"),
                    chunk_index=node.metadata.get("chunk_index", 0),
                    score=node.score or 0.0,
                ),
            )
            chunks.append(chunk)

        logger.info(f"Retrieved {len(chunks)} chunks")

        return ChunkRetrievalResponse(
            chunks=chunks,
            query=request.query,
        )
