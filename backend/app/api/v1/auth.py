from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.google_oauth import exchange_code_for_tokens, generate_auth_url, get_user_info
from app.models.schemas import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.models.user import User
from app.services.auth_service import (
    create_access_token,
    create_user,
    get_user_by_email,
    get_user_by_google_id,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if await get_user_by_email(db, body.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = await create_user(db, body.email, body.password, body.full_name)
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, body.email)
    if not user or not user.hashed_password or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(user.id))


# ── Google OAuth ──────────────────────────────────────────────────────────────

@router.get("/google/login")
async def google_login(response: Response):
    auth_url, state = generate_auth_url()
    response.set_cookie("oauth_state", state, httponly=True, samesite="lax", max_age=600)
    return {"auth_url": auth_url}


@router.get("/google/callback", response_model=TokenResponse)
async def google_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
    oauth_state: str | None = Cookie(default=None),
):
    if not oauth_state or oauth_state != state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    tokens = await exchange_code_for_tokens(code)
    user_info = await get_user_info(tokens["access_token"])

    google_id = user_info["sub"]
    email = user_info.get("email", "")

    user = await get_user_by_google_id(db, google_id)
    if not user:
        user = await get_user_by_email(db, email)
        if user:
            user.google_id = google_id
            await db.commit()
        else:
            user = await create_user(
                db,
                email=email,
                full_name=user_info.get("name"),
                google_id=google_id,
                avatar_url=user_info.get("picture"),
                is_email_verified=True,
            )

    return TokenResponse(access_token=create_access_token(user.id))
