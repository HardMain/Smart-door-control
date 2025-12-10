import logging
from fastapi import FastAPI

from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart Door Control API",
    description="API для управления умным дверным звонком",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Smart Door Control API is running"
}