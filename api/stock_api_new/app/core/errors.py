from fastapi import Request
from fastapi.responses import JSONResponse 
from fastapi.exceptions import RequestValidationError 
from fastapi import HTTPException 

from app.schemas.common import ErrorResponse 

def _trace_id(request : Request) -> str | None:
    return getattr(request.state ,'trace_id', None)


async def http_exception_handler(request: Request, exc: HTTPException):
    code = "HTTP_ERROR"
    if exc.status_code == 400:
        code = "BAD_REQUEST"
    elif exc.status_code == 404:
        code = "NOT_FOUND"
    elif exc.status_code == 401:
        code = "UNAUTHORIZED"
    elif exc.status_code == 403:
        code = "FORBIDDEN"
    elif exc.status_code == 429:
        code = "RATE_LIMITED"
    elif exc.status_code == 502:
        code = "UPSTREAM_ERROR"   
    elif exc.status_code == 503:
        code = "SERVICE_UNAVAILABLE"

    body = ErrorResponse(
        error_code=code,
        message=str(exc.detail),
        trace_id=_trace_id(request),
    )
    return JSONResponse(status_code=exc.status_code, 
                        content=body.model_dump())


async def validation_exception_handler(request : Request, exc : RequestValidationError):
    body = ErrorResponse(
        error_code='VALIDATION_ERROR',
        message='Invalid request parameters', 
        trace_id=_trace_id(request),
    )

    return JSONResponse(status_code=422,
                        content=body.model_dump())


async def unhandled_exception_handler(request: Request, exc: Exception):
    body = ErrorResponse(
        error_code='INTERNAL_ERROR',
        message='Internal server error',
        trace_id=_trace_id(request),
    )
    return JSONResponse(status_code=500, 
                        content=body.model_dump())