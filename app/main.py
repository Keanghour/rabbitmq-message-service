from fastapi import FastAPI
from app.routes.queue_routes import router
from app.middleware.cors import setup_cors
from app.middleware.exception_handler import setup_exception_handlers

app = FastAPI(
    title="RabbitMQ Queue API",
    version="1.0"
)

# Setup middleware
setup_cors(app)
setup_exception_handlers(app)

# Include routes
app.include_router(router)