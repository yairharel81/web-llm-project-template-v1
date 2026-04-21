import asyncio
import logging
import os
from pathlib import Path
from typing import Protocol

from app.core.config import settings

logger = logging.getLogger(__name__)

LOCAL_STORAGE_DIR = Path("local_storage")


class StorageService(Protocol):
    async def upload_file(
        self, file_bytes: bytes, destination: str, content_type: str = "application/octet-stream"
    ) -> str: ...

    async def get_download_url(self, path: str, expiry_minutes: int = 60) -> str: ...

    async def delete_file(self, path: str) -> None: ...

    async def download_file(self, path: str) -> bytes: ...


class MockStorageService:
    def __init__(self) -> None:
        LOCAL_STORAGE_DIR.mkdir(exist_ok=True)

    async def upload_file(
        self, file_bytes: bytes, destination: str, content_type: str = "application/octet-stream"
    ) -> str:
        target = LOCAL_STORAGE_DIR / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(file_bytes)
        logger.info("[mock storage] Uploaded %s (%d bytes)", destination, len(file_bytes))
        return str(target)

    async def get_download_url(self, path: str, expiry_minutes: int = 60) -> str:
        return f"http://localhost:8000/static/{path}"

    async def delete_file(self, path: str) -> None:
        target = LOCAL_STORAGE_DIR / path
        if target.exists():
            target.unlink()
        logger.info("[mock storage] Deleted %s", path)

    async def download_file(self, path: str) -> bytes:
        return (LOCAL_STORAGE_DIR / path).read_bytes()


class GCSStorageService:
    def __init__(self) -> None:
        from google.cloud import storage

        self._client = storage.Client(project=settings.gcs_project_id)
        self._bucket = self._client.bucket(settings.gcs_bucket_name)

    async def upload_file(
        self, file_bytes: bytes, destination: str, content_type: str = "application/octet-stream"
    ) -> str:
        loop = asyncio.get_event_loop()
        blob = self._bucket.blob(destination)
        await loop.run_in_executor(
            None,
            lambda: blob.upload_from_string(file_bytes, content_type=content_type),
        )
        return f"gs://{settings.gcs_bucket_name}/{destination}"

    async def get_download_url(self, path: str, expiry_minutes: int = 60) -> str:
        import datetime

        loop = asyncio.get_event_loop()
        blob = self._bucket.blob(path)
        url = await loop.run_in_executor(
            None,
            lambda: blob.generate_signed_url(
                expiration=datetime.timedelta(minutes=expiry_minutes), method="GET"
            ),
        )
        return url

    async def delete_file(self, path: str) -> None:
        loop = asyncio.get_event_loop()
        blob = self._bucket.blob(path)
        await loop.run_in_executor(None, blob.delete)

    async def download_file(self, path: str) -> bytes:
        loop = asyncio.get_event_loop()
        blob = self._bucket.blob(path)
        return await loop.run_in_executor(None, blob.download_as_bytes)


def get_storage_service() -> StorageService:
    if settings.use_mock_storage:
        return MockStorageService()
    return GCSStorageService()
