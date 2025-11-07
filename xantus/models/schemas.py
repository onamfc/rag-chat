"""Data models and schemas for API requests and responses."""

from typing import Literal, Optional
from pydantic import BaseModel, Field


# ===== Chat Models =====

class ChatMessage(BaseModel):
    """A single chat message."""

    role: Literal["system", "user", "assistant"] = Field(
        description="The role of the message sender"
    )
    content: str = Field(
        description="The content of the message"
    )


class ChatCompletionRequest(BaseModel):
    """Request for chat completion."""

    messages: list[ChatMessage] = Field(
        description="List of chat messages"
    )
    use_context: bool = Field(
        default=True,
        description="Whether to use document context for RAG"
    )
    include_sources: bool = Field(
        default=False,
        description="Whether to include source citations in the response"
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (overrides config)"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        gt=0,
        description="Maximum tokens to generate (overrides config)"
    )
    stream: bool = Field(
        default=False,
        description="Whether to stream the response"
    )


class ChatChoice(BaseModel):
    """A single choice in chat completion."""

    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None


class ChatUsage(BaseModel):
    """Token usage information."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class SourceCitation(BaseModel):
    """A source citation for a chat response."""

    file_name: str = Field(
        description="Name of the source document"
    )
    page_label: Optional[str] = Field(
        default=None,
        description="Page number or label in the document"
    )
    chunk_index: int = Field(
        description="Index of the chunk within the document"
    )
    score: float = Field(
        description="Relevance score of this source"
    )
    text: str = Field(
        description="The actual text content from the source"
    )


class ChatCompletionResponse(BaseModel):
    """Response for chat completion."""

    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatChoice]
    usage: Optional[ChatUsage] = None
    sources: Optional[list[SourceCitation]] = Field(
        default=None,
        description="Source citations if include_sources was enabled"
    )


class ChatStreamChunk(BaseModel):
    """A chunk in a streaming chat response."""

    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: list[dict]


# ===== Ingestion Models =====

class IngestRequest(BaseModel):
    """Request to ingest a document."""

    file_name: str = Field(
        description="Name of the file being ingested"
    )


class IngestResponse(BaseModel):
    """Response after ingesting a document."""

    document_id: str = Field(
        description="Unique ID of the ingested document"
    )
    file_name: str = Field(
        description="Name of the ingested file"
    )
    num_chunks: int = Field(
        description="Number of chunks created from the document"
    )
    status: str = Field(
        default="success",
        description="Status of the ingestion"
    )


class DocumentInfo(BaseModel):
    """Information about an ingested document."""

    document_id: str
    file_name: str
    num_chunks: int
    ingested_at: str


class ListDocumentsResponse(BaseModel):
    """Response listing all ingested documents."""

    documents: list[DocumentInfo]
    total: int


class DeleteDocumentResponse(BaseModel):
    """Response after deleting a document."""

    document_id: str
    status: str = "deleted"


# ===== Embedding Models =====

class EmbeddingRequest(BaseModel):
    """Request to generate embeddings."""

    input: str | list[str] = Field(
        description="Text or list of texts to embed"
    )


class EmbeddingData(BaseModel):
    """A single embedding result."""

    object: str = "embedding"
    embedding: list[float]
    index: int


class EmbeddingResponse(BaseModel):
    """Response for embedding generation."""

    object: str = "list"
    data: list[EmbeddingData]
    model: str
    usage: dict


# ===== Chunk Retrieval Models =====

class ChunkRetrievalRequest(BaseModel):
    """Request to retrieve similar chunks."""

    query: str = Field(
        description="Query text to find similar chunks for"
    )
    top_k: Optional[int] = Field(
        default=None,
        gt=0,
        description="Number of chunks to retrieve (overrides config)"
    )


class ChunkMetadata(BaseModel):
    """Metadata for a retrieved chunk."""

    document_id: str
    file_name: str
    chunk_index: int
    score: float


class RetrievedChunk(BaseModel):
    """A retrieved text chunk with metadata."""

    text: str
    metadata: ChunkMetadata


class ChunkRetrievalResponse(BaseModel):
    """Response containing retrieved chunks."""

    chunks: list[RetrievedChunk]
    query: str


# ===== Health Check Models =====

class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str = "0.1.0"
    components: dict[str, str]
