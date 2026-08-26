from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from app.collectors.registry import build_collectors
from app.collectors.support import is_expected_collector_gap
from app.core.exceptions import CollectorError, ServiceNotSupportedError
from app.core.logging import get_logger
from app.dependencies.engine import DependencyEngine
from app.floci.client import FlociClient
from app.floci.connection import ConnectionManager
from app.models.inventory import InventorySnapshot, ServiceError
from app.models.resource import Resource

logger = get_logger(__name__)


class InventoryService:
    def __init__(
        self,
        floci_client: FlociClient,
        connection: ConnectionManager,
        collector_names: list[str] | None = None,
    ) -> None:
        self.floci_client = floci_client
        self.connection = connection
        all_collectors = build_collectors(floci_client)
        if collector_names is not None:
            self.collectors = {
                name: all_collectors[name]
                for name in collector_names
                if name in all_collectors
            }
        else:
            self.collectors = all_collectors
        self.engine = DependencyEngine()
        self.relationship_count = 0
        self._snapshot: InventorySnapshot | None = None
        self._lock = asyncio.Lock()

    async def refresh(self) -> InventorySnapshot:
        async with self._lock:
            connected = await self.connection.check()
            sem = asyncio.Semaphore(5)

            async def limited(name, collector):
                async with sem:
                    return await self._run_collector(name, collector)

            results = await asyncio.gather(
                *[limited(name, collector) for name, collector in self.collectors.items()]
            )
            resources: list[Resource] = []
            errors: list[ServiceError] = []
            unsupported: list[str] = []
            services: dict[str, int] = {}
            for name, collected, error, is_unsupported in results:
                if is_unsupported:
                    unsupported.append(name)
                    services[name] = 0
                    continue
                if error:
                    errors.append(ServiceError(service=name, message=error))
                    services[name] = 0
                    continue
                services[name] = len(collected)
                resources.extend(collected)
            snapshot = InventorySnapshot(
                connected=connected,
                timestamp=datetime.now(timezone.utc),
                services=services,
                total_resources=len(resources),
                errors=errors,
                unsupported=unsupported,
                resources=resources,
            )
            self.relationship_count = len(self.engine.build(resources))
            self._snapshot = snapshot
            return snapshot

    async def get_snapshot(self, force: bool = False) -> InventorySnapshot:
        if force or self._snapshot is None:
            return await self.refresh()
        return self._snapshot

    def current(self) -> InventorySnapshot | None:
        return self._snapshot

    async def resources_for_service(self, service: str) -> list[Resource]:
        if service not in self.collectors:
            raise ServiceNotSupportedError(service)
        snapshot = await self.get_snapshot()
        return [item for item in snapshot.resources if item.service == service]

    async def _run_collector(self, name: str, collector) -> tuple[str, list[Resource], str | None, bool]:
        try:
            collected = await collector.collect()
            return name, collected, None, not collector.supported
        except CollectorError as exc:
            if is_expected_collector_gap(exc) or is_expected_collector_gap(exc.__cause__ or exc):
                return name, [], None, True
            logger.debug("Collector failed: %s %s", name, exc)
            return name, [], str(exc), False
        except Exception as exc:
            if is_expected_collector_gap(exc):
                return name, [], None, True
            logger.debug("Collector failed: %s %s", name, exc)
            return name, [], str(exc), False
