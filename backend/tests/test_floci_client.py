from unittest.mock import MagicMock

import pytest

from app.core.config import Settings
from app.floci.client import FlociClient


def test_get_client_reuses_instances(monkeypatch: pytest.MonkeyPatch) -> None:
    created: list[str] = []

    def fake_client(service_name: str, **kwargs):
        created.append(service_name)
        mock = MagicMock()
        mock.service_name = service_name
        mock.kwargs = kwargs
        return mock

    settings = Settings()
    client = FlociClient(settings)
    monkeypatch.setattr(client._session, "client", fake_client)

    first = client.get_client("ec2")
    second = client.get_client("ec2")
    s3 = client.get_client("s3")
    lambda_client = client.get_client("lambda")

    assert first is second
    assert s3 is not first
    assert created == ["ec2", "s3", "lambda"]
    assert lambda_client.kwargs["endpoint_url"] == settings.floci_endpoint
