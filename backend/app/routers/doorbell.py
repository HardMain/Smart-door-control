from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from app.models import get_db
from app.schemas import VisitResponse
from app.dependencies import get_doorbell_service, get_s3_service, verify_api_key
from app.services import DoorbellService, S3Service

router = APIRouter(prefix="/doorbell", tags=["doorbell"])


@router.post("/ring", response_model=VisitResponse)
async def ring_doorbell(
    db: AsyncSession = Depends(get_db),
    doorbell_service: DoorbellService = Depends(get_doorbell_service)
):
    visit = await doorbell_service.handle_doorbell_press(db)
    return visit


@router.post("/unlock")
async def unlock_door(
    doorbell_service: DoorbellService = Depends(get_doorbell_service),
    _: bool = Depends(verify_api_key)
):
    await doorbell_service.unlock_door()
    return {"message": "Door unlocked successfully"}


@router.get("/history", response_model=List[VisitResponse])
async def get_history(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    doorbell_service: DoorbellService = Depends(get_doorbell_service)
):
    visits = await doorbell_service.get_visit_history(db, limit, offset)
    return visits


@router.get("/visit/{visit_id}/photo")
async def get_photo(
    visit_id: int,
    db: AsyncSession = Depends(get_db),
    s3_service: S3Service = Depends(get_s3_service)
):
    from sqlalchemy import select
    from app.models import Visit

    result = await db.execute(select(Visit).where(Visit.id == visit_id))
    visit = result.scalar_one_or_none()

    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    try:
        photo_data = s3_service.client.get_object(
            s3_service.bucket_name,
            visit.photo_url
        )

        return StreamingResponse(
            io.BytesIO(photo_data.read()),
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f"inline; filename=visit_{visit_id}.jpg"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Photo not found: {e}")