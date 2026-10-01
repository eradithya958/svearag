import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from svearag.api.dependencies import get_container
from svearag.api.routes import router
from svearag.core.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan context."""
    container = get_container()
    logger.info(
        "Starting SveaRAG application server", extra_data={"env": container.settings.environment}
    )
    # Auto-index corpus on startup if empty
    if container.indexed_doc_count == 0:
        container.initialize_corpus()
    yield
    logger.info("Shutting down SveaRAG application server")


def create_app() -> FastAPI:
    """Builds and configures the FastAPI application."""
    app = FastAPI(
        title="SveaRAG Assistant API",
        description="Production-grade RAG assistant for Swedish Public Services (Migrationsverket & Skatteverket)",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Structured Request Logging Middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        start_time = time.perf_counter()

        response: Response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        response.headers["X-Request-ID"] = req_id

        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code}",
            extra_data={
                "request_id": req_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )
        return response

    app.include_router(router)

    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

        @app.get("/", response_class=FileResponse, include_in_schema=False)
        def serve_index():
            return FileResponse(static_dir / "index.html")

    return app


app = create_app()
