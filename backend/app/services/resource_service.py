from __future__ import annotations

from app.core.exceptions import ResourceNotFoundError, ServiceNotSupportedError
from app.models.resource import Resource
from app.services.inventory_service import InventoryService


class ResourceService:
    def __init__(self, inventory: InventoryService) -> None:
        self.inventory = inventory

    async def list_resources(
        self,
        service: str | None = None,
        search: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Resource], int]:
        snapshot = await self.inventory.get_snapshot()
        items = snapshot.resources
        if service:
            if service not in self.inventory.collectors:
                raise ServiceNotSupportedError(service)
            items = [item for item in items if item.service == service]
        if search:
            needle = search.lower()
            items = [
                item
                for item in items
                if needle in (item.name or "").lower()
                or needle in item.id.lower()
                or needle in (item.arn or "").lower()
                or needle in item.resource_type.lower()
                or needle in item.service.lower()
            ]
        if status:
            wanted = status.lower()
            items = [item for item in items if (item.status or "").lower() == wanted]
        total = len(items)
        start = max(page - 1, 0) * page_size
        return items[start : start + page_size], total

    async def get_resource(self, service: str, resource_id: str) -> Resource:
        snapshot = await self.inventory.get_snapshot()
        candidates = [
            item
            for item in snapshot.resources
            if item.service == service
            and (item.id == resource_id or item.id.endswith(f":{resource_id}") or item.name == resource_id)
        ]
        if not candidates:
            # Allow full id passed as path
            candidates = [item for item in snapshot.resources if item.id == resource_id]
        if not candidates:
            raise ResourceNotFoundError(resource_id)
        return candidates[0]
