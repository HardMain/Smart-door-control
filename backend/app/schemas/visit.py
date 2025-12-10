from datetime import datetime
from pydantic import BaseModel, computed_field

from app.config import settings


class VisitBase(BaseModel):
    timestamp: datetime


class VisitCreate(BaseModel):
    photo_url: str


class VisitResponse(VisitBase):
    id: int
    photo_url: str

    @computed_field
    @property
    def photo_download_url(self) -> str:
        if settings.public_api_url:
            return f"{settings.public_api_url}/doorbell/visit/{self.id}/photo"
        else:
            return f"/doorbell/visit/{self.id}/photo"

    class Config:
        from_attributes = True