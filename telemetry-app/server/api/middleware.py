from fastapi import Request
from server.logs.logger import logger

def register_middleware(app):
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        logger.info("[API] Request started: %s", request.url.path)

        response = await call_next(request)

        logger.info("[API] Request finished: %s\n", request.url.path)
        return response