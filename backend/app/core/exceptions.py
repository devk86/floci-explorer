from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class FlociError(Exception):
    """Base application error."""


class FlociConnectionError(FlociError):
    def __init__(self, message: str = "Unable to reach Floci") -> None:
        super().__init__(message)


class CollectorError(FlociError):
    def __init__(self, service: str, message: str) -> None:
        self.service = service
        super().__init__(message)


class ResourceNotFoundError(FlociError):
    def __init__(self, resource_id: str) -> None:
        self.resource_id = resource_id
        super().__init__(f"Resource not found: {resource_id}")


class ServiceNotSupportedError(FlociError):
    def __init__(self, service: str) -> None:
        self.service = service
        super().__init__(f"Service is not supported: {service}")


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
