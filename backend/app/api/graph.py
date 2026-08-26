from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/graph")
async def get_graph(request: Request) -> dict:
    graph = await request.app.state.graph.build()
    request.app.state.last_relationship_count = len(graph.edges)
    return graph.model_dump()
