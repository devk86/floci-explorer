from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.models.inventory import InventorySnapshot
from app.models.graph import Graph
from app.models.resource import Resource


def test_inventory_and_resources_endpoints(client: TestClient, app) -> None:
    snapshot = InventorySnapshot(
        connected=True,
        timestamp=datetime.now(timezone.utc),
        services={"lambda": 1, "s3": 0},
        total_resources=1,
        resources=[
            Resource(
                id="lambda:process-order",
                service="lambda",
                resource_type="function",
                name="process-order",
                status="Active",
                metadata={"environment": {"API_KEY": "super-secret"}},
            )
        ],
    )
    app.state.inventory.get_snapshot = AsyncMock(return_value=snapshot)
    app.state.inventory.resources_for_service = AsyncMock(return_value=snapshot.resources)
    app.state.inventory.collectors = {"lambda": object(), "s3": object()}
    app.state.resources.list_resources = AsyncMock(return_value=(snapshot.resources, 1))
    app.state.resources.get_resource = AsyncMock(return_value=snapshot.resources[0])
    app.state.graph.build = AsyncMock(return_value=Graph(nodes=[], edges=[]))

    inventory = client.get("/api/inventory")
    assert inventory.status_code == 200
    assert inventory.json()["total_resources"] == 1
    app.state.inventory.get_snapshot.assert_called_with(force=False)

    forced = client.get("/api/inventory?refresh=true")
    assert forced.status_code == 200
    app.state.inventory.get_snapshot.assert_called_with(force=True)

    listed = client.get("/api/resources?search=order")
    assert listed.status_code == 200
    assert listed.json()["items"][0]["metadata"]["environment"]["API_KEY"] == "********"

    graph = client.get("/api/graph")
    assert graph.status_code == 200
    assert graph.json()["nodes"] == []
