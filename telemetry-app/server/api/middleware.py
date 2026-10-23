from fastapi import Request
from server.logger import logger

def register_middleware(app):
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        logger.info("Request started: %s", request.url.path)

        response = await call_next(request)

        logger.info("Request finished: %s\n", request.url.path)
        return response