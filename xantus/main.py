"""Main FastAPI application for Xantus."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from injector import Injector

from xantus.config.settings import get_settings, Settings
from xantus.container import create_injector
from xantus.api import chat_router, ingest_router, embeddings_router
from xantus.models.schemas import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Global injector
_injector: Injector | None = None


def get_injector() -> Injector:
    """Get the global injector instance."""
    if _injector is None:
        raise RuntimeError("Injector not initialized")
    return _injector


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application."""
    global _injector

    logger.info("Starting Xantus application...")

    # Load settings
    settings = get_settings()
    logger.info(f"Loaded settings with LLM provider: {settings.llm.provider}")

    # Create dependency injection container
    _injector = create_injector(settings)
    logger.info("Dependency injection container initialized")

    yield

    logger.info("Shutting down Xantus application...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Xantus",
        description="A private RAG system for chatting with your documents",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Configure CORS
    if settings.server.cors_enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.server.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.info("CORS enabled")

    # Include routers
    app.include_router(chat_router.router)
    app.include_router(ingest_router.router)
    app.include_router(embeddings_router.router)

    # Health check endpoint
    @app.get("/health", response_model=HealthResponse)
    async def health_check() -> HealthResponse:
        """Health check endpoint."""
        return HealthResponse(
            status="healthy",
            version="0.1.0",
            components={
                "llm": settings.llm.provider,
                "embedding": settings.embedding.provider,
                "vector_store": settings.vector_store.provider,
            },
        )

    logger.info("FastAPI application created successfully")

    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    logger.info(f"Starting server on {settings.server.host}:{settings.server.port}")

    uvicorn.run(
        "xantus.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=True,
    )
