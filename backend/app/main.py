import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.database import engine, Base
from app.routers import doorbell_router
from app.dependencies import get_doorbell_manager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

    doorbell_manager = get_doorbell_manager()

    logger.info("Application started successfully")

    yield

    logger.info("Shutting down application...")
    doorbell_manager.cleanup()
    logger.info("Application shutdown complete")

app = FastAPI(
    title="Smart Door Control API",
    description="API для управления умным дверным звонком",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(doorbell_router)

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Smart Door Control API is running",
        "sensors_enabled": settings.sensors_enabled,
        "camera_enabled": settings.camera_enabled
    }