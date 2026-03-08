from fastapi import Request
from fastapi.responses import JSONResponse
from app.utils.response import api_response
from app.middleware.custom_exceptions import QueueError, ValidationError

def setup_exception_handlers(app):
    @app.exception_handler(QueueError)
    async def queue_exception_handler(request: Request, exc: QueueError):
        return JSONResponse(
            status_code=500,
            content=api_response(
                status_code=500,
                desc="Queue processing failed",
                error=exc.message,
            )
        )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=400,
            content=api_response(
                status_code=400,
                desc="Validation failed",
                error=exc.message
            )
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=api_response(
                status_code=500,
                desc="Internal server error",
                error=str(exc)
            )
        )