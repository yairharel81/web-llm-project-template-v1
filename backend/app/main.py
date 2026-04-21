from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router
from app.core.config import settings
from app.core.redis import close_redis, get_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_redis()  # pre-connect
    yield
    await close_redis()


app = FastAPI(
    title="Web LLM Template",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
