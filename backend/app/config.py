from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/doorbell"

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "doorbell-photos"
    minio_secure: bool = False

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    public_api_url: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()