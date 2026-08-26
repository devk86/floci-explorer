from __future__ import annotations

import asyncio
from typing import Any

from botocore.exceptions import UnknownServiceError

from app.collectors.support import is_expected_collector_gap
from app.core.exceptions import CollectorError
from app.core.logging import get_logger
from app.floci.client import FlociClient
from app.models.resource import Resource

logger = get_logger(__name__)


class BaseCollector:
    service_name: str
    supported: bool = True

    def __init__(self, floci_client: FlociClient) -> None:
        self.floci_client = floci_client

    def client(self, service_name: str | None = None):
        return self.floci_client.get_client(service_name or self.service_name)

    async def collect(self) -> list[Resource]:
        try:
            return await asyncio.to_thread(self.collect_sync)
        except CollectorError:
            raise
        except UnknownServiceError:
            self.supported = False
            return []
        except Exception as exc:
            if is_expected_collector_gap(exc):
                self.supported = False
                return []
            logger.debug("Collector %s failed: %s", self.service_name, exc)
            raise CollectorError(self.service_name, str(exc)) from exc

    def collect_sync(self) -> list[Resource]:
        raise NotImplementedError

    def paginate(self, client, operation: str, key: str, **kwargs) -> list[Any]:
        items: list[Any] = []
        try:
            paginator = client.get_paginator(operation)
            for page in paginator.paginate(**kwargs):
                items.extend(self._extract(page, key))
            return items
        except Exception:
            method = getattr(client, operation)
            page = method(**kwargs)
            return self._extract(page, key)

    def _extract(self, page: Any, key: str) -> list[Any]:
        current = page
        for part in key.split("."):
            if not isinstance(current, dict):
                return []
            current = current.get(part)
        if current is None:
            return []
        if isinstance(current, list):
            return current
        return [current]
