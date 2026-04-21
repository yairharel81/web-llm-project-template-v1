import logging
from collections import defaultdict
from typing import Any, Protocol

from app.core.config import settings

logger = logging.getLogger(__name__)


class FirestoreService(Protocol):
    async def set(self, collection: str, doc_id: str, data: dict) -> None: ...
    async def get(self, collection: str, doc_id: str) -> dict | None: ...
    async def update(self, collection: str, doc_id: str, data: dict) -> None: ...
    async def delete(self, collection: str, doc_id: str) -> None: ...
    async def list(self, collection: str, filters: list[tuple] | None = None) -> list[dict]: ...


class MockFirestoreService:
    def __init__(self) -> None:
        self._store: dict[str, dict[str, dict]] = defaultdict(dict)

    async def set(self, collection: str, doc_id: str, data: dict) -> None:
        self._store[collection][doc_id] = {"id": doc_id, **data}
        logger.info("[mock firestore] set %s/%s", collection, doc_id)

    async def get(self, collection: str, doc_id: str) -> dict | None:
        return self._store[collection].get(doc_id)

    async def update(self, collection: str, doc_id: str, data: dict) -> None:
        if doc_id in self._store[collection]:
            self._store[collection][doc_id].update(data)

    async def delete(self, collection: str, doc_id: str) -> None:
        self._store[collection].pop(doc_id, None)

    async def list(self, collection: str, filters: list[tuple] | None = None) -> list[dict]:
        docs = list(self._store[collection].values())
        if filters:
            for field, op, value in filters:
                if op == "==":
                    docs = [d for d in docs if d.get(field) == value]
        return docs


class RealFirestoreService:
    def __init__(self) -> None:
        from google.cloud import firestore

        self._db = firestore.AsyncClient(
            project=settings.firestore_project_id,
            database=settings.firestore_database,
        )

    async def set(self, collection: str, doc_id: str, data: dict) -> None:
        await self._db.collection(collection).document(doc_id).set(data)

    async def get(self, collection: str, doc_id: str) -> dict | None:
        doc = await self._db.collection(collection).document(doc_id).get()
        return doc.to_dict() if doc.exists else None

    async def update(self, collection: str, doc_id: str, data: dict) -> None:
        await self._db.collection(collection).document(doc_id).update(data)

    async def delete(self, collection: str, doc_id: str) -> None:
        await self._db.collection(collection).document(doc_id).delete()

    async def list(self, collection: str, filters: list[tuple] | None = None) -> list[dict]:
        query = self._db.collection(collection)
        if filters:
            for field, op, value in filters:
                query = query.where(field, op, value)
        docs = await query.get()
        return [{"id": d.id, **d.to_dict()} for d in docs]


def get_firestore_service() -> FirestoreService:
    if settings.use_mock_firestore:
        return MockFirestoreService()
    return RealFirestoreService()
