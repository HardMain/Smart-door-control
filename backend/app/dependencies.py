from functools import lru_cache
from fastapi import Header, HTTPException, status

from app.hardware import DoorbellManager, CameraService
from app.services import S3Service, DoorbellService
from app.config import settings

_doorbell_manager = None
_camera_service = None
_s3_service = None

def get_doorbell_manager() -> DoorbellManager:
    global _doorbell_manager
    if _doorbell_manager is None:
        _doorbell_manager = DoorbellManager()
    return _doorbell_manager

def get_camera_service() -> CameraService:
    global _camera_service
    if _camera_service is None:
        _camera_service = CameraService()
    return _camera_service

def get_s3_service() -> S3Service:
    global _s3_service
    if _s3_service is None:
        _s3_service = S3Service()
    return _s3_service

def get_doorbell_service() -> DoorbellService:
    return DoorbellService(
        doorbell_manager=get_doorbell_manager(),
        camera_service=get_camera_service(),
        s3_service=get_s3_service()
    )

def verify_api_key(x_api_key: str = Header(None)):
    if not settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured on server"
        )

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )

    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )

    return True