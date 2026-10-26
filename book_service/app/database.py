from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongo_url)
    return _client


def get_db():
    return get_client()[settings.mongo_db]


def get_books_collection():
    return get_db()["books"]


async def close_client():
    global _client
    if _client is not None:
        _client.close()
        _client = None
