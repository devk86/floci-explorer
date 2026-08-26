import pytest
from unittest.mock import AsyncMock

from app.core.exceptions import ResourceNotFoundError
from app.models.inventory import InventorySnapshot
from app.models.resource import Resource
from datetime import datetime, timezone
from app.services.resource_service import ResourceService


class FakeInventory:
    collectors = {"lambda": object(), "s3": object()}

    def __init__(self, resources: list[Resource]) -> None:
        self._resources = resources

    async def get_snapshot(self, force: bool = False) -> InventorySnapshot:
        return InventorySnapshot(
            connected=True,
            timestamp=datetime.now(timezone.utc),
            services={"lambda": 1},
            total_resources=len(self._resources),
            resources=self._resources,
        )


@pytest.mark.asyncio
async def test_resource_search_and_pagination() -> None:
    resources = [
        Resource(id="lambda:process-order", service="lambda", resource_type="function", name="process-order", status="Active"),
        Resource(id="lambda:notify", service="lambda", resource_type="function", name="notify", status="Active"),
        Resource(id="s3:orders", service="s3", resource_type="bucket", name="orders", status="available"),
    ]
    service = ResourceService(FakeInventory(resources))
    items, total = await service.list_resources(search="ORDER", page=1, page_size=10)
    assert total == 2
    items, total = await service.list_resources(service="lambda", page=1, page_size=1)
    assert total == 2
    assert len(items) == 1


@pytest.mark.asyncio
async def test_resource_404() -> None:
    service = ResourceService(FakeInventory([]))
    with pytest.raises(ResourceNotFoundError):
        await service.get_resource("lambda", "missing")
