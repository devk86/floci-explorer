from fastapi import APIRouter, HTTPException, Request

from app.core.exceptions import ServiceNotSupportedError
from app.models.inventory import InventorySnapshot

router = APIRouter()


@router.get("/inventory")
async def get_inventory(request: Request, refresh: bool = False) -> dict:
    snapshot: InventorySnapshot = await request.app.state.inventory.get_snapshot(force=refresh)
    return {
        "connected": snapshot.connected,
        "timestamp": snapshot.timestamp.isoformat(),
        "services": snapshot.services,
        "total_resources": snapshot.total_resources,
        "errors": [],
        "unsupported": snapshot.unsupported,
        "total_relationships": request.app.state.inventory.relationship_count,
    }


@router.get("/inventory/{service}")
async def get_inventory_service(service: str, request: Request) -> dict:
    try:
        resources = await request.app.state.inventory.resources_for_service(service)
    except ServiceNotSupportedError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "service": service,
        "count": len(resources),
        "resources": [item.model_dump() for item in resources],
    }
