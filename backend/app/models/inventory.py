from datetime import datetime

from pydantic import BaseModel, Field

from app.models.resource import Resource


class ServiceError(BaseModel):
    service: str
    message: str


class InventorySnapshot(BaseModel):
    connected: bool
    timestamp: datetime
    services: dict[str, int] = Field(default_factory=dict)
    total_resources: int = 0
    errors: list[ServiceError] = Field(default_factory=list)
    unsupported: list[str] = Field(default_factory=list)
    resources: list[Resource] = Field(default_factory=list)
