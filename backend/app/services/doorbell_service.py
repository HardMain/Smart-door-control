import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.hardware import DoorbellManager, CameraService
from app.services.s3 import S3Service
from app.models import Visit

logger = logging.getLogger(__name__)


class DoorbellService:
    def __init__(
        self,
        doorbell_manager: DoorbellManager,
        camera_service: CameraService,
        s3_service: S3Service
    ):
        self.doorbell_manager = doorbell_manager
        self.camera_service = camera_service
        self.s3_service = s3_service

    async def handle_doorbell_press(self, db: AsyncSession):
        logger.info("Handling doorbell press")

        photo_bytes = await self.camera_service.capture_photo()

        photo_url = await self.s3_service.upload_photo(photo_bytes)

        visit = Visit(
            timestamp=datetime.utcnow(),
            photo_url=photo_url
        )
        db.add(visit)
        await db.commit()
        await db.refresh(visit)

        logger.info(f"Visit recorded: ID={visit.id}, URL={photo_url}")

        return visit

    async def unlock_door(self):
        await self.doorbell_manager.unlock_door()

    async def get_visit_history(self, db: AsyncSession, limit: int = 50, offset: int = 0):
        result = await db.execute(
            select(Visit).order_by(Visit.timestamp.desc()).limit(limit).offset(offset)
        )
        return result.scalars().all()