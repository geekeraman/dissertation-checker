"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Dissertation Checker"
    max_upload_size_mb: int = 50
    cors_origins: list[str] = ["http://localhost:5173"]
    temp_dir: str = "tmp"

    class Config:
        env_file = ".env"


settings = Settings()
