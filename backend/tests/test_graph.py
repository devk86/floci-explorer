from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.models.inventory import InventorySnapshot
from app.models.resource import Resource
from app.services.graph_service import GraphService


class FakeInventory:
    def __init__(self, resources: list[Resource], errors=None) -> None:
        self._resources = resources
        self._errors = errors or []

    async def get_snapshot(self, force: bool = False) -> InventorySnapshot:
        return InventorySnapshot(
            connected=True,
            timestamp=datetime.now(timezone.utc),
            total_resources=len(self._resources),
            resources=self._resources,
            errors=self._errors,
        )


@pytest.mark.asyncio
async def test_graph_empty() -> None:
    graph = await GraphService(FakeInventory([])).build()
    assert graph.nodes == []
    assert graph.edges == []


@pytest.mark.asyncio
async def test_graph_one_resource() -> None:
    graph = await GraphService(
        FakeInventory(
            [Resource(id="s3:a", service="s3", resource_type="bucket", name="a")]
        )
    ).build()
    assert len(graph.nodes) == 1
    assert graph.edges == []


@pytest.mark.asyncio
async def test_graph_with_relationships() -> None:
    resources = [
        Resource(
            id="lambda:fn",
            service="lambda",
            resource_type="function",
            name="fn",
            metadata={"environment": {"BUCKET_NAME": "a"}},
        ),
        Resource(id="s3:a", service="s3", resource_type="bucket", name="a"),
    ]
    graph = await GraphService(FakeInventory(resources)).build()
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    assert graph.edges[0].data.confidence == 0.7


@pytest.mark.asyncio
async def test_graph_keeps_nodes_when_collector_failed() -> None:
    from app.models.inventory import ServiceError

    graph = await GraphService(
        FakeInventory(
            [Resource(id="s3:a", service="s3", resource_type="bucket", name="a")],
            errors=[ServiceError(service="lambda", message="boom")],
        )
    ).build()
    assert len(graph.nodes) == 1
    assert graph.errors == []
