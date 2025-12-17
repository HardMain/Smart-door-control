import json
import logging
import io
from datetime import datetime, timedelta
from minio import Minio
from minio.error import S3Error

from app.config import settings

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )
        self.bucket_name = settings.minio_bucket_name
        self._ensure_bucket_exists()
        self._set_public_policy()

    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Bucket '{self.bucket_name}' created")
            else:
                logger.info(f"Bucket '{self.bucket_name}' already exists")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
            raise

    def _set_public_policy(self):
        try:
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
                    }
                ]
            }
            self.client.set_bucket_policy(self.bucket_name, json.dumps(policy))
            logger.info(f"Bucket '{self.bucket_name}' set to public read")
        except S3Error as e:
            logger.warning(f"Could not set bucket policy (may already exist): {e}")

    def get_public_url(self, object_name: str) -> str:
        protocol = "https" if settings.minio_secure else "http"
        return f"{protocol}://{settings.minio_endpoint}/{self.bucket_name}/{object_name}"

    def get_presigned_url(self, object_name: str, expires: int = 3600) -> str:
        try:
            return self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=expires)
            )
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise

    def get_photo_url(self, object_name: str, use_presigned: bool = False) -> str:
        return self.get_presigned_url(object_name) if use_presigned else self.get_public_url(object_name)
    
    async def upload_photo(self, photo_bytes: bytes) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        object_name = f"photos/{timestamp}.jpg"

        try:
            photo_stream = io.BytesIO(photo_bytes)
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=photo_stream,
                length=len(photo_bytes),
                content_type="image/jpeg"
            )
            logger.info(f"Photo uploaded to S3: {object_name}")
            return object_name
        except S3Error as e:
            logger.error(f"Error uploading photo to S3: {e}")
            raise