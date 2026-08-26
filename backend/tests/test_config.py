import pytest

from app.core.config import Settings, get_settings


def test_default_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FLOCI_ENDPOINT", raising=False)
    get_settings.cache_clear()
    settings = Settings()
    assert settings.floci_endpoint == "http://127.0.0.1:4566"
    assert settings.aws_region == "us-east-1"
    assert settings.aws_access_key_id == "test"


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FLOCI_ENDPOINT", "http://floci:4566")
    monkeypatch.setenv("AWS_REGION", "eu-west-1")
    get_settings.cache_clear()
    settings = Settings()
    assert settings.floci_endpoint == "http://floci:4566"
    assert settings.aws_region == "eu-west-1"
