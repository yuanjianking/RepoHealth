"""
FastAPI application entry point.
"""

import asyncio
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import get_settings
from app.core.logger import get_logger
from app.api.v1.endpoints import repo, webhook
from app.services.event_history_service import EventHistoryService
from app.services.event_queue import event_queue
from app.services.storage_service import StorageService
from app.workers.event_worker import run_event_worker

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    logger.info("Starting up RepoHealth Backend API...")

    storage = StorageService()
    history_service = EventHistoryService()
    worker_task = asyncio.create_task(run_event_worker(storage, history_service, event_queue))

    yield

    worker_task.cancel()
    await asyncio.gather(worker_task, return_exceptions=True)
    logger.info("Shutting down RepoHealth Backend API...")


# Create FastAPI application
app = FastAPI(
    title="RepoHealth Backend API",
    description="FastAPI backend for RepoHealth project",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(repo.router, prefix="/api/v1/repo")
app.include_router(webhook.router, prefix="/api/v1/webhook")

# Add middleware for request timing
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": request.url.path,
        },
    )



# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "RepoHealth Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


# Health check endpoint (basic)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )