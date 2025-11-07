"""FastAPI router for document ingestion."""

import logging

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException

from xantus.models.schemas import (
    IngestResponse,
    ListDocumentsResponse,
    DeleteDocumentResponse,
)
from xantus.services.ingest_service import IngestService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["ingest"])


def get_ingest_service() -> IngestService:
    """Dependency to get ingest service instance."""
    from xantus.main import get_injector
    return get_injector().get(IngestService)


@router.post("/ingest/file")
async def ingest_file(
    file: UploadFile = File(...),
    ingest_service: IngestService = Depends(get_ingest_service),
) -> IngestResponse:
    """
    Ingest a document file into the vector store.

    Supports various document formats including PDF, TXT, DOCX, etc.
    """
    logger.info(f"Received file upload: {file.filename}")

    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")

    try:
        result = await ingest_service.ingest_file(
            file_name=file.filename,
            file_content=file.file,
        )
        return result
    except Exception as e:
        logger.error(f"Error ingesting file: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest file: {str(e)}"
        )


@router.get("/documents")
async def list_documents(
    ingest_service: IngestService = Depends(get_ingest_service),
) -> ListDocumentsResponse:
    """
    List all ingested documents.

    Returns metadata about each document including ID, filename, and chunk count.
    """
    logger.info("Listing all documents")

    return await ingest_service.list_documents()


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    ingest_service: IngestService = Depends(get_ingest_service),
) -> DeleteDocumentResponse:
    """
    Delete a document from the vector store.

    Args:
        document_id: The ID of the document to delete
    """
    logger.info(f"Deleting document: {document_id}")

    try:
        return await ingest_service.delete_document(document_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting document: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )
