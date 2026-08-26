from __future__ import annotations

from typing import Any

import boto3
from botocore.client import BaseClient
from botocore.config import Config

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

BOTO_SERVICE_ALIASES = {
    "lambda": "lambda",
    "eventbridge": "events",
    "events": "events",
    "apigateway": "apigateway",
    "stepfunctions": "stepfunctions",
    "cloudwatch": "cloudwatch",
    "cognito": "cognito-idp",
    "msk": "kafka",
    "cloudmap": "servicediscovery",
    "neptune": "rds",
}


class FlociClient:
    """Central boto3 client factory pointed at the Floci endpoint."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._clients: dict[str, BaseClient] = {}
        self._session = boto3.Session(
            aws_access_key_id=self.settings.aws_access_key_id,
            aws_secret_access_key=self.settings.aws_secret_access_key,
            region_name=self.settings.aws_region,
        )
        self._boto_config = Config(
            retries={"max_attempts": 2, "mode": "standard"},
            connect_timeout=3,
            read_timeout=10,
        )

    def get_client(self, service_name: str) -> BaseClient:
        boto_service = BOTO_SERVICE_ALIASES.get(service_name, service_name)
        if boto_service not in self._clients:
            logger.debug("Creating Floci boto3 client", extra={"service": boto_service})
            self._clients[boto_service] = self._session.client(
                boto_service,
                endpoint_url=self.settings.floci_endpoint,
                config=self._boto_config,
            )
        return self._clients[boto_service]

    def client_kwargs(self) -> dict[str, Any]:
        return {
            "endpoint_url": self.settings.floci_endpoint,
            "region_name": self.settings.aws_region,
            "aws_access_key_id": self.settings.aws_access_key_id,
            "aws_secret_access_key": self.settings.aws_secret_access_key,
        }
