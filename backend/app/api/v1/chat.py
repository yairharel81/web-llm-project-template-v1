from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.v1.deps import get_current_user
from app.core.gemini import get_gemini_service
from app.models.schemas import ChatRequest
from app.models.user import User

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/")
async def chat(body: ChatRequest, current_user: User = Depends(get_current_user)):
    """Non-streaming chat — returns full response."""
    service = get_gemini_service()
    messages = [{"role": m.role, "content": m.content} for m in body.messages]
    response = await service.chat(messages, body.system_prompt)
    return {"response": response}


@router.post("/stream")
async def chat_stream(body: ChatRequest, current_user: User = Depends(get_current_user)):
    """Streaming chat via SSE — yields tokens as they arrive from Gemini."""
    service = get_gemini_service()
    messages = [{"role": m.role, "content": m.content} for m in body.messages]

    async def generate():
        async for token in service.stream_chat(messages, body.system_prompt):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
