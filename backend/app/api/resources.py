from fastapi import APIRouter, HTTPException, Query, Request

from app.core.exceptions import ResourceNotFoundError, ServiceNotSupportedError
from app.dependencies.engine import DependencyEngine
from app.services.secrets import mask_resource

router = APIRouter()


@router.get("/resources")
async def list_resources(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: str | None = None,
    status: str | None = None,
    service: str | None = None,
) -> dict:
    items, total = await request.app.state.resources.list_resources(
        service=service,
        search=search,
        status=status,
        page=page,
        page_size=page_size,
    )
    show_secrets = request.app.state.settings.show_secrets
    return {
        "items": [mask_resource(item, show_secrets).model_dump() for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/resources/{service}")
async def list_service_resources(
    service: str,
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: str | None = None,
    status: str | None = None,
) -> dict:
    try:
        items, total = await request.app.state.resources.list_resources(
            service=service,
            search=search,
            status=status,
            page=page,
            page_size=page_size,
        )
    except ServiceNotSupportedError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    show_secrets = request.app.state.settings.show_secrets
    return {
        "items": [mask_resource(item, show_secrets).model_dump() for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/resources/{service}/{resource_id:path}")
async def get_resource(
    service: str,
    resource_id: str,
    request: Request,
    show_secrets: bool = Query(False),
) -> dict:
    try:
        item = await request.app.state.resources.get_resource(service, resource_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    snapshot = await request.app.state.inventory.get_snapshot()
    relationships = DependencyEngine().build(snapshot.resources)
    related = [
        rel.model_dump()
        for rel in relationships
        if rel.source == item.id or rel.target == item.id
    ]
    reveal = show_secrets or request.app.state.settings.show_secrets
    payload = mask_resource(item, reveal).model_dump()
    payload["relationships"] = related
    return payload
