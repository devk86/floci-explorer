from typing import Any

from pydantic import BaseModel, Field


class GraphNodeData(BaseModel):
    label: str
    service: str
    resource_type: str
    status: str | None = None
    name: str | None = None


class GraphNode(BaseModel):
    id: str
    type: str
    data: GraphNodeData


class GraphEdgeData(BaseModel):
    confidence: float
    relationship: str
    source_field: str | None = None


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str
    data: GraphEdgeData


class Graph(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)
