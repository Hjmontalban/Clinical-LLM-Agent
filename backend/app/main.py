import logging
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.router import router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(get_settings().debug)
    try:
        await init_db()
    except Exception:
        logger.exception("Database init failed during startup")
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description="Evidence-grounded biomedical research assistant API",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list + ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def ensure_db_middleware(request: Request, call_next):
        try:
            await init_db()
        except Exception:
            logger.exception("Database init failed in middleware")
        return await call_next(request)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "path": request.url.path,
            },
        )

    # Mount at /api (primary) and root (fallback if platform strips prefix)
    app.include_router(router, prefix="/api")
    return app


app = create_app()
