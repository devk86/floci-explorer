from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.floci.client import FlociClient

logger = get_logger(__name__)


class ConnectionManager:
    def __init__(
        self,
        settings: Settings | None = None,
        floci_client: FlociClient | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.floci_client = floci_client or FlociClient(self.settings)
        self.connected: bool = False
        self.last_success_at: datetime | None = None
        self.last_error: str | None = None

    async def check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(self.settings.floci_endpoint)
            # Floci/AWS emulators often return 4xx on GET /; reachability is enough.
            self.connected = response.status_code < 500
            if self.connected:
                self.last_success_at = datetime.now(timezone.utc)
                self.last_error = None
            else:
                self.last_error = f"HTTP {response.status_code}"
            return self.connected
        except httpx.HTTPError as exc:
            logger.warning("Floci connectivity check failed: %s", exc)
            self.connected = False
            self.last_error = str(exc)
            return False

    def status(self) -> dict[str, Any]:
        return {
            "connected": self.connected,
            "endpoint": self.settings.floci_endpoint,
            "region": self.settings.aws_region,
            "last_success_at": self.last_success_at.isoformat() if self.last_success_at else None,
            "last_error": self.last_error,
        }
