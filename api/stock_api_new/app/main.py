from fastapi import FastAPI 
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException

from app.core.config import settings 
from app.api.v1.router import api_router 
from app.core.trace import TraceIdMiddleware 
from app.core.errors import (
    http_exception_handler, 
    validation_exception_handler, 
    unhandled_exception_handler,
)

app = FastAPI(title=settings.app_name)

app.add_middleware(TraceIdMiddleware)

app.include_router(api_router, prefix=settings.api_prefix)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)