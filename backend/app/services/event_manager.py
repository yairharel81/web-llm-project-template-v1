"""Redis pub/sub → SSE bridge.

Publish an event:
    await event_manager.publish(user_id, SSEEvent(type="my_event", data={...}))

Subscribe in an SSE endpoint:
    async for event in event_manager.subscribe(user_id):
        yield event
"""
import asyncio
import json
import logging
from collections.abc import AsyncGenerator

from app.core.redis import get_redis
from app.models.schemas import SSEEvent

logger = logging.getLogger(__name__)

CHANNEL_PREFIX = "sse:"


def _channel(user_id: int) -> str:
    return f"{CHANNEL_PREFIX}{user_id}"


async def publish(user_id: int, event: SSEEvent) -> None:
    redis = await get_redis()
    await redis.publish(_channel(user_id), event.model_dump_json())


async def subscribe(user_id: int) -> AsyncGenerator[str, None]:
    """Yields SSE-formatted strings for use in a StreamingResponse."""
    redis = await get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe(_channel(user_id))
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=30)
            if message and message["type"] == "message":
                data = message["data"]
                yield f"data: {data}\n\n"
            else:
                yield ": ping\n\n"  # keep-alive
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        pass
    finally:
        await pubsub.unsubscribe(_channel(user_id))
        await pubsub.aclose()
