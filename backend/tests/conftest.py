from collections.abc import Iterator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import create_app


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    get_settings.cache_clear()
    monkeypatch.setenv("FLOCI_ENDPOINT", "http://127.0.0.1:4566")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")
    return Settings(
        floci_endpoint="http://127.0.0.1:4566",
        aws_region="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


@pytest.fixture
def app(settings: Settings, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "app.floci.connection.ConnectionManager.check",
        AsyncMock(return_value=True),
    )
    application = create_app()
    return application


@pytest.fixture
def client(app, settings: Settings) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        connection = MagicMock()
        connection.check = AsyncMock(return_value=True)
        connection.connected = True
        connection.last_success_at = None
        connection.last_error = None
        connection.settings = settings
        connection.status.return_value = {
            "connected": True,
            "endpoint": settings.floci_endpoint,
            "region": settings.aws_region,
            "last_success_at": None,
            "last_error": None,
        }
        app.state.connection = connection
        app.state.settings = settings
        yield test_client
