from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/health/reconnect")
async def reconnect(request: Request) -> dict:
    return await health(request)


@router.get("/health")
async def health(request: Request) -> dict:
    connection = request.app.state.connection
    connected = await connection.check()
    return {
        "status": "ok",
        "floci_connected": connected,
        "endpoint": connection.settings.floci_endpoint,
        "region": connection.settings.aws_region,
        "last_success_at": (
            connection.last_success_at.isoformat() if connection.last_success_at else None
        ),
        "last_error": getattr(connection, "last_error", None),
    }
