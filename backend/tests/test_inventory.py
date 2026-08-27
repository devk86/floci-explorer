import pytest

from app.collectors.base import BaseCollector
from app.core.exceptions import CollectorError
from app.floci.client import FlociClient
from app.models.resource import Resource
from app.services.inventory_service import InventoryService
from unittest.mock import AsyncMock, MagicMock


class OkCollector(BaseCollector):
    service_name = "s3"

    def collect_sync(self) -> list[Resource]:
        return [
            Resource(
                id="s3:a",
                service="s3",
                resource_type="bucket",
                name="a",
            )
        ]


class BoomCollector(BaseCollector):
    service_name = "lambda"

    async def collect(self) -> list[Resource]:
        raise CollectorError("lambda", "boom")


@pytest.mark.asyncio
async def test_inventory_isolates_collector_failure() -> None:
    inventory = InventoryService(MagicMock(spec=FlociClient), MagicMock())
    inventory.connection.check = AsyncMock(return_value=True)
    inventory.collectors = {
        "s3": OkCollector(MagicMock()),
        "lambda": BoomCollector(MagicMock()),
    }
    snapshot = await inventory.refresh()
    assert snapshot.total_resources == 1
    assert snapshot.services["s3"] == 1
    assert snapshot.services["lambda"] == 0
    assert snapshot.errors[0].service == "lambda"


@pytest.mark.asyncio
async def test_get_snapshot_force_recrawls() -> None:
    calls = {"n": 0}

    class CountingCollector(BaseCollector):
        service_name = "s3"

        def collect_sync(self) -> list[Resource]:
            calls["n"] += 1
            return [
                Resource(
                    id=f"s3:{calls['n']}",
                    service="s3",
                    resource_type="bucket",
                    name=str(calls["n"]),
                )
            ]

    inventory = InventoryService(MagicMock(spec=FlociClient), MagicMock())
    inventory.connection.check = AsyncMock(return_value=True)
    inventory.collectors = {"s3": CountingCollector(MagicMock())}

    first = await inventory.get_snapshot()
    cached = await inventory.get_snapshot(force=False)
    assert calls["n"] == 1
    assert cached.resources[0].id == first.resources[0].id

    forced = await inventory.get_snapshot(force=True)
    assert calls["n"] == 2
    assert forced.resources[0].id == "s3:2"
