from app.dependencies.engine import DependencyEngine
from app.models.graph import Graph, GraphEdge, GraphEdgeData, GraphNode, GraphNodeData
from app.services.inventory_service import InventoryService


class GraphService:
    def __init__(self, inventory: InventoryService, engine: DependencyEngine | None = None) -> None:
        self.inventory = inventory
        self.engine = engine or DependencyEngine()

    async def build(self) -> Graph:
        snapshot = await self.inventory.get_snapshot()
        node_ids = {item.id for item in snapshot.resources}
        nodes = [
            GraphNode(
                id=item.id,
                type=item.service,
                data=GraphNodeData(
                    label=item.name or item.id,
                    service=item.service,
                    resource_type=item.resource_type,
                    status=item.status,
                    name=item.name,
                ),
            )
            for item in snapshot.resources
        ]
        relationships = self.engine.build(snapshot.resources)
        edges: list[GraphEdge] = []
        for rel in relationships:
            if rel.source not in node_ids or rel.target not in node_ids:
                continue
            edges.append(
                GraphEdge(
                    id=f"{rel.source}->{rel.target}:{rel.relationship}",
                    source=rel.source,
                    target=rel.target,
                    label=rel.relationship,
                    data=GraphEdgeData(
                        confidence=rel.confidence,
                        relationship=rel.relationship,
                        source_field=rel.source_field,
                    ),
                )
            )
        return Graph(
            nodes=nodes,
            edges=edges,
            errors=[],
        )
