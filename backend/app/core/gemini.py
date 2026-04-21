import asyncio
from collections.abc import AsyncGenerator
from typing import Protocol

from google import genai
from google.genai import types

from app.core.config import settings


class GeminiService(Protocol):
    async def chat(self, messages: list[dict], system_prompt: str = "") -> str: ...
    async def stream_chat(
        self, messages: list[dict], system_prompt: str = ""
    ) -> AsyncGenerator[str, None]: ...


class MockGeminiService:
    async def chat(self, messages: list[dict], system_prompt: str = "") -> str:
        last = messages[-1]["content"] if messages else "hello"
        return f"[mock] Echo: {last}"

    async def stream_chat(
        self, messages: list[dict], system_prompt: str = ""
    ) -> AsyncGenerator[str, None]:
        response = await self.chat(messages, system_prompt)
        for word in response.split():
            yield word + " "
            await asyncio.sleep(0.05)


class RealGeminiService:
    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.gemini_api_key)

    def _build_contents(self, messages: list[dict]) -> list[types.Content]:
        return [
            types.Content(
                role=msg["role"],
                parts=[types.Part(text=msg["content"])],
            )
            for msg in messages
        ]

    async def chat(self, messages: list[dict], system_prompt: str = "") -> str:
        loop = asyncio.get_event_loop()
        config = types.GenerateContentConfig(
            system_instruction=system_prompt or None,
        )
        response = await loop.run_in_executor(
            None,
            lambda: self._client.models.generate_content(
                model=settings.gemini_model,
                contents=self._build_contents(messages),
                config=config,
            ),
        )
        return response.text or ""

    async def stream_chat(
        self, messages: list[dict], system_prompt: str = ""
    ) -> AsyncGenerator[str, None]:
        loop = asyncio.get_event_loop()
        config = types.GenerateContentConfig(
            system_instruction=system_prompt or None,
        )
        contents = self._build_contents(messages)

        def _stream():
            return list(
                self._client.models.generate_content_stream(
                    model=settings.gemini_model,
                    contents=contents,
                    config=config,
                )
            )

        chunks = await loop.run_in_executor(None, _stream)
        for chunk in chunks:
            if chunk.text:
                yield chunk.text


def get_gemini_service() -> GeminiService:
    if settings.use_mock_gemini:
        return MockGeminiService()
    return RealGeminiService()
