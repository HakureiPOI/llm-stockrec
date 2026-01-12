import secrets
from fastapi import Request 
from starlette.middleware.base import BaseHTTPMiddleware 

TRACE_HEADER = 'X-Trace-Id'

class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request : Request, call_next):
        trace_id = request.headers.get(TRACE_HEADER) or secrets.token_hex(8)

        request.state.trace_id = trace_id
        
        response = await call_next(request)
        response.headers[TRACE_HEADER] = trace_id

        return response