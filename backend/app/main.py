from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import graph, health, inventory, resources, terraform, websocket
from app.api.websocket import ConnectionHub
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.dependencies.engine import DependencyEngine
from app.floci.client import FlociClient
from app.floci.connection import ConnectionManager
from app.services.graph_service import GraphService
from app.services.inventory_service import InventoryService
from app.services.resource_service import ResourceService

logger = get_logger(__name__)
STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = get_settings()
    floci_client = FlociClient(settings)
    connection = ConnectionManager(settings, floci_client)
    inventory = InventoryService(floci_client, connection)
    resource_service = ResourceService(inventory)
    graph_service = GraphService(inventory, DependencyEngine())
    app.state.settings = settings
    app.state.floci_client = floci_client
    app.state.connection = connection
    app.state.inventory = inventory
    app.state.resources = resource_service
    app.state.graph = graph_service
    app.state.hub = ConnectionHub()
    app.state.last_relationship_count = 0
    await connection.check()
    logger.info("Floci Explorer backend started")
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="Floci Explorer",
        description="Discover and map AWS infrastructure running inside Floci.",
        version="0.1.0",
        lifespan=lifespan,
    )
    origins = [item.strip() for item in settings.cors_origins.split(",") if item.strip()]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health.router, prefix="/api")
    application.include_router(inventory.router, prefix="/api")
    application.include_router(resources.router, prefix="/api")
    application.include_router(graph.router, prefix="/api")
    application.include_router(terraform.router, prefix="/api")
    application.include_router(websocket.router)
    _mount_frontend(application)
    return application


def _mount_frontend(application: FastAPI) -> None:
    if not STATIC_DIR.is_dir():
        return
    assets = STATIC_DIR / "assets"
    if assets.is_dir():
        application.mount("/assets", StaticFiles(directory=assets), name="assets")

    @application.get("/{full_path:path}")
    async def spa(full_path: str):
        candidate = STATIC_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(STATIC_DIR / "index.html")


app = create_app()
