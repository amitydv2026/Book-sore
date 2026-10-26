from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/orderdb"
    book_service_url: str = "http://book-service:8000"
    app_host: str = "0.0.0.0"
    app_port: int = 8001

    class Config:
        env_file = ".env"


settings = Settings()
