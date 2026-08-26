from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Resource(BaseModel):
    id: str
    service: str
    resource_type: str
    name: str | None = None
    arn: str | None = None
    region: str | None = None
    status: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    raw: dict[str, Any] = Field(default_factory=dict)
    origin: str = "floci"


def isoformat_dt(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def tag_dict(tags: Any) -> dict[str, str]:
    if not tags:
        return {}
    if isinstance(tags, dict):
        return {str(k): str(v) for k, v in tags.items()}
    result: dict[str, str] = {}
    for tag in tags:
        if isinstance(tag, dict) and "Key" in tag:
            result[str(tag["Key"])] = str(tag.get("Value", ""))
    return result
