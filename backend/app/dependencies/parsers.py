from __future__ import annotations

import re

from app.models.resource import Resource

TABLE_ENV_KEYS = {"TABLE", "TABLE_NAME", "DYNAMODB_TABLE", "DDB_TABLE"}
BUCKET_ENV_KEYS = {"BUCKET", "BUCKET_NAME", "S3_BUCKET", "S3_BUCKET_NAME"}


def env_values(resource: Resource, keys: set[str]) -> list[tuple[str, str]]:
    env = (resource.metadata or {}).get("environment") or {}
    found: list[tuple[str, str]] = []
    for key, value in env.items():
        if key.upper() in keys and isinstance(value, str) and value.strip():
            found.append((key, value.strip()))
    return found


def name_from_arn(arn: str) -> str:
    return arn.rstrip("/").split(":")[-1].split("/")[-1]


def lambda_arn_from_integration_uri(uri: str) -> str | None:
    match = re.search(r"functions/(arn:aws:lambda:[^/]+)/invocations", uri)
    if match:
        return match.group(1)
    match = re.search(r"arn:aws:lambda:[^:]+:[^:]+:function:([^:/]+)", uri)
    if match:
        return match.group(0)
    return None
