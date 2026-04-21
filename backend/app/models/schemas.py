from datetime import datetime

from pydantic import BaseModel, EmailStr


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── User ──────────────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str | None
    avatar_url: str | None
    role: str
    is_email_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str  # "user" | "model"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    system_prompt: str = ""


# ── Tasks ─────────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str
    description: str | None = None


class TaskStatusUpdate(BaseModel):
    status: str  # "todo" | "in_progress" | "done"


class TaskOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── SSE Events ────────────────────────────────────────────────────────────────

class SSEEvent(BaseModel):
    type: str
    data: dict
