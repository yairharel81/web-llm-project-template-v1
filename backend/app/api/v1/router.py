from fastapi import APIRouter

from app.api.v1 import auth, chat, events, tasks, users

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(events.router)
router.include_router(chat.router)
router.include_router(tasks.router)
