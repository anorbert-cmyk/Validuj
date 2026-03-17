from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.db import ensure_database
from app.routes.api import router as api_router
from app.routes.auth import router as auth_router
from app.routes.billing import router as billing_router
from app.routes.seo import router as seo_router
from app.routes.stream import router as stream_router
from app.routes.webhooks import router as webhooks_router
from app.routes.web import router as web_router
from app.services.analysis_runner import AnalysisRunner
from app.services.model_router import ModelRouter
from app.services.search_service import SearchService


def create_app() -> FastAPI:
    settings = get_settings()
    ensure_database()

    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:3000",
            "http://localhost:3000",
            settings.app_base_url,
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount("/static", StaticFiles(directory="/workspace/app/static"), name="static")

    templates = Jinja2Templates(directory="/workspace/app/templates")
    app.state.settings = settings
    app.state.templates = templates
    app.state.analysis_runner = AnalysisRunner(
        router=ModelRouter(settings),
        search_service=SearchService(settings),
    )

    app.include_router(seo_router)
    app.include_router(web_router)
    app.include_router(api_router)
    app.include_router(auth_router)
    app.include_router(billing_router)
    app.include_router(webhooks_router)
    app.include_router(stream_router)
    return app


app = create_app()
