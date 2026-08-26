from pydantic import BaseModel, Field


class Relationship(BaseModel):
    source: str
    target: str
    relationship: str
    confidence: float
    source_field: str | None = None
