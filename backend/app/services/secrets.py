from copy import deepcopy
from typing import Any

from app.models.resource import Resource

SENSITIVE_KEY_PARTS = (
    "secret",
    "password",
    "token",
    "api_key",
    "apikey",
    "access_key",
    "private_key",
    "credential",
)


def mask_value(_value: Any) -> str:
    return "********"


def mask_mapping(data: dict[str, Any], show_secrets: bool) -> dict[str, Any]:
    if show_secrets:
        return data
    masked: dict[str, Any] = {}
    for key, value in data.items():
        lowered = key.lower()
        if any(part in lowered for part in SENSITIVE_KEY_PARTS):
            masked[key] = mask_value(value)
        elif isinstance(value, dict):
            masked[key] = mask_mapping(value, show_secrets)
        else:
            masked[key] = value
    return masked


def mask_resource(resource: Resource, show_secrets: bool) -> Resource:
    clone = resource.model_copy(deep=True)
    env = (clone.metadata or {}).get("environment")
    if isinstance(env, dict):
        clone.metadata["environment"] = mask_mapping(env, show_secrets)
    if isinstance(clone.raw, dict):
        clone.raw = mask_mapping(deepcopy(clone.raw), show_secrets)
    return clone
