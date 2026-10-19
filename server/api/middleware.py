
from contextvars import Token
import uuid

from server.logger import trace_id_var

def register_middleware(app):
    @app.middleware("http")
    async def tracing_middleware(request, call_next):
        trace_id = uuid.uuid4().hex
        print(trace_id)

        token: Token = trace_id_var.set(trace_id)

        try:
            response = await call_next(request)
            return response
        finally:
            # Reset the trace id, so it doesnt overwrite the other requests
            trace_id_var.reset(token)