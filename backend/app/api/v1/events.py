from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services import event_manager
from app.services.auth_service import decode_token, get_user_by_id

router = APIRouter(prefix="/events", tags=["events"])


async def get_current_user_from_query(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> User:
    """SSE-specific auth: reads JWT from ?token= query param since EventSource cannot set headers."""
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.get("/stream")
async def stream_events(current_user: User = Depends(get_current_user_from_query)):
    """SSE endpoint — connect once, receive real-time events for the current user."""
    return StreamingResponse(
        event_manager.subscribe(current_user.id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
