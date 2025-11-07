"""Service for ingesting documents into the vector store."""

import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

from injector import inject
from llama_index.core import (
    Document,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.vector_stores.types import VectorStore

from xantus.config.settings import Settings
from xantus.models.schemas import (
    DocumentInfo,
    IngestResponse,
    ListDocumentsResponse,
    DeleteDocumentResponse,
)

logger = logging.getLogger(__name__)


class IngestService:
    """Service for document ingestion operations."""

    @inject
    def __init__(
        self,
        settings: Settings,
        embedding: BaseEmbedding,
        vector_store: VectorStore,
    ):
        """
        Initialize the ingestion service.

        Args:
            settings: Application settings
            embedding: Embedding model
            vector_store: Vector store instance
        """
        self.settings = settings
        self.embedding = embedding
        self.vector_store = vector_store

        # Create text splitter based on config
        self.text_splitter = SentenceSplitter(
            chunk_size=settings.rag.chunk_size,
            chunk_overlap=settings.rag.chunk_overlap,
        )

        # Storage directory for uploaded files
        self.storage_dir = Path("./data/uploaded_docs")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Document metadata storage (in production, use a database)
        self.document_metadata = {}

        # Load existing document metadata from disk
        self._load_metadata_from_disk()

    def _load_metadata_from_disk(self):
        """
        Load document metadata from existing files in storage directory.

        This allows the service to recover metadata after a restart.
        """
        try:
            # Scan storage directory for uploaded files
            for file_path in self.storage_dir.glob("*"):
                if file_path.is_file() and not file_path.name.startswith("."):
                    # Parse filename format: {document_id}_{original_filename}
                    parts = file_path.name.split("_", 1)
                    if len(parts) == 2:
                        document_id, file_name = parts

                        # Try to get chunk count from ChromaDB
                        num_chunks = 0
                        try:
                            from llama_index.vector_stores.chroma import ChromaVectorStore

                            if isinstance(self.vector_store, ChromaVectorStore):
                                collection = self.vector_store._collection
                                # Query for chunks with this document_id
                                results = collection.get(
                                    where={"document_id": document_id}
                                )
                                num_chunks = len(results.get("ids", []))
                        except Exception as e:
                            logger.debug(f"Could not get chunk count for {document_id}: {e}")

                        # Create document metadata entry
                        self.document_metadata[document_id] = DocumentInfo(
                            document_id=document_id,
                            file_name=file_name,
                            num_chunks=num_chunks,
                            ingested_at=datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        )

            if self.document_metadata:
                logger.info(f"Loaded metadata for {len(self.document_metadata)} existing documents")
        except Exception as e:
            logger.error(f"Error loading metadata from disk: {e}", exc_info=True)

    async def ingest_file(
        self,
        file_name: str,
        file_content: BinaryIO,
    ) -> IngestResponse:
        """
        Ingest a document file.

        Args:
            file_name: Name of the file
            file_content: Binary file content

        Returns:
            Ingestion response with document info
        """
        logger.info(f"Starting ingestion of file: {file_name}")

        # Generate document ID from file content hash
        content_bytes = file_content.read()
        document_id = hashlib.sha256(content_bytes).hexdigest()[:16]

        # Save file to storage
        file_path = self.storage_dir / f"{document_id}_{file_name}"
        with open(file_path, "wb") as f:
            f.write(content_bytes)

        # Load and parse the document
        documents = SimpleDirectoryReader(
            input_files=[str(file_path)]
        ).load_data()

        # Add metadata to documents
        for doc in documents:
            doc.metadata.update({
                "document_id": document_id,
                "file_name": file_name,
                "ingested_at": datetime.utcnow().isoformat(),
            })

        # Split documents into chunks
        nodes = self.text_splitter.get_nodes_from_documents(documents)

        # Add chunk index to metadata
        for idx, node in enumerate(nodes):
            node.metadata["chunk_index"] = idx

        logger.info(f"Created {len(nodes)} chunks from document {file_name}")

        # Create storage context with vector store
        storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )

        # Create index and insert nodes
        index = VectorStoreIndex(
            nodes=nodes,
            storage_context=storage_context,
            embed_model=self.embedding,
        )

        # Store document metadata
        self.document_metadata[document_id] = DocumentInfo(
            document_id=document_id,
            file_name=file_name,
            num_chunks=len(nodes),
            ingested_at=datetime.utcnow().isoformat(),
        )

        logger.info(f"Successfully ingested document {file_name} with ID {document_id}")

        return IngestResponse(
            document_id=document_id,
            file_name=file_name,
            num_chunks=len(nodes),
            status="success",
        )

    async def list_documents(self) -> ListDocumentsResponse:
        """
        List all ingested documents.

        Returns:
            List of document information
        """
        documents = list(self.document_metadata.values())

        return ListDocumentsResponse(
            documents=documents,
            total=len(documents),
        )

    async def delete_document(self, document_id: str) -> DeleteDocumentResponse:
        """
        Delete a document from the vector store.

        Args:
            document_id: ID of the document to delete

        Returns:
            Deletion response

        Raises:
            ValueError: If document not found
        """
        if document_id not in self.document_metadata:
            raise ValueError(f"Document {document_id} not found")

        # Get document info before deleting metadata
        doc_info = self.document_metadata[document_id]

        # Delete from vector store
        try:
            # ChromaDB supports deletion by metadata filtering
            from llama_index.vector_stores.chroma import ChromaVectorStore

            if isinstance(self.vector_store, ChromaVectorStore):
                # Access the underlying ChromaDB collection
                collection = self.vector_store._collection

                # Delete all chunks with this file_name
                # Note: LlamaIndex stores its own doc_id in the 'document_id' field,
                # so we filter by file_name instead which is reliably stored at top-level
                collection.delete(
                    where={"file_name": doc_info.file_name}
                )
                logger.info(f"Deleted document {doc_info.file_name} (ID: {document_id}) from ChromaDB vector store")
            else:
                # For other vector stores (Qdrant, etc.), implement as needed
                logger.warning(
                    f"Vector store deletion not implemented for {type(self.vector_store).__name__}"
                )
        except Exception as e:
            logger.error(f"Error deleting from vector store: {e}", exc_info=True)
            # Continue with metadata and file deletion even if vector store deletion fails

        # Remove from metadata
        self.document_metadata.pop(document_id)

        # Remove file from storage
        file_path = self.storage_dir / f"{document_id}_{doc_info.file_name}"
        if file_path.exists():
            file_path.unlink()

        logger.info(f"Successfully deleted document {document_id}")

        return DeleteDocumentResponse(
            document_id=document_id,
            status="deleted",
        )
